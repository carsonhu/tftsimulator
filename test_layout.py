"""The dummy layout (layout.py, restructure step 5): where the dummies stand and what reads it."""
import pytest

import set19items
from buildstore import load_build
from layout import Layout, around, distance, hex_distance, ricochet, ring
from set19champs import Draven, Varus
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


def placed(layout, n=8, attack_range=4):
    c = dummy()
    c.attack_range = attack_range
    ds = [dummy() for _ in range(n)]
    layout.place(c, ds)
    return c, ds


def test_rings():
    for radius, size in ((1, 6), (2, 12), (3, 18)):
        hexes = ring((4, 0), radius)
        assert len(set(hexes)) == size and all(hex_distance(h, (4, 0)) == radius for h in hexes)
        assert hexes[0] == (4 + radius, 0)  # starts behind the target


def test_default_is_the_old_line():
    # the target at attack range, then dummies 1, 2, 3 ... hexes from it in a line (B12), nearest first
    c, ds = placed(Layout())
    assert distance(c, ds[0]) == 4
    assert [distance(ds[0], d) for d in ds] == list(range(8))
    assert around(ds[0], 1, ds) == ds[1:2] and around(ds[0], 2, ds) == ds[1:3]
    c, ds = placed(Layout(), attack_range=1)
    assert distance(c, ds[0]) == 1


def test_counts_and_rings():
    lay = Layout(adjacent=6, two_hex=12)
    assert lay.count == 19
    c, ds = placed(lay, n=lay.count)
    assert len(around(ds[0], 1, ds)) == 6 and len(around(ds[0], 2, ds)) == 18
    assert ds[1:7] == around(ds[0], 1, ds)  # placement order is nearest the target first
    with pytest.raises(ValueError):
        Layout(adjacent=7)


def test_ricochets():
    c, ds = placed(Layout())
    assert ricochet(ds[0], [ds[0]], ds) == (ds[1], 1)
    assert ricochet(ds[1], [ds[0], ds[1]], ds) == (ds[2], 1)
    assert ricochet(ds[1], [ds[1]], ds) == (ds[2], 1)  # a tie goes on down the line
    c, ds = placed(Layout(), n=2)
    assert ricochet(ds[1], ds, ds) == (ds[0], 1)  # every dummy hit: the nearest other one
    c, ds = placed(Layout(), n=1)
    assert ricochet(ds[0], ds, ds) == (ds[0], 0)  # one dummy: back to it
    c, ds = placed(Layout(two_hex=0))
    assert ricochet(ds[1], [ds[0], ds[1]], ds) == (ds[2], 2)  # nobody 2 hexes from the target: a longer flight


def fight(champ, item=None, layout=None, seconds=12, n=8):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate([item] if item else [], [], champ, ds, seconds, layout=layout)
    return ds


def test_titanic_hydra_hits_every_neighbour():
    # TR_Add_EnemiesWithinHexRange 1 around the target: the target and every enemy next to it (owner, 2026-11-17)
    for adjacent in (0, 1, 3, 6):
        d = Draven(1, build=load_build(V))
        fight(d, set19items.TitanicHydra(), Layout(adjacent=adjacent), seconds=3)
        amount = d.hp.stat * 0.02 + d.atk.stat * d.bonus_ad.stat * 0.04
        first = [dm[0] for t, dm, *_ in d.dmgVector]
        assert first[:adjacent + 1] == [pytest.approx(amount)] * (adjacent + 1)
        assert first[adjacent + 1] != pytest.approx(amount)


def test_varus_splash_reads_the_layout():
    # one cast in 8 s (test_varus): 260 on the target, 50% (130) on each enemy next to it
    for adjacent in (0, 2, 6):
        v = Varus(1, build=load_build(V))
        fight(v, layout=Layout(adjacent=adjacent), seconds=8)
        rows = [round(dm[0], 2) for t, dm, *_ in v.dmgVector]
        assert rows.count(260) == 1 and rows.count(130) == adjacent

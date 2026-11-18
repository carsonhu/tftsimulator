"""The dummy layout (layout.py, restructure step 5): where the dummies stand and what reads it. One number, the
targets (owner, 2026-11-18): the target and targets - 1 enemies next to it."""
import pytest

import set19items
from buildstore import load_build
from layout import Layout, around, distance, hex_distance, ricochet, ring
from set19champs import Draven, Varus
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


def placed(layout, attack_range=4):
    c = dummy()
    c.attack_range = attack_range
    ds = [dummy() for _ in range(layout.count)]
    layout.place(c, ds)
    return c, ds


def test_rings():
    for radius, size in ((1, 6), (2, 12), (3, 18)):
        hexes = ring((4, 0), radius)
        assert len(set(hexes)) == size and all(hex_distance(h, (4, 0)) == radius for h in hexes)
        assert hexes[0] == (4 + radius, 0)  # starts behind the target


def test_targets_stand_next_to_the_target():
    # default 3: the target at attack range, 2 enemies next to it, each next to the one before
    c, ds = placed(Layout())
    assert len(ds) == 3 and distance(c, ds[0]) == 4
    assert [distance(ds[0], d) for d in ds] == [0, 1, 1] and distance(ds[1], ds[2]) == 1
    assert around(ds[0], 1, ds) == ds[1:]
    c, ds = placed(Layout(), attack_range=1)
    assert distance(c, ds[0]) == 1
    c, ds = placed(Layout(7))
    assert len(around(ds[0], 1, ds)) == 6
    for bad in (0, 8):
        with pytest.raises(ValueError):
            Layout(bad)


def test_one_target_has_a_spare_out_of_play():
    c, ds = placed(Layout(1))
    assert len(ds) == 2 and not ds[1].in_play
    assert around(ds[0], 99, ds) == [] and ricochet(ds[0], [ds[0]], ds) == (ds[0], 0)


def test_ricochets():
    c, ds = placed(Layout())
    assert ricochet(ds[0], [ds[0]], ds) == (ds[1], 1)
    assert ricochet(ds[1], [ds[0], ds[1]], ds) == (ds[2], 1)
    assert ricochet(ds[2], ds, ds) == (ds[0], 1)  # every dummy hit: the nearest other one, ties on in order


def fight(champ, item=None, layout=None, seconds=12):
    ds = [dummy() for _ in range((layout or Layout()).count)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate([item] if item else [], [], champ, ds, seconds, layout=layout)
    return ds


def test_titanic_hydra_hits_one_neighbour_whatever_the_targets():
    # the target and one enemy next to it (owner, 2026-11-18), with 1, 3 or 7 targets
    for targets in (1, 3, 7):
        d = Draven(1, build=load_build(V))
        fight(d, set19items.TitanicHydra(), Layout(targets), seconds=3)
        amount = d.hp.stat * 0.02 + d.atk.stat * d.bonus_ad.stat * 0.04
        first = [dm[0] for t, dm, *_ in d.dmgVector]
        assert first[:2] == [pytest.approx(amount)] * 2 and first[2] != pytest.approx(amount)


def test_varus_splash_reads_the_targets():
    # one cast in 8 s (test_varus): 260 on the target, 50% (130) on each other target
    for targets in (1, 3, 7):
        v = Varus(1, build=load_build(V))
        fight(v, layout=Layout(targets), seconds=8)
        rows = [round(dm[0], 2) for t, dm, *_ in v.dmgVector]
        assert rows.count(260) == 1 and rows.count(130) == targets - 1

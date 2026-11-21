"""The dummy layout (layout.py, restructure step 5): where the dummies stand and what reads it. One number, the
targets (owner, 2026-11-18): the target and targets - 1 enemies next to it, and no others in play (owner, 2026-11-19:
the one always 2 hexes behind is gone). Default 2 targets: the target and one behind it."""
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
    # default 2: the target at attack range and one enemy behind it, in a line with the champion
    c, ds = placed(Layout())
    assert [d.hex for d in ds] == [(4, 0), (5, 0)] and all(d.in_play for d in ds)
    assert [distance(ds[0], d) for d in ds] == [0, 1]
    assert around(ds[0], 1, ds) == ds[1:2] and around(ds[0], 2, ds) == ds[1:]
    c, ds = placed(Layout(), attack_range=1)
    assert distance(c, ds[0]) == 1 and [d.hex for d in ds] == [(1, 0), (2, 0)]
    # more targets fill the hexes next to the target, and they are every enemy in play
    c, ds = placed(Layout(3))
    assert [distance(ds[0], d) for d in ds] == [0, 1, 1]
    c, ds = placed(Layout(7))
    assert len(around(ds[0], 1, ds)) == 6 and len(ds) == 7
    # a melee unit takes one of the hexes next to the target: the 7th target stands 2 away
    c, ds = placed(Layout(7), attack_range=1)
    assert len(around(ds[0], 1, ds)) == 5 and distance(ds[0], ds[-1]) == 2
    for bad in (0, 10):  # up to 9 (Vladimir's TARGETS_MAX; the page's cap is otherwise 7)
        with pytest.raises(ValueError):
            Layout(bad)
    c, ds = placed(Layout(9))  # 9 fit on the 2 rings round the target
    assert len({d.hex for d in ds}) == 9 and all(d.in_play for d in ds)


def test_one_target_is_the_only_enemy_in_play():
    # the target alone (owner, 2026-11-19: Jhin with 1 target hits 1), and a spare out of play (Titanic Hydra's
    # neighbour) that nothing else sees
    c, ds = placed(Layout(1))
    assert len(ds) == 2 and [d.in_play for d in ds] == [True, False]
    assert around(ds[0], 99, ds) == []
    assert ricochet(ds[0], [ds[0]], ds) == (ds[0], 0)


def test_ricochets():
    c, ds = placed(Layout(3))
    assert ricochet(ds[0], [ds[0]], ds) == (ds[1], 1)
    assert ricochet(ds[1], [ds[0], ds[1]], ds) == (ds[2], 1)
    assert ricochet(ds[2], ds, ds)[1] == 1  # every dummy hit: the nearest other one


def fight(champ, item=None, layout=None, seconds=12):
    ds = [dummy() for _ in range((layout or Layout()).count)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate([item] if item else [], [], champ, ds, seconds, layout=layout)
    return ds


def test_titanic_hydra_hits_one_neighbour_whatever_the_targets():
    # the target and one enemy next to it (owner, 2026-11-18), with 1, 3 or 7 targets (with 1, the spare)
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


def test_line_shape_stands_behind_the_target():
    # "line" (a champion's TARGETS_SHAPE): each enemy 1 hex further behind the target, in line with the champion
    c, ds = placed(Layout(3, "line"))
    assert [d.hex for d in ds] == [(4, 0), (5, 0), (6, 0)]
    with pytest.raises(ValueError):
        Layout(2, "ring")


def test_jhin_gets_a_line_of_at_most_3():
    import sim_entry
    lay = sim_entry._layout({"champ": "Jhin", "layout": {"targets": 7}})
    assert (lay.targets, lay.shape) == (3, "line")
    jhin = next(c for c in sim_entry.get_catalog()["champions"] if c["name"] == "Jhin")
    assert (jhin["targetsMax"], jhin["targetsShape"]) == (3, "line")
    lay = sim_entry._layout({"champ": "Kayn", "layout": {"targets": 7}})
    assert (lay.targets, lay.shape) == (2, "line")
    assert sim_entry._layout({"champ": "Kayn"}).targets == 1  # his default (owner, 2026-11-19)
    lay = sim_entry._layout({"champ": "Bard", "layout": {"targets": 7}})  # a wave: the cluster, every target
    assert (lay.targets, lay.shape) == (7, "cluster")
    assert sim_entry._layout({"champ": "Ezreal", "layout": {"targets": 7}}).targets == 7


def test_jhin_with_one_target_hits_only_it():
    # owner, 2026-11-19: his piercing shots after ascension have nobody behind the target to pass through; with 3,
    # the two behind it take pierced damage
    import sim_entry
    cfg = {"champ": "Jhin", "level": 1, "items": ["NoItem"] * 3, "buffs": [], "slice": "Craftable",
           "layout": {"targets": 1}, "enemy": {"hp": 1800, "armor": 100, "mr": 100}, "seconds": 30, "row": 0}
    assert {d["to"] for d in sim_entry.run_trace(cfg)["damage"]} == {1}  # units[0] is Jhin
    cfg["layout"] = {"targets": 3}
    assert {d["to"] for d in sim_entry.run_trace(cfg)["damage"]} == {1, 2, 3}


def test_kayn_swipe_reaches_two_hexes():
    # owner, 2026-11-19: with 2 targets his swipe hits the target and the enemy behind it (2 hexes from him)
    import sim_entry
    cfg = {"champ": "Kayn", "level": 1, "items": ["NoItem"] * 3, "buffs": [], "slice": "Craftable",
           "layout": {"targets": 2}, "enemy": {"hp": 1800, "armor": 100, "mr": 100}, "seconds": 30, "row": 0}
    assert {d["to"] for d in sim_entry.run_trace(cfg)["damage"]} == {1, 2}  # units[0] is Kayn
    cfg["layout"] = {"targets": 1}
    assert {d["to"] for d in sim_entry.run_trace(cfg)["damage"]} == {1}

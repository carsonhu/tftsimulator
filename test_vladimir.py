"""Vladimir (champions/Vladimir.md): two cast timelines from GA_Vladimir19_Spell (D1), checked against the owner's
60 fps VOD7 (22-23-46-350, rounds 4-2 and 4-3: Vladimir 1-star, Bloodthirster, Prodigy Emblem, Prodigy (5)).

VOD7 was played on client 6011486: the panel's 8 mana regen = Prodigy (5) member 6 + 1 + the emblem's 1."""
import pytest

import set19buffs
import set19items
from buildstore import load_build
from layout import Layout
from set19champs import Vladimir
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.6011486.Set19.Shipping.pbe'


class LoggedVladimir(Vladimir):
    def __init__(self, level=1, build=V):
        super().__init__(level, build=load_build(build))
        self.mana_log, self.cast_log = [], []
        self.stage = 4

    def addMana(self, amount, time=None):
        before = self.curMana
        super().addMana(amount, time)
        self.mana_log.append((self.tick, amount, before, self.curMana))

    def performAbility(self, opponents, items, time):
        self.cast_log.append((self.tick, self.big_cast()))
        super().performAbility(opponents, items, time)


def fight(v, items=(), buffs=(), seconds=25, targets=3):
    lay = Layout(targets, Vladimir.TARGETS_SHAPE, Vladimir.TARGETS_RINGS)
    ds = [dummy() for _ in range(lay.count)]
    for d in ds:
        d.armor.base, d.mr.base = 0, 0
    Simulator().simulate(list(items), list(buffs), v, ds, seconds, layout=lay)
    rows = {}
    for t, d, *_ in v.dmgVector:
        rows.setdefault(round(t * 30), []).append(round(d[0], 4))
    return ds, rows


def test_two_timelines_from_the_build():
    v = LoggedVladimir(1)
    assert v.locks[v.NORMAL] == pytest.approx((30 / 30, 29 / 30))  # CastNormal 'Unlock' 0.9503 s
    assert v.locks[v.SPECIAL] == pytest.approx((55 / 30, 54 / 30))  # CastSpecial 'Unlock' 1.8 s
    assert round(v.cast_at * 30, 3) == 4.275 and round(v.drop_at * 30, 3) == 53.889


def test_vod7_every_fifth_cast_is_the_chandelier():
    # VOD7 4-2: the 5th cast's lock 47.5-55 ticks, the 6th and 7th <= 30; regen 8/s, attacks +10 at AS 0.90
    v = LoggedVladimir(1)
    fight(v, items=[set19items.Bloodthirster(), set19items.ProdigyEmblem()], buffs=[set19buffs.Prodigy(5)])
    assert v.manaRegen.stat == 8 and round(v.aspd.stat, 2) == 0.9 and v.hp.stat == 1300  # the panel
    assert [big for _, big in v.cast_log][:7] == [False] * 4 + [True] + [False] * 2
    attacks = [t for t, a, before, after in v.mana_log if a == 10]
    for cast, big in v.cast_log[:6]:
        fill = max(t for t, a, before, after in v.mana_log if t <= cast and after > before)
        assert cast == fill + 1
        lock = 54 if big else 29
        gain = next(t for t, a, before, after in v.mana_log if t > cast and after > before)
        assert cast + lock <= gain <= cast + lock + 8  # the next regen step after the lock
        # the next attack's mana after a regen fill: VOD7 44 ticks (normal), 68.5 (5th cast)
        assert next(t for t in attacks if t > cast) - fill == (69 if big else 44)


def test_normal_cast_hits_three_and_wraps():
    # MagicDamageCalc1 = APDamage x AP on the target and the 2 nearest, at 'Cast' (5 ticks: ticks_up(4.275));
    # GetRepeatingListFromTargetData: one enemy takes all 3
    for targets, expect in ((3, [0, 1, 2]), (2, [0, 1, 0]), (1, [0, 0, 0])):
        v = LoggedVladimir(1)
        ds, rows = fight(v, seconds=4, targets=targets)
        cast = v.cast_log[0][0]
        dmg = v.row('APDamage', star=1) * v.ap.stat
        assert rows[cast + 5] == [pytest.approx(dmg)] * 3
        assert [ds.index(d) for d in v.main_targets(ds[0])] == expect


def test_chandelier_falls_off_by_ring():
    # every enemy: ChandelierDamage x AP x max(1%, 1 - 10% x ring), linear (the script's FMax(min, 1 - 0.1 x n)); rings
    # by the owner's table (2026-11-20): the target at 0, then 1, 1, 2, 2, 3, 3, the rest 4; fewer drop the furthest
    for targets, shares in ((3, [1, 0.9, 0.9]), (7, [1, 0.9, 0.9, 0.8, 0.8, 0.7, 0.7]),
                            (9, [1, 0.9, 0.9, 0.8, 0.8, 0.7, 0.7, 0.6, 0.6])):
        v = LoggedVladimir(1)
        ds, rows = fight(v, items=[set19items.ProdigyEmblem()], buffs=[set19buffs.Prodigy(5)], targets=targets)
        cast = next(t for t, big in v.cast_log if big)
        full = v.row('ChandelierDamage', star=1) * v.ap.stat
        assert sorted(rows[cast + 54], reverse=True) == pytest.approx([full * x for x in shares])


def test_page_targets_default_seven_at_least_three():
    # owner, 2026-11-20: default 7, minimum 3 (he Captivates 3), at most 9
    import json
    import sim_entry
    from test_sim_entry import cfg
    meta = next(c for c in json.loads(sim_entry.catalog_json())['champions'] if c['name'] == 'Vladimir')
    assert (meta['targetsDefault'], meta['targetsMin'], meta['targetsMax']) == (7, 3, 9)
    for asked, got in ((1, 3), (7, 7), (9, 9), (12, 9)):
        assert sim_entry._layout(cfg(champ='Vladimir', layout={'targets': asked})).targets == got


def test_targets_stand_on_the_rings():
    # owner, 2026-11-20: the target at the chandelier's centre, then a pair at 1, 2, 3 and 4 hexes on two arms from it
    # (compact: the front row from the corner unit and the diagonal back); his main cast's others = the adjacent pair
    from layout import distance
    v = LoggedVladimir(1)
    ds, rows = fight(v, seconds=1, targets=9)
    assert [distance(ds[0], d) for d in ds] == [0, 1, 1, 2, 2, 3, 3, 4, 4]
    assert len({d.hex for d in ds}) == 9 and (0, 0) not in {d.hex for d in ds}
    arms = [d.hex for d in ds[1:]]  # two straight lines from the target, 60 degrees apart
    assert arms[0::2] == [(3, 0), (4, 0), (5, 0), (6, 0)] and arms[1::2] == [(3, -1), (4, -2), (5, -3), (6, -4)]
    assert v.main_targets(ds[0]) == ds[:3]

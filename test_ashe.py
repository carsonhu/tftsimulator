"""Ashe end to end (champions/Ashe.md): numbers from build rls-19.1.0.5973071; rhythm against the owner's 60 fps PBE
VOD5 (0-57-11-500, f13727-15020: Ashe 1-star with Tear of the Goddess and Quicksilver)."""
import pytest

import set19items
from buildstore import load_build
from events import ONHIT_AFTER
from item import Item
from set19champs import Ashe
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


class LoggedAshe(Ashe):
    def __init__(self, level=1):
        super().__init__(level, build=load_build(V))
        self.mana_log, self.casts, self.releases = [], [], []

    def addMana(self, amount, time=None):
        before = self.curMana
        super().addMana(amount, time)
        self.mana_log.append((self.tick, amount, before, self.curMana))

    def performAbility(self, opponents, items, time):
        super().performAbility(opponents, items, time)
        self.casts.append((self.tick, round(self.timing.cast_lock * 30)))

    def onLaunch(self, opponents, items):
        super().onLaunch(opponents, items)
        self.releases.append((self.tick, self._this_empowered))


class OnHitLog(Item):
    """Records each on-hit event's effectiveness."""
    LISTENS = {ONHIT_AFTER: frozenset()}

    def __init__(self):
        super().__init__("OnHitLog")
        self.seen = []

    def performAbility(self, phase, time, champion, input_=0):
        self.seen.append((champion.tick, input_.effectiveness))
        return input_


def fight(c, items=(), buffs=(), seconds=12, n=8, tear=False):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    if tear:
        c.manaRegen.modify("+", 1)  # Tear of the Goddess's 1 regen (components are not registered)
    Simulator().simulate(list(items), list(buffs), c, ds, seconds)
    return [(round(t * 30), round(d[0], 4)) for t, d, *_ in c.dmgVector]


def attacks(c):
    return [t for t, a, before, after in c.mana_log if a == 10 and after > before]


def test_build_numbers_and_timing():
    a = LoggedAshe(1)
    assert (a.curMana, a.fullMana.stat, a.aspd.stat, a.attack_range, a.atk.stat) == (20, 60, 0.75, 5, 50)
    t = a.timing
    assert [(v['selector'], v['launch']) for v in t.variants] == [(1, 0.2971), (2, 0.2971), (3, 0)]
    assert t.rate_threshold == 1.0 and not t.lock_scales_with_as  # G20 from the build
    assert [x[1] for x in a.arrows] == [0, 0.075, 0.15]
    # CT_Ashe19_ASToCastSpeed: 0.3333 s up to 1 AS, linear to 0.15 s at 5 AS
    assert a.table_value('CT_Ashe19_ASToCastSpeed', 'ASToCastTime', 0.93) == pytest.approx(0.33333, abs=1e-5)
    assert a.table_value('CT_Ashe19_ASToCastSpeed', 'ASToCastTime', 3) == pytest.approx(0.24167, abs=1e-5)


def test_vod5_rhythm():
    # VOD5 (ticks from combat start): attacks +10 at 5.5, 41, 74.5, 108 (fills); the mana lock lifts 123.5 ticks
    # after the filling attack (engine 125: 11-tick cast, 6 flurries ~22 ticks apart at AS 1.3-1.4); the first normal
    # attack 149 after it (engine 148); the next 28 later (engine 30)
    a = LoggedAshe(1)
    fight(a, items=[set19items.Quicksilver()], tear=True)
    assert attacks(a)[:4] == [5, 40, 73, 106]
    fill = 106
    assert a.casts[0] == (107, 11)
    flurries = [t for t, e in a.releases if e]
    assert len(flurries) >= 6 and flurries[:6] == [119, 141, 164, 186, 208, 230]
    # the lock ends the tick after the 6th flurry: the first mana after the cast comes after it
    assert next(t for t, x, before, after in a.mana_log if t > 107 and after > before) > 230
    assert attacks(a)[4] - fill == 148


def test_flurries_deal_arrows_with_reduced_on_hit():
    # each flurry: 3 arrows of 33 x AD at 1 star, every one applying on-hit effects at 0.6; normal attacks at 1
    a, log = LoggedAshe(1), OnHitLog()
    rows = fight(a, items=[log], seconds=12)
    cast = a.casts[0][0]
    arrows = [(t, d) for t, d in rows if t > cast and d == 33]
    flurries = [t for t, e in a.releases if e]
    assert len(arrows) == 3 * len([t for t in flurries if t < rows[-1][0] - 5])
    assert sum(1 for t, e in log.seen if e == 0.6) == len(arrows)  # every arrow, and only arrows, at 0.6
    assert {e for t, e in log.seen} == {0.6, 1.0}
    # the empower adds 30% + 20% x AP attack speed while it lasts
    b = LoggedAshe(1)
    fight(b, seconds=2)
    base = b.aspd.stat
    c = LoggedAshe(1)
    c.curMana = 60
    fight(c, seconds=1)
    assert c.aspd.stat == pytest.approx(base + 0.75 * 0.5)

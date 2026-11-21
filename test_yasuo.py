"""Yasuo (champions/Yasuo.md): GA_Yasuo19_Spell (D1) on build rls-19.1.0.6011486, checked against the owner's 60 fps
VOD8 (13-2-9-650: Yasuo 1 star with Hand of Justice, Infinity Edge and Infinity Force, Slayer (4), at 4-1 and 4-3)."""
import set19buffs
import set19items
from buildstore import load_build
from layout import Layout
from set19champs import Yasuo
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.6011486.Set19.Shipping.pbe'


class LoggedYasuo(Yasuo):
    def __init__(self, level=1):
        super().__init__(level, build=load_build(V))
        self.casts, self.mana_log = [], []

    def addMana(self, amount, time=None):
        super().addMana(amount, time)
        self.mana_log.append((self.tick, amount, self.curMana))

    def performAbility(self, opponents, items, time):
        self.casts.append(self.tick)
        super().performAbility(opponents, items, time)


def fight(y, items=(), buffs=(), seconds=10, targets=2):
    lay = Layout(targets)
    ds = [dummy() for _ in range(lay.count)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate(list(items), list(buffs), y, ds, seconds, layout=lay)
    rows = {}
    for t, d, *_ in y.dmgVector:
        rows.setdefault(round(t * 30), []).append(round(d[0], 4))
    return ds, rows


def vod8_yasuo():
    y = LoggedYasuo(1)
    y.stage = 4
    items = [set19items.HandOfJustice(), set19items.InfinityEdge(), set19items.InfinityForce()]
    return y, items, [set19buffs.Slayer(4)]


def test_build_numbers():
    y = LoggedYasuo(1)
    assert (y.curMana, y.fullMana.stat, y.aspd.stat, y.attack_range, y.atk.stat, y.hp.stat) == (0, 30, 0.85, 1, 60, 1100)
    # End Spell at each chrono's 'Unlock': NoDash 0.6409 s, UltKnockup 1.4317 s (mana lock; cast lock + 1 tick)
    assert {k: (round(c * 30), round(m * 30)) for k, (c, m) in y.locks.items()} == {
        Yasuo.BASE: (21, 20), Yasuo.ULT: (44, 43)}
    assert y.casts_to_ult == 3


def test_vod8_panel_bonus_ad():
    # VOD8 4-1 / 4-3 panel: bonus AD 108% = the items' 101% + Heartsteel (1)'s fielded Kayn 7% (KaynAD; owner,
    # 2026-11-21: Kayn was on the board)
    y, items, buffs = vod8_yasuo()
    fight(y, items, buffs + [set19buffs.Heartsteel(1, 1)], seconds=0.1)
    assert y.numAttacks == 0 and round(y.bonus_ad.stat, 3) == 2.08


def test_vod8_4_1_rhythm():
    # VOD8 4-1 (f65152-66266): AS 1.62, 1,400 HP, crit 80%; attacks 36-38 frames apart; casts 136 / 137 frames apart;
    # the banked overflow 21 ticks after the filling attack (NoDash), 44 ticks for every 3rd cast (the ult); the next
    # attack 10 ticks after the lock ends
    y, items, buffs = vod8_yasuo()
    fight(y, items, buffs, seconds=12)
    assert round(y.aspd.stat, 3) == 1.615 and y.hp.stat == 1400 and round(y.crit.stat, 2) == 0.8
    assert [b - a for a, b in zip(y.casts, y.casts[1:])][:2] == [68, 68]
    attacks = [t for t, amt, _ in y.mana_log if amt == 10]
    for cast, lock in zip(y.casts[:3], (20, 20, 43)):
        assert min(t for t in attacks if t > cast) - (cast + lock) == 10


def test_stab_line_and_ult():
    # the stab hits the target and the enemy behind it (a 2-hex line); every 3rd cast: two knockup hits of half
    # UltDamageAD x AD on the target, then the slam on the enemies within 1 hex of it
    y = LoggedYasuo(1)
    _, rows = fight(y, seconds=20)
    first, ult = y.casts[0], y.casts[2]
    stab = 180 * 1.0  # SlashDamageAD x AD (1 star, no bonus AD), dummies without armor
    assert rows[first + 6] == [stab, stab]  # 'Damage' 0.194 s -> tick 6
    assert rows[ult + 6] == [200.0] and rows[ult + 16] == [200.0]  # 0.5 x 400, 'Damage1' / 'Damage2'
    assert rows[ult + 35] == [210.0, 210.0]  # 'Slam' 1.1514 s: 180 x AD + 30 x AP (both multipliers 1)
    assert y.stacks == 0


def test_one_target():
    y = LoggedYasuo(1)
    _, rows = fight(y, seconds=6, targets=1)
    assert rows[y.casts[0] + 6] == [180.0]

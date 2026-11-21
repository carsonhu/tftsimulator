"""Vayne (champions/Vayne.md): GA_Vayne19_Spell (D1) on build rls-19.1.0.6011486, checked against the owner's 60 fps
VOD8 (13-2-9-650: Vayne 1 star with Kraken's Fury, Rock and Trickshot inactive, at 4-2)."""
import set19buffs
import set19items
from buildstore import load_build
from layout import Layout
from set19champs import Vayne
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.6011486.Set19.Shipping.pbe'


class LoggedVayne(Vayne):
    def __init__(self, level=1):
        super().__init__(level, build=load_build(V))
        self.casts, self.launch_log, self.mana_log = [], [], []

    def performAbility(self, opponents, items, time):
        self.casts.append(self.tick)
        super().performAbility(opponents, items, time)

    def onLaunch(self, opponents, items):
        super().onLaunch(opponents, items)
        self.launch_log.append((self.tick, self._planned))

    def addMana(self, amount, time=None):
        before = self.curMana
        super().addMana(amount, time)
        self.mana_log.append((self.tick, amount, self.curMana - before))


def fight(v, items=(), buffs=(), seconds=10, targets=2, hp=1000):
    lay = Layout(targets)
    ds = [dummy() for _ in range(lay.count)]
    for d in ds:
        d.armor.base = d.mr.base = 0
        d.hp.base = hp
    Simulator().simulate(list(items), list(buffs), v, ds, seconds, layout=lay)
    rows = {}
    for t, d, *_ in v.dmgVector:
        rows.setdefault(round(t * 30), []).append(round(d[0], 4))
    return ds, rows


def test_build_numbers():
    v = LoggedVayne(1)
    assert (v.curMana, v.fullMana.stat, v.aspd.stat, v.attack_range, v.atk.stat, v.hp.stat) == (0, 50, 0.8, 5, 62, 850)
    assert v.row('NumAttacks') == 3
    # selectors: SequentialAttack (0.3007 s of 1.6333 s), UltTumbleAttack (0.2323 s of 1.3 s), UltAttack (0.3677 s of
    # 1.6667 s, PlayRateScalingThreshold 0.72)
    assert [(x['selector'], round(x['launch'], 4), round(x['length'], 4), x['rate_threshold'])
            for x in v.timing.variants] == [(1, 0.3007, 1.6333, None), (2, 0.2323, 1.3, None), (3, 0.3677, 1.6667, 0.72)]


def test_vod8_4_2_cast():
    # VOD8 4-2 (Kraken's Fury: AS 0.88; its +3.5% AD per launch marks every launch on the panel): launches 68 frames
    # apart (f70722, 70790, 70858, 70927, 70995 = the filling one, mana +10 at each); the cast one tick later; the
    # first bolt launched at f71055 = 29 ticks after the cast (tumble 7 + 14 at CastSpeed 1.1, + 1, then the
    # UltTumbleAttack windup 7); no mana from the three bolts (f71055, 71177, 71253), +10 again at the 4th (f71319)
    v = LoggedVayne(1)
    fight(v, [set19items.KrakensFury()], seconds=12)
    assert round(v.aspd.stat, 3) == 0.88
    launches = [t for t, _ in v.launch_log]
    assert [b - a for a, b in zip(launches, launches[1:5])] == [34, 34, 34, 34]
    cast = v.casts[0]
    assert cast == launches[4] + 1
    bolts = [t for t, sel in v.launch_log if sel != Vayne.NORMAL]
    assert [sel for t, sel in v.launch_log if t >= cast][:4] == [Vayne.ULT_TUMBLE, Vayne.ULT, Vayne.ULT, Vayne.NORMAL]
    assert bolts[0] - cast == 29
    gained = {t: g for t, amount, g in v.mana_log if amount == 10}
    assert [gained[t] for t in bolts] == [0, 0, 0]
    assert gained[min(t for t in launches if t > bolts[-1])] == 10
    # Kraken's Fury hears every custom launch (the panel's AD % rose at each bolt): a stack per launch, bolts included
    assert round(v.bonus_ad.stat, 3) == round(1.1 + len(launches) * 0.035, 3)


def test_vod8_panel_bonus_ad():
    # VOD8 4-2 planning panel: bonus AD 17% = Kraken's Fury 10% + Heartsteel (1)'s fielded Kayn 7% (KaynAD; owner,
    # 2026-11-21: Kayn was on the board), before any launch
    v = LoggedVayne(1)
    fight(v, [set19items.KrakensFury()], [set19buffs.Heartsteel(1, 1)], seconds=0.1)
    assert v.launch_log == [] and round(v.bonus_ad.stat, 3) == 1.17 and round(v.aspd.stat, 3) == 0.88


def test_bolt_damage():
    # each bolt: DamageAD x AD physical + PercentMaxHealthDamage x the target's max Health true, on the target only
    v = LoggedVayne(1)
    _, rows = fight(v, seconds=12, hp=2000)
    bolts = [t for t, sel in v.launch_log if sel != Vayne.NORMAL]
    flight = v.chrono_projectile_ticks(Vayne.BOLT, 'Bolt', v.target_hexes())
    assert rows[bolts[0] + flight] == [165.0, 30.0]  # 165 x AD 1.0; 1.5% of 2000


def test_trickshot_ricochet():
    # Trickshot (2): one ricochet at RichochetDamage 0.22, both parts, from the target to the nearest other dummy
    v = LoggedVayne(1)
    _, rows = fight(v, buffs=[set19buffs.Trickshot(2)], seconds=12, hp=2000)
    bolts = [t for t, sel in v.launch_log if sel != Vayne.NORMAL]
    land = bolts[0] + v.chrono_projectile_ticks(Vayne.BOLT, 'Bolt', v.target_hexes())
    bounce = land + v.chrono_projectile_ticks(Vayne.BOUNCE, 'Bolt', 1)
    assert rows[land] == [165.0, 30.0]
    assert rows[bounce] == [round(165 * 0.22, 4), round(30 * 0.22, 4)]


def test_cast_speed_caps_at_two():
    # CastSpeed = clamp(AS / base, 1, 2): at AS 2.4 the tumble's Unlock plays twice as fast: 7 + 8 + 1 ticks
    v = LoggedVayne(1)
    v.aspd.modify('MultiplyAdditive', 3.0)
    assert v.cast_speed() == 2.0
    v.performAbility([], [], 0)
    assert round(v.timing.cast_lock * 30) == 16

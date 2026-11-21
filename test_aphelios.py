"""Aphelios (champions/Aphelios.md): GA_Aphelios19_Ability and GA_Aphelios19_CombatPassive (D1) on build
rls-19.1.0.6011486, checked against the owner's 60 fps VOD8 (13-2-9-650: Aphelios 1 star, Heartsteel (3), with Kraken's
Fury at 5-5 and Guinsoo's Rageblade + Kraken's Fury at 6-1)."""
import layout
import set19buffs
import set19items
from buildstore import load_build
from layout import Layout
from set19champs import Aphelios
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.6011486.Set19.Shipping.pbe'


class LoggedAphelios(Aphelios):
    def __init__(self, level=1):
        super().__init__(level, build=load_build(V))
        self.casts, self.launch_log, self.mana_log = [], [], []

    def performAbility(self, opponents, items, time):
        self.casts.append(self.tick)
        super().performAbility(opponents, items, time)

    def onLaunch(self, opponents, items):
        super().onLaunch(opponents, items)
        self.launch_log.append((self.tick, round(self.aspd.stat, 3), self.chakrams))

    def addMana(self, amount, time=None):
        before = self.curMana
        super().addMana(amount, time)
        self.mana_log.append((self.tick, amount, self.curMana - before))


def fight(a, items=(), buffs=(), seconds=24, targets=2, hp=10000):
    lay = Layout(targets)
    ds = [dummy() for _ in range(lay.count)]
    for d in ds:
        d.armor.base = d.mr.base = 0
        d.hp.base = hp
    Simulator().simulate(list(items), list(buffs), a, ds, seconds, layout=lay)
    rows = {}
    for t, d, *_ in a.dmgVector:
        rows.setdefault(round(t * 30), []).append(round(d[0], 4))
    return ds, rows


def test_build_numbers():
    a = LoggedAphelios(1)
    assert (a.curMana, a.fullMana.stat, a.aspd.stat, a.attack_range, a.atk.stat, a.hp.stat) == (40, 180, 0.8, 5, 60, 900)
    # Crescendum's LaunchAttack (ledger P15), not the build's attack_launch 0.3 (the Empowered group's)
    assert round(a.timing.launch, 4) == 0.3342
    assert round(a.timing.cast_lock * 30) == 66  # 'Unlock' 2.1371 s -> tick 65, + 1


def test_vod8_5_5_panel_attack_speed():
    # VOD8 5-5 planning panel: AS 0.93 = 0.8 x (1 + Kraken's Fury 10% + Heartsteel's ApheliosAS 6%, his own bonus as a
    # fielded member), bonus AD 10% (Kraken's; no Kayn this time)
    a = LoggedAphelios(1)
    fight(a, [set19items.KrakensFury()], [set19buffs.Heartsteel(3, 0)], seconds=0.1)
    assert round(a.aspd.stat, 2) == 0.93 and round(a.bonus_ad.stat, 3) == 1.1


def test_vod8_5_5_cast():
    # VOD8 5-5 (Kraken's +3.5% AD per launch marks each launch): 14 launches fill the bar (40 + 14 x 10); the panel's
    # AS shows 1.53 at f109005 (the Unlock's AS buff, 66.5 ticks after the 14th launch at f108872), the next launch at
    # f109026 = 77 ticks after the 14th (engine 77), then AS 1.65 (Kraken's 15th stack: +15% AS) and 1.05 at f109244
    # when the buff ends (186 ticks after the 14th; engine removes it at 187)
    a = LoggedAphelios(1)
    fight(a, [set19items.KrakensFury()], [set19buffs.Heartsteel(3, 0)])
    launches = [t for t, _, _ in a.launch_log]
    cast = a.casts[0]
    assert len([t for t in launches if t < cast]) == 14 and cast == launches[13] + 1
    after = [x for x in a.launch_log if x[0] > cast]
    assert after[0][0] - launches[13] == 77
    assert [s for _, s, _ in after[:2]] == [1.528, 1.648]
    assert a.mana_locked_until - launches[13] == 187
    gained = [(t, g) for t, amount, g in a.mana_log if t > cast and g > 0]
    assert gained[0][0] >= a.mana_locked_until  # Mana.Locked while the AS buff lasts


def test_vod8_6_1_cast():
    # VOD8 6-1 (Guinsoo's Rageblade + Kraken's Fury): the 14th launch fills the bar; the next launch 74 ticks later in
    # the VOD (f119697 -> f119845) at AS 2.34: the engine's 77 is 3 ticks late (OPEN-QUESTIONS 7ab: a fresh attack's
    # windup at high AS)
    a = LoggedAphelios(1)
    fight(a, [set19items.GuinsoosRageblade(), set19items.KrakensFury()], [set19buffs.Heartsteel(3, 0)])
    launches = [t for t, _, _ in a.launch_log]
    cast = a.casts[0]
    assert cast == launches[13] + 1
    after = [x for x in a.launch_log if x[0] > cast]
    assert after[0][0] - launches[13] == 77 and after[0][1] == 2.336


def test_chakrams_every_fourth_launch():
    # no Bias: 0 Chakrams at combat start, one more at every 4th launch; each launch sends that many, each
    # HeartsteelStan_ADDamage x AD (7 at 1 star, AD 1.0) after the leg-time tier's flight
    a = LoggedAphelios(1)
    _, rows = fight(a, seconds=12)
    assert [c for _, _, c in a.launch_log[:9]] == [0, 0, 0, 1, 1, 1, 1, 2, 2]
    t4 = a.launch_log[3][0]
    # AS 0.8: leg = 1.25 x 0.35 / 2 = 0.219 s -> tier 0.2 s = 6 ticks
    assert a.chakram_flight() == 6
    assert 7.0 in rows[t4 + 6]


def test_bias_starts_with_five_chakrams():
    a = LoggedAphelios(1)
    _, rows = fight(a, buffs=[set19buffs.Heartsteel(3, 1 << set19buffs.Heartsteel.BIAS)], seconds=2)
    t, _, n = a.launch_log[0]
    assert n == 5 and rows[t + a.chakram_flight()].count(7.0) == 5


def test_max_chakrams_buff():
    # at 15 Chakrams the next attack damage applies GE_Aphelios19_MaxChakramBuff: + MaxChakramsExtraAD (30%) AD
    a = LoggedAphelios(1)
    a.aspd.modify('MultiplyAdditive', 3.0)
    fight(a, buffs=[set19buffs.Heartsteel(3, 1 << set19buffs.Heartsteel.BIAS)], seconds=24)
    assert a.chakrams == 15 and a.max_buff and round(a.bonus_ad.stat, 3) == 1.3


def test_cast_bolts_and_splits():
    # 2 targets: the 2 nearest, repeated to NumEnemies (3): [nearest, other, nearest]; each primary victim takes
    # PhysicalDamageCalc1 (280 x AD + 60 x AP) and its split bolts hit the other dummy for 15% of it
    a = LoggedAphelios(1)
    a.curMana = a.fullMana.stat
    ds, rows = fight(a, seconds=4)
    targets = a.spell_targets()
    assert len(targets) == 3 and targets[0] is targets[2] and targets[0] is not targets[1]
    hits = [d for t in sorted(rows) for d in rows[t] if d in (340.0, 51.0)]
    assert hits.count(340.0) == 3 and hits.count(51.0) == 3
    assert layout.distance(ds[0], ds[1]) == 1


def test_one_target_takes_all_three_bolts():
    a = LoggedAphelios(1)
    a.curMana = a.fullMana.stat
    _, rows = fight(a, seconds=4, targets=1)
    hits = [d for t in sorted(rows) for d in rows[t] if d == 340.0]
    assert len(hits) == 3


def test_three_star_barrage_in_expectation():
    # 3 stars: a shot every ThreeStarRefireDelay from 'LaunchAttack' 2.1 s, never an attack after it
    a = LoggedAphelios(3)
    a.curMana = a.fullMana.stat
    fight(a, seconds=4)
    assert a.busy_until > 10 ** 6 and [t for t, _, _ in a.launch_log if t > a.casts[0]] == []

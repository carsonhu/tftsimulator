"""Graves (champions/Graves.md): GA_Graves19_Spell and GA_Graves19_Passive (D1) on build rls-19.1.0.6011486, checked
against the owner's 60 fps VOD8 (13-2-9-650: Graves 1 star with Edge of Night, Infinity Force and Bloodthirster at 5-7,
Heartsteel (3) with Aphelios fielded)."""
import set19buffs
import set19items
from buildstore import load_build
from layout import Layout
from set19champs import Graves
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.6011486.Set19.Shipping.pbe'
APHELIOS = 1 << 2  # Heartsteel's 'Fielded' box for Aphelios (traits/heartsteel.py MEMBERS)


class LoggedGraves(Graves):
    def __init__(self, level=1):
        super().__init__(level, build=load_build(V))
        self.casts, self.dashes, self.launch_log, self.mana_log, self.as_log, self.bullets = [], [], [], [], [], []

    def performAbility(self, opponents, items, time):
        self.casts.append(self.tick)
        before = self.hex
        super().performAbility(opponents, items, time)
        self.dashes.append((before, self.hex, round(self.timing.cast_lock * 30)))

    def onLaunch(self, opponents, items):
        super().onLaunch(opponents, items)
        self.launch_log.append((self.tick, self._this_empowered))

    def addMana(self, amount, time=None):
        before = self.curMana
        super().addMana(amount, time)
        self.mana_log.append((self.tick, self.curMana - before))

    def update(self, opponents, items, time):
        super().update(opponents, items, time)
        v = round(self.aspd.stat, 3)
        if not self.as_log or self.as_log[-1][1] != v:
            self.as_log.append((self.tick, v))

    def _bullet_lands(self, target, first):
        self.bullets.append((self.tick, target, first))
        super()._bullet_lands(target, first)


def fight(g, items=(), buffs=(), seconds=10, targets=2):
    lay = Layout(targets)
    ds = [dummy() for _ in range(lay.count)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate(list(items), list(buffs), g, ds, seconds, layout=lay)
    return ds


def vod8_graves():
    g = LoggedGraves(1)
    g.stage = 5
    items = [set19items.EdgeOfNight(), set19items.InfinityForce(), set19items.Bloodthirster()]
    return g, items, [set19buffs.Heartsteel(3, APHELIOS)]


def test_build_numbers():
    g = LoggedGraves(1)
    assert (g.curMana, g.fullMana.stat, g.aspd.stat, g.attack_range, g.atk.stat, g.hp.stat) == (0, 30, 0.6, 2, 85, 1100)
    assert g.timing.launch == 0.12 and [v['launch'] for v in g.timing.variants] == [0.12, 0.12]
    assert round(g.timing.cast_lock * 30) == 1  # the build's lockout: an instant cast
    assert (g.on_attack_at, round(g.arrive_at, 4)) == (0.52, 0.3964)
    assert g.bullet_damage(1, 1.0, 1.0) == 45 and g.row('NumMissiles') == 5


def test_vod8_5_7_panel():
    # VOD8 5-7 panel (32:09-32:12): 1,400 HP, AD 132, 55% bonus AD, 55% AP, AS 1.09 = 0.6 x (1 + 0.3 Fighter stage 5
    # + 0.06 Aphelios' Heartsteel bonus + 0.15 Edge of Night + 0.3 Infinity Force); 1.84 under the cast's +125%
    g, items, buffs = vod8_graves()
    fight(g, items, buffs, seconds=0.1)
    assert g.hp.stat == 1400 and round(g.atk.stat * g.bonus_ad.stat, 2) == 131.75 and round(g.ap.stat, 2) == 1.55
    assert round(g.aspd.stat, 3) == 1.086
    g, items, buffs = vod8_graves()
    fight(g, items, buffs, seconds=3)
    assert [v for _, v in g.as_log][:2] == [1.086, 1.836]


def test_vod8_5_7_casts():
    # VOD8 5-7 (PvE; attack mana steps at f115916, 115972, 116026: 28, 27 ticks apart). Cast 1 (AS 1.09 -> 1.84 on
    # f116026): AS back to 1.09 at f116114 (+44 ticks), first mana f116124 (+49). Cast 2 (f116233): AS back at
    # f116299 (+33), first mana f116309 (+38). The 11 ticks between them: the first cast's dash ('Arrive' 12 ticks
    # instead of the 1-tick lockout); the second finds him on his best hex already.
    g, items, buffs = vod8_graves()
    fight(g, items, buffs, seconds=8)
    starts = [t for t, e in g.launch_log if not e][:3]
    assert [b - a for a, b in zip(starts, starts[1:])] == [27, 28]
    (c1, c2) = g.casts[:2]
    assert g.dashes[:2] == [((0, 0), (1, 0), 12), ((1, 0), (1, 0), 1)]
    assert [t - c1 for t, v in g.as_log if t > c1][:1] == [44]
    assert [t - c2 for t, v in g.as_log if t > c2][:1] == [33]
    first_mana = [[t - c for t, d in g.mana_log if t > c and d > 0][0] for c in (c1, c2)]
    assert first_mana == [48, 37]  # VOD 49 / 38: one tick later on both (as T10)


def test_empowered_attacks_give_no_mana_and_end_the_buff():
    # the mana lock ends with the AS buff, at the 2nd empowered attack's CustomEventOnAttack1: both attacks' mana is lost
    g, items, buffs = vod8_graves()
    fight(g, items, buffs, seconds=4)  # one cast
    (c,) = g.casts
    emp = [t for t, e in g.launch_log if e]
    off = [t for t, v in g.as_log if t > c][0]
    assert len(emp) == 2 and g.mana_locked_until == off and emp[1] < off
    assert not [t for t, d in g.mana_log if d > 0 and c <= t < off]


def test_cone_after_the_dash_hits_the_target_five_times():
    # 1 target 2 hexes off: from his hex 3 bullets would hit it; a hex next to it holds all 5, so he dashes there
    g = LoggedGraves(1)
    fight(g, seconds=6, targets=1)
    assert g.dashes[0] == ((0, 0), (1, 0), 12)
    volley = [b for b in g.bullets if b[0] == g.bullets[0][0]]
    assert len(volley) == 5 and len({id(b[1]) for b in volley}) == 1
    assert sum(1 for b in volley if b[2]) == 1  # one bullet is the attack (GE_Graves19_Damage, IsAttack)


def test_no_dash_when_a_dummy_stands_in_front():
    # 5+ targets: the layout puts the 5th on the hex between him and the target. Every bullet's rectangle from his own
    # hex holds a unit and the middle one the target (TR_Sort_SlotForGravesStyleShotgun's score 5), so he stays; each
    # bullet is destroyed on the first unit it meets, the one in front.
    g = LoggedGraves(1)
    ds = fight(g, seconds=6, targets=7)
    assert g.dashes[0] == ((0, 0), (0, 0), 1)
    volley = [b for b in g.bullets if b[0] == g.bullets[0][0]]
    assert len(volley) == 5 and all(b[1] is ds[4] for b in volley) and ds[4].hex == (1, 0)


def test_cone_spreads_over_the_target_and_its_neighbours():
    # 3 targets: he dashes beside the target (0, 1), from where 5 bullets hit and the outer two reach the neighbours
    g = LoggedGraves(1)
    ds = fight(g, seconds=6, targets=3)
    assert g.dashes[0] == ((0, 0), (0, 1), 12)
    t0 = g.bullets[0][0]
    volley = [ds.index(b[1]) for b in g.bullets if b[0] <= t0 + 4]
    assert sorted(volley) == [0, 0, 0, 1, 2]

"""Olaf with the hero augment Axe Crescendo, a separate champion (champions/Olaf_HeroAugment.md): numbers from build
rls-19.1.0.5973071; mana and rhythm against the owner's 60 fps PBE VOD5 (0-57-11-500, f18522-19295: 1-star with
Quicksilver)."""
import set19items
from buildstore import load_build
from set19champs import OlafHeroAugment
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


class LoggedOlaf(OlafHeroAugment):
    def __init__(self, level=1):
        super().__init__(level, build=load_build(V))
        self.mana_log, self.casts, self.releases = [], [], []

    def addMana(self, amount, time=None):
        before = self.curMana
        super().addMana(amount, time)
        self.mana_log.append((self.tick, amount, before, self.curMana))

    def performAbility(self, opponents, items, time):
        self.casts.append(self.tick)
        super().performAbility(opponents, items, time)

    def onLaunch(self, opponents, items):
        super().onLaunch(opponents, items)
        self.releases.append((self.tick, self._this_empowered))


def fight(c, items=(), buffs=(), seconds=14, n=8):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate(list(items), list(buffs), c, ds, seconds)
    return [(round(t * 30), round(d[0], 4)) for t, d, *_ in c.dmgVector]


def gains(c):
    return [t for t, a, before, after in c.mana_log if after > before]


def test_build_numbers_and_animations():
    o = LoggedOlaf(1)
    assert (o.name, o.hp.stat, o.fullMana.stat, o.aspd.stat, o.attack_range, o.atk.stat) == (
        'Olaf (Hero)', 500, 50, 0.7, 4, 45)
    fight(o, seconds=1)
    assert o.crit.stat == 0 and o.manaRegen.stat == 0 and o.manaPerAttack.stat == 10  # role stats at combat
    # CD_Olaf19_Attack: normal attacks 0.32 s of 1.0 s, the empowered one 0.5 s of 1.1667 s
    assert [(v['selector'], v['launch'], v['length']) for v in o.timing.variants] == [
        (1, 0.32, 1), (2, 0.32, 1), (3, 0.5, 1.1667)]
    assert round(o.timing.cast_lock * 30) == 1 and o.default_traits == ['Pentakill']


def test_vod5_rhythm_and_mana_lock():
    # VOD5: +10 per attack, no regen; gaps 37, 36, 34, 33.5 (Quicksilver ramping); the attack that fills the bar, then
    # nothing until the first normal attack after the two axes, 77 ticks later; the second cast on the 5th attack
    o = LoggedOlaf(1)
    fight(o, items=[set19items.Quicksilver()])
    assert {round(after - before, 3) for t, a, before, after in o.mana_log if after > before} == {10}
    g = gains(o)
    assert [b - a for a, b in zip(g, g[1:])][:4] == [37, 36, 35, 34]
    fill = g[4]
    assert o.casts[0] == fill + 1 and g[5] - fill == 77
    assert [e for t, e in o.releases][:9] == [False] * 5 + [True, True] + [False] * 2
    assert o.casts[1] == g[9] + 1  # 5 more attacks fill the bar again


def test_axes_grow_and_hit_for_spell_damage():
    # 2 axes on the first cast, 3 on the second (ExtraAttacksPerCast 1); each 150 x AD + 15 x AP physical at 1 star
    o = LoggedOlaf(1)
    rows = fight(o, seconds=45)
    runs, cur = [], 0
    for t, e in o.releases:
        if e:
            cur += 1
        elif cur:
            runs.append(cur)
            cur = 0
    assert runs[:3] == [2, 3, 4]
    assert sum(1 for t, d in rows if d == 165) == sum(runs) + cur
    assert all(d == 45 for t, d in rows if d != 165)  # no crit (0%), base AD

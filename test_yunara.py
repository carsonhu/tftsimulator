"""Yunara end to end (champions/Yunara.md) and Swiftstriker: numbers from build rls-19.1.0.5973071; timing against the
owner's 60 fps PBE VOD2 (16-35-16-966, Yunara 1*, no items, Swiftstriker (2), f6200-7140)."""
import set19buffs
from buildstore import load_build
from set19champs import Varus, Yunara
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


class LoggedYunara(Yunara):
    def __init__(self, level=1, walk=0):
        super().__init__(level, build=load_build(V))
        self.releases, self.casts, self.as_log, self.walk = [], [], {}, walk

    def onLaunch(self, opponents, items):
        self.releases.append(self.tick)
        super().onLaunch(opponents, items)

    def performAbility(self, opponents, items, time):
        self.casts.append(self.tick)
        super().performAbility(opponents, items, time)

    def update(self, opponents, items, time):
        if self.tick == 0 and self.walk:
            self.busy_until = self.walk  # VOD2: she walks into range before her first attack
        self.as_log[self.tick] = round(self.aspd.stat, 4)
        return super().update(opponents, items, time)


def fight(c, buffs=(), seconds=12, n=8):
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.armor.base = 0
    Simulator().simulate([], list(buffs), c, ds, seconds)
    return [(round(t * 30), round(d[0], 2)) for t, d, *_ in c.dmgVector]


def test_build_numbers_and_timing():
    y = LoggedYunara(1)
    assert (y.curMana, y.fullMana.stat, y.aspd.stat, y.attack_range) == (50, 80, 0.7, 4)
    assert y.timing.cast_keeps_rhythm and y.timing.animations == 2
    assert y.orb_times[0] == 0.101 and len(y.orb_times) == 11


def test_vod2_releases_with_swiftstriker():
    # VOD2: Swiftstriker's stacks show at f6612, 6732, 6852, 6972, 7092 (every 2 s from 2 s: combat start f6492).
    # Mana steps (releases) in ticks from combat start; the 6th fell while 30/80 wasn't detected. She first walks
    # into range (13.5 ticks, modelled as a 14-tick delay); from there the engine is within a tick, through the cast.
    vod = [21.5, 61, 98.5, 136, 172, None, 242, 275, 308]
    y = LoggedYunara(1, walk=14)
    fight(y, buffs=[set19buffs.Swiftstriker(2)])
    assert all(abs(e - v) <= 1 for e, v in zip(y.releases, vod) if v is not None)
    assert y.casts[0] == 99  # VOD: 0/80 on the 3rd release's frame (98.5)
    # panel AS: 0.77 in planning (Team 10%), then +5% of base every 2 s: 0.80, 0.84, 0.87, 0.91, 0.94
    assert [y.as_log[t] for t in (0, 59, 60, 120, 180, 240, 300, 330)] == [0.77, 0.77, 0.805, 0.84, 0.875, 0.91, 0.945,
                                                                          0.945]


def test_orbs_after_each_cast():
    # one orb per cast, fired on every launch after it: 13 x AD + 3 x AP = 16 at 1*, landing 3 (0.101 s of a 0.5 / AS
    # chrono) + 14 (1850 units/s over 4 hexes) ticks after the release
    y = LoggedYunara(1)
    rows = fight(y, seconds=20)
    first, second = y.casts[:2]
    after = [r for r in y.releases if r > first]
    assert (after[0] + 17, 16) in rows
    assert not any(d == 16 for t, d in rows if t < after[0] + 17)
    two = [r for r in y.releases if r > second][0]
    assert [(t - two, d) for t, d in rows if d == 16 and t > two] [:2] == [(17, 16), (18, 16)]


def test_swiftstriker_team_bonus_reaches_non_members():
    v = Varus(1, build=load_build(V))
    Simulator().itemStats([set19buffs.Swiftstriker(2)] + v.items, v)
    assert round(v.aspd.stat, 4) == 0.77  # Varus 0.7 x 1.1; no stacks (not a Swiftstriker)


def test_ionic_spark_letters_and_gift():
    # DA_IonicSpark19 (B22): a letter (+7% AS, stacking) at 4, 8, 12 s for members; at (5)+ one 25% gift, AD for an
    # Attack-role unit (Yunara: AttackMarksman), as the 1st (0 s), 2nd (4 s) or 3rd (8 s) gift, or none
    def gains(level, gift, seconds=13):
        y = Yunara(1, build=load_build(V))
        log, orig = [], y.update

        def upd(opp, items, time):
            before = (y.aspd.add, y.bonus_ad.add)
            orig(opp, items, time)
            if (y.aspd.add, y.bonus_ad.add) != before:
                log.append((y.tick, round(y.aspd.add, 6), round(y.bonus_ad.add, 6)))
        y.update = upd
        Simulator().simulate([], [set19buffs.IonicSpark(level, gift)], y, [dummy()], seconds)
        return log

    assert gains(0, 0) == []
    assert gains(3, 0) == [(120, 7, 0), (240, 14, 0), (360, 21, 0)]  # (3): no gift
    assert gains(5, 0) == [(0, 0, 25), (120, 7, 25), (240, 14, 25), (360, 21, 25)]
    assert gains(5, 2) == [(120, 7, 0), (240, 14, 25), (360, 21, 25)]
    assert gains(5, 3) == gains(3, 0)

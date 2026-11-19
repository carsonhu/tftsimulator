"""The timing core, tick by tick (docs/ASSUMPTIONS.md T1-T6, G1-G7).

Each test states the rule it checks and the exact ticks it expects; the arithmetic is written out so a failure says
which rule moved. A test champion with no role item, so its mana comes only from what the test sets.
"""
import math

import pytest

from champion import Champion
from simulator import Simulator
from timing import TPS, Timing, ticks_up


class Probe(Champion):
    """Records attack landings (damage rows) and cast ticks."""

    def __init__(self, timing, aspd=1.0, mana=(0, 30), per_attack=10, attack_range=1, ad=100):
        super().__init__('Probe', 1000, ad, mana[0], mana[1], aspd, 0, 0, 1)
        self.items = []  # no role item: mana per attack comes only from here
        self.manaPerAttack.base = per_attack
        self.timing = timing
        self.attack_range = attack_range
        self.cast_ticks = []

    def performAbility(self, opponents, items, time):
        self.cast_ticks.append(self.tick)


def dummy():
    d = Champion('Dummy', 100000, 0, 0, 1000, 0.01, 0, 0, 1)
    d.items = []
    return d


def run(probe, seconds=6):
    Simulator().simulate([], [], probe, [dummy()], seconds)
    hits = [round(t * TPS) for t, *_ in probe.dmgVector]
    return hits, probe.cast_ticks


def test_ticks_up_matches_the_client_rule():
    # G1: an event at t seconds lands on ceil(t*30 - 0.06)
    assert ticks_up(0.3) == 9            # 9.00 -> 9
    assert ticks_up(0.3067) == 10        # 9.20 -> 10
    assert ticks_up(0.3020) == 9         # 9.06 - 0.06 = 9.00 -> 9 (slack)
    assert ticks_up(0.0) == 0


def test_first_hit_one_windup_in_then_every_period():
    # G3 + T2: fresh attack at tick 0, hit at launch; AS 1.0 -> a 30-tick period
    hits, _ = run(Probe(Timing(launch=0.3), aspd=1.0, mana=(0, -1)), seconds=3)
    assert hits == [9, 39, 69]


def test_fractional_period_alternates_and_does_not_drift():
    # T2: AS 0.8 = 37.5 ticks; the remainder carries, so gaps alternate 38/37 (half rounds up), never drift
    hits, _ = run(Probe(Timing(launch=0.3), aspd=0.8, mana=(0, -1)), seconds=8)
    gaps = [b - a for a, b in zip(hits, hits[1:])]
    assert set(gaps) == {37, 38}
    assert hits[-1] - hits[0] == round(37.5 * (len(hits) - 1))


def test_release_stretches_only_when_the_period_is_longer_than_the_animation():
    # G2: release = launch * max(1, period / attack_len)
    # Ahri's attack: launch 0.3067, animation 3.2 s, AS 0.8 (1.25 s period) -> no stretch -> ticks_up(0.3067) = 10
    hits, _ = run(Probe(Timing(launch=0.3067, attack_len=3.2), aspd=0.8, mana=(0, -1)), seconds=1)
    assert hits == [10]
    # animation 0.7 s: stretch 1.25 / 0.7; 0.3067 * 1.7857 = 0.5477 s -> 16.43 - 0.06 -> 17
    hits, _ = run(Probe(Timing(launch=0.3067, attack_len=0.7), aspd=0.8, mana=(0, -1)), seconds=1)
    assert hits == [17]
    # high AS never shrinks it: AS 4 (7.5-tick period) still releases at 10
    hits, _ = run(Probe(Timing(launch=0.3067, attack_len=0.7), aspd=4.0, mana=(0, -1)), seconds=0.5)
    assert hits[0] == 10


def test_release_shrinks_below_the_play_rate_threshold():
    # G20: with PlayRateScalingThreshold T, release = launch * period / (T * attack_len) once that is below launch.
    # Malzahar's attack (launch 0.445 s, 1.0 s, T 0.941): at AS 1.0 (1 s period) G2's 0.445 s -> 14 ticks
    t = Timing(launch=0.445, attack_len=1.0, rate_threshold=0.941)
    assert t.release_ticks(30) == 14
    # AS 1.5 (20-tick period): 0.445 * 0.6667 / 0.941 = 0.3153 s = 9.46 ticks -> 10 (G2: 14)
    assert t.release_ticks(20) == 10
    assert Timing(launch=0.445, attack_len=1.0).release_ticks(20) == 14
    # T = 1 is G19's rule
    assert Timing(launch=0.445, attack_len=1.0, rate_threshold=1.0).release_ticks(20) == \
        Timing(launch=0.445, attack_len=1.0, release_scales_with_period=True).release_ticks(20)
    # longer periods still stretch (G2)
    assert t.release_ticks(60) == Timing(launch=0.445, attack_len=1.0).release_ticks(60) == 27
    # a variant's own threshold wins over the unit's; a variant with None set keeps G2
    v = Timing(launch=0.445, attack_len=1.0, rate_threshold=0.5, animations=1,
               variants=[{'selector': 1, 'min_as': None, 'launch': 0.445, 'length': 1.0, 'rate_threshold': None}])
    assert v.release_ticks(20, selector=1, aspd=1.5) == 14


def test_projectile_lands_after_its_flight():
    # G4: range 4, speed 1500: 4 * 215 / 1500 = 0.5733 s -> 17.2 - 0.06 -> 18 ticks after the release (tick 9)
    hits, _ = run(Probe(Timing(launch=0.3, proj_speed=1500), aspd=1.0, mana=(0, -1), attack_range=4), seconds=2)
    assert hits[0] == 9 + 18


def test_melee_casts_the_tick_after_the_filling_hit_then_a_fresh_attack():
    # T3 melee mana on the hit: hits 9, 39, 69 fill 30 mana -> T4 cast at 70
    # T5: cast lock 1.0 s -> no attack before 100; fresh attack starts at 100, hits one windup later (109)
    p = Probe(Timing(launch=0.3, cast_lock=1.0), aspd=1.0, mana=(0, 30))
    hits, casts = run(p, seconds=4)
    assert casts[0] == 70
    assert hits[:4] == [9, 39, 69, 109]


def test_ranged_mana_at_the_release_then_cast_the_next_tick():
    # T3 default for ranged: mana at the release (Set 19 VOD: Neeko, Draven, Varus). Releases 9, 39, 69: the third
    # fills 30 mana -> T4 cast at 70; its projectile is already in flight. Cast lock 1.0 s -> a fresh attack at 100,
    # released at 109; landings are release + flight (4 hexes * 215 / 1500 = 0.573 s -> 18 ticks).
    p = Probe(Timing(launch=0.3, cast_lock=1.0, proj_speed=1500), aspd=1.0, mana=(0, 30), attack_range=4)
    hits, casts = run(p, seconds=4.5)
    assert casts[0] == 70
    assert hits[:4] == [27, 57, 87, 127]


def test_mana_at_the_start_when_set():
    # mana_at='start' (per champion, with evidence): starts 0, 30, 60 -> the third start fills -> cast at 61; the
    # attack started at 60 still releases at 69 during the cast (T4); fresh attack at 61 + 30 = 91, released at 100
    p = Probe(Timing(launch=0.3, cast_lock=1.0, mana_at='start'), aspd=1.0, mana=(0, 30), attack_range=4)
    hits, casts = run(p, seconds=4)
    assert casts[0] == 61
    assert hits[:4] == [9, 39, 69, 100]


def test_mana_lock_blocks_mana_until_it_ends():
    # T5: mana lock 2.0 s after a cast at 70 -> mana from hits before tick 130 is lost
    p = Probe(Timing(launch=0.3, cast_lock=1.0, mana_lock=2.0), aspd=1.0, mana=(0, 30))
    run(p, seconds=8)
    # hits after the cast: 109 (locked), 139, 169, 199 (+10 each) -> full at 199 -> second cast at 200
    assert p.cast_ticks[:2] == [70, 200]


def test_locks_scale_with_attack_speed_when_the_script_reads_it():
    # G7: base AS 1.0, current 2.0 (item) -> the cast's 29 ticks to its end play in 14.5, then G5's tick: 0.5167 s
    # one cast only: starts full, no mana afterwards
    p = Probe(Timing(launch=0.3, cast_lock=1.0, lock_scales_with_as=True), aspd=1.0, mana=(30, 30), per_attack=0)
    p.aspd.modify('MultiplyAdditive', 2)  # +100% AS
    run(p, seconds=2)
    assert len(p.cast_ticks) == 1
    assert p.busy_until - p.cast_ticks[0] == 16


def test_overflow_mana_is_kept():
    # G10 (inherited, open): 12 mana per hit, max 30: 36 at the third hit -> 6 left after the cast
    p = Probe(Timing(launch=0.3, cast_lock=1.0), aspd=1.0, mana=(0, 30), per_attack=12)
    run(p, seconds=2.5)
    assert p.cast_ticks[0] == 70 and p.curMana == 6


def test_scheduled_spell_effect_lands_on_its_tick():
    # T6: an effect 0.833 s after a cast at tick 70 lands on 70 + ticks_up(0.833) = 70 + 25
    seen = []

    class Delayed(Probe):
        def performAbility(self, opponents, items, time):
            super().performAbility(opponents, items, time)
            self.schedule(0.833, lambda: seen.append(self.tick))

    run(Delayed(Timing(launch=0.3, cast_lock=1.0), aspd=1.0, mana=(0, 30)), seconds=4)
    assert seen[0] == 70 + 25


def test_timing_from_build_reads_ahri():
    from buildstore import load_build
    t = Timing.from_build(load_build('rls-19.1.0.5973071.Set19.Shipping.pbe').champion('DA_Ahri19'))
    assert (t.launch, t.attack_len, t.proj_speed) == (0.3067, 3.2, 1750)
    assert t.cast_lock == 1 and t.mana_lock == 0.9667 and t.lock_scales_with_as is False
    assert t.source['cast_lock'].startswith('build rls-19.1.0.5973071')


def test_an_on_hit_payer_pays_the_filling_attack_at_its_release_and_not_again_on_landing():
    # T3: a ranged unit that pays on the hit (mana_at='hit') pays at the release an attack whose mana fills the bar,
    # casts the next tick, and that attack's landing must not pay again. Windup 15 (0.5 s), flight 13 (0.43 s).
    # Lands 28 (+10), 58 (+20); the third releases at 75 and fills (+10 -> 30) -> cast at 76 -> 0. Cast lock 3 ticks:
    # fresh attack at 79, released 94, lands 107. The filling attack lands at 88 and must not add 10.
    p = Probe(Timing(launch=0.5, cast_lock=0.1, mana_at='hit', proj_speed=2000), aspd=1.0, mana=(0, 30),
              attack_range=4)
    run(p, seconds=3.4)  # last tick 101
    assert p.cast_ticks == [76]
    assert p.curMana == 0

"""Tick rules and per-champion timing for the Set 19 simulator.

The game advances in 30 Hz ticks (docs/ASSUMPTIONS.md G1). Every engine decision is made in whole ticks; seconds
appear only at the edges (input timing values, `time` passed to items, the damage vector).

Each rule here names its ledger entry. The rules and their tick arithmetic follow tftFightSim's engine
(crates/engine/src/sim.rs), which was checked against the 18.5 replays; Set 19 evidence is collected per champion in
champions/<Name>.md.
"""
import math

TPS = 30
# A client timeline event fires on the first tick at or after its time, with this much slack (in ticks): an event
# 0.06 ticks past a boundary still lands on it (Set 18 replays: Sivir >= 0.03, Rek'Sai > 0.052, Kennen < 0.075).
TICK_SLACK = 0.06
HEX_UNITS = 215.0  # world units per hex for projectile flight (G4; Set 18 replays: 212-217)


def ticks_up(seconds):
    """A client timeline event at `seconds` lands on this tick (G1)."""
    return max(0, math.ceil(seconds * TPS - TICK_SLACK))


def ticks(seconds):
    """A duration already measured on the tick grid (e.g. a build's lockout), to whole ticks."""
    return max(0, round(seconds * TPS))


class Timing:
    """How one champion's attacks and casts are timed. Seconds in, ticks out.

    launch       attack start -> release (ranged) or hit (melee) at an unstretched animation (G2)
    attack_len   the attack animation's length; the release stretches by period / attack_len when the attack period
                 is longer (G2). 0 = never stretch.
    proj_speed   attack projectile speed (units/s); 0 = the attack lands at the release (melee) (G4)
    distance     hexes to the target for projectile flight; None = the champion's attack range
    mana_at      when an attack pays its mana: 'start', 'release' or 'hit'. Set 18 replays: most ranged units at the
                 attack start, melee on the hit (T3)
    cast_lock    cast start -> the earliest next attack start (G5); then a fresh attack begins (T5)
    mana_lock    cast start -> mana can be gained again (G6); None = cast_lock
    lock_scales_with_as  the spell's script reads attack speed: both locks scale by base AS / current AS (G7, a
                 generic rule; a champion whose script uses its own curve overrides scaled_locks)
    cast_cancels_attack  a ranged attack under way when the cast starts never releases (T4); default: it still releases
    source       {field: where the value came from}, e.g. 'build rls-19.1.0.5973071', a VOD, or 'set18 compat'
    """

    def __init__(self, launch=0.0, attack_len=0.0, proj_speed=0.0, distance=None, mana_at=None, cast_lock=0.0,
                 mana_lock=None, lock_scales_with_as=False, cast_cancels_attack=False, source=None):
        self.launch = launch
        self.attack_len = attack_len
        self.proj_speed = proj_speed
        self.distance = distance
        self.mana_at = mana_at
        self.cast_lock = cast_lock
        self.mana_lock = mana_lock
        self.lock_scales_with_as = lock_scales_with_as
        self.cast_cancels_attack = cast_cancels_attack
        self.source = dict(source or {})

    @classmethod
    def from_build(cls, champion_entry, spell=None):
        """From a buildstore Champion: attack timeline, projectile and one spell's predicted locks.

        `spell` picks the spell timeline by ability name (default: the first one in the build). Every field read
        here is recorded in `source`; anything the build lacks keeps its default and is recorded as 'default'.
        """
        t = champion_entry.timing
        where = f'build {champion_entry.build.version}'
        src = {}
        kw = {}
        for field, key in (('launch', 'attack_launch'), ('attack_len', 'attack_len'), ('proj_speed', 'proj_speed')):
            if t.get(key) is not None:
                kw[field] = t[key]
                src[field] = where
        spells = t.get('spells') or []
        sp = next((s for s in spells if s['ga'] == spell), None) if spell else (spells[0] if spells else None)
        if spell and sp is None:
            raise KeyError(f'{champion_entry.key}: no spell timeline {spell!r} in {where}')
        if sp is not None:
            if sp.get('lockout') is not None:
                kw['cast_lock'] = sp['lockout']
                src['cast_lock'] = f'{where} {sp["ga"]}'
            if sp.get('manalock_removed') is not None:
                kw['mana_lock'] = sp['manalock_removed']
                src['mana_lock'] = f'{where} {sp["ga"]}'
            kw['lock_scales_with_as'] = bool(sp.get('reads_attack_speed'))
            src['lock_scales_with_as'] = f'{where} {sp["ga"]}'
        for f in ('launch', 'attack_len', 'proj_speed', 'cast_lock', 'mana_lock'):
            src.setdefault(f, 'default')
        return cls(source=src, **kw)

    def release_ticks(self, period_ticks):
        """Attack start -> release/hit, in ticks, for an attack period of `period_ticks` (G2): the attack animation
        stretches to the period when the period is longer, never shrinks. At least 1 tick."""
        stretch = 1.0
        if self.attack_len > 0:
            stretch = max(1.0, (period_ticks / TPS) / self.attack_len)
        return max(1, ticks_up(self.launch * stretch))

    def flight_ticks(self, attack_range):
        """Release -> hit for a projectile (G4); 0 for melee."""
        if self.proj_speed <= 0:
            return 0
        hexes = self.distance if self.distance is not None else max(1, attack_range or 1)
        return ticks_up(hexes * HEX_UNITS / self.proj_speed)

    def mana_moment(self, ranged):
        """'start', 'release' or 'hit' (T3 default: ranged at the attack start, melee on the hit)."""
        return self.mana_at or ('start' if ranged else 'hit')

    def scaled_locks(self, base_as, current_as):
        """(cast lock, mana lock) in seconds at the current attack speed."""
        mana_lock = self.cast_lock if self.mana_lock is None else self.mana_lock
        if self.lock_scales_with_as and current_as > 0 and base_as > 0:
            f = base_as / current_as
            return self.cast_lock * f, mana_lock * f
        return self.cast_lock, mana_lock

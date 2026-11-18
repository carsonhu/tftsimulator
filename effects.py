"""Timed effects on a unit (docs/RESTRUCTURE.md step 4): one type for every effect that lasts a while, in whole ticks.

An ActiveEffect is a GAS active effect: it holds its modifiers on the unit's attributes while it lasts (keyed by its
name, so they come off exactly), may act every period, and follows a stacking rule. Units keep them in
`unit.effects` (name -> effect); `apply_effect` and `expire_effects` are the only ways in and out.

The stacking rule every current effect has: one instance per name on a unit; applying it again while it lasts
renews it, keeping the later end and the higher level, and a periodic effect keeps its period's phase
(StackPeriodResetPolicy NeverReset, GE_Burn). One sunder, shred or burn per target is ledger I7's rule: their
records carry StackLimitCount 1 but no StackingType, and a limit without a stacking type does nothing (VOD2:
Quicksilver's StackLimitCount 9 doesn't cap it, docs/ITEMS.md). Effects that stack as separate instances (Striker's
Flail's buff: TFTStackGameplayEffectInstancesEffectComponent, AggregateBySource) use one name per instance.
"""
import math

from stats import FastDeepCopy
from timing import TPS


class ActiveEffect(FastDeepCopy):
    """One effect on a unit.

    name: the instance's name on the unit (see the module's stacking rule).
    modifiers: [(attribute field, op, value, channel)] held on the unit while the effect lasts.
    level: the level it was applied at (a burn's BurnWound level), kept at the highest on renewal.
    period: ticks between periodic actions, or None; the first comes one period after application unless
    period_on_application (bExecutePeriodicEffectOnApplication). Whoever runs the action calls due().
    last_tick: the last tick the effect covers; it is removed before the tick after.
    """

    def __init__(self, name, modifiers=(), level=None, period=None, period_on_application=False):
        self.name = name
        self.modifiers = list(modifiers)
        self.level = level
        self.period = period
        self.period_on_application = period_on_application
        self.last_tick = None
        self.next_period = None

    def due(self, tick):
        """How many periodic actions are due by `tick` (inclusive, within the effect's last tick); advances them."""
        n = 0
        while self.period and self.next_period <= tick and self.next_period <= self.last_tick:
            n += 1
            self.next_period += self.period
        return n


def apply_effect(unit, effect, tick, last_tick):
    """Put `effect` on `unit` at `tick`, covering ticks up to `last_tick`; returns the effect now active there."""
    current = unit.effects.get(effect.name)
    if current is not None:  # renew (StackLimitCount 1): later end, higher level, period phase kept (NeverReset)
        current.last_tick = max(current.last_tick, last_tick)
        if effect.level is not None:
            current.level = effect.level if current.level is None else max(current.level, effect.level)
        return current
    effect.last_tick = last_tick
    if effect.period:
        effect.next_period = tick if effect.period_on_application else tick + effect.period
    for field, op, value, channel in effect.modifiers:
        getattr(unit, field).modify(op, value, channel, key=effect.name)
    unit.effects[effect.name] = effect
    return effect


def expire_effects(unit, tick):
    """Remove the effects whose last tick is before `tick` (called at the start of each tick)."""
    for name, effect in list(unit.effects.items()):
        if tick > effect.last_tick:
            for field, _, _, _ in effect.modifiers:
                getattr(unit, field).remove(name)
            del unit.effects[name]


def legacy_last_tick(applied_time, duration, on_actor):
    """The last tick a sunder, shred or Striker's Flail buff covered before step 4, kept for one commit so the tables
    stay identical: the old status ended on the first tick k with k / TPS > applied_time + duration, compared in float
    seconds, at the start of that tick on the acting champion (last tick k - 1) and after the champion acted on a
    dummy (last tick k). That is the applied tick + 30 x duration (+1 on a dummy), but a tick less for about 3% of
    application ticks, from float rounding alone."""
    end = applied_time + duration
    k = max(0, math.floor(end * TPS) - 2)
    while not k / TPS > end:
        k += 1
    return k - 1 if on_actor else k

"""Debuffs an item puts on the damaged target (ledger I7): sunder and shred (DebuffItem) and burn (BurnItem)."""
from buildstore import BuildDataError, load_build
from effects import ActiveEffect, apply_effect, last_tick
from timing import TPS, ticks_up
from items.base import BuildItem


# ---------------------------------------------------------------- debuffs on the damaged target (I7)
def debuff_value(champion, row, level):
    """A shared debuff's value at the level an item passes (MakeDebuffGameplayEffectSpecHandle): the build's
    globals.debuff_level_to_value row (CT_DebuffLevelToValue; ShredSunderChill 30 -> 0.7, BurnWound 1 -> 0.01)."""
    from build_champion import curve_at  # build_champion imports the item registries
    g = ((getattr(champion, "build", None) or load_build()).data.get("globals") or {}).get("debuff_level_to_value")
    if not g or row not in g:
        raise BuildDataError(f"the build has no globals.debuff_level_to_value.{row} (re-snapshot)")
    return curve_at(g[row]["points"], level, g[row]["interp"] or "Linear")


class DebuffItem(BuildItem):
    """An item whose script answers the holder's attack and spell damage (WaitForDealDamage, Damage.Source.Unit) by
    applying a debuff to the damaged unit after the damage (PostApply): the next hit is reduced, not that one.
    LEVEL_PARAM / DURATION_PARAM name the GA parameters whose curve rows give the level and duration."""
    GA = None
    LEVEL_PARAM = DURATION_PARAM = None

    def __init__(self, phases=("PostOnDealDamage",)):
        super().__init__(phases=phases)

    def param_row(self, champion, param):
        return self.row(champion, self.ga_param(champion, self.GA, param))

    def performAbility(self, phase, time, champion, input_=0):
        target = getattr(champion, "lastDamagedOpponent", None)
        if phase == "PostOnDealDamage" and target is not None and input_ and input_[0]:
            self.debuff(champion, target, time, self.param_row(champion, self.LEVEL_PARAM),
                        self.param_row(champion, self.DURATION_PARAM))
        return input_

    def debuff(self, champion, target, time, level, duration):
        raise NotImplementedError


def apply_burn(champion, target, level, duration):
    """GE_Burn on `target` from `champion` (I7), as an effects.ActiveEffect with the build's rules (globals.burn):
    one burn per target (StackLimitCount 1); a new application renews the duration but not the period
    (NeverReset); the first tick is one period after application (bExecutePeriodicEffectOnApplication false). It
    covers ticks up to the applied tick + ticks_up(duration)."""
    g = champion.build.data["globals"]["burn"]
    burn = ActiveEffect("Burn", level=level, period=ticks_up(g["period"]), period_on_application=bool(g["on_application"]))
    apply_effect(target, burn, champion.tick, last_tick(champion.tick, duration))
    champion.__dict__.setdefault("burning", {})[id(target)] = target


def tick_burns(champion):
    """Deal the burns due this tick, once per tick however many burn items the holder has: true damage of
    BurnWound(level) x the target's max HP, not boosted by anything (owner, 2026-11-17; I7)."""
    if getattr(champion, "burn_tick", None) == champion.tick:
        return
    champion.burn_tick = champion.tick
    for target in (getattr(champion, "burning", None) or {}).values():
        burn = target.effects.get("Burn")
        for _ in range(burn.due(champion.tick) if burn is not None else 0):
            dmg = debuff_value(champion, "BurnWound", burn.level) * target.hp.stat
            # items=[]: a burn tick is not an attack or a spell, so no on-hit effect answers it
            champion.doDamage(target, [], 0, dmg, dmg, "true", champion.tick / TPS)


class BurnItem(DebuffItem):
    """An item that burns (and wounds: nothing against dummies) the targets of the holder's attacks and spells."""
    def __init__(self):
        super().__init__(phases=("preCombat", "PostOnDealDamage", "onUpdate"))

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.burning = {}
        elif phase == "onUpdate":
            tick_burns(champion)
        return super().performAbility(phase, time, champion, input_)

    def debuff(self, champion, target, time, level, duration):
        apply_burn(champion, target, level, duration)

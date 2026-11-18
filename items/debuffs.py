"""Debuffs an item puts on the damaged target (ledger I7): sunder and shred (DebuffItem). Burn is not simulated."""
from buildstore import BuildDataError, load_build
from effects import ActiveEffect, apply_effect, last_tick
from events import DAMAGE_POST, UNIT
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
    LISTENS = {DAMAGE_POST: frozenset((UNIT,))}  # WaitForDealDamage(Damage.Source.Unit), PostApply

    def __init__(self, phases=()):
        super().__init__(phases=phases)

    def param_row(self, champion, param):
        return self.row(champion, self.ga_param(champion, self.GA, param))

    def performAbility(self, phase, time, champion, input_=0):
        if phase == DAMAGE_POST and input_.amount:
            self.debuff(champion, input_.target, time, self.param_row(champion, self.LEVEL_PARAM),
                        self.param_row(champion, self.DURATION_PARAM))
        return input_

    def debuff(self, champion, target, time, level, duration):
        raise NotImplementedError


def shared_rule(champion, effect, attribute):
    """(op, channel) of the single `attribute` modifier of a shared effect (GE_MRShred, GE_ArmorSunder, ...): the
    effect is one asset whoever applies it, read from the first item script in the build that lists it."""
    build = getattr(champion, "build", None) or load_build()
    for entry in (build.data.get("items") or {}).values():
        ge = (entry.get("script_effects") or {}).get(effect)
        if ge:
            ms = [m for m in ge.get("modifiers") or [] if m["attribute"] == attribute]
            if len(ms) != 1:
                raise BuildDataError(f"{effect} has no single {attribute} modifier in build {build.version}")
            return ms[0]["op"], ms[0].get("channel", 1)
    raise BuildDataError(f"no item script in build {build.version} lists {effect}")


def apply_shred(champion, target, level, duration):
    """GE_MRShred on `target` at debuff `level` for `duration` s: MagicResist x ShredSunderChill(level) on Channel2,
    one "Shred" per target whoever applies it (the later end and the higher level win, effects.py)."""
    op, channel = shared_rule(champion, "GE_MRShred", "MagicResist")
    shred = ActiveEffect("Shred", [("mr", op, debuff_value(champion, "ShredSunderChill", level), channel)])
    apply_effect(target, shred, champion.tick, last_tick(champion.tick, duration))


def apply_sunder(champion, target, level, duration):
    """GE_ArmorSunder on `target` at debuff `level` for `duration` s: Armor x ShredSunderChill(level) on Channel2, one
    "Sunder" per target whoever applies it (the later end and the higher level win, effects.py)."""
    op, channel = shared_rule(champion, "GE_ArmorSunder", "Armor")
    sunder = ActiveEffect("Sunder", [("armor", op, debuff_value(champion, "ShredSunderChill", level), channel)])
    apply_effect(target, sunder, champion.tick, last_tick(champion.tick, duration))

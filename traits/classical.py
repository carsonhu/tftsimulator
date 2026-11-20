"""The Classical trait (DA_Virtuosos19)."""
from effects import ActiveEffect, apply_effect, last_tick
from registry import register
from timing import TPS, ticks_up
from traits.base import BuildTrait

CAPTIVATED = "Captivated"


def captivate(champion, target, duration):
    """GE_Virtuosos19_Captivate on `target` for `duration` s, applied by a Classical champion's own rule (Samira: her
    crits) when the board has Classical (ApplyCaptivate checks the trait level >= 1). Instances don't stack: the enemy
    is Captivated while any is running, so the latest end wins (effects.py renewal)."""
    if champion.trait_tier(Classical.KEY) == 0:
        return
    apply_effect(target, ActiveEffect(CAPTIVATED, []), champion.tick, last_tick(champion.tick, duration))


@register("trait")
class Classical(BuildTrait):
    """Classical (DA_Virtuosos19): "Classical champions Captivate enemies in unique ways. They gain Damage Amp,
    increased by 1% every 6 seconds an enemy is Captivated." CT_Virtuosos19 at the tier: VirtuosoDA (8/18/33%),
    DAFromCaptivating (1%), SecondsPerDA (6), DATickCheckRate (0.25 s).

    Members get GE_Virtuoso19_VirtuosoDA (OutgoingDamageMultiplier + VirtuosoDA, infinite) with the item stats (I1).
    While an enemy is Captivated (the tag GE_Virtuosos19_Captivate grants), GA_Virtuosos19_DamageAmp runs on it: at
    once and then every DATickCheckRate (a looping timer, cleared when the Captivate ends) it applies
    GE_Virtuosos19_ApplyTickDA to every Classical ally: OutgoingDamageMultiplier + DATickCheckRate x
    DAFromCaptivating / SecondsPerDA, infinite, for the rest of combat. Captivates come from Classical champions'
    own rules (`captivate`); other Classical units on the board are not simulated, so only the champion's own count.
    The Captivated's 10% reduced damage, the roses, the bench chance and the emblem change no damage dealt.
    """
    KEY = "DA_Virtuosos19"
    display_name = "Classical"

    def __init__(self, level=0, params=0):
        super().__init__(level, params, phases=["preCombat", "onUpdate"])
        self.timers = {}  # id(enemy) -> exact time (s) of its next tick

    def member(self, champion):
        return champion.has_trait(self.KEY)

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.trait_tier(self.KEY) and self.member(champion):
            champion.dmgMultiplier.modify("+", champion.trait_value(self.KEY, "VirtuosoDA"))

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            self.timers = {}
            return input_
        if not self.member(champion) or champion.trait_tier(self.KEY) == 0:
            return input_
        rate = champion.trait_value(self.KEY, "DATickCheckRate")
        per_tick = rate * champion.trait_value(self.KEY, "DAFromCaptivating") / champion.trait_value(self.KEY, "SecondsPerDA")
        now = champion.tick / TPS
        for enemy in champion.opponents:
            if CAPTIVATED not in enemy.effects:
                self.timers.pop(id(enemy), None)  # the Captivate ended: the timer is cleared (K2_OnDormant)
                continue
            due = self.timers.setdefault(id(enemy), now)  # newly Captivated: a tick at once
            while ticks_up(due) <= champion.tick:
                champion.dmgMultiplier.modify("+", per_tick)
                due += rate
            self.timers[id(enemy)] = due
        return input_


Classical.levels = [0] + Classical.breakpoints()

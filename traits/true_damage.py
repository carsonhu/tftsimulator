"""The TrueDamage trait."""
from registry import register
from traits.base import BuildTrait


@register("trait")
class TrueDamage(BuildTrait):
    """True Damage (DA_TrueDamage19), A-Side (Win) only: "True Damage members deal 18% / 30% bonus true damage."

    DA_TrueDamage19 has six tiers, three per side (A-Side: trait levels 1-3 at (3), (5), (5) Prismatic; B-Side: 4-6).
    The A-Side (3) tier gives members GE_TrueDamage19_GrantBonusTDGA, whose GA_TrueDamage19_DealBonusTD answers every
    damage the unit deals (WaitForDealDamage, Damage.Source.Unit, PostApply) with GE_TrueDamage19_DealTrueDamage:
    the damage dealt x SideB_BonusTDPercent at the trait level (B19). The (5) tier's effects in this build are an
    execute and omnivamp whose rows are 0; the owner ruled (2026-11-17) to follow its tooltip, 30% bonus true damage.
    The B-Side's combat effects and the Prismatic quest tiers are not modelled. The bonus is not itself a trigger
    (no other effect hears it) and is not amplified again.
    """
    KEY = "DA_TrueDamage19"
    display_name = "True Damage"
    levels = [0, 3, 5]  # A-Side units on the board

    def __init__(self, level=0, params=0):
        super().__init__(level, params, phases=["PostOnDealDamage"])

    def applyStats(self, champion):
        if getattr(champion, "trait_tiers", None) is None:
            champion.trait_tiers = {}
        # A-Side trait level: 1 at (3), 2 at (5) (the Prismatic level 3 needs its quest)
        champion.trait_tiers[self.KEY] = 2 if self.level >= 5 else 1 if self.level >= 3 else 0

    def performAbility(self, phase, time, champion, input_=0):
        if (champion.trait_tier(self.KEY) == 0 or self.KEY not in (champion.data.d.get("trait_keys") or [])
                or not input_ or not input_[0]):
            return input_
        bonus = champion.trait_value(self.KEY, "SideB_BonusTDPercent") * input_[0]
        # items=[]: nothing reacts to the bonus itself (and it doesn't trigger itself)
        champion.doDamage(champion.lastDamagedOpponent, [], 0, bonus, bonus, "true", time)
        return input_

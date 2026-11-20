"""The Arcanist trait."""
from registry import register
from traits.base import BuildTrait, pct


@register("trait")
class Arcanist(BuildTrait):
    """Arcanist (DA_Arcanist19): "Your team gains Ability Power, Arcanists gain more." CT_Arcanist19 at the tier:
    ArcanistAP (25/50/70%), NonArcanistAP (12/18/30%).

    DA_Arcanist19's TargetEffectsForTier (B16): GE_19_Arcanist_TeamAP (AbilityPower + NonArcanistAP) on allies
    without the trait (TFTAddAlliesWithoutTraitRule), GE_19_Arcanist_SelfishAP (AbilityPower + ArcanistAP) on allies
    with it (TFTAddAlliesWithTraitsOfSource): a member gets ArcanistAP only, not both. Both infinite, Channel1 (bonus
    AP, so Rabadon's multiplies it, I5). Applied in the static-stats pass like items (I1). The emblem (mana on kill)
    is not modelled.
    """
    KEY = "DA_Arcanist19"
    display_name = "Arcanist"
    team_trait = True  # its team-wide half reaches non-members: offered in Team Traits (owner, 2026-11-19)

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.trait_tier(self.KEY) == 0:
            return
        member = champion.has_trait(self.KEY)
        champion.ap.modify("+", champion.trait_value(self.KEY, "ArcanistAP" if member else "NonArcanistAP"))

    @classmethod
    def team_card(cls, build):
        t = build.trait(cls.KEY)
        return {"text": "Your team gains Ability Power.",
                "rows": cls.team_tiers(build, lambda i: [[pct(t.row("NonArcanistAP", col=i)), "AP"]])}


Arcanist.levels = [0] + Arcanist.breakpoints()

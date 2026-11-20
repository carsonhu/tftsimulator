"""The Prodigy trait."""
from registry import register
from traits.base import BuildTrait


@register("trait")
class Prodigy(BuildTrait):
    """Prodigy (DA_Prodigy19): "Your team gains 1 Mana Regen. Prodigies gain more." CT_Prodigy19 at the tier:
    AllyBonusManaRegen (1), ProdigyBonusManaRegen (2/3/6/7), PercentDamageAllyHeal (12% at (5)).

    DA_Prodigy19's tier effects: GE_19_Prodigy_NonTrait (ManaPerSecond + AllyBonusManaRegen) on allies without the
    trait (TFTAddAlliesWithoutTraitRule), GE_19_Prodigy_Trait (ManaPerSecond + ProdigyBonusManaRegen +
    AllyBonusManaRegen) on members: a member gets 2/3/6/7 + 1. Both infinite, Channel1, applied with the item stats
    (I1). The (5) heal (GA_19_Prodigy_AllyHeal: the lowest-Health ally heals for a share of Prodigies' spell damage)
    changes no damage and is not modelled; nor is the emblem.
    """
    KEY = "DA_Prodigy19"
    display_name = "Prodigy"
    team_trait = True  # its team-wide half reaches non-members: offered in Team Traits (owner, 2026-11-19)

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.trait_tier(self.KEY) == 0:
            return
        regen = champion.trait_value(self.KEY, "AllyBonusManaRegen")
        if self.KEY in (champion.data.d.get("trait_keys") or []):
            regen += champion.trait_value(self.KEY, "ProdigyBonusManaRegen")
        champion.manaRegen.modify("+", regen)


Prodigy.levels = [0] + Prodigy.breakpoints()

"""The Hitmaker trait."""
from registry import register
from traits.base import BuildTrait


@register("trait")
class Hitmaker(BuildTrait):
    """Hitmaker (DA_Hitmaker19): "Hitmakers gain 12% Attack Damage. The Hitmakers with the most items become Big Shots,
    gaining even more Attack Damage." CT_Hitmaker19 at the tier: BaseAD (12%), BonusAD (20/35%), NumHitmakers (1/2).

    Every member: DA_Hitmaker19's tier effect GE_19_Hitmaker_BaseAD (AttackDamage + BaseAD) (B18).
    Big Shots: GA_Hitmaker19 UpdateBigShots, outside combat, registers MostItemsTargetEffects: the NumHitmakers members
    first by TR_Sort_ByNumItemsEquipped (after TR_Sort_ByStrongestRules and an attribute sort) get
    GE_19_Hitmaker_BonusAD (AttackDamage + BonusAD) as well: 32% / 47% in all. Which members those are depends on the
    whole board, so it is the "Is Big Shot" flag (default 1). Both effects are infinite, Channel1 (bonus AD,
    multiplied by Deathblade, I5). The emblem is not modelled.
    """
    KEY = "DA_Hitmaker19"
    display_name = "Hitmaker"
    team_trait = False  # the flag is about this champion, not membership

    @staticmethod
    def extraParameters():
        return {"Title": "Is Big Shot", "Min": 0, "Max": 1, "Default": 1}

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.trait_tier(self.KEY) == 0 or self.KEY not in (champion.data.d.get("trait_keys") or []):
            return
        champion.bonus_ad.addStat(champion.trait_value(self.KEY, "BaseAD") * 100)
        if self.params:
            champion.bonus_ad.addStat(champion.trait_value(self.KEY, "BonusAD") * 100)


Hitmaker.levels = [0] + Hitmaker.breakpoints()

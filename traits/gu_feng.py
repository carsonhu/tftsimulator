"""The Gu Feng trait."""
from registry import register
from traits.base import BuildTrait


@register("trait")
class GuFeng(BuildTrait):
    """Gu Feng (DA_Heavenscale19): "Gu Feng champions gain stats, scaling with your player level." CT_Heavenscale19 at
    the tier: HeavenscaleStats (2 from (2)), HeavenscaleHPPercent (2% from (3)).

    (2) GE_Heavenscale19_BaseStats on members (client asset, rls-19.1.0.5986094 export): AttackDamage and AbilityPower
    + 0.01 x GenericCalc1, Armor and MagicResist + 1 x GenericCalc1, where GenericCalc1 = HeavenscaleStats x player
    level: +2% AD and AP and +2 Armor and MR per level (VOD4 19:16 tooltip: "2% AD AP and 2 Armor MR per level").
    Infinite, Channel1, with the item stats (I1). (3) GE_Heavenscale19_HPStats: HealthMax x (1 + HeavenscaleHPPercent x
    level), applied too (it changes no damage against dummies). (4)'s Scrolls (and Level 11) are not modelled: the
    owner, 2026-11-18: realistically only the (2) is relevant. The player level is the parameter, default 8 (owner,
    2026-11-18).
    """
    KEY = "DA_Heavenscale19"
    display_name = "Gu Feng"

    DEFAULT_LEVEL = 8

    @staticmethod
    def extraParameters():
        return {"Title": "Player level", "Min": 1, "Max": 10, "Default": GuFeng.DEFAULT_LEVEL}

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.trait_tier(self.KEY) == 0 or not champion.has_trait(self.KEY):
            return
        level = int(self.params or self.DEFAULT_LEVEL)  # 0 = not set: the default
        per_level = champion.trait_value(self.KEY, "HeavenscaleStats") * level  # GenericCalc1
        champion.bonus_ad.modify("+", 0.01 * per_level)
        champion.ap.modify("+", 0.01 * per_level)
        champion.armor.modify("+", per_level)
        champion.mr.modify("+", per_level)
        hp_pct = champion.trait_value(self.KEY, "HeavenscaleHPPercent")
        if hp_pct:
            champion.hp.modify("MultiplyAdditive", 1 + hp_pct * level)  # GenericCalc2


GuFeng.levels = [0] + GuFeng.breakpoints()

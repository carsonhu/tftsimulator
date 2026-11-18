"""The Jazz trait."""
from registry import register
from traits.base import BuildTrait


@register("trait")
class Jazz(BuildTrait):
    """Jazz (DA_Jazz19): "For each active trait (except uniques), your team gains bonus Health and Damage Amp."
    CT_Jazz19 at the tier: JazzHealthPercent (1.5/2.5/3.5%), JazzDamageAmp (1/1.5/2%) per active trait.

    Every ally gains JazzDamageAmp x the number of active non-unique traits as damage amp (and Health, which changes
    no damage against dummies). The count is a board question, so it is the parameter: 'Active traits' (Jazz itself
    counts), default 5. Infinite, with the item stats (I1). The Dig on This augment is not modelled here.
    """
    KEY = "DA_Jazz19"
    display_name = "Jazz"

    @staticmethod
    def extraParameters():
        return {"Title": "Active traits", "Min": 1, "Max": 15, "Default": 5}

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.trait_tier(self.KEY) == 0:
            return
        n = int(self.params or 5)  # 0 = not set: the default
        champion.dmgMultiplier.modify("+", champion.trait_value(self.KEY, "JazzDamageAmp") * n)


Jazz.levels = [0] + Jazz.breakpoints()

"""The Composer trait (Malzahar's unique trait)."""
from registry import register
from traits.base import BuildTrait


@register("trait")
class Composer(BuildTrait):
    """Composer (DA_Malzahar19_UniqueTrait, Malzahar's own): "Mystical Instruments can appear in your shop. There is
    one of each rarity. For each one you have, your team gains 3% Ability Power. Malzahar gains double."

    GA_Malzahar19_UniqueTrait counts the instruments the army holds (Set19.Trait.Composer.Has<Instrument> tags) and
    sets Malzahar's Stack to it (GE_Malzahar19_SetStack). The trait's effects: GE_Malzahar19_TeamwideAP on every
    ally, Malzahar included (TFTAddAllAlliesTargetRule): AbilityPower + GenericCalc1 = UniqueTrait_APPerInstrument
    (3%) x Stack; GE_Malzahar19_MalzaharAP on Malzahar: AbilityPower + GenericCalc2 = UniqueTrait_MalzaharBonusAPPercent
    (1) x GenericCalc1. Both infinite, Channel1, applied with the item stats (I1). The parameter is the instruments
    held (0-5): a shop outcome, the page's choice. The Baron Nashor unlock is not modelled.
    """
    KEY = "DA_Malzahar19_UniqueTrait"
    display_name = "Composer"
    team_trait = True  # its team-wide half reaches non-members: offered in Team Traits (owner, 2026-11-19)
    INSTRUMENTS = 5  # one of each rarity

    @staticmethod
    def extraParameters():
        return {"Title": "Instruments", "Min": 0, "Max": Composer.INSTRUMENTS, "Default": 0}

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.trait_tier(self.KEY) == 0:
            return
        team = champion.trait_value(self.KEY, "UniqueTrait_APPerInstrument") * int(self.params or 0)
        if self.KEY in (champion.data.d.get("trait_keys") or []):  # Malzahar: the teamwide AP and his own again
            team += champion.trait_value(self.KEY, "UniqueTrait_MalzaharBonusAPPercent") * team
        if team:
            champion.ap.modify("+", team)


Composer.levels = [0] + Composer.breakpoints()

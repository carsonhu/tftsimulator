"""The Choreographer trait."""
from registry import register
from traits.base import BuildTrait


@register("trait")
class Choreographer(BuildTrait):
    """Choreographer (DA_Choreographer19): "Allies who start in the front 2 rows gain Shield. All other allies gain
    Damage Amp. Choreographers gain double." CT_Choreographer19 at the tier: Shield (150/225/375/550), DamageAmp
    (6/10/15/20%), ChoreographerPercentMult (2).

    Allies starting in the back rows get GA_Choreographer_Backline: GE_Choreographer_BacklineDamageAmp, SetByCaller
    Set19.Trait.Choreographer.DamageAmp = DamageAmp x ChoreographerPercentMult for a Choreographer (0x74-0x149),
    taken as the unit's damage amp for the combat. Front-row allies get GA_Choreographer_Frontline's shield instead,
    which changes no damage against dummies. Where the simulated unit starts is the parameter: 'By range' (the
    default) puts a unit with attack range 1 in the front rows and any other in the back; or pick either row. The
    (5) dash (DashPercentHealthTriger) and the Dance Party augment are not modelled.
    """
    KEY = "DA_Choreographer19"
    display_name = "Choreographer"
    ROWS = ["By range", "Front 2 rows", "Back rows"]

    @staticmethod
    def extraParameters():
        return {"Title": "Starts in", "Min": 0, "Max": len(Choreographer.ROWS) - 1, "Default": 0,
                "Options": Choreographer.ROWS}

    def back_row(self, champion):
        row = self.ROWS[int(self.params or 0)]
        return champion.attack_range > 1 if row == "By range" else row == "Back rows"

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.trait_tier(self.KEY) == 0 or not self.back_row(champion):
            return
        amp = champion.trait_value(self.KEY, "DamageAmp")
        if self.KEY in (champion.data.d.get("trait_keys") or []):
            amp *= champion.trait_value(self.KEY, "ChoreographerPercentMult")
        champion.dmgMultiplier.modify("+", amp)


Choreographer.levels = [0] + Choreographer.breakpoints()

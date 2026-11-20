"""The Choreographer trait."""
from registry import register
from traits.base import BuildTrait, pct


@register("trait")
class Choreographer(BuildTrait):
    """Choreographer (DA_Choreographer19): "Allies who start in the front 2 rows gain Shield. All other allies gain
    Damage Amp. Choreographers gain double." CT_Choreographer19 at the tier: Shield (150/225/375/550), DamageAmp
    (6/10/15/20%), ChoreographerPercentMult (2).

    Allies starting in the back rows get GA_Choreographer_Backline: GE_Choreographer_BacklineDamageAmp, SetByCaller
    Set19.Trait.Choreographer.DamageAmp = DamageAmp x ChoreographerPercentMult for a Choreographer (0x74-0x149),
    taken as the unit's damage amp for the combat. Front-row allies get GA_Choreographer_Frontline's shield instead,
    which changes no damage against dummies. The simulated unit is taken to start in the back 2 rows, whatever its
    range (owner, 2026-11-18). The (5) dash (DashPercentHealthTriger) and the Dance Party augment are not modelled.
    """
    KEY = "DA_Choreographer19"
    display_name = "Choreographer"
    team_trait = True  # its team-wide half reaches non-members: offered in Team Traits (owner, 2026-11-19)

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.trait_tier(self.KEY) == 0:
            return
        amp = champion.trait_value(self.KEY, "DamageAmp")
        if self.KEY in (champion.data.d.get("trait_keys") or []):
            amp *= champion.trait_value(self.KEY, "ChoreographerPercentMult")
        champion.dmgMultiplier.modify("+", amp)

    @classmethod
    def team_card(cls, build):
        t = build.trait(cls.KEY)
        return {"text": "Allies who start in the back 2 rows gain Damage Amp (front-row allies a Shield instead).",
                "rows": cls.team_tiers(build, lambda i: [[pct(t.row("DamageAmp", col=i)), "DamageAmp"]])}


Choreographer.levels = [0] + Choreographer.breakpoints()

"""The KDA trait."""
from registry import register
from timing import ticks_up
from traits.base import BuildTrait


@register("trait")
class KDA(BuildTrait):
    """K/DA (DA_KDA19): "K/DA champions release new songs based on their total star level. At Combat Start and after
    8 seconds, they gain power for each of their songs." `level` is the members' total star level (B14).

    GA_KDA19 applies GE_KDA19_BonusApplier to the members at combat start (TriggerOnCombatStart) and once more after
    MidCombatTrigger seconds; GA_KDA19_BonusApplier then applies, by tier (m = PreviousTraitBoost from tier 4, else 1):
      tier >= 1 (POP/STARS): GE_KDA19_ManaReduction, ManaMax MultiplyCompound by the chain (ManaReduction x m - 1) x -1
                 = 1 - 0.1 m; infinite, stack limit 1 (the second trigger adds nothing)
      tier >= 2 (DRUM GO DUM): a shield (nothing against dummies)
      tier >= 3 (VILLAIN): GE_KDA19_DecayingAS (_Boosted from tier 4): AttackSpeed MultiplyAdditive 1 + DecayingAS (x m),
                 for ASDuration s, periodic 0.25 s with bChangeOverTimeForPeriodic toward 1: the bonus falls by
                 1/32 of itself every 0.25 s (B14)
    Tier 5 (WATCH ME, a stun) changes nothing against dummies; tier 6 (FIRESTARTER) is the trait's damage
    (GE_KDA19_FirestarterDoT with the trait as source), not the unit's, and is not counted; tier 7 is 4-star units.
    """
    KEY = "DA_KDA19"
    display_name = "K/DA"
    DECAY_PERIOD = 0.25  # GE_KDA19_DecayingAS Period (effect literal)

    def __init__(self, level=0, params=0):
        super().__init__(level, params, phases=["preCombat"])

    def row(self, champion, name):
        """CT_KDA19 rows have one point (1); a curve is flat outside its points, so every tier reads it."""
        return champion.trait_value(self.KEY, name, tier=1)

    def _member(self, champion):
        return self.KEY in (champion.data.d.get("trait_keys") or []) and champion.trait_tier(self.KEY) > 0

    def _boost(self, champion):
        return self.row(champion, "PreviousTraitBoost") if champion.trait_tier(self.KEY) >= 4 else 1

    def applyStats(self, champion):
        super().applyStats(champion)
        if not self._member(champion):
            return
        m = self._boost(champion)
        # x (1 - reduction) on max mana after every Channel1 change (Dawncore's too), as before step 3
        champion.fullMana.modify("MultiplyCompound", 1 - self.row(champion, "ManaReduction") * m, channel=2)

    def performAbility(self, phase, time, champion, input_=0):
        if not self._member(champion) or champion.trait_tier(self.KEY) < 3:
            return input_
        m = self._boost(champion)
        bonus = self.row(champion, "DecayingAS") * m  # the AS bonus at the trigger, decaying to 0
        duration = self.row(champion, "ASDuration")
        steps = int(round(duration / self.DECAY_PERIOD))
        triggers = [0.0]
        if self.row(champion, "TriggerOnCombatStart") != 1:
            triggers = []
        triggers.append(self.row(champion, "MidCombatTrigger"))
        for n, t0 in enumerate(triggers):
            key = f"KDA decaying AS {id(self)} {n}"  # one effect per trigger, its size stepped down
            for j in range(steps + 1):
                # the bonus held from step j to step j + 1; at the end of the duration it is gone
                held = bonus * (1 - j / steps) if j < steps else 0.0
                champion.schedule_tick(champion.tick + ticks_up(t0 + j * self.DECAY_PERIOD),
                                       lambda v=held, k=key: champion.aspd.modify("MultiplyAdditive", 1 + v, key=k)
                                       if v else champion.aspd.remove(k))
        return input_


KDA.levels = [0] + KDA.breakpoints()

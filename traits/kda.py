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
        champion.fullMana.mult *= 1 - self.row(champion, "ManaReduction") * m

    def performAbility(self, phase, time, champion, input_=0):
        if not self._member(champion) or champion.trait_tier(self.KEY) < 3:
            return input_
        m = self._boost(champion)
        bonus = self.row(champion, "DecayingAS") * m * 100  # attack speed points
        duration = self.row(champion, "ASDuration")
        steps = int(round(duration / self.DECAY_PERIOD))
        triggers = [0.0]
        if self.row(champion, "TriggerOnCombatStart") != 1:
            triggers = []
        triggers.append(self.row(champion, "MidCombatTrigger"))
        for t0 in triggers:
            for j in range(steps + 1):
                # the bonus held from step j to step j + 1; at the end of the duration it is gone
                before = bonus * (1 - (j - 1) / steps) if j else 0.0
                after = bonus * (1 - j / steps) if j < steps else 0.0
                delta = after - before
                champion.schedule_tick(champion.tick + ticks_up(t0 + j * self.DECAY_PERIOD),
                                       lambda d=delta: champion.aspd.addStat(d))
        return input_


KDA.levels = [0] + KDA.breakpoints()

"""The Trickshot trait."""
from registry import register
from stats import Attack
from timing import TPS, projectile_ticks
from events import ONHIT_PRE
from traits.base import BuildTrait


def bounce_hexes(opponents):
    """Hexes a Trickshot ricochet travels between dummies (B12): the next one stands 1 hex away; with a single dummy
    the ricochet returns to it (the bounce computer re-picks an already-hit enemy when none is left), 0 hexes."""
    return 1 if len(opponents) > 1 else 0


@register("trait")
class Trickshot(BuildTrait):
    """Trickshot (DA_Trickshot19): "Trickshots' Attacks and Abilities ricochet. Each ricochet deals a percentage of
    the previous bounce's damage." CT_Trickshot19 at the tier: NumRichochets (1/1/2), RichochetDamage (0.22/0.33/0.33).

    Attacks (members only; GA_LaunchProjectileAttack_Trickshot19 -> BounceComputer_Autoattacks ->
    HandleAutoAttackBounce): when an attack lands, ricochet k = 1..NumRichochets flies the attack's projectile from
    the previous target to the next (nearest not yet hit) and applies GE_AutoAttack_Bounce_Trickshot19:
    BasicAttackDamage x RichochetDamage^k (MMC_TrickshotReduction), physical, with the attack's crit result
    (PassInCritResult; the engine averages crits, so the same chance). Not an attack (no IsAttack tag): no mana, no
    attack count. Its on-hit effects at RichochetDamage^k are not modelled (no listed item has one).
    Spells: each member's own script handles the spell ricochets (e.g. Draven) at the same tier.
    """
    KEY = "DA_Trickshot19"
    display_name = "Trickshot"

    LISTENS = {ONHIT_PRE: frozenset()}  # the attack's own hit (ricochets apply no on-hit effects)

    def performAbility(self, phase, time, champion, input_=0):
        opponents = champion.opponents
        if self.KEY not in (champion.data.d.get("trait_keys") or []) or champion.trait_tier(self.KEY) == 0:
            return input_
        n = int(champion.trait_value(self.KEY, "NumRichochets"))
        r = champion.trait_value(self.KEY, "RichochetDamage")
        step = projectile_ticks(champion.timing.proj_speed, bounce_hexes(opponents))
        for k in range(1, n + 1):
            def ricochet(k=k):
                target = opponents[k % len(opponents)]
                attack = Attack(opponents=[target], scaling=lambda level, baseAD, AD, AP: baseAD * AD * r ** k,
                                canCrit=True, canOnHit=False, attackType="physical", numTargets=1,
                                regularAuto=False)
                champion.doAttack(attack, champion.items, champion.tick / TPS)
            champion.schedule_tick(champion.tick + k * step, ricochet)
        return input_


Trickshot.levels = [0] + Trickshot.breakpoints()

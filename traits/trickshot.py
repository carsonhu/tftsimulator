"""The Trickshot trait."""
from registry import register
from stats import Attack
from timing import TPS, projectile_ticks
from events import ON_SPELL, ONHIT_PRE
from traits.base import BuildTrait


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
        if self.KEY not in (champion.data.d.get("trait_keys") or []) or champion.trait_tier(self.KEY) == 0:
            return input_
        if ON_SPELL in input_.tags:
            return input_  # an on-hit spell (Gnar's rock) is not a launched attack: its own script ricochets it
        n = int(champion.trait_value(self.KEY, "NumRichochets"))
        r = champion.trait_value(self.KEY, "RichochetDamage")
        # the dummies stand still, so the whole chain is known at the hit: each ricochet departs on the previous
        # one's arrival, to the nearest dummy not yet hit (the layout, B12)
        target, hit, at = input_.target, [input_.target], champion.tick
        for k in range(1, n + 1):
            target, hexes = champion.ricochet(target, hit)
            hit.append(target)
            at += projectile_ticks(champion.timing.proj_speed, hexes)

            def ricochet(k=k, target=target):
                attack = Attack(opponents=[target], scaling=lambda level, baseAD, AD, AP: baseAD * AD * r ** k,
                                canCrit=True, canOnHit=False, attackType="physical", numTargets=1,
                                regularAuto=False)
                champion.doAttack(attack, champion.items, champion.tick / TPS)
            champion.schedule_tick(at, ricochet)
        return input_


Trickshot.levels = [0] + Trickshot.breakpoints()

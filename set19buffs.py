"""Set 19 traits, augments and other buffs. Each is written from the selected build; a class is live only when
listed in one of the registries below."""
from buildstore import load_build
from item import Item
from stats import Attack
from timing import TPS, projectile_ticks

class_buffs = []  # traits
augments = []
stat_buffs = []
wisps = []
no_buff = ["NoBuff"]


class Buff(Item):
    """A trait or augment: `level` is the breakpoint (0 = off), `params` any extra input (see extraParameters)."""
    levels = [0]

    def __init__(self, name, level, params, phases):
        super().__init__(name, phases=phases)
        self.level = level
        self.params = params

    def performAbility(self, phase, time, champion, input_=0):
        raise NotImplementedError("Please Implement this method")

    def ability(self, phase, time, champion, input_=0):
        if self.level == 0:
            return input_
        if self.phases and phase in self.phases:
            return self.performAbility(phase, time, champion, input_)
        return input_

    @staticmethod
    def extraParameters():
        return 0

    def hashFunction(self):
        init_tuple = (self.name, str(self.level))
        param_tuple = (self.params,) if isinstance(self.params, int) else tuple(self.params)
        return init_tuple + param_tuple

    def __hash__(self):
        return hash(self.hashFunction())


class NoBuff(Buff):
    levels = [0]
    display_name = "NoItem"

    def __init__(self, level=0, params=0):
        super().__init__(self.display_name, level, params, phases=None)

    def performAbility(self, phase, time, champion, input_=0):
        return 0


# ---------------------------------------------------------------- traits from the build (ledger B11)
class BuildTrait(Buff):
    """A Set 19 trait whose numbers come from the selected build.

    `level` is how many units with the trait the board fields (0 = inactive), offered at the build's breakpoints.
    In the static-stats pass (Item.applyStats, before any combat phase) the trait records the tier those units reach
    under the champion's own build (B11) in `champion.trait_tiers[KEY]`, so every phase can read it; a member's spell
    reads its trait's values at that tier (`BuildChampion.trait_value`). A trait whose effect is entirely inside its
    members' spells (Encore) does nothing else.
    """
    KEY = None
    levels = [0]

    def __init__(self, level=0, params=0, phases=None):
        super().__init__(self.display_name, level, params, phases=phases)

    @classmethod
    def breakpoints(cls, build=None):
        return (build or load_build()).trait(cls.KEY).thresholds

    def applyStats(self, champion):
        build = getattr(champion, "build", None) or load_build()
        tiers = getattr(champion, "trait_tiers", None)
        if tiers is None:
            tiers = champion.trait_tiers = {}
        tiers[self.KEY] = build.trait(self.KEY).tier_of(self.level)

    def performAbility(self, phase, time, champion, input_=0):
        return input_


class Encore(BuildTrait):
    """Encore (DA_Encore19): "When Encore champions fire projectiles with their abilities, they fire an extra one
    with reduced effectiveness." The extra missiles are in each member's spell script, which reads
    CT_Encore19 RecastEffectiveness at the Encore tier (e.g. Neeko). Non-members are unaffected."""
    KEY = "DA_Encore19"
    display_name = "Encore"


Encore.levels = [0] + Encore.breakpoints()  # the newest build's breakpoints (units on the board)

class_buffs.append("Encore")


def bounce_hexes(opponents):
    """Hexes a Trickshot ricochet travels between dummies (B12): the next one stands 1 hex away; with a single dummy
    the ricochet returns to it (the bounce computer re-picks an already-hit enemy when none is left), 0 hexes."""
    return 1 if len(opponents) > 1 else 0


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

    def __init__(self, level=0, params=0):
        super().__init__(level, params, phases=["onAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        opponents = input_
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

class_buffs.append("Trickshot")

"""Set 19 traits, augments and other buffs. Each is written from the selected build; a class is live only when
listed in one of the registries below."""
from buildstore import load_build
from item import Item

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
    At combat start the trait records the tier those units reach under the champion's own build (B11) in
    `champion.trait_tiers[KEY]`; a member's spell reads its trait's values at that tier
    (`BuildChampion.trait_value`). A trait whose effect is entirely inside its members' spells (Encore) does nothing
    else here.
    """
    KEY = None
    levels = [0]

    def __init__(self, level=0, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    @classmethod
    def breakpoints(cls, build=None):
        return (build or load_build()).trait(cls.KEY).thresholds

    def performAbility(self, phase, time, champion, input_=0):
        build = getattr(champion, "build", None) or load_build()
        tiers = getattr(champion, "trait_tiers", None)
        if tiers is None:
            tiers = champion.trait_tiers = {}
        tiers[self.KEY] = build.trait(self.KEY).tier_of(self.level)
        return 0


class Encore(BuildTrait):
    """Encore (DA_Encore19): "When Encore champions fire projectiles with their abilities, they fire an extra one
    with reduced effectiveness." The extra missiles are in each member's spell script, which reads
    CT_Encore19 RecastEffectiveness at the Encore tier (e.g. Neeko). Non-members are unaffected."""
    KEY = "DA_Encore19"
    display_name = "Encore"


Encore.levels = [0] + Encore.breakpoints()  # the newest build's breakpoints (units on the board)

class_buffs.append("Encore")

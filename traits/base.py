"""The trait base classes: Buff, NoBuff and BuildTrait (a trait read from the build, ledger B11)."""
from buildstore import load_build
from item import Item


class Buff(Item):
    """A trait or augment: `level` is the breakpoint (0 = off), `params` any extra input (see extraParameters)."""
    levels = [0]

    def __init__(self, name, level, params, phases):
        super().__init__(name, phases=phases)
        self.level = level
        self.params = params

    def performAbility(self, phase, time, champion, input_=0):
        raise NotImplementedError("Please Implement this method")

    def hears(self, moment, event):
        return self.level != 0 and super().hears(moment, event)  # an inactive trait hears nothing

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

    # ---- the card a Team Traits row shows (sim_entry.get_cards "team"): the team-wide half only, from the build
    @classmethod
    def team_tiers(cls, build, stats_at, text=""):
        """[{threshold, label, stats, text}] for each distinct breakpoint: stats_at(tier) -> [[value, tag], ...]."""
        out = []
        for tier, threshold in enumerate(sorted(set(build.trait(cls.KEY).thresholds)), start=1):
            stats = stats_at(tier)
            if stats is not None:
                out.append({"threshold": threshold, "label": f"({threshold})", "stats": stats, "text": text})
        return out


def pct(v):
    """0.12 -> '12%', 0.015 -> '1.5%' (a card's stat value)."""
    return f"{round(v * 100, 1):g}%"

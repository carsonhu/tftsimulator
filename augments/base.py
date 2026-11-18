"""The augment base class: an augment whose numbers come from the selected build (DA_<Name> in build.augments)."""
from buildstore import BuildDataError, load_build
from traits.base import Buff


class BuildAugment(Buff):
    """An augment the player holds (level 1 = held). Rows are read from the build's augment entry by name; every
    augment row is a single value (one curve point)."""
    KEY = None
    levels = [1]

    def __init__(self, level=1, params=0, phases=None):
        super().__init__(self.display_name, level, params, phases=phases)

    def value(self, champion, row):
        build = getattr(champion, "build", None) or load_build()
        pts = build.augment(self.KEY).row(row)
        if not pts or len({v for t, v in pts}) != 1:
            raise BuildDataError(f"{self.KEY}: row {row!r} is not a single value in build {build.version}")
        return pts[0][1]

    def applyStats(self, champion):
        if self.level:
            self.stats(champion)

    def stats(self, champion):
        """The augment's unconditional stats (the static-stats pass, I1)."""

    def performAbility(self, phase, time, champion, input_=0):
        return input_

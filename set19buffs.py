"""Set 19 traits, augments and other buffs. Each is written from the selected build; a class is live only when
listed in one of the registries below."""
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

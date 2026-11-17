"""Set 19 champions: build_champion.BuildChampion subclasses. A class is live only when it is named in champ_list.

Each champion is added after its worksheet (champions/<Name>.md) has the evidence its timing needs (decision D5).
"""
from champion import Champion
from timing import Timing

champ_list = []


class TrainingDummy(Champion):
    """The opponents: they never attack, cast or die (G9); the UI sets their HP, armor and MR."""

    def __init__(self, level=1):
        super().__init__('Training Dummy', 1800, 0, 0, -1, 0.01, 100, 100, 1)
        self.timing = Timing(source={'all': 'dummy: never attacks'})

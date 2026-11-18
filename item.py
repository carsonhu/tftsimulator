from stats import FastDeepCopy


class Item(FastDeepCopy):
    def __init__(self, name, phases=None):
        self.name = name
        self.phases = phases


    def applyStats(self, champion):
        """Static stats from the selected build, applied with the fixed stats before any combat phase
        (Simulator.itemStats). prePreCombat stays free for flags that items read in preCombat (set18's Retribution).
        Set 19 items and traits override this (set19items.BuildItem, set19buffs.BuildTrait)."""
        return None

    def performAbility(self, phases, time, champion, input_=0):
        raise NotImplementedError("Please Implement this method for {}".format(self.name))       

    def ability(self, phase, time, champion, input_=0):
        if self.phases and phase in self.phases:
            return self.performAbility(phase, time, champion, input_)
        return input_

    def hashFunction(self):
        return (self.name,)

    def __hash__(self):
        return hash(self.hashFunction())
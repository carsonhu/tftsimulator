from stats import FastDeepCopy


class Item(FastDeepCopy):
    # combat events this item reacts to: moment -> the tags an event must carry (events.py)
    LISTENS = {}

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

    def hears(self, moment, event):
        wants = self.LISTENS.get(moment)
        return wants is not None and wants <= event.tags

    def on_event(self, moment, event, champion):
        """A combat event this item listens to; by default handled in performAbility(moment, time, champion, event)."""
        self.performAbility(moment, event.time, champion, event)

    def ability(self, phase, time, champion, input_=0):
        if self.phases and phase in self.phases:
            return self.performAbility(phase, time, champion, input_)
        return input_

    def hashFunction(self):
        return (self.name,)

    def __hash__(self):
        return hash(self.hashFunction())
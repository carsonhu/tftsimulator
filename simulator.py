import math

from timing import TPS


class Simulator(object):
    def __init__(self):
        self.current_time = 0
        self.frameTime = 1 / TPS

    def itemStats(self, items, champion):
        # static stats first (the build's: Item.applyStats), then the phases in order:
        # prePreCombat is for flags other effects read in preCombat
        for item in items:
            item.applyStats(champion)
        for phase in ("prePreCombat", "preCombat", "postPreCombat"):
            for item in items:
                item.ability(phase, 0, champion)

    def simulate(self, items, buffs, champion, opponents, duration, frameRate=TPS):
        """Run `duration` seconds of combat in whole 30 Hz ticks (T1). `frameRate` is accepted for old callers and
        ignored: the game's rate is fixed (G1), and a finer step would split events the game puts on one tick.
        dmgVector rows: (time, damage, AS, mana, max mana)."""
        champion.item_count += len([item for item in items if item.name != "NoItem"])
        items = items + buffs + champion.items
        champion.items = items
        champion.opponents = opponents
        self.itemStats(items, champion)
        champion.prepare_timing()
        # Combat opens with a fresh attack at tick 0, released one windup in (G3); movement is not modelled, so
        # melee units don't spend time closing in.

        # preCombat can append items (Arbiter, Mecha), so this has to come
        # after itemStats. Nothing appends once the tick loop is running.
        champion.onUpdateItems = [
            item
            for item in items
            if getattr(item, "phases", None) and "onUpdate" in item.phases
        ]

        for opponent in opponents:
            # dummies never act (update() is never called on them); only their statuses tick
            opponent.opponents = champion

        n_ticks = math.ceil(duration * TPS - 1e-9)
        for tick in range(n_ticks):
            self.current_time = tick / TPS
            champion.update(opponents, items, self.current_time)
            for opponent in opponents:
                if opponent.statuses and self.current_time >= opponent.nextStatusUpdate:
                    opponent.updateStatuses(self.current_time)
        self.current_time = n_ticks / TPS
        return champion.dmgVector

    def simulateUlt(self, items, buffs, champion, opponents):
        items = items + buffs + champion.items
        champion.items = items
        champion.opponents = opponents
        self.itemStats(items, champion)
        champion.performAbility(opponents, items, 0)
        return champion.dmgVector

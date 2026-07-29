class Simulator(object):
    def __init__(self):
        self.current_time = 0
        self.frameTime = 1 / 30
        # self.frameTime = 1/60

    def itemStats(self, items, champion):
        for item in items:
            champion.addStats(item)
        for phase in ("prePreCombat", "preCombat", "postPreCombat"):
            for item in items:
                item.ability(phase, 0, champion)

    def simulate(self, items, buffs, champion, opponents, duration, frameRate=30):
        # there's no real distinction between items and buffs
        # dmgVector: (Time, Damage Dealt, current AS, current Mana)
        self.frameTime = 1 / frameRate
        champion.item_count += len([item for item in items if item.name != "NoItem"])
        items = items + buffs + champion.items
        champion.items = items
        champion.opponents = opponents
        self.itemStats(items, champion)
        self.current_time = 0

        # preCombat can append items (Arbiter, Mecha), so this has to come
        # after itemStats. Nothing appends once the frame loop is running.
        champion.onUpdateItems = [
            item
            for item in items
            if getattr(item, "phases", None) and "onUpdate" in item.phases
        ]

        for opponent in opponents:
            opponent.nextAttackTime = duration * 2
            # normally set by update(); done here so it still holds on the
            # frames we skip below
            opponent.opponents = champion

        while self.current_time < duration:
            champion.update(opponents, items, self.current_time)
            for opponent in opponents:
                # Opponents carry no items and never act: nextAttackTime is
                # pushed past the end of combat and nothing reads their mana or
                # attack counters. Only their statuses (shred, corrosion, a DoT)
                # need ticking. Doing just that instead of a full update is what
                # keeps this loop from spending 8/9 of its time on the dummies
                # rather than the champion being measured.
                if opponent.statuses and self.current_time >= opponent.nextStatusUpdate:
                    opponent.updateStatuses(self.current_time)
            self.current_time += self.frameTime
        return champion.dmgVector

    def simulateUlt(self, items, buffs, champion, opponents):
        items = items + buffs + champion.items
        champion.items = items
        champion.opponents = opponents
        self.itemStats(items, champion)
        champion.performAbility(opponents, items, 0)
        return champion.dmgVector

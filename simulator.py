class Simulator(object):
    def __init__(self):
        self.current_time = 0
        self.frameTime = 1 / 30
        # self.frameTime = 1/60

    def itemStats(self, items, champion):
        for item in items:
            champion.addStats(item)
        for item in items:  # mb.
            item.ability("prePreCombat", 0, champion)
        for item in items:
            item.ability("preCombat", 0, champion)
        for item in items:
            item.ability("postPreCombat", 0, champion)

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

        for opponent in opponents:
            opponent.nextAttackTime = duration * 2
        while self.current_time < duration:
            champion.update(opponents, items, self.current_time)
            for opponent in opponents:
                opponent.update(champion, [], self.current_time)
            self.current_time += self.frameTime
        return champion.dmgVector

    def simulateUlt(self, items, buffs, champion, opponents):
        items = items + buffs + champion.items
        champion.items = items
        champion.opponents = opponents
        self.itemStats(items, champion)
        champion.performAbility(opponents, items, 0)
        return champion.dmgVector

from set18buffs import Buff


class ChampRole(Buff):
    def __init__(self):
        super().__init__(name="Role", level=1, params=0, phases="preCombat")

    def performAbility(self, phase, time, champion, input_=0):
        manaPerAttack = 0
        manaRegen = 0
        fighterAsScaling = {2: 5, 3: 10, 4: 20, 5: 30, 6: 30}
        archetype = champion.role.archetype
        if archetype == "Caster":
            manaPerAttack = 7
            manaRegen = 2
        elif archetype == "Tank":
            manaPerAttack = 5
        elif archetype in ["Marksman", "Fighter", "Assassin"]:
            manaPerAttack = 10
        if archetype == "Fighter":
            champion.aspd.addStat(fighterAsScaling[champion.stage])
        champion.manaPerAttack.addStat(manaPerAttack)
        champion.manaRegen.addStat(manaRegen)
        return 0

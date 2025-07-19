from set15buffs import Buff
from role import Role


class ChampRole(Buff):
    def __init__(self):
        super().__init__(name="Role", level=1, params=0, phases="preCombat")

    def performAbility(self, phase, time, champion, input_=0):
        manaPerAttack = 0
        manaRegen = 0
        if champion.role == Role.CASTER:
            manaPerAttack = 7
            manaRegen = 2
        elif champion.role == Role.TANK:
            manaPerAttack = 5
        elif champion.role in [Role.ASSASSIN, Role.MARKSMAN, Role.FIGHTER]:
            manaPerAttack = 10
        champion.manaPerAttack.addStat(manaPerAttack)
        champion.manaRegen.addStat(manaRegen)
        return 0

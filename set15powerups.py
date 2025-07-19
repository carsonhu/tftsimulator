from set15buffs import Buff


class AttackExpert(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Attack Expert", level, params, phases=["preCombat"])
        self.base_scaling = 5
        self.scaling = 0.3

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(self.base_scaling)
        champion.bonus_ad.addMultiplier += self.scaling
        return 0


class CriticalThreat(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__(
            "CriticalThreat", level, params, phases=["preCombat", "onUpdate"]
        )
        self.critBonus = 0.05
        self.nextBonus = 3

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.canSpellCrit = True
        elif phase == "onUpdate":
            if time >= self.nextBonus:
                self.nextBonus += 3
                champion.crit.addStat(self.critBonus)
        return 0


class MagicExpert(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Magic Expert", level, params, phases=["preCombat"])
        self.base_scaling = 10
        self.scaling = 0.3

    def performAbility(self, phase, time, champion, input_=0):
        champion.ap.addStat(self.base_scaling)
        champion.ap.addMultiplier += self.scaling
        return 0


class OnTheEdge(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("On the Edge", level, params, phases=["preCombat"])
        self.scaling = 0.35

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(self.scaling)
        return 0


class FinalAscent(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("FinalAscent", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        if "Kayle" in champion.name:
            champion.finalAscent = True
        return 0


class Bludgeoner(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Bludgeoner", level, params, phases=["preCombat"])
        self.scaling = 0.4

    def performAbility(self, phase, time, champion, input_=0):
        champion.armorPierce.addStat(self.scaling)
        return 0


class KeenEye(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("KeenEye", level, params, phases=["preCombat"])
        self.scaling = 0.4

    def performAbility(self, phase, time, champion, input_=0):
        champion.mrPierce.addStat(self.scaling)
        return 0


class HerosArc(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Hero's Arc", level, params, phases=["preCombat"])
        self.scaling = 0.045

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(self.scaling * champion.tactician_level)
        if champion.tactician_level == 10:
            champion.dmgMultiplier.addStat(0.35)
        return 0


class BestestBoy(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("BestestBoy", level, params, phases=["onUpdate"])
        self.scaling = 12
        self.next_bonus = 5

    def performAbility(self, phase, time, champion, input_=0):
        # in the future this will be done beforehand
        if champion.name == "Smolder":
            if time > self.next_bonus:
                self.next_bonus += 5
                champion.bonus_ad.addStat(self.scaling)
        return 0


class PowerFont(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Power Font", level, params, phases=["onUpdate"])
        self.scaling = 1
        self.next_bonus = 0

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.next_bonus:
            self.next_bonus += 3
            champion.manaRegen.addStat(self.scaling)
        return 0


class SuperGenius(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Super Genius", level, params, phases=["onUpdate"])
        # self.scaling = 1
        self.next_bonus = 2

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.next_bonus:
            self.next_bonus += 2
            champion.ap.addStat(champion.manaRegen.stat)
        return 0


class Annihilation(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__(
            "Annihilation", level, params, phases=["preCombat", "onUpdate"]
        )
        self.scaling = 0.15
        self.takedown_scaling = 0.15
        self.activated = False

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.dmgMultiplier.addStat(self.scaling)
        elif phase == "onUpdate":
            if not self.activated and time > champion.first_takedown:
                champion.dmgMultiplier.addStat(self.takedown_scaling)
                self.activated = True
        return 0


class GatherForce(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Gather Force", level, params, phases=["preAbility"])
        self.scaling = 0.4

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(self.scaling * champion.fullMana.stat)
        return 0


class MindBattery(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Mind Battery", level, params, phases=["preAbility"])
        self.activated = False

    def performAbility(self, phase, time, champion, input_=0):
        if not self.activated:
            champion.manaRegen.addStat(5)
            champion.ap.addStat(30)
            self.activated = True
        return 0


class RampingRage(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Ramping Rage", level, params, phases=["postAttack"])
        self.scaling = 3

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(self.scaling)
        return 0


class Surge66(Buff):
    # not sure what doubles means
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Surge66", level, params, phases=["preCombat", "postAttack"])
        self.aspd_scaling = 15
        self.ap_scaling = 10

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.aspd.addStat(self.aspd_scaling)
            champion.ap.addStat(self.ap_scaling)
        if phase == "postAttack":
            if champion.numAttacks == 15:
                champion.aspd.addStat(self.aspd_scaling)
                champion.ap.addStat(self.ap_scaling)
            elif champion.numAttacks == 66:  # idk if this is how it works
                champion.aspd.addStat(self.aspd_scaling * 2)
                champion.ap.addStat(self.ap_scaling * 2)
        return 0


class Kahunahuna(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Kahunahuna", level, params, phases=["postAttack"])
        self.stacks = 0
        self.scaling = 200

    def performAbility(self, phase, time, champion, input_=0):
        self.stacks += 1
        if self.stacks % 6 == 0:
            baseDmg = self.scaling * champion.bonus_ad.stat
            champion.doDamage(
                champion.opponents[0], [], 0, baseDmg, baseDmg, "true", time
            )
        return 0

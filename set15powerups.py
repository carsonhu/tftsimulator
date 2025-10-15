import math

from set15buffs import Buff
from stats import JhinBonusAD

import status


class AttackExpert(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Attack Expert", level, params, phases=["preCombat"])
        self.base_scaling = 5
        self.scaling = 0.35

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(self.base_scaling)
        champion.bonus_ad.addMultiplier += self.scaling
        return 0


class SolarBreath(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Solar Breath", level, params, phases=["preCombat"])
        self.scaling = 0.15

    def performAbility(self, phase, time, champion, input_=0):
        champion.extraDmgMultiplier.addStat(self.scaling)
        return 0


class SkyPiercer(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Sky Piercer", level, params, phases=["preCombat"])
        self.scaling = 0.05

    def performAbility(self, phase, time, champion, input_=0):
        for opponent in champion.opponents:
            opponent.armor.mult = 0.7
            opponent.mr.mult = 0.7

        champion.extraDmgMultiplier.addStat(self.scaling)
        return 0


class SpiritSword(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__(
            "Spirit Sword",
            level,
            params,
            phases=["preCombat", "onCrit", "onDealDamage"],
        )
        self.buffActive = False
        self.proc_scaling = 0.3

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.crit.addStat(0.2)
        elif phase == "onCrit":
            self.buffActive = True
        elif phase == "onDealDamage":
            if self.buffActive:
                self.buffActive = False
                spell_dmg = self.proc_scaling * input_
                champion.doDamage(
                    champion.opponents[0],
                    [],
                    0,
                    spell_dmg,
                    spell_dmg,
                    "magical",
                    time,
                )
            return input_
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
        self.scaling = 0.35

    def performAbility(self, phase, time, champion, input_=0):
        champion.ap.addStat(self.base_scaling)
        champion.ap.addMultiplier += self.scaling
        return 0


class DriftDuo(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Drift Duo", level, params, phases=["preCombat"])
        self.scaling = 3

    def performAbility(self, phase, time, champion, input_=0):
        champion.manaRegen.addStat(self.scaling)
        return 0


class FuryBreak(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__(
            "Fury Break (15s)", level, params, phases=["preCombat", "onUpdate"]
        )
        self.as_scaling = 25
        self.time_bonus = 15
        self.buff_duration = 4

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.aspd.addStat(self.as_scaling)
        if phase == "onUpdate":
            if time > self.time_bonus:
                self.time_bonus = 999
                champion.applyStatus(
                    status.DecayingASModifier("FuryBreak"),
                    self,
                    time,
                    self.buff_duration,
                    300,
                )
        return 0


class Hemorrhage(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__(
            "Hemorrhage (Instant)", level, params, phases=["PostOnDealSpellDamage"]
        )
        self.scaling = 0.6

    def performAbility(self, phase, time, champion, input_=0):
        # input: (dmg, dtype)
        dmg = input_[0] * self.scaling
        champion.doDamage(champion.opponents[0], [], 0, dmg, dmg, "true", time)
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
        self.scaling = 0.45

    def performAbility(self, phase, time, champion, input_=0):
        champion.armorPierce.addStat(self.scaling)
        return 0


class FairyTail(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__(
            "Fairy Tail (instant dmg)", level, params, phases=["postAbility"]
        )
        # guessing the scaling
        self.scaling = {1: 80, 2: 119, 3: 158, 4: 197, 5: 236, 6: 275}

    def performAbility(self, phase, time, champion, input_=0):
        dmg = self.scaling[champion.stage] * 2
        champion.doDamage(champion.opponents[0], [], 0, dmg, dmg, "magical", time)
        return 0


class ArtisticKO(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Artistic KO", level, params, phases=["preCombat"])
        self.scaling = 1.35

    def performAbility(self, phase, time, champion, input_=0):
        champion.ultMultiplier = self.scaling
        return 0


class RisingChaos(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("RisingChaos", level, params, phases=["preAbility"])
        self.orbs = 1

    def performAbility(self, phase, time, champion, input_=0):
        if champion.name == "Syndra":
            for orb in range(self.orbs):
                champion.multiTargetSpell(
                    champion.opponents,
                    champion.items,
                    time,
                    1,
                    champion.chaosAbilityScaling,
                    "magical",
                )
            self.orbs += 1
        return 0


class BulletHell(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Bullet Hell", level, params, phases=["preCombat"])
        self.scaling = 1.3

    def performAbility(self, phase, time, champion, input_=0):
        if champion.name == "Ashe" or champion.name == "Yuumi":
            if hasattr(champion, "projectile_multiplier"):
                champion.projectile_multiplier = self.scaling
                return 0
        elif hasattr(champion, "projectiles"):
            champion.projectiles = round(champion.projectiles * self.scaling)

        return 0


class IceBender(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__(
            "Ice Bender", level, params, phases=["preCombat", "preAbility"]
        )
        self.scaling = 0.25

    def performAbility(self, phase, time, champion, input_=0):
        if champion.name == "Ryze":
            if phase == "preCombat":
                # make sure he can't do shit
                champion.nextAttackTime = 3
                champion.attackWindupLockout = 3
            elif phase == "preAbility":
                champion.multiTargetSpell(
                    champion.opponents,
                    champion.items,
                    time,
                    champion.num_targets,
                    lambda x, y, z: self.scaling * champion.abilityScaling(x, y, z),
                    "magical",
                )
        return 0


class StarStudent(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Star Student", level, params, phases=["postPreCombat"])
        self.hp_scaling = 200
        self.potential_scaling = 1.4

    def performAbility(self, phase, time, champion, input_=0):
        champion.hp.addStat(self.hp_scaling)
        if hasattr(champion, "potential"):
            champion.potential = math.ceil(champion.potential * self.potential_scaling)
        return 0


class Mage(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Mage", level, params, phases=["preCombat", "postAbility"])
        self.dmgMultiplierScaling = -0.2

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            # cast twice = not quite double cast time but close to it
            champion.castTime *= 1.8
            champion.dmgMultiplier.mult = (
                champion.dmgMultiplier.mult + self.dmgMultiplierScaling
            )
        elif phase == "postAbility":
            champion.numCasts += 1
            champion.performAbility(champion.opponents, champion.items, time)


class Precision(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Precision", level, params, phases=["preCombat", "preAttack"])
        self.set_aspd = 0.7
        # self.as_conversion = 0.8
        self.atk_multiplier = 1.3
        self.extra_mana = 5

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.aspd.base = self.set_aspd
            champion.aspd.as_cap = self.set_aspd
            champion.bonus_ad = JhinBonusAD(
                champion.bonus_ad.base,
                champion.bonus_ad.mult,
                champion.bonus_ad.add,
                champion.aspd,
            )
            champion.manaPerAttack.addStat(self.extra_mana)
        elif phase == "preAttack":
            # doublecheck to ensure it doesn't activate during cast
            if input_.regularAuto:
                input_.scaling = (
                    lambda level, baseAD, AD, AP: baseAD * AD * self.atk_multiplier
                )
            return input_
        return 0


class KeenEye(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Keen Eye", level, params, phases=["preCombat"])
        self.scaling = 0.45

    def performAbility(self, phase, time, champion, input_=0):
        champion.mrPierce.addStat(self.scaling)
        return 0


class KillerInstinct(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Killer Instinct", level, params, phases=["preCombat"])
        self.scaling = 3

    def performAbility(self, phase, time, champion, input_=0):
        champion.manaRegen.addStat(self.scaling)
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


class Efficient(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Efficient", level, params, phases=["preCombat"])
        self.scaling = 15

    def performAbility(self, phase, time, champion, input_=0):
        champion.fullMana.addStat(-1 * self.scaling)
        return 0


class Weights(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Weights", level, params, phases=["preCombat"])
        self.scaling = 50

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(self.scaling)
        return 0


class WindWall(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Wind Wall", level, params, phases=["preCombat"])
        self.scaling = 0.6

    def performAbility(self, phase, time, champion, input_=0):
        champion.crit.addStat(self.scaling)
        return 0


class CornerCarry(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Corner Carry", level, params, phases=["preCombat"])
        self.scaling = 30

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(self.scaling)
        return 0


class MaxSpeed(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Max Speed", level, params, phases=["preCombat"])
        self.base = 15
        self.takedown_interval = 3

    def performAbility(self, phase, time, champion, input_=0):
        to_add = self.base + (champion.takedowns // self.takedown_interval)
        champion.aspd.addStat(to_add)
        return 0


class MaxAttack(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Max Attack", level, params, phases=["preCombat"])
        self.base = 12
        self.takedown_interval = 2

    def performAbility(self, phase, time, champion, input_=0):
        to_add = self.base + (champion.takedowns // self.takedown_interval)
        champion.bonus_ad.addStat(to_add)
        return 0


class MaxArcana(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Max Arcana", level, params, phases=["preCombat"])
        self.base = 20
        self.takedown_interval = 2

    def performAbility(self, phase, time, champion, input_=0):
        to_add = self.base + (champion.takedowns // self.takedown_interval)
        champion.ap.addStat(to_add)
        return 0


class HatTrick(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Hat Trick", level, params, phases=["preCombat"])
        self.base = 16
        self.stat_per_takedown = 0.75

    def performAbility(self, phase, time, champion, input_=0):
        to_add = self.base + champion.takedowns * self.stat_per_takedown
        champion.bonus_ad.addStat(to_add)
        champion.ap.addStat(to_add)
        return 0


class BestestBoy(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("BestestBoy", level, params, phases=["onUpdate"])
        self.scaling = 14
        self.bonus_interval = 4
        self.next_bonus = 1

    def performAbility(self, phase, time, champion, input_=0):
        # in the future this will be done beforehand
        if champion.name == "Smolder":
            if time > self.next_bonus:
                self.next_bonus += self.bonus_interval
                champion.bonus_ad.addStat(self.scaling)
        elif champion.name == "KogMaw":
            if time > self.next_bonus:
                self.next_bonus += self.bonus_interval
                champion.ap.addStat(self.scaling)
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
        self.bonus_interval = 2

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.next_bonus:
            self.next_bonus += self.bonus_interval
            # adaptive does not multiply it
            champion.ap.addStat(champion.manaRegen.stat)
        return 0


class Annihilation(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__(
            "Annihilation", level, params, phases=["preCombat", "onUpdate"]
        )
        self.scaling = 0.12
        self.takedown_scaling = 0.16
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


class DarkAmulet(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Dark Amulet", level, params, phases=["preAbility"])
        self.scaling = 12

    def performAbility(self, phase, time, champion, input_=0):
        champion.ap.addStat(self.scaling)


class SuperMega(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Super Mega", level, params, phases=["preCombat"])
        self.scaling = 20

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(self.scaling)
        champion.super_mega = True


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
        self.scaling = 3.5

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(self.scaling)
        return 0


class Desperado(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Desperado", level, params, phases=["postAttack"])
        self.attack_threshold = 8
        self.scaling = 1

    def performAbility(self, phase, time, champion, input_=0):
        if champion.numAttacks % self.attack_threshold == 0:
            baseDmg = champion.atk.stat * champion.bonus_ad.stat * self.scaling
            # could change this to 5 opps
            for i in range(5):
                champion.doDamage(
                    champion.opponents[0], [], 0, baseDmg, baseDmg, "physical", time
                )
        return 0


class Surge66(Buff):
    # not sure what doubles means
    levels = [1]

    def __init__(self, level, params):
        super().__init__("Surge66", level, params, phases=["preCombat", "postAttack"])
        self.aspd_scaling = 20
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
        self.scaling = 150

    def performAbility(self, phase, time, champion, input_=0):
        self.stacks += 1
        if self.stacks % 6 == 0:
            baseDmg = self.scaling * champion.bonus_ad.stat
            champion.doDamage(
                champion.opponents[0], [], 0, baseDmg, baseDmg, "true", time
            )
        return 0

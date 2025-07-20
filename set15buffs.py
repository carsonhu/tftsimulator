from item import Item
from stats import JhinBonusAD

import status
import ast


def get_classes_from_file(file_path):
    with open(file_path, "r") as file:
        file_content = file.read()

    # Parse the file content into an AST
    tree = ast.parse(file_content)

    # Extract all class definitions
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    return classes


# Example usage
file_path = "set15powerups.py"
powerups = get_classes_from_file(file_path)

class_buffs = [
    "SupremeCells",
    "BattleAcademia",
    "Duelist",
    "Executioner",
    "Prodigy",
    "Sniper",
    "Sorcerer",
    "Luchador",
    "MonsterTrainer",
    "SoulFighter",
    "Strategist",
]

augments = [
    "BackupDancers",
    "Shred30",
    "BlazingSoulI",
    "BlazingSoulII",
    "MacesWill",
    "Backup",
    "Moonlight",
    "FinalAscension",
    "CyberneticUplinkII",
    "CyberneticUplinkIII",
    "StandUnitedI",
    "Ascension",
    "CyberneticImplantsII",
    "CyberneticImplantsIII",
    "PumpingUpI",
    "PumpingUpII",
    "PumpingUpIII",
    "NoScoutNoPivot",
    "HoldTheLine",
    "AdaptiveStyle",
    "TonsOfStats",
]

stat_buffs = ["ASBuff"]

no_buff = ["NoBuff"]


class Buff(Item):
    levels = [0]

    def __init__(self, name, level, params, phases):
        super().__init__(name, phases=phases)
        self.level = level
        self.params = params

    def performAbility(self, phase, time, champion, input_=0):
        raise NotImplementedError("Please Implement this method")

    def ability(self, phase, time, champion, input_=0):
        # if it's level 0 of an ability
        if self.level == 0:
            return input_
        if self.phases and phase in self.phases:
            return self.performAbility(phase, time, champion, input_)
        return input_

    def extraParameters():
        return 0

    def hashFunction(self):
        # Hash function used for caching;
        # (name, level, params)
        init_tuple = (self.name, str(self.level))
        if isinstance(self.params, int):
            param_tuple = (self.params,)
        else:
            param_tuple = tuple(self.params)
        return init_tuple + param_tuple

    def __hash__(self):
        return hash(self.hashFunction())


class NoBuff(Buff):
    levels = [0]

    def __init__(self, level, params):
        # params is number of stacks
        super().__init__("NoItem", level, params, phases=None)

    def performAbility(self, phase, time, champion, input_=0):
        return 0


class ASBuff(Buff):
    levels = [1]

    def __init__(self, level, params):
        # params is number of stacks
        super().__init__(
            "Attack Speed " + str(level), level, params, phases=["preCombat"]
        )
        self.as_buff = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(self.as_buff)
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "AS", "Min": 0, "Max": 100, "Default": 0}

    def extraBuff(self, as_buff):
        self.as_buff = as_buff


# CLASS BUFFS


class SupremeCells(Buff):
    levels = [0, 2, 3, 4]

    def __init__(self, level, params):
        super().__init__(
            "SupremeCells " + str(level), level, params, phases=["preCombat"]
        )
        self.scaling = {2: 12, 3: 30, 4: 50}

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(self.scaling[self.level])
        return 0


class Sniper(Buff):
    levels = [0, 2, 3, 4, 5]

    def __init__(self, level, params):
        # params is number of hexes
        super().__init__("Sniper " + str(level), level, params, phases=["preCombat"])
        self.scaling = {0: 0, 2: 0.1, 3: 0.15, 4: 0.25, 5: 0.3}
        self.base_scaling = {0: 0, 2: 0.04, 3: 0.06, 4: 0.09, 5: 0.12}
        self.base_bonus = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(
            self.base_scaling[self.level] + self.scaling[self.level] * self.base_bonus
        )
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Hexes", "Min": 0, "Max": 8, "Default": 4}

    def extraBuff(self, hexes):
        self.base_bonus = hexes


class BattleAcademia(Buff):
    levels = [0, 3, 5, 7]

    def __init__(self, level, params):
        super().__init__(
            "Battle Academia " + str(level), level, params, phases=["preCombat"]
        )
        self.scaling = {3: 3, 5: 5, 7: 7}

    def performAbility(self, phase, time, champion, input_=0):
        champion.potential = self.scaling[self.level]
        return 0


class Prodigy(Buff):
    levels = [0, 2, 3, 4, 5]

    def __init__(self, level, params):
        super().__init__("Prodigy " + str(level), level, params, phases=["preCombat"])
        self.scaling = {0: 0, 2: 3, 3: 5, 4: 7, 5: 9}
        self.non_prodigy_scaling = {0: 0, 2: 1, 3: 2, 4: 3, 5: 4}
        self.is_prodigy = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        value_to_add = (
            self.scaling[self.level]
            if self.is_prodigy
            else self.non_prodigy_scaling[self.level]
        )
        champion.manaRegen.addStat(value_to_add)
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Is Prodigy", "Min": 0, "Max": 1, "Default": 1}

    def extraBuff(self, is_prodigy):
        self.is_prodigy = is_prodigy


class Strategist(Buff):
    levels = [0, 2, 3, 4, 5]

    def __init__(self, level, params):
        super().__init__(
            "Strategist " + str(level), level, params, phases=["preCombat"]
        )
        self.scaling = {2: 0.04, 3: 0.07, 4: 0.11, 5: 0.15}
        self.is_strategist = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        mult = 3 if self.is_strategist else 1
        champion.dmgMultiplier.addStat(self.scaling[self.level] * mult)
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Is Strat", "Min": 0, "Max": 1, "Default": 1}

    def extraBuff(self, is_strategist):
        self.is_strategist = is_strategist


class SoulFighter(Buff):
    levels = [0, 2, 4, 6, 8]

    def __init__(self, level, params):
        super().__init__(
            "Soul Fighter " + str(level),
            level,
            params,
            phases=["onUpdate", "onDealDamage"],
        )
        self.scaling = {2: 120, 4: 200, 6: 300, 8: 450}
        self.ad_scaling = {2: 1, 4: 2, 6: 3, 8: 4}
        self.true_dmg_scaling = {2: 0.1, 4: 0.16, 6: 0.24, 8: 0.36}
        self.next_bonus = 1
        self.max_stacks = 8
        self.stacks = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            if time > self.next_bonus:
                if self.stacks < self.max_stacks:
                    self.next_bonus += 1
                    self.stacks += 1
                    champion.hp.addStat(self.scaling[self.level])
                    champion.bonus_ad.addStat(self.ad_scaling[self.level])
                    champion.ap.addStat(self.ad_scaling[self.level])
        elif phase == "onDealDamage":
            if self.stacks == self.max_stacks:
                true_dmg = self.true_dmg_scaling[self.level] * input_
                champion.doDamage(
                    champion.opponents[0],
                    [],
                    0,
                    true_dmg,
                    true_dmg,
                    "true",
                    time,
                )
            return input_
        return 0


class Executioner(Buff):
    levels = [0, 2, 3, 4, 5]

    def __init__(self, level, params):
        super().__init__(
            "Executioner " + str(level), level, params, phases=["preCombat"]
        )
        self.critChanceScaling = {2: 0.25, 3: 0.35, 4: 0.45, 5: 0.55}
        self.critDmgScaling = {2: 0.1, 3: 0.12, 4: 0.15, 5: 0.2}

    def performAbility(self, phase, time, champion, input=0):
        champion.canSpellCrit = True
        champion.critDmg.addStat(self.critDmgScaling[self.level])
        champion.crit.addStat(self.critChanceScaling[self.level] * 0.5)
        return 0


class Sorcerer(Buff):
    levels = [0, 2, 4, 6]

    def __init__(self, level, params):
        super().__init__("Sorcerer " + str(level), level, params, phases=["preCombat"])
        self.scaling = {2: 20, 4: 50, 6: 80}

    def performAbility(self, phase, time, champion, input=0):
        champion.ap.addStat(self.scaling[self.level])
        return 0


class Luchador(Buff):
    levels = [0, 2, 4]

    def __init__(self, level, params):
        super().__init__("Luchador " + str(level), level, params, phases=["preCombat"])
        self.scaling = {2: 15, 4: 40}

    def performAbility(self, phase, time, champion, input=0):
        champion.bonus_ad.addStat(self.scaling[self.level])
        return 0


class MonsterTrainer(Buff):
    levels = [0, 15, 30, 40]

    def __init__(self, level, params):
        super().__init__(
            "Monster Trainer " + str(level), level, params, phases=["preCombat"]
        )
        self.trainer_level = level

    def performAbility(self, phase, time, champion, input=0):
        champion.trainer_level += self.trainer_level
        # smolder only
        if champion.name == "Smolder":
            champion.bonus_ad.addStat(champion.trainer_level)
            if champion.trainer_level >= 30:
                champion.fullMana.addStat(-10)
                champion.armorPierce.addStat(0.5)
        return 0


class Duelist(Buff):
    levels = [0, 2, 4, 6]

    def __init__(self, level=0, params=0):
        super().__init__("Duelist", level, params, phases=["postAttack"])
        self.scaling = {2: 4, 4: 7, 6: 10}
        self.stacks = 0

    def performAbility(self, phase, time, champion, input_=0):
        if self.stacks < 12:
            champion.aspd.addStat(self.scaling[self.level])
            self.stacks += 1
        return 0


# Unit buffs


class GnarUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Gadagadagada!", level, params, phases=["preAttack"])
        self.as_scaling = 8
        self.stacks = 0
        self.max_stacks = 10

    def performAbility(self, phase, time, champion, input_=0):
        if self.stacks < self.max_stacks:
            self.stacks += 1
            champion.aspd.addStat(self.as_scaling * champion.ap.stat)
        return 0


class KayleUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Unleash the Demon", level, params, phases=["preAttack"])
        self.buff_duration = 3
        self.finalAscentAP = 5
        self.finalAscent10Scaling = 0.55

    def performAbility(self, phase, time, champion, input_=0):
        champion.multiTargetSpell(
            champion.opponents,
            champion.items,
            time,
            1,
            champion.passiveAbilityScaling,
            "magical",
        )
        if champion.finalAscent:
            if champion.tactician_level >= 7 and champion.numAttacks % 3 == 0:
                champion.ap.addStat(self.finalAscentAP)
            if champion.tactician_level == 10:
                num_targets = int(champion.num_targets * 1.5)
                for i in range(2):
                    champion.multiTargetSpell(
                        champion.opponents,
                        champion.items,
                        time,
                        num_targets,
                        lambda x, y, z: self.finalAscent10Scaling
                        * champion.waveAbilityScaling(x, y, z),
                        "magical",
                    )
                for opponent in champion.opponents[0:num_targets]:
                    opponent.applyStatus(
                        status.MRReduction("MR"), champion, time, 3, 0.8
                    )
        if champion.tactician_level >= 6 and champion.tactician_level < 9:
            if champion.numAttacks % 3 == 0:
                champion.multiTargetSpell(
                    champion.opponents,
                    champion.items,
                    time,
                    champion.num_targets,
                    champion.waveAbilityScaling,
                    "magical",
                )
                for opponent in champion.opponents[0 : champion.num_targets]:
                    opponent.applyStatus(
                        status.MRReduction("MR"), champion, time, 3, 0.8
                    )
        elif champion.tactician_level >= 9:
            num_targets = int(champion.num_targets * 1.5)
            champion.multiTargetSpell(
                champion.opponents,
                champion.items,
                time,
                num_targets,
                champion.waveAbilityScaling,
                "magical",
            )
            for opponent in champion.opponents[0:num_targets]:
                opponent.applyStatus(status.MRReduction("MR"), champion, time, 3, 0.8)

        return 0


class JhinUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__(
            "The Curtain Falls",
            level,
            params,
            phases=["preCombat", "preAttack"],
        )
        self.aspd_cap_scaling = [0.75, 0.75, 0.85]

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.aspd.base = self.aspd_cap_scaling[champion.level - 1]
            champion.aspd.as_cap = self.aspd_cap_scaling[
                champion.level - 1
            ]  # hopefully silvermere isnt in the game
            champion.bonus_ad = JhinBonusAD(
                champion.bonus_ad.base,
                champion.bonus_ad.mult,
                champion.bonus_ad.add,
                champion.aspd,
            )
        elif phase == "preAttack":
            if champion.numAttacks % 4 == 0:
                input_.canOnHit = True
                input_.canCrit = champion.canSpellCrit
                input_.attackType = "physical"
                input_.scaling = lambda level, baseAD, AD, AP: champion.abilityScaling(
                    level, AD, AP
                )
        return 0


class MundoUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Give em the Chair!", level, params, phases=["preAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        input_.scaling = champion.passiveAbilityScaling
        return input_


# AUGMENTS


class HoldTheLine(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("HoldTheLine", level, params, phases=["preCombat"])
        self.ad_scaling = 9
        self.ap_scaling = 10
        self.frontliners = 7

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(self.ad_scaling * self.frontliners)
        champion.ap.addStat(self.ap_scaling * self.frontliners)
        return 0


class GlassCannonI(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        # vayne bolts inflicts status "Silver Bolts"
        super().__init__("Glass Cannon I", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(0.13)
        return 0


class GlassCannonII(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Glass Cannon II", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(0.2)
        return 0


class Moonlight(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__(
            "Moonlight (for 3* champs)", level, params, phases=["preCombat"]
        )

    def performAbility(self, phase, time, champion, input_=0):
        if champion.level == 3:
            champion.bonus_ad.addStat(45)
            champion.ap.addStat(45)
        return 0


class MacesWill(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Maces Will", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(6)
        champion.crit.addStat(0.2)
        return 0


class TonsOfStats(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Tons of Stats", level, params, phases=["preCombat"])
        self.scaling = 4

    def performAbility(self, phase, time, champion, input_=0):
        champion.hp.addStat(self.scaling * 11)
        champion.bonus_ad.addStat(self.scaling)
        champion.ap.addStat(self.scaling)
        champion.aspd.addStat(self.scaling)
        champion.armor.addStat(self.scaling)
        champion.mr.addStat(self.scaling)
        # hacky
        if champion.curMana < champion.fullMana.stat:
            champion.curMana += self.scaling
        return 0


class Backup(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Backup", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(12)
        return 0


class StandUnitedI(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Stand United", level, params, phases=["preCombat"])
        self.scaling = 1.5

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(champion.num_traits * self.scaling)
        champion.ap.addStat(champion.num_traits * self.scaling)
        return 0


class CyberneticImplantsII(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Cybernetic Implants II", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(20)
        return 0


class CyberneticImplantsIII(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Cybernetic Implants III", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(30)
        return 0


class PumpingUpI(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Pumping Up I", level, params, phases=["preCombat"])
        self.base_scaling = 6
        self.bonus_scaling = 0.5

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(
            self.base_scaling + self.bonus_scaling * 6 * (champion.stage - 2)
        )
        return 0


class PumpingUpII(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Pumping Up II", level, params, phases=["preCombat"])
        self.base_scaling = 8
        self.bonus_scaling = 1

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(
            self.base_scaling + self.bonus_scaling * 6 * (champion.stage - 2)
        )
        return 0


class PumpingUpIII(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Pumping Up III", level, params, phases=["preCombat"])
        self.base_scaling = 12
        self.bonus_scaling = 2

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(
            self.base_scaling + self.bonus_scaling * 6 * (champion.stage - 2)
        )
        return 0


class NoScoutNoPivot(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("No Scout no Pivot", level, params, phases=["preCombat"])
        self.scaling = 2

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(self.scaling * 5 * (champion.stage - 2))
        champion.ap.addStat(self.scaling * 5 * (champion.stage - 2))
        return 0


class BlazingSoulI(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Blazing Soul I", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(20)
        champion.ap.addStat(20)
        return 0


class BlazingSoulII(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Blazing Soul II", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(35)
        champion.ap.addStat(35)
        return 0


class AdaptiveStyle(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("AdaptiveStyle", level, params, phases=["preAttack"])
        self.stacks = 0
        self.max_stacks = 20

    def performAbility(self, phase, time, champion, input_=0):
        for item in champion.items:
            if "Duelist" in item.name and self.stacks < self.max_stacks:
                self.stacks += 1
                champion.bonus_ad.addStat(2)
                champion.ap.addStat(2)
                break
        return 0


class Ascension(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Ascension", level, params, phases=["onUpdate"])
        self.dmgBonus = 0.6
        self.nextBonus = 15

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            if time >= self.nextBonus:
                self.nextBonus += 99999
                champion.dmgMultiplier.addStat(self.dmgBonus)
        return 0


class ScopedWeaponsII(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("ScopedWeaponsII", level, params, phases=["preCombat"])
        self.scaling = 25

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(self.scaling)
        return 0


class FinalAscension(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__(
            "Final Ascension", level, params, phases=["preCombat", "onUpdate"]
        )
        self.initialDmgBonus = 0.15
        self.dmgBonus = 0.35
        self.nextBonus = 15

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.dmgMultiplier.addStat(self.initialDmgBonus)
        elif phase == "onUpdate":
            if time >= self.nextBonus:
                self.nextBonus += 99999
                champion.dmgMultiplier.addStat(self.dmgBonus)
        return 0


class BackupDancers(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Backup Dancers", level, params, phases=["onUpdate"])
        self.asBonus = 10.5
        self.nextBonus = 3

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            if time >= self.nextBonus:
                self.nextBonus += 3
                champion.aspd.addStat(self.asBonus)
        return 0


class CyberneticUplinkII(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Cybernetic Uplink II", level, params, phases=["onUpdate"])
        self.manaBonus = 2
        self.nextBonus = 1

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            if time >= self.nextBonus:
                champion.addMana(self.manaBonus)
                self.nextBonus += 1
        return 0


class CyberneticUplinkIII(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Cybernetic Uplink III", level, params, phases=["onUpdate"])
        self.manaBonus = 3
        self.nextBonus = 1

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            if time >= self.nextBonus:
                champion.addMana(self.manaBonus)
                self.nextBonus += 1
        return 0


class Shred30(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("30% Armor/MR Shred", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        for opponent in champion.opponents:
            opponent.applyStatus(
                status.ArmorReduction("Armor 30"), champion, time, 30, 0.7
            )
            opponent.applyStatus(status.MRReduction("MR 30"), champion, time, 30, 0.7)
        return 0

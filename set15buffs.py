import ast

import status
from item import Item
from stats import Attack, JhinBonusAD


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
    "SoulFighter",
    "Strategist",
    "Mentor",
    "Edgelord",
    "Bastion",
    "StarGuardian"
]

augments = [
    "BackupDancers",
    "Shred30",
    "BlazingSoulI",
    "BlazingSoulII",
    "MacesWill",
    "BestFriendsI",
    "BestFriendsII",
    "TinyButDeadly",
    "Moonlight",
    "FinalAscension",
    "CyberneticUplinkII",
    "CyberneticUplinkIII",
    "StandUnitedI",
    "Ascension",
    "CyberneticImplantsII",
    "CyberneticImplantsIII",
    "KnowYourEnemy",
    "PumpingUpI",
    "PumpingUpII",
    "PumpingUpIII",
    "NoScoutNoPivot",
    "HoldTheLine",
    "AdaptiveStyle",
    "MessHall",
    "TonsOfStats",
    "LearnFromTheBest",
    "LitFuseSolo",
    "LitFuseDuo",
    "LitFuseTrio",
    "WaterLotusI",
    "WaterLotusII",
    "Hero101",
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
        self.scaling = {2: 0.12, 3: 0.30, 4: 0.50}

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(self.scaling[self.level])
        return 0


class Sniper(Buff):
    levels = [0, 2, 3, 4, 5]

    def __init__(self, level, params):
        # params is number of hexes
        super().__init__("Sniper " + str(level), level, params, phases=["preCombat"])
        self.base_scaling = {0: 0, 2: 0.13, 3: 0.16, 4: 0.22, 5: 0.25}
        self.scaling = {0: 0, 2: 0.03, 3: 0.05, 4: 0.07, 5: 0.1}
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
        if (
            "Ezreal" in champion.name or "Katarina" in champion.name
        ):  # increases cast time a bit
            champion.castTime = champion.secondaryCastTime

        return 0


class Prodigy(Buff):
    levels = [0, 2, 3, 4, 5]

    def __init__(self, level, params):
        super().__init__("Prodigy " + str(level), level, params, phases=["preCombat"])
        self.scaling = {0: 0, 2: 3, 3: 4, 4: 6, 5: 7}
        self.non_prodigy_scaling = {0: 0, 2: 1, 3: 1, 4: 1, 5: 1}
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
        self.scaling = {2: 0.04, 3: 0.06, 4: 0.1, 5: 0.14}
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
        self.scaling = {2: 120, 4: 200, 6: 300, 8: 650}
        self.ad_scaling = {2: 1, 4: 2, 6: 3, 8: 4}
        self.true_dmg_scaling = {2: 0.1, 4: 0.16, 6: 0.22, 8: 0.28}
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


class StarGuardian(Buff):
    # levels = [1]
    # Star guardian works differently from other traits
    levels = [0, 1]

    def __init__(self, level, params):
        super().__init__(f"Star Guardian {level}", level, params, phases=["preCombat", "onUpdate", "postAbility"])
        self.scaling = {
            0: 0, 
            1: 1,
            2: 1,
            3: 1.05,
            4: 1.1,
            5: 1.12,
            6: 1.14,
            7: 1.16,
            8: 1.18,
            9: 1.2,
            10: 1.5,
        }

        # Syndra: Gain 5 Ability Power every 3 seconds
        self.syndra_interval = 3
        self.next_syndra = 3
        self.syndra_ap = 6  

        # Xayah: Every 3rd attack deals 60 (+ 75) magic damage
        self.xayah_base = 60
        # 1: 0, 2: 0, 3: 75, 4: 150, 5: 225, 6: 300
        self.xayah_stage = 75

        # Ahri: After casting, gain 3 Mana over 2 seconds. Adjusting this to be instant only screws up syndra.
        self.ahri_mana = 3

        # Jinx: +8% Attack Speed. +25% AS after takedowns, decaying over 3s
        # Simplified to 8 + (20.5 x SG scaling)
        self.jinx_base = 8
        self.jinx_scaling = 20.5

        # Seraphine: Gain 5 ArmorMRHealth and 5% ADASCritCrit Damage
        self.seraphine_base = 5

        # Emblem 1
        self.emblem_scaling = .1
        # Emblem 2

    def performAbility(self, phase, time, champion, input_=0):
        emblem_scaling = 1
        # emblem_scaling += champion.star_guardians["Emblem"] * self.emblem_scaling
        level = sum(champion.star_guardians.values())
        scaling = self.scaling[level] * emblem_scaling
        if phase == "preCombat":
            if champion.star_guardians["Jinx"]:
                champion.aspd.addStat(self.jinx_base + self.jinx_scaling * scaling)
            if champion.star_guardians["Seraphine"]:
                champion.bonus_ad.addStat(self.seraphine_base * scaling)
                champion.aspd.addStat(self.seraphine_base * scaling)
                champion.crit.addStat(self.seraphine_base * scaling / 100)
                champion.critDmg.addStat(self.seraphine_base * scaling / 100)
        if phase == "postAbility":
            if champion.star_guardians["Ahri"]:
                champion.addMana(self.ahri_mana * scaling)
        if phase == "onUpdate":
            if champion.star_guardians["Syndra"]:
                if time > self.next_syndra:
                    self.next_syndra += self.syndra_interval
                    champion.ap.addStat(self.syndra_ap * scaling)
        if phase == "preAttack":
            if champion.star_guardians["Xayah"]:
                if champion.numAttacks % 3 == 0:
                    dmg = self.xayah_base + max(champion.stage - 2, 0) * self.xayah_stage
                    dmg *= scaling
                    champion.doDamage(champion.opponents[0], [], 0, dmg, dmg, "magical", time)

        return 0
    

class Mentor(Buff):
    levels = [1, 4]

    def __init__(self, level, params):
        super().__init__("Mentor " + str(level), level, params, phases=["prePreCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        if self.level == 1 and champion.name in champion.mentors:
            champion.mentors[champion.name] = True
            # if you want to set the other ones be my guest
        elif self.level == 4:
            champion.upgraded = True
            champion.mentors["Udyr"] = True
            champion.mentors["Yasuo"] = True
            champion.mentors["Ryze"] = True
        return 0


class MentorBuff(Buff):
    levels = [1]

    def __init__(self, level, params):
        super().__init__("MentorBuff", level, params, phases=["preCombat"])

        # divincorp base
        self.adBase = 8
        self.asBase = 10
        self.manaPerAttackBase = 2

    def performAbility(self, phase, time, champion, input_=0):

        if champion.mentors["Udyr"]:
            champion.bonus_ad.addStat(self.adBase)
            champion.ap.addStat(self.adBase)
        if champion.mentors["Yasuo"]:
            champion.aspd.addStat(self.asBase)
        if champion.mentors["Ryze"]:
            champion.manaPerAttack.addStat(self.manaPerAttackBase)
        return 0


class Edgelord(Buff):
    levels = [0, 2, 4, 6]

    def __init__(self, level, params):
        super().__init__("Edgelord " + str(level), level, params, phases=["preCombat"])
        self.scaling = {2: 15, 4: 40, 6: 60}

    def performAbility(self, phase, time, champion, input=0):
        champion.bonus_ad.addStat(self.scaling[self.level])
        champion.aspd.addStat(20)
        return 0


class Executioner(Buff):
    levels = [0, 2, 3, 4, 5]

    def __init__(self, level, params):
        super().__init__(
            "Executioner " + str(level), level, params, phases=["preCombat"]
        )
        self.critChanceScaling = {2: 0.25, 3: 0.35, 4: 0.5, 5: 0.55}
        self.critDmgScaling = {2: 0.1, 3: 0.12, 4: 0.18, 5: 0.28}

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


class Bastion(Buff):
    levels = [0, 2, 4, 6]

    def __init__(self, level, params):
        super().__init__(
            "Bastion " + str(level), level, params, phases=["preCombat", "onUpdate"]
        )
        self.scaling = {2: 18, 4: 40, 6: 75}
        self.doubleTime = 10

    def performAbility(self, phase, time, champion, input=0):
        if phase == "preCombat":
            champion.armor.addStat(self.scaling[self.level] * 2)
            champion.mr.addStat(self.scaling[self.level] * 2)
        elif phase == "onUpdate" and time > self.doubleTime:
            champion.mr.addStat(-1 * self.scaling[self.level])
            self.doubleTime = 999
        return 0


class Luchador(Buff):
    levels = [0, 2, 4]

    def __init__(self, level, params):
        super().__init__("Luchador " + str(level), level, params, phases=["preCombat"])
        self.scaling = {2: 15, 4: 40}

    def performAbility(self, phase, time, champion, input=0):
        champion.bonus_ad.addStat(self.scaling[self.level])
        return 0


class Duelist(Buff):
    levels = [0, 2, 4, 6]

    def __init__(self, level=0, params=0):
        super().__init__("Duelist " + str(level), level, params, phases=["postAttack"])
        self.scaling = {2: 4, 4: 7, 6: 10}
        self.stacks = 0

    def performAbility(self, phase, time, champion, input_=0):
        if self.stacks < 12:
            champion.aspd.addStat(self.scaling[self.level])
            self.stacks += 1
        return 0


# Unit buffs


class KaisaUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Missile Massacre", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(champion.takedowns)
        return 0


class SmolderUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Burn Blast", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.armorPierce.addStat(0.3)
        return 0


class KennenUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Nine Thousand Volts", level, params, phases=["preAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.multiTargetSpell(
            champion.opponents,
            champion.items,
            time,
            1,
            champion.passiveAbilityScaling,
            "magical",
        )
        return 0


class TwistedFateUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("52 Card Calamity", level, params, phases=["preAttack"])
        # self.newAttack = Attack()

    def performAbility(self, phase, time, champion, input_=0):
        # attack 1: .7 power on enemy 1
        # attack 2: .4 (or .49?) power on enemy 2
        # spell 1: 1 power on enemy 1
        # spell 2: .7 power on enemy 2
        # spell 3: .4 (or .49?) power on enemy 3
        for index in range(1, 3):
            # 1: .7
            # 2: .49
            #
            newAttack = Attack()
            newAttack.opponents = champion.opponents
            newAttack.canCrit = champion.canCrit
            newAttack.canOnHit = True
            newAttack.numTargets = 1
            newAttack.scaling = lambda a, x, y, z: 0.7 ** (index) * input_.scaling(
                a, x, y, z
            )
            champion.doAttack(newAttack, champion.items, time)
        for index in range(3):
            # TF spell portion can't crit without spellcrit
            champion.multiTargetSpell(
                champion.opponents,
                champion.items,
                time,
                1,
                lambda x, y, z: 0.7 ** (index) * champion.autoAbilityScaling(x, y, z),
                "magical",
            )
        champion.marks += 1

        return 0


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


class AsheUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Gates of Avarosa", level, params, phases=["preAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        if champion.ultAutos > 0:
            champion.multiTargetSpell(
                champion.opponents,
                champion.items,
                time,
                1,
                champion.abilityScaling,
                "physical",
            )
            champion.ultAutos -= 1
            if champion.ultAutos == 0:
                champion.manalockTime = time + 0.01
        return 0


class KayleUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Unleash the Demon", level, params, phases=["preAttack"])
        self.buff_duration = 3
        self.finalAscentAP = 6
        self.finalAscent10Scaling = 0.6

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
                input_.canCrit = True
                input_.attackType = "physical"
                input_.scaling = lambda level, baseAD, AD, AP: champion.abilityScaling(
                    level, AD, AP
                )
        return 0


class ViegoUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__(
            "Combo of the Ruined King",
            level,
            params,
            phases=["preAttack"],
        )

    def performAbility(self, phase, time, champion, input_=0):
        if champion.ult_phase == 0:
            input_.canOnHit = True
            input_.canCrit = True
            input_.attackType = "magical"
            input_.scaling = (
                lambda level, baseAD, AD, AP: champion.autoAbilityScaling(level, AD, AP)
                + baseAD * AD
            )
        elif champion.ult_phase > 0:
            input_.canOnHit = True
            input_.canCrit = champion.canSpellCrit
            input_.attackType = "magical"
            input_.scaling = lambda level, baseAD, AD, AP: champion.abilityScaling(
                level, AD, AP
            )
            champion.ult_phase = (champion.ult_phase + 1) % 4
            if champion.ult_phase == 0:
                champion.manalockTime = time + 0.01
        return input_


class ZiggsUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__(
            "Orbital Ordinance",
            level,
            params,
            phases=["preAttack"],
        )

    def performAbility(self, phase, time, champion, input_=0):
        input_.canOnHit = True
        input_.canCrit = True
        input_.attackType = "magical"
        input_.scaling = (
            lambda level, baseAD, AD, AP: champion.autoAbilityScaling(level, AD, AP)
            + baseAD * AD
        )
        return input_


class JinxUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__(
            "Star Rocket Blast Off!",
            level,
            params,
            phases=["postAttack", "onCrit"],
        )
        self.max_AS = [60, 60, 300]
        self.attack_critted = False
        self.current_bonus = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onCrit" and not self.attack_critted and not input_:
            self.attack_critted = True
        if phase == "postAttack":
            max_amt = self.max_AS[champion.level - 1] * champion.ap.stat
            amt = 6 if not self.attack_critted else 9
            amt *= champion.ap.stat
            # print("Jinx current AP: ", champion.ap.stat)
            if max_amt > self.current_bonus:
                amt_to_add = min(max_amt - self.current_bonus, amt)
                # print("Amt to add: ", amt_to_add)
                self.current_bonus += amt_to_add
                champion.aspd.addStat(amt_to_add)
            self.attack_critted = False


class KogmawUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Static Surge", level, params, phases=["preAttack", "preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.aspd.as_cap = 6
        if phase == "preAttack":
            champion.multiTargetSpell(
                champion.opponents,
                champion.items,
                time,
                1,
                champion.passiveAbilityScaling,
                "magical",
            )
            if champion.nextAutoEnhanced:
                targets = 3
                champion.multiTargetSpell(
                    champion.opponents,
                    champion.items,
                    time,
                    targets,
                    champion.abilityScaling,
                    "magical",
                )
                for opponent in champion.opponents[0:targets]:
                    opponent.applyStatus(
                        status.MRReduction("MR 30"), champion, time, 4, 0.7
                    )
                champion.nextAutoEnhanced = False

        return 0


class MundoUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Give em the Chair!", level, params, phases=["preAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        input_.scaling = champion.passiveAbilityScaling
        return input_


class ShenUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("TwilightAssault", level, params, phases=["preAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        if champion.ultAutos > 0:
            champion.multiTargetSpell(
                champion.opponents,
                champion.items,
                time,
                1,
                champion.abilityScaling,
                "true",
            )
            champion.ultAutos -= 1
            if champion.ultAutos == 0:
                champion.manalockTime = time + 0.01
        return 0


# AUGMENTS


class LearnFromTheBest(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Learn From The Best", level, params, phases=["preCombat"])
        self.udyr_scaling = 4
        self.yas_scaling = 5
        self.ryze_scaling = 1

    def performAbility(self, phase, time, champion, input_=0):
        boost = {1: 0, 2: 1, 3: 2}.get(champion.level, 0)
        champion.bonus_ad.addStat(boost * self.udyr_scaling)
        champion.ap.addStat(boost * self.udyr_scaling)

        champion.aspd.addStat(boost * self.yas_scaling)
        champion.manaPerAttack.addStat(boost * self.ryze_scaling)

        return 0


class WaterLotusI(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__(
            "Water Lotus I",
            level,
            params,
            phases=["preCombat", "onCrit", "postAbility"],
        )
        self.crit_scaling = 0.05
        self.scaling = 0.09
        self.duration = 3
        self.restoreMana = False

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.crit.addStat(self.crit_scaling)
            champion.canSpellCrit = True
        elif phase == "onCrit" and input_:
            # input is is_spell
            self.restoreMana = True
        elif phase == "postAbility" and self.restoreMana:
            self.restoreMana = False
            champion.applyStatus(
                status.ManaRegenModifier("Water Lotus I"),
                champion,
                time,
                self.duration,
                params=self.scaling * champion.fullMana.stat / self.duration,
            )
        return 0


class WaterLotusII(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__(
            "Water Lotus II (instant mana restore)",
            level,
            params,
            phases=["preCombat", "onCrit", "postAbility"],
        )
        self.crit_scaling = 0.2
        self.scaling = 0.15
        self.duration = 3
        self.restoreMana = False

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.crit.addStat(self.crit_scaling)
            champion.canSpellCrit = True
        elif phase == "onCrit" and input_:
            # input is is_spell
            self.restoreMana = True
        elif phase == "postAbility" and self.restoreMana:
            self.restoreMana = False
            champion.applyStatus(
                status.ManaRegenModifier("Water Lotus II"),
                champion,
                time,
                self.duration,
                params=self.scaling * champion.fullMana.stat / self.duration,
            )
        return 0


class LitFuseSolo(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Lit Fuse (Solo)", level, params, phases=["onUpdate"])
        self.activation_time = 6
        self.manaBonus = 60

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.activation_time:
            self.activation_time = 999
            champion.addMana(self.manaBonus)
        return 0


class LitFuseDuo(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Lit Fuse (Duo)", level, params, phases=["onUpdate"])
        self.activation_time = 6
        self.manaBonus = 30

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.activation_time:
            self.activation_time = 999
            champion.addMana(self.manaBonus)
        return 0


class LitFuseTrio(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Lit Fuse (Trio)", level, params, phases=["onUpdate"])
        self.activation_time = 6
        self.manaBonus = 20

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.activation_time:
            self.activation_time = 999
            champion.addMana(self.manaBonus)
        return 0


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


class KnowYourEnemy(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        # vayne bolts inflicts status "Silver Bolts"
        super().__init__("Know Your Enemy", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(0.15)
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


class Hero101(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Hero101", level, params, phases=["preCombat"])
        self.scaling = 0.15

    def performAbility(self, phase, time, champion, input_=0):
        # may not interact well with other forms of scaling, watch out
        for item in champion.items:
            if "Academia" in item.name:
                champion.fullMana.mult -= self.scaling
                break
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


class BestFriendsI(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Best Friends I", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(12)
        champion.armor.addStat(12)
        return 0


class BestFriendsII(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Best Friends II", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(15)
        champion.armor.addStat(20)
        return 0
    

class TinyButDeadly(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Tiny But Deadly", level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(30)
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


class MessHall(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__("Mess Hall", level, params, phases=["onUpdate", "preAttack"])
        self.activation_time = 10
        self.activated = False
        self.aspd_scaling = 20
        self.dmg_scaling = 1.4

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            if time > self.activation_time and not self.activated:
                self.activated = True
                champion.aspd.addStat(self.aspd_scaling)
        elif phase == "preAttack" and self.activated:
            dmg = champion.atk.stat * champion.bonus_ad.stat * self.dmg_scaling
            champion.doDamage(champion.opponents[0], [], 0, dmg, dmg, "magical", time)
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
        self.max_stacks = 15

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
        self.asBonus = 9
        self.nextBonus = 0

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

# ...existing code...
import ast
from collections import deque

from bilgewater_utils import optimize_bilgewater_stats
from item import Item
from role import Role
from stats import Attack, JhinBonusAD

import status


def get_classes_from_file(file_path):
    with open(file_path, "r") as file:
        file_content = file.read()

    # Parse the file content into an AST
    tree = ast.parse(file_content)

    # Extract all class definitions
    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    return classes


class_buffs = [
    "Freljord",
    "Arcanist",
    "Longshot",
    "Invoker",
    "Quickstriker",
    "Yordle",
    "Caretaker",
    "Gunslinger",
    "Void",
    "Vanquisher",
    "Zaun",
    "ShadowIsles",
    "HexMech",
    "Disruptor",
    "Slayer",
    "Shurima",
    "StarForger",
    "Bilgewater",
    "IoniaEnlightened",
    "IoniaProsperous",
    # "IoniaBlades",
]

augments = [
    "Shred30",
    "Shred20",
    "MacesWill",
    "BestFriendsI",
    "BestFriendsII",
    "TrifectaI",
    "TrifectaII",
    "TinyButDeadly",
    "StandUnitedI",
    "Ascension",
    "AscensionOld",
    "KnowYourEnemy",
    "HoldTheLine5",
    "HoldTheLine7",
    "TonsOfStats",
    "JeweledLotusI",
    "JeweledLotusII",
    "FireAxiom",
    "AirAxiom",
    "WaterAxiom",
    "ContinuumCogs",
    "OverclockedCapacitors",
    "SeraphimsStaff",
    "Retribution",
    "GlassCannonI",
    "GlassCannonII",
    "NoScoutNoPivot",
    "MessHall",
    "SoulAwakening",
    "FocusedFire",
    "Corrosion",
    "CryMeARiver",
    "AccelerationGate",
    "MagnetronCoil",
    "WarlordsHonor"
]

void_buffs = ["SpitterSpines", "LeechingNucleus", "AdrenalineModules"]

stat_buffs = ["ASBuff"]

no_buff = ["NoBuff"]


class ChampionAbilityScaling:
    """Picklable wrapper for champion ability scaling."""

    def __init__(self, champion):
        self.champion = champion

    def __call__(self, level, AD, bonusAD, AP):
        return self.champion.abilityScaling(level, bonusAD, AP)


class ScaledChampionAbilityScaling:
    """Picklable wrapper for scaled champion ability scaling."""

    def __init__(self, champion, scale_factor):
        self.champion = champion
        self.scale_factor = scale_factor

    def __call__(self, level, AD, bonusAD, AP):
        return self.scale_factor * self.champion.abilityScaling(level, bonusAD, AP)


class ScaledChampionAbilityScaling2:
    """Picklable wrapper for scaled champion ability scaling.
    we'll fix this lmao"""

    def __init__(self, champion, scale_factor):
        self.champion = champion
        self.scale_factor = scale_factor

    def __call__(self, level, bonusAD, AP):
        return self.scale_factor * self.champion.abilityScaling(level, bonusAD, AP)


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
    display_name = "NoItem"

    def __init__(self, level, params):
        # params is number of stacks
        super().__init__(self.display_name, level, params, phases=None)

    def performAbility(self, phase, time, champion, input_=0):
        return 0


class ASBuff(Buff):
    levels = [1]
    display_name = "Attack Speed Buff"

    def __init__(self, level, params):
        # params is number of stacks
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
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


class ShadowIsles(Buff):
    levels = [0, 2, 3, 4, 5]
    display_name = "Shadow Isles"

    def __init__(self, level, params):
        # params is number of hexes
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["prePreCombat"]
        )
        self.scaling = {0: 0, 2: 18, 3: 20, 4: 25, 5: 33}
        self.souls = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        champion.souls = self.souls
        champion.bonus_ad.addStat(self.scaling[self.level])
        champion.ap.addStat(self.scaling[self.level])
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Souls", "Min": 0, "Max": 999, "Default": 20}

    def extraBuff(self, souls):
        self.souls = souls


class Longshot(Buff):
    levels = [0, 2, 3, 4, 5]
    display_name = "Longshot"

    def __init__(self, level, params):
        # params is number of hexes
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.base_scaling = {0: 0, 2: 0.18, 3: 0.2, 4: 0.24, 5: 0.3}
        self.scaling = {0: 0, 2: 0.02, 3: 0.03, 4: 0.04, 5: 0.05}
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


class Yordle(Buff):
    levels = [0, 2, 3, 4, 5, 6, 7, 8]
    display_name = "Yordle"

    def __init__(self, level, params):
        # params is number of hexes
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.aspd_per_yordle = 5
        self.num_three_stars = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        amt_to_add = self.aspd_per_yordle * self.level + self.num_three_stars * (
            self.aspd_per_yordle
        )
        champion.aspd.addStat(amt_to_add)
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "# 3* Yordles", "Min": 0, "Max": 8, "Default": 0}

    def extraBuff(self, num_three_stars):
        self.num_three_stars = num_three_stars


class Freljord(Buff):
    levels = [0, 3, 5, 7]
    display_name = "Freljord"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.dmgamp_scaling = {3: 0.1, 5: 0.16, 7: 0.22}
        self.is_freljord = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        multiplier = 2.5 if self.is_freljord else 1
        value_to_add = self.dmgamp_scaling[self.level] * multiplier
        champion.dmgMultiplier.addStat(value_to_add)
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Is Freljord", "Min": 0, "Max": 1, "Default": 1}

    def extraBuff(self, is_freljord):
        self.is_freljord = is_freljord


class Invoker(Buff):
    levels = [0, 2, 4]
    display_name = "Invoker"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.scaling = {2: 0.25, 4: 0.4}
        self.team_mana_regen = 1
        self.is_invoker = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        champion.manaRegen.addStat(self.team_mana_regen)
        if self.is_invoker:
            champion.manaGainMultiplier.addStat(self.scaling[self.level])
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Is Invoker", "Min": 0, "Max": 1, "Default": 1}

    def extraBuff(self, is_invoker):
        self.is_invoker = is_invoker


class Caretaker(Buff):
    levels = [1]
    display_name = "Caretaker"

    def __init__(self, level, params):
        super().__init__(f"{self.display_name}", level, params, phases=["preCombat"])
        self.num_three_stars = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        champion.num_three_stars = self.num_three_stars
        champion.castTime = 2 + 0.25 * self.num_three_stars
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "# 3 Stars", "Min": 0, "Max": 9, "Default": 0}

    def extraBuff(self, num_three_stars):
        self.num_three_stars = num_three_stars


class StarForger(Buff):
    levels = [0, 25, 60, 140, 300, 475, 750]
    display_name = "Star Forger"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.stardust = self.level

    def performAbility(self, phase, time, champion, input_=0):
        champion.stardust = self.stardust
        return 0


class HexMech(Buff):
    levels = [1]
    display_name = "HexMech"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name}", level, params, phases=["postPreCombat"]
        )
        self.pilot_star_level = 0
        self.adScaling = [20, 30, 40]
        self.dmgAmpScaling = [0.12, 0.2, 0.3]
        self.manaRegenScaling = [2, 4, 5]
        self.critScaling = [0.4, 0.7, 1]
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        if champion.pilot:
            if champion.pilot == Role.FIGHTER:
                champion.bonus_ad.addStat(self.adScaling[self.pilot_star_level - 1])
            elif champion.pilot == Role.MARKSMAN:
                champion.dmgMultiplier.addStat(
                    self.dmgAmpScaling[self.pilot_star_level - 1]
                )
            elif champion.pilot == Role.CASTER:
                champion.manaRegen.addStat(
                    self.manaRegenScaling[self.pilot_star_level - 1]
                )
            elif champion.pilot == Role.ASSASSIN:
                champion.crit.addStat(self.critScaling[self.pilot_star_level - 1])
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Pilot Level", "Min": 1, "Max": 3, "Default": 3}

    def extraBuff(self, pilot_star_level):
        self.pilot_star_level = pilot_star_level


class Quickstriker(Buff):
    levels = [0, 2, 3, 4, 5]
    display_name = "Quickstriker"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.scaling = {2: 20, 3: 32.5, 4: 45, 5: 60}
        self.team_as = 15
        self.is_quickstriker = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(self.team_as)
        if self.is_quickstriker:
            champion.aspd.addStat(self.scaling[self.level])
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Is Quick", "Min": 0, "Max": 1, "Default": 1}

    def extraBuff(self, is_quickstriker):
        self.is_quickstriker = is_quickstriker


class Shurima(Buff):
    levels = [0, 2]
    display_name = "Shurima"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["onUpdate"]
        )
        self.scaling = 2
        self.next_AS = 0

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.next_AS:
            champion.aspd.addStat(self.scaling)
            self.next_AS = time + 1
        return 0


class Bilgewater(Buff):
    levels = [0, 3, 5, 7, 10]
    display_name = "Bilgewater"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        # Calculate optimal stats based on current silver serpents
        stats = optimize_bilgewater_stats(self.silver_serpents)

        # Apply multiplier for level 10
        multiplier = 2 if self.level >= 10 else 1

        # Apply stats
        # HP is applied as a percentage multiplier (e.g., 4% -> 0.04)
        if stats["HP"] > 0:
            champion.hp.mult += (stats["HP"] / 100.0) * multiplier

        # AS is applied as a flat value (e.g., 4% -> 4)
        if stats["AS"] > 0:
            champion.aspd.addStat(stats["AS"] * multiplier)

        # AD is applied as bonus AD
        if stats["AD"] > 0:
            champion.bonus_ad.addStat(stats["AD"] * multiplier)

        # AP is applied directly
        if stats["AP"] > 0:
            champion.ap.addStat(stats["AP"] * multiplier)

        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Serpents", "Min": 0, "Max": 1000, "Default": 0}

    def extraBuff(self, silver_serpents):
        self.silver_serpents = silver_serpents


class Arcanist(Buff):
    levels = [0, 2, 4, 6]
    display_name = "Arcanist"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.scaling = {2: 15, 4: 20, 6: 35}
        self.arcanist_scaling = {2: 25, 4: 50, 6: 70}
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        amt_to_add = (
            self.scaling[self.level]
            if not self.is_arcanist
            else self.arcanist_scaling[self.level]
        )
        champion.ap.addStat(amt_to_add)
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Is Arcanist", "Min": 0, "Max": 1, "Default": 1}

    def extraBuff(self, is_arcanist):
        self.is_arcanist = is_arcanist


class IoniaEnlightened(Buff):
    levels = [0, 3, 5, 7]
    display_name = "Ionia (Enlightened)"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.scaling = {3: 10, 5: 15, 7: 20}
        self.lvl_scaling = {3: 2, 5: 3, 7: 4}
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        amt_to_add = self.scaling[self.level] + self.lvl_scaling[self.level] * champion.level
        champion.bonus_ad.addStat(amt_to_add)
        champion.ap.addStat(amt_to_add)
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Lvl Override", "Min": 0, "Max": 10, "Default": 0}

    def extraBuff(self, level):
        if level != 0:
            champion.level = level


class IoniaProsperous(Buff):
    levels = [0, 3, 5, 7]
    display_name = "Ionia (Prosperous)"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.scaling = {3: 10, 5: 25, 7: 40}
        self.gold_scaling = 2
        self.gold = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        amt_to_add = self.scaling[self.level] * (1 + self.gold *.02)
        champion.bonus_ad.addStat(amt_to_add)
        champion.ap.addStat(amt_to_add)
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Gold", "Min": 0, "Max": 200, "Default": 20}

    def extraBuff(self, gold):
        self.gold = gold
     

class IoniaBlades(Buff):
    levels = [0, 3, 5, 7]
    display_name = "Ionia (Blades)"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat", "postAttack"]
        )
        self.scaling = {3: 15, 5: 25, 7: 50}
        self.blade_scaling = {0: 0, 3: .3, 5: .38, 7: .45}
        self.bmActive = False
        self.bmAutoCount = 0


    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.bonus_ad.addStat(self.scaling[self.level])
            champion.ap.addStat(self.scaling[self.level])
        elif phase == "postAttack":
            # Implement doublestrike logic here
            if not self.bmActive:
                self.bmAutoCount += self.blade_scaling[self.level]
                if self.bmAutoCount >= 1:
                    champion.aspd.mult = 4
                    self.bmActive = True
                    self.bmAutoCount -= 1
            else:
                # should this increment it as well? probably not.
                champion.aspd.mult = 1
                self.bmActive = False
                self.bmAutoCount = 0
            return 0
        return 0


class Slayer(Buff):
    levels = [0, 2, 4, 6]
    display_name = "Slayer"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.scaling = {2: 20, 4: 30, 6: 40}
        self.bonus_amp = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        amt_to_add = self.scaling[self.level] * (1 + self.bonus_amp)
        champion.bonus_ad.addStat(amt_to_add)
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Amp (0-50%)", "Min": 0.0, "Max": 0.5, "Default": 0.25}

    def extraBuff(self, bonus_amp):
        self.bonus_amp = bonus_amp


class Gunslinger(Buff):
    levels = [0, 2, 4]
    display_name = "Gunslinger"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}",
            level,
            params,
            phases=["preCombat", "postAttack"],
        )
        self.adScaling = {2: 22, 4: 40}
        self.extraDamage = {2: 100, 4: 200}
        self.stacks = 0

    def performAbility(self, phase, time, champion, input=0):
        if phase == "preCombat":
            champion.bonus_ad.addStat(self.adScaling[self.level])
        if phase == "postAttack":
            self.stacks += 1
            if self.stacks % 4 == 0:
                champion.doDamage(
                    champion.opponents[0],
                    [],
                    0,
                    self.extraDamage[self.level],
                    self.extraDamage[self.level],
                    "physical",
                    time,
                )
        return 0


class Zaun(Buff):
    levels = [0, 3, 5, 7]
    display_name = "Zaun"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["onUpdate"]
        )
        self.shimmer_time = {0: 0, 3: 4, 5: 4, 7: 3}
        self.next_shimmer = self.shimmer_time[level]
        self.decaying_as = {3: 90, 5: 90, 7: 90 * 1.3}
        self.buff_duration = {3: 4, 5: 4, 7: 4}

    def performAbility(self, phase, time, champion, input=0):
        if phase == "onUpdate":
            if time >= self.next_shimmer:
                champion.applyStatus(
                    status.DecayingASModifier("Zaun"),
                    self,
                    time,
                    self.buff_duration[self.level],
                    self.decaying_as[self.level],
                )
                self.next_shimmer += self.shimmer_time[self.level] * 2
        return 0


class Void(Buff):
    levels = [0, 2, 4, 6]
    display_name = "Void"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.asScaling = {2: 8, 4: 18, 6: 33}

    def performAbility(self, phase, time, champion, input=0):
        if phase == "preCombat":
            champion.aspd.addStat(self.asScaling[self.level])
        return 0


class Disruptor(Buff):
    levels = [0, 2, 4]
    display_name = "Disruptor"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.scaling = {2: 0.25, 4: 0.45}

    def performAbility(self, phase, time, champion, input=0):
        if phase == "preCombat":
            champion.extraDmgMultiplier.addStat(self.scaling[self.level])
        return 0


class Vanquisher(Buff):
    levels = [0, 2, 3, 4, 5]
    display_name = "Vanquisher"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.critChanceScaling = {2: 0.15, 3: 0.2, 4: 0.25, 5: 0.3}
        self.critDmgScaling = {2: 0.15, 3: 0.2, 4: 0.25, 5: 0.3}

    def performAbility(self, phase, time, champion, input=0):
        champion.canSpellCrit = True
        champion.critDmg.addStat(self.critDmgScaling[self.level])
        champion.crit.addStat(self.critChanceScaling[self.level])
        return 0


# Unit buffs


class RumbleUlt(Buff):
    levels = [1]
    display_name = "Artillery Barrage"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["onUpdate"])
        self.next_missile = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            missiles = 3 + (champion.aspd.add // 33)
            if time >= self.next_missile:
                champion.multiTargetSpell(
                    champion.opponents,
                    champion.items,
                    time,
                    1,
                    champion.abilityScaling,
                    "magical",
                )
                self.next_missile = time + 1 / missiles
            


class ZoeUlt(Buff):
    levels = [1]
    display_name = "Double Trouble Bubble"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            # permashred everyone. Not exactly accurate but it'll do
            for opponent in champion.opponents:
                opponent.applyStatus(
                    status.MRReduction("Zoe MR 30"), champion, time, 30, 0.7
                )


class ApheliosUlt(Buff):
    levels = [1]
    display_name = "Incendiary Onslaught"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name,
            level,
            params,
            phases=["preCombat", "preAttack", "postAbility"],
        )

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            # permashred everyone
            for opponent in champion.opponents:
                opponent.applyStatus(
                    status.ArmorReduction("Aph Armor 30"), champion, time, 30, 0.7
                )
        elif phase == "postAbility" and champion.severumActivated:
            # severum was activated, apply buff
            champion.severumActivated = False
            champion.aspd.addStat(200)
        elif phase == "preAttack":
            if champion.severumAttacksLeft == 0:
                # Infernum
                input_.numTargets = 3
            else:
                input_.canCrit = champion.canSpellCrit
                input_.scaling = ChampionAbilityScaling(champion)
                champion.severumAttacksLeft -= 1
                if champion.severumAttacksLeft == 0:
                    # deactivate
                    champion.aspd.addStat(-200)
                    champion.manalockTime = time + 0.01
        return 0


class AzirUlt(Buff):
    levels = [1]
    display_name = "Arise!"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        for index, soldier_attack in enumerate(
            champion.soldier_intervals[0 : champion.soldiers]
        ):
            if champion.numAttacks > soldier_attack:
                champion.soldier_intervals[index] += 3
                champion.multiTargetSpell(
                    champion.opponents,
                    champion.items,
                    time,
                    1,
                    champion.abilityScaling,
                    "magical",
                )
        return 0


class JhinUlt(Buff):
    levels = [1]
    display_name = "Curtain Call"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        if champion.ultAutos > 0:
            input_.canOnHit = True
            input_.canCrit = champion.canSpellCrit
            input_.attackType = "physical"
            input_.scaling = (
                ChampionAbilityScaling(champion)
                if champion.ultAutos > 1
                else ScaledChampionAbilityScaling(champion, 2.44)
            )
            champion.ultAutos -= 1
            if champion.ultAutos == 0:
                champion.manalockTime = time + 0.01
                champion.aspd.base = 0.7
                champion.aspd.as_cap = 5
        return 0


class DravenUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__(
            "Spinning Axes", level, params, phases=["preAttack", "onUpdate"]
        )
        self.attack_queue = deque()
        self.axe_return_time = 1.3

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preAttack":
            if champion.axes > 0:
                input_.canOnHit = True
                input_.canCrit = champion.canCrit
                input_.attackType = "physical"
                input_.scaling = ChampionAbilityScaling(champion)
                champion.axes -= 1
                self.attack_queue.append(time + self.axe_return_time)
        if phase == "onUpdate":
            if self.attack_queue and self.attack_queue[0] < time:
                if champion.axes < 2:
                    champion.axes += 1
                self.attack_queue.popleft()
        return 0


class KaisaUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__(
            "Icathian Rain", level, params, phases=["postPreCombat", "preAttack"]
        )
        self.autoCount = 0  # separate counter for empowered autos
        # todo: fix so it resets on cast

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "postPreCombat":
            # check if champ's bonus AD or AP is higher
            if champion.bonus_ad.stat < champion.ap.stat:
                champion.ad_version = False
                # fix role stuff: hardcoded in, but caster is 7 mpA, 2 mana regen. Marksman is 10 mpA, 0 mana regen.
                champion.manaRegen.addStat(-2)
                champion.manaPerAttack.addStat(3)
                champion.manalockDuration = 5
                champion.role = Role.MARKSMAN
                champion.castTime = 0
                champion.curMana = 10  # need to change curmana to be a stat
                champion.fullMana.base = 30
                champion.atk.base = 25

        elif phase == "preAttack" and not champion.ad_version and champion.ultActive:
            if self.autoCount % 5 == 0:
                champion.multiTargetSpell(
                    champion.opponents,
                    champion.items,
                    time,
                    1,
                    champion.empoweredAbilityScaling2,
                    "magical",
                )
            else:
                champion.multiTargetSpell(
                    champion.opponents,
                    champion.items,
                    time,
                    1,
                    champion.empoweredAbilityScaling,
                    "magical",
                )
            self.autoCount += 1
        return 0


class TwistedFateUlt(Buff):
    levels = [1]
    display_name = "Stacked Deck"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        # input_.canOnHit = True
        # input_.canCrit = champion.canSpellCrit
        # input_.attackType = 'magical'
        # input_.scaling = ChampionAbilityScaling(champion)
        # if champion.numAttacks % 3 == 0:
        #     champion.multiTargetSpell(
        #         champion.opponents,
        #         champion.items,
        #         time,
        #         champion.num_targets - 2,
        #         champion.extraAbilityScaling,
        #     "magical",
        # )
        return 0


class JinxUlt(Buff):
    levels = [1]
    display_name = "Switcheroo"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        if champion.numAttacks >= champion.auto_threshold[champion.level - 1]:
            input_.canOnHit = True
            input_.canCrit = champion.canCrit
            input_.attackType = "physical"
            input_.scaling = ChampionAbilityScaling(champion)
            for i in range(2):
                champion.doAttack(input_, champion.items, time)
        return 0


class THexUlt(Buff):
    levels = [1]
    display_name = "Hextech Arsenal"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["onUpdate"])
        self.missiles_to_send = 0
        self.missile_count = 0
        self.mana_drain = 30

    def performAbility(self, phase, time, champion, input_=0):
        if champion.ultActive:
            if champion.firstMissile:
                champion.firstMissile = False
                champion.curMana = champion.fullMana.stat
            if champion.curMana > 0:
                if time > champion.nextDrain:
                    print("Draining THex ult: {} {}".format(time, champion.curMana))
                    champion.nextDrain += 0.25
                    champion.curMana -= self.mana_drain / 4
                    for i in range(champion.num_targets):
                        scale_factor = 1.0
                        if i == 1:
                            scale_factor = 0.3
                        elif i >= 2:
                            scale_factor = 0.1

                        scaling_func = (
                            champion.abilityScaling
                            if scale_factor == 1.0
                            else ScaledChampionAbilityScaling2(champion, scale_factor)
                        )

                        champion.multiTargetSpell(
                            champion.opponents,
                            champion.items,
                            time,
                            1,
                            scaling_func,
                            "physical",
                        )

                    self.missiles_to_send += champion.missilesPerTick
                    while self.missiles_to_send > 1:
                        self.missile_count += 1
                        print("Sending missile {}".format(self.missile_count))
                        self.missiles_to_send -= 1
                        champion.multiTargetSpell(
                            champion.opponents,
                            champion.items,
                            time,
                            1,
                            champion.extraAbilityScaling,
                            "physical",
                        )

            if champion.curMana <= 0:
                champion.ultActive = False
                champion.nextAttackTime = time + 0.01
                champion.curMana = 0
        return 0


class VeigarUlt(Buff):
    levels = [1]
    display_name = "Dark Storm"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])
        self.multScaling = 0.5

    def performAbility(self, phase, time, champion, input_=0):
        champion.canSpellCrit = True
        champion.ap.addMultiplier += self.multScaling
        return 0


class ViegoUlt(Buff):
    levels = [1]
    display_name = "Blade of the Ruined King"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name, level, params, phases=["preCombat", "preAttack"]
        )

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.aspd.addStat(10 + champion.souls // 6)
        elif phase == "preAttack":
            if champion.numCasts > 0:
                champion.multiTargetSpell(
                    champion.opponents,
                    champion.items,
                    time,
                    1,
                    champion.extraAbilityScaling,
                    "magical",
                )

        return 0


class YoneUlt(Buff):
    levels = [1]
    display_name = "Kin of the Stained Blade"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        if champion.numAttacks % 2 == 1:
            champion.multiTargetSpell(
                champion.opponents,
                champion.items,
                time,
                1,
                champion.adAutoAbilityScaling,
                "physical",
            )
        else:
            champion.multiTargetSpell(
                champion.opponents,
                champion.items,
                time,
                1,
                champion.apAutoAbilityScaling,
                "magical",
            )
        return 0


class MissFortuneUlt(Buff):
    levels = [1]
    display_name = "Heartbreaker"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name, level, params, phases=["preCombat", "preAttack"]
        )
        self.newAttack = Attack()

    def MFScaling(level, baseAD, AD, AP=0):
        return baseAD * AD * 0.5

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            self.newAttack.opponents = champion.opponents
            self.newAttack.canCrit = champion.canCrit
            self.newAttack.canOnHit = True
            self.newAttack.numTargets = 1
            self.newAttack.attackType = "physical"
            self.newAttack.scaling = MissFortuneUlt.MFScaling
        elif phase == "preAttack":
            champion.doAttack(self.newAttack, champion.items, time)


class YunaraUlt(Buff):
    levels = [1]

    def __init__(self, level=1, params=0):
        super().__init__(
            "Transcendent State",
            level,
            params,
            phases=["preCombat", "preAttack", "onCrit", "PostOnDealDamage"],
        )
        self.newAttack = Attack()
        self.critBonus = False
        self.true_dmg_scaling = 0.33

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            self.newAttack.opponents = champion.opponents
            self.newAttack.canCrit = champion.canSpellCrit
            self.newAttack.canOnHit = True
            self.newAttack.numTargets = 1
        if champion.ultActive:
            if phase == "preAttack":
                input_.canOnHit = True
                input_.canCrit = champion.canSpellCrit
                input_.attackType = "physical"
                input_.scaling = ChampionAbilityScaling(champion)
                for index in range(1, champion.num_targets):
                    # 1: .6
                    # 2: .36
                    self.newAttack.scaling = ScaledChampionAbilityScaling(
                        champion, 0.25**index
                    )
                    champion.doAttack(self.newAttack, champion.items, time)
            elif phase == "onCrit":
                self.critBonus = True
            elif phase == "PostOnDealDamage":
                if self.critBonus:
                    true_dmg = self.true_dmg_scaling * input_[0]
                    champion.doDamage(
                        champion.opponents[0],
                        [],
                        0,
                        true_dmg,
                        true_dmg,
                        "true",
                        time,
                    )
                self.critBonus = False
                # return input_
        return input_


# VOID BUFFS


class LeechingNucleus(Buff):
    levels = [1]
    display_name = "Leeching Nucleus"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["onDealDamage"])
        self.stacks = 0
        self.max_stacks = 10
        self.scaling = 2

    def performAbility(self, phase, time, champion, input_=0):
        if self.stacks < self.max_stacks:
            self.stacks += 1
            champion.bonus_ad.addStat(self.scaling)
            champion.ap.addStat(self.scaling)
        return input_


class AdrenalineModules(Buff):
    levels = [1]
    display_name = "Adrenaline Modules"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name, level, params, phases=["preCombat", "preAttack"]
        )
        self.initial_scaling = 0.18
        self.bonus_threshold = 3
        self.bonus_scaling = 0.01

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.dmgMultiplier.addStat(self.initial_scaling)
        elif phase == "preAttack":
            if champion.numAttacks % self.bonus_threshold == 0:
                champion.dmgMultiplier.addStat(self.bonus_scaling)
        return 0


class SpitterSpines(Buff):
    levels = [1]
    display_name = "Spitter Spines (unfinished)"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["PostOnDealDamage"])
        self.threshold = 1000
        self.next_dmg = self.threshold
        self.dmg = 111

    def performAbility(self, phase, time, champion, input_=0):
        if champion.dmgDealt > self.next_dmg:
            for i in range(2):
                champion.doDamage(
                    champion.opponents[0], [], 0, self.dmg, self.dmg, "physical", time
                )
            self.next_dmg += champion.dmgDealt + self.threshold
        return 0


# AUGMENTS


class Kahunahuna(Buff):
    levels = [1]
    display_name = "Kahunahuna"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["postAttack"])
        self.stacks = 0
        self.scaling = 2

    def performAbility(self, phase, time, champion, input_=0):
        self.stacks += 1
        if self.stacks % 5 == 0:
            baseDmg = self.scaling * champion.atk.stat * champion.bonus_ad.stat
            champion.doDamage(
                champion.opponents[0], [], 0, baseDmg, baseDmg, "true", time
            )
        return 0


class SeraphimsStaff(Buff):
    levels = [1]
    display_name = "Seraphim's Staff"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name,
            level,
            params,
            phases=["preCombat"],
        )

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.seraphim = True
        return 0


class Retribution(Buff):
    levels = [1]
    display_name = "Retribution"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name,
            level,
            params,
            phases=["preCombat"],
        )

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.retribution = True
        return 0


class JeweledLotusI(Buff):
    levels = [1]
    display_name = "Jeweled Lotus I"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name,
            level,
            params,
            phases=["preCombat"],
        )
        self.crit_scaling = 0.2

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.crit.addStat(self.crit_scaling)
            champion.canSpellCrit = True
        return 0


class JeweledLotusII(Buff):
    levels = [1]
    display_name = "Jeweled Lotus II"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name,
            level,
            params,
            phases=["preCombat"],
        )
        self.crit_scaling = 0.25
        self.crit_dmg_scaling = 0.1

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.crit.addStat(self.crit_scaling)
            champion.critDmg.addStat(self.crit_dmg_scaling)
            champion.canSpellCrit = True
        return 0


class HoldTheLine5(Buff):
    levels = [1]
    display_name = "Hold The Line (5 units)"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])
        self.ad_scaling = 9
        self.ap_scaling = 10
        self.frontliners = 5

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(self.ad_scaling * self.frontliners)
        champion.ap.addStat(self.ap_scaling * self.frontliners)
        return 0


class HoldTheLine7(Buff):
    levels = [1]
    display_name = "Hold The Line (7 units)"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])
        self.ad_scaling = 9
        self.ap_scaling = 10
        self.frontliners = 7

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(self.ad_scaling * self.frontliners)
        champion.ap.addStat(self.ap_scaling * self.frontliners)
        return 0


class GlassCannonI(Buff):
    levels = [1]
    display_name = "Glass Cannon I"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(0.17)
        return 0


class KnowYourEnemy(Buff):
    levels = [1]
    display_name = "Know Your Enemy"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(0.15)
        return 0


class GlassCannonII(Buff):
    levels = [1]
    display_name = "Glass Cannon II"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(0.3)
        return 0


class SoulAwakening(Buff):
    levels = [1]
    display_name = "Soul Awakening"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name, level, params, phases=["onUpdate", "onDealDamage"]
        )
        self.ad_ap_boost = 2
        self.next_boost = 1
        self.deal_true_damage = False
        self.true_dmg_boost = 0.12

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            if time > self.next_boost:
                self.next_boost += 1
                champion.bonus_ad.addStat(self.ad_ap_boost)
                champion.ap.addStat(self.ad_ap_boost)
            if self.next_boost == 10:
                self.next_boost = 999
                self.deal_true_damage = True
        elif phase == "onDealDamage":
            if self.deal_true_damage:
                dmg = (
                    input_ * self.true_dmg_boost
                )  # note: this may interact badly with other things
                champion.doDamage(champion.opponents[0], [], 0, dmg, dmg, "true", time)
            return input_
        return 0


class MacesWill(Buff):
    levels = [1]
    display_name = "Maces Will"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(6)
        champion.crit.addStat(0.2)
        return 0


class TonsOfStats(Buff):
    levels = [1]
    display_name = "Tons of Stats"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])
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
    display_name = "Best Friends I"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(10)
        champion.armor.addStat(10)
        return 0


class BestFriendsII(Buff):
    levels = [1]
    display_name = "Best Friends II"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(15)
        champion.armor.addStat(18)
        return 0


class TrifectaI(Buff):
    levels = [1]
    display_name = "Trifecta I"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(20)
        return 0


class TrifectaII(Buff):
    levels = [1]
    display_name = "Trifecta II"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(30)
        return 0


class TinyButDeadly(Buff):
    levels = [1]
    display_name = "Tiny But Deadly"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(30)
        return 0


class FireAxiom(Buff):
    levels = [1]
    display_name = "Fire Axiom (no burn)"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(15)
        champion.ap.addStat(15)
        return 0


class PreparationI(Buff):
    levels = [1]
    display_name = "Preparation I"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(12)
        champion.ap.addStat(12)
        return 0


class PreparationII(Buff):
    levels = [1]
    display_name = "Preparation II"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(16)
        champion.ap.addStat(16)
        return 0


class WarlordsHonor(Buff):
    levels = [1]
    display_name = "Warlord's Honor"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(24)
        champion.ap.addStat(24)
        return 0


class StandUnitedI(Buff):
    levels = [1]
    display_name = "Stand United"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])
        self.scaling = 1.5

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(champion.num_traits * self.scaling)
        champion.ap.addStat(champion.num_traits * self.scaling)
        return 0


class PumpingUpI(Buff):
    levels = [1]
    display_name = "Pumping Up I"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])
        self.base_scaling = 6
        self.bonus_scaling = 0.5

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(
            self.base_scaling + self.bonus_scaling * 6 * (champion.stage - 2)
        )
        return 0


class PumpingUpII(Buff):
    levels = [1]
    display_name = "Pumping Up II"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])
        self.base_scaling = 10
        self.bonus_scaling = 1

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(
            self.base_scaling + self.bonus_scaling * 6 * (champion.stage - 2)
        )
        return 0


class PumpingUpIII(Buff):
    levels = [1]
    display_name = "Pumping Up III"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])
        self.base_scaling = 16
        self.bonus_scaling = 2

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(
            self.base_scaling + self.bonus_scaling * 6 * (champion.stage - 2)
        )
        return 0


class MessHall(Buff):
    levels = [1]
    display_name = "Mess Hall"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name, level, params, phases=["onUpdate", "preAttack"]
        )
        self.activation_time = 10
        self.activated = False
        self.aspd_scaling = 8
        self.base_dmg = 25
        self.dmg_scaling = 1.4

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            if time > self.activation_time and not self.activated:
                self.activated = True
                champion.aspd.addStat(self.aspd_scaling)
        elif phase == "preAttack" and self.activated:
            # 50 AD, 30 AP: 1.5 + 1.3 - 1 = 1.8
            scaling = champion.bonus_ad.stat + champion.ap.stat - 1
            dmg = self.base_dmg * scaling
            champion.doDamage(champion.opponents[0], [], 0, dmg, dmg, "magical", time)
            champion.doDamage(champion.opponents[0], [], 0, dmg, dmg, "magical", time)
        return 0


class NoScoutNoPivot(Buff):
    levels = [1]
    display_name = "No Scout no Pivot"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])
        self.ad_scaling = 1
        self.ap_scaling = 1.5

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(self.ad_scaling * 5 * (champion.stage - 2))
        champion.ap.addStat(self.ap_scaling * 5 * (champion.stage - 2))
        return 0


class AdaptiveStyle(Buff):
    levels = [1]
    display_name = "AdaptiveStyle"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preAttack"])
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
    display_name = "Ascension"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["onUpdate"])
        self.dmgBonus = 0.4
        self.nextBonus = 12

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            if time >= self.nextBonus:
                self.nextBonus += 99999
                champion.dmgMultiplier.addStat(self.dmgBonus)
        return 0


class AscensionOld(Buff):
    levels = [1]
    display_name = "Ascension (Old)"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["onUpdate"])
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
    display_name = "ScopedWeaponsII"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])
        self.scaling = 25

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(self.scaling)
        return 0


class BackupDancers(Buff):
    levels = [1]
    display_name = "Backup Dancers"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["onUpdate"])
        self.asBonus = 9
        self.nextBonus = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            if time >= self.nextBonus:
                self.nextBonus += 3
                champion.aspd.addStat(self.asBonus)
        return 0


class FocusedFire(Buff):
    levels = [1]
    display_name = "Focused Fire"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["onUpdate"])
        self.adBonus = 10
        self.nextBonus = 0
        self.bonusInterval = 5

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            if time >= self.nextBonus:
                self.nextBonus += self.bonusInterval
                champion.bonus_ad.addStat(self.adBonus)
        return 0


class KeepAway(Buff):
    levels = [1]
    display_name = "Keep Away"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])
        self.scaling = 20

    def performAbility(self, phase, time, champion, input_=0):
        for item in champion.items:
            if "Longshot" in item.name:
                champion.aspd.addStat(self.scaling)
                break
        return 0


class AirAxiom(Buff):
    levels = [1]
    display_name = "Air Axiom"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(20)
        for opponent in champion.opponents:
            opponent.applyStatus(
                status.ArmorReduction("Air Hex"), champion, time, 30, 0.7
            )
        return 0


class WaterAxiom(Buff):
    levels = [1]
    display_name = "Water Axiom"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.manaRegen.addStat(3)
        for opponent in champion.opponents:
            opponent.applyStatus(
                status.MRReduction("Water Hex"), champion, time, 30, 0.7
            )
        return 0


class ContinuumCogs(Buff):
    levels = [1]
    display_name = "Continuum Cogs"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["onUpdate"])
        self.manaRegenBonus = 2
        self.apBonus = 15
        self.interval = 8

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            if time >= self.interval:
                self.interval = 999
                champion.manaRegen.addStat(self.manaRegenBonus)
                champion.ap.addStat(self.apBonus)
        return 0


class OverclockedCapacitors(Buff):
    levels = [1]
    display_name = "Overclocked Capacitors"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["onUpdate"])
        self.asBonus = 25
        self.interval = 8

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            if time >= self.interval:
                self.interval = 999
                champion.aspd.addStat(self.asBonus)
        return 0


class Shred30(Buff):
    levels = [1]
    display_name = "30% Armor/MR Shred"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        for opponent in champion.opponents:
            opponent.applyStatus(
                status.ArmorReduction("Armor 30"), champion, time, 30, 0.7
            )
            opponent.applyStatus(status.MRReduction("MR 30"), champion, time, 30, 0.7)
        return 0


class Shred20(Buff):
    levels = [1]
    display_name = "20% Armor/MR Shred"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        for opponent in champion.opponents:
            opponent.applyStatus(
                status.ArmorReduction("Armor 20"), champion, time, 30, 0.8
            )
            opponent.applyStatus(status.MRReduction("MR 20"), champion, time, 30, 0.8)
        return 0


class Demacia(Buff):
    levels = [0, 3, 5, 7]
    display_name = "Demacia"

    def __init__(self, level, params):
        super().__init__(f"{self.display_name} {level}", level, params, phases=None)

    def performAbility(self, phase, time, champion, input_=0):
        return 0


class Ionia(Buff):
    levels = [0, 3, 5, 7]
    display_name = "Ionia"

    def __init__(self, level, params):
        super().__init__(f"{self.display_name} {level}", level, params, phases=None)

    def performAbility(self, phase, time, champion, input_=0):
        return 0


class Noxus(Buff):
    levels = [0, 3, 5, 7]
    display_name = "Noxus"

    def __init__(self, level, params):
        super().__init__(f"{self.display_name} {level}", level, params, phases=None)

    def performAbility(self, phase, time, champion, input_=0):
        return 0


class WarwickUlt(Buff):
    levels = [1]
    display_name = "Eternal Hunger"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["postAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "postAttack":
            if champion.opponents:
                champion.multiTargetSpell(
                    [champion.opponents[0]],
                    champion.items,
                    time,
                    1,
                    champion.bonusAbilityScaling,
                    "physical"
                )
        return 0


class Corrosion(Buff):
    levels = [1]
    display_name = "Corrosion"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name, level, params, phases=["preCombat"]
        )

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            for opponent in champion.opponents:
                opponent.applyStatus(status.CorrosionStatus(), champion, time, 30, 0)
        return 0


class CryMeARiver(Buff):
    levels = [1]
    display_name = "Cry Me A River"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name, level, params, phases=["preCombat", "onUpdate"]
        )
        self.stage_2_active = False

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.manaRegen.addStat(1)
        elif phase == "onUpdate":
            if not self.stage_2_active and time >= 12:
                # After 12 seconds, increase to 3 (so add 2 more)
                champion.manaRegen.addStat(2)
                self.stage_2_active = True
        return 0


class AccelerationGate(Buff):
    levels = [1]
    display_name = "Acceleration Gate"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name, level, params, phases=["postAbility"]
        )

    def performAbility(self, phase, time, champion, input_=0):
        if time < 8:
            return 0
            
        # "After casting... restore 35% max mana over 2 seconds"
        # We use a status effect for the mana over time
        champion.applyStatus(status.AccelerationGateStatus(), champion, time, 2, 0)
        return 0


class MagnetronCoil(Buff):
    levels = [1]
    display_name = "Magnetron Coil (8 casts)"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name, level, params, phases=["onUpdate"]
        )
        self.active = False
        self.casts = 8

    def performAbility(self, phase, time, champion, input_=0):
        if time >= 8 and not self.active:
            self.active = True
            champion.dmgMultiplier.addStat(0.16 + self.casts * .01)
        return 0

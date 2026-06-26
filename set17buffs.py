# ...existing code...
import ast
from collections import deque

from item import Item
from role import Role
from stats import Attack, JhinBonusAD
from utils import lucky_chance

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
    "Fateweaver",
    "NOVA",
    "Timebreaker",
    "Sniper",
    "Anima",
    "Challenger",
    "Voyager",
    "Marauder",
    "DarkStar",
    "Rogue",
    "Conduit",
    "Meeple",
    "Bastion",
    "Arbiter",
    "Shepherd",
    "Replicator",
    "SpaceGroove",
    "FactoryNew",
    "StargazerHuntress",
    "StargazerMedallion",
    "StargazerFountain",
    "Mecha",
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
    "KnowYourEnemy",
    "HoldTheLine5",
    "HoldTheLine7",
    "TonsOfStats",
    "JeweledLotusI",
    "JeweledLotusII",
    "SeraphimsStaff",
    "Retribution",
    "GlassCannonI",
    "GlassCannonII",
    "NoScoutNoPivot",
    "SoulAwakening",
    "FocusedFire",
    "Corrosion",
    "CryMeARiver",
    "WarlordsHonor",
    "Kahunahuna",
    "ClockworkAccelerator",
    "BaronsLair",
    "PartialAscension",
    "EarlyLearnings",
    "AccelerationHex",
    "AccelerationHexEmpowered",
    "StarlightHex",
    "StarlightHexEmpowered",
    "Concentration",
]

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


class DarkStar(Buff):
    levels = [0, 2, 4, 6, 9]
    display_name = "Dark Star"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        # 2 and 9 do nothing
        self.scaling = {0: 0, 2: 0, 4: 45, 6: 45, 9: 0}
        self.is_strongest = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        multiplier = 1.7 if (self.level == 6 and self.is_strongest) else 1
        amt_to_add = self.scaling[self.level] * multiplier
        champion.bonus_ad.addStat(amt_to_add)
        champion.ap.addStat(amt_to_add)
        return 0

    def extraParameters():
        return {"Title": "Is Strongest", "Min": 0, "Max": 1, "Default": 0}

    def extraBuff(self, is_strongest):
        self.is_strongest = is_strongest


class Rogue(Buff):
    levels = [0, 2, 3, 4, 5]
    display_name = "Rogue"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.scaling = {0: 0, 2: 15, 3: 30, 4: 45, 5: 60}
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(self.scaling[self.level])
        champion.ap.addStat(self.scaling[self.level])
        return 0

    def extraParameters():
        return 0

    def extraBuff(self, params):
        pass


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


class Conduit(Buff):
    levels = [0, 2, 3, 4, 5]
    display_name = "Conduit"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        # (2) 1 | 3, (3) 1 | 5, (4) 2 | 7, (5) 3 | 9
        self.team_mana_regen = {0: 0, 2: 1, 3: 1, 4: 2, 5: 3}
        self.conduit_mana_regen = {0: 0, 2: 3, 3: 5, 4: 7, 5: 9}
        self.is_conduit = 0
        self.extraBuff(params)

    def ability(self, phase, time, champion, input_=0):
        # Override to ensure innate effect even at level 0
        if self.phases and phase in self.phases:
            return self.performAbility(phase, time, champion, input_)
        return input_

    def performAbility(self, phase, time, champion, input_=0):
        # Innate bonus
        if self.is_conduit:
            champion.manaGainMultiplier.addStat(0.20)

        # Team/Conduit regen
        if self.level >= 2:
            regen = (
                self.conduit_mana_regen[self.level]
                if self.is_conduit
                else self.team_mana_regen[self.level]
            )
            champion.manaRegen.addStat(regen)
        return 0

    def extraParameters():
        return {"Title": "Is Conduit", "Min": 0, "Max": 1, "Default": 1}

    def extraBuff(self, is_conduit):
        self.is_conduit = is_conduit


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
            archetype = champion.pilot.archetype
            if archetype == "Fighter":
                champion.bonus_ad.addStat(self.adScaling[self.pilot_star_level - 1])
            elif archetype == "Marksman":
                champion.dmgMultiplier.addStat(
                    self.dmgAmpScaling[self.pilot_star_level - 1]
                )
            elif archetype == "Caster":
                champion.manaRegen.addStat(
                    self.manaRegenScaling[self.pilot_star_level - 1]
                )
            elif archetype == "Assassin":
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
        amt_to_add = (
            self.scaling[self.level] + self.lvl_scaling[self.level] * champion.level
        )
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
        amt_to_add = self.scaling[self.level] * (1 + self.gold * 0.02)
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
            f"{self.display_name} {level}",
            level,
            params,
            phases=["preCombat", "postAttack"],
        )
        self.scaling = {3: 15, 5: 25, 7: 50}
        self.blade_scaling = {0: 0, 3: 0.3, 5: 0.38, 7: 0.45}
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
                champion.role = Role.ATTACK_MARKSMAN
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


# AUGMENTS


class Kahunahuna(Buff):
    levels = [1]
    display_name = "Kahunahuna"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["postAttack"])
        self.stacks = 0
        self.scaling = 1.25

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
        self.crit_scaling = 0.15

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.retribution = True
            champion.crit.addStat(self.crit_scaling)
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
        self.crit_scaling = 0.1

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.crit.addStat(self.crit_scaling)
            champion.addPrecision()
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
            champion.addPrecision()
        return 0


class HoldTheLine5(Buff):
    levels = [1]
    display_name = "Hold The Line (5 units)"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])
        self.ad_scaling = 8
        self.ap_scaling = 9
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
        self.ad_scaling = 8
        self.ap_scaling = 9
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
        champion.dmgMultiplier.addStat(0.16)
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
        champion.dmgMultiplier.addStat(0.25)
        return 0


class SoulAwakening(Buff):
    levels = [1]
    display_name = "Soul Awakening"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name, level, params, phases=["onUpdate", "onDealDamage"]
        )
        self.ad_ap_boost = 1.5
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
        champion.crit.addStat(0.25)
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
        champion.armor.addStat(9)
        champion.mr.addStat(9)
        return 0


class BestFriendsII(Buff):
    levels = [1]
    display_name = "Best Friends II"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(15)
        champion.armor.addStat(14)
        champion.armor.addStat(14)

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
        champion.aspd.addStat(33)
        return 0


class WarlordsHonor(Buff):
    levels = [1]
    display_name = "Warlord's Honor"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(20)
        champion.ap.addStat(20)
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


class NoScoutNoPivot(Buff):
    levels = [1]
    display_name = "No Scout no Pivot"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])
        self.ad_scaling = 1
        self.ap_scaling = 1

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(self.ad_scaling * 5 * (champion.stage - 2))
        champion.ap.addStat(self.ap_scaling * 5 * (champion.stage - 2))
        return 0


class EarlyLearnings(Buff):
    levels = [1]
    display_name = "Early Learnings (assume 1-cost)"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])
        self.base = 5
        self.ad_scaling = 2
        self.ap_scaling = 2

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(
            self.base + self.ad_scaling * 5 * (champion.stage - 2)
        )
        champion.ap.addStat(self.base + self.ap_scaling * 5 * (champion.stage - 2))
        return 0


class AccelerationHex(Buff):
    levels = [1]
    display_name = "Acceleration Hex"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(30)
        return 0


class AccelerationHexEmpowered(Buff):
    levels = [1]
    display_name = "Acceleration Hex (Empowered)"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(45)
        return 0


class StarlightHex(Buff):
    levels = [1]
    display_name = "Starlight Hex"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.manaRegen.addStat(3)
        return 0


class StarlightHexEmpowered(Buff):
    levels = [1]
    display_name = "Starlight Hex (Empowered)"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.manaRegen.addStat(4.5)
        return 0


class Concentration(Buff):
    levels = [1]
    display_name = "Concentration"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["postPreCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "postPreCombat":
            if "Conduit" in getattr(champion, "default_traits", []):
                champion.castTime += 1
                champion.manalockDuration += 1
                champion.concentration = True
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
        self.dmgBonus = 0.35
        self.nextBonus = 12

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            if time >= self.nextBonus:
                self.nextBonus += 99999
                champion.dmgMultiplier.addStat(self.dmgBonus)
        return 0


class PartialAscension(Buff):
    levels = [1]
    display_name = "Partial Ascension"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["onUpdate"])
        self.dmgBonus = 0.2
        self.nextBonus = 12

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
                    "physical",
                )
        return 0


class ClockworkAccelerator(Buff):
    levels = [1]
    display_name = "Clockwork Accelerator"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["onUpdate"])
        self.asBonus = 9
        self.nextBonus = 3

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            if time >= self.nextBonus:
                self.nextBonus += 3
                champion.aspd.addStat(self.asBonus)
        return 0


class BaronsLair(Buff):
    levels = [1]
    display_name = "Baron's Lair"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["onUpdate"])
        self.statBonus = 5
        self.nextBonus = 8

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            if time >= self.nextBonus:
                self.nextBonus += 1
                champion.bonus_ad.addStat(self.statBonus)
                champion.ap.addStat(self.statBonus)
        return 0


class Corrosion(Buff):
    levels = [1]
    display_name = "Corrosion"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

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
                # After 12 seconds, increase to 4 (so add 3 more)
                champion.manaRegen.addStat(3)
                self.stage_2_active = True
        return 0


class CaitlynUlt(Buff):
    levels = [1]
    display_name = "Aim for the Head"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preAttack"])
        self.counter = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preAttack" and input_.regularAuto:
            p = 0.15
            increment = (
                lucky_chance(p) if getattr(champion, "luckyAbility", False) else p
            )
            self.counter += increment
            if self.counter > 0.9999:
                input_.scaling = ChampionAbilityScaling(champion)
                self.counter -= 1
        return input_


class Fateweaver(Buff):
    levels = [0, 2, 4]
    display_name = "Fateweaver"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )

    def ability(self, phase, time, champion, input_=0):
        # Override Buff's level 0 check to allow Fateweaver's innate property
        if self.phases and phase in self.phases:
            return self.performAbility(phase, time, champion, input_)
        return input_

    def performAbility(self, phase, time, champion, input_=0):
        # Innate: Fateweavers have Precision.
        champion.addPrecision()

        # (2) Chance effects on abilities are Lucky.
        if self.level >= 2:
            champion.luckyAbility = True

        # (4) Gain 20% Crit Chance and 20% Crit Damage. Critical strikes are also Lucky.
        if self.level >= 4:
            champion.luckyCrit = True
            champion.crit.addStat(0.20)
            champion.critDmg.addStat(0.20)

        return 0


class NOVA(Buff):
    levels = [0, 2, 5]
    display_name = "N.O.V.A."

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}",
            level,
            params,
            phases=["preCombat", "onUpdate"],
        )

    def ability(self, phase, time, champion, input_=0):
        if self.phases and phase in self.phases:
            return self.performAbility(phase, time, champion, input_)
        return input_

    def trigger_nova(self, time, champion):
        if self.level >= 2:
            novas = getattr(champion, "novas", {})
            if novas.get("Aatrox"):
                for opp in champion.opponents:
                    opp.armor.mult = 0.7
                    opp.mr.mult = 0.7
            if novas.get("Caitlyn"):
                champion.aspd.addStat(20)
            if novas.get("Akali"):
                champion.addPrecision()

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            self.triggered = False
            if not hasattr(champion, "novas"):
                champion.novas = {}
        elif phase == "onUpdate":
            if time >= 6 and not getattr(self, "triggered", False):
                self.triggered = True
                self.trigger_nova(time, champion)
        return input_


class Sniper(Buff):
    levels = [0, 2, 3, 4]
    display_name = "Sniper"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.base_scaling = {0: 0, 2: 0.18, 3: 0.24, 4: 0.28}
        self.scaling = {0: 0, 2: 0.02, 3: 0.03, 4: 0.04}
        self.base_bonus = 0
        self.extraBuff(params)

    def extraParameters():
        return {"Title": "Hexes", "Min": 0, "Max": 8, "Default": 4}

    def extraBuff(self, hexes):
        self.base_bonus = hexes

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(
            self.base_scaling[self.level] + self.scaling[self.level] * self.base_bonus
        )
        return 0


class Timebreaker(Buff):
    levels = [0, 2, 4]
    display_name = "Timebreaker"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.is_timebreaker = 1
        self.extraBuff(params)

    def extraParameters():
        return {"Title": "Is TB", "Min": 0, "Max": 1, "Default": 1}

    def extraBuff(self, is_timebreaker):
        self.is_timebreaker = is_timebreaker

    def performAbility(self, phase, time, champion, input_=0):
        if self.level >= 2:
            champion.aspd.addStat(15)
            if self.level >= 4 and self.is_timebreaker:
                champion.aspd.addStat(40)
        return 0


class Anima(Buff):
    levels = [0, 3, 6]
    display_name = "Anima"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )

    def performAbility(self, phase, time, champion, input_=0):
        # Anima doesn't do anything for now
        return 0


class Challenger(Buff):
    levels = [0, 2, 3, 4, 5]
    display_name = "Challenger"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )

    def performAbility(self, phase, time, champion, input_=0):
        # Global 10% AS
        champion.aspd.addStat(10)

        # Challenger bonus for challengers
        if "Challenger" in getattr(champion, "default_traits", []):
            scaling = {0: 0, 2: 15, 3: 28, 4: 42, 5: 55}
            if self.level in scaling:
                bonus_as = scaling[self.level] * 1.25
                champion.aspd.addStat(bonus_as)
        return 0


class Voyager(Buff):
    levels = [0, 2, 3, 4, 5, 6]
    display_name = "Voyager"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.scaling = {0: 0, 2: 0.09, 3: 0.15, 4: 0.18, 5: 0.22, 6: 0.27}
        self.is_voyager = 1
        self.extraBuff(params)

    def extraParameters():
        return {"Title": "Is Voyager", "Min": 0, "Max": 1, "Default": 1}

    def extraBuff(self, is_voyager):
        self.is_voyager = is_voyager

    def performAbility(self, phase, time, champion, input_=0):
        if champion.role.archetype not in ["Tank", "Fighter"]:
            bonus = self.scaling.get(self.level, 0)
            if self.is_voyager:
                bonus *= 2
            champion.dmgMultiplier.addStat(bonus)
        return 0


class Marauder(Buff):
    levels = [0, 2, 4, 6]
    display_name = "Marauder"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )

    def performAbility(self, phase, time, champion, input_=0):
        # Global 5% AS
        champion.omnivamp.addStat(0.05)

        # Marauder bonus for marauders
        if "Marauder" in getattr(champion, "default_traits", []):
            ad_scaling = {0: 0, 2: 18, 4: 35, 6: 55}
            vamp_scaling = {0: 0, 2: 0.05, 4: 0.07, 6: 0.10}
            if self.level in ad_scaling:
                champion.bonus_ad.addStat(ad_scaling[self.level])
                champion.omnivamp.addStat(vamp_scaling[self.level])
        return 0


class Meeple(Buff):
    levels = [0, 3, 5, 7, 10]
    display_name = "Meeple"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        # (3) 2 meeps, 100 HP, (5) 3 meeps, 400 HP, (7) 4 meeps, 400 HP, (10) 6 meeps, 500 HP
        self.hp_scaling = {0: 0, 3: 100, 5: 400, 7: 400, 10: 500}
        self.meep_scaling = {0: 0, 3: 2, 5: 3, 7: 4, 10: 6}

    def performAbility(self, phase, time, champion, input_=0):
        if self.level >= 3:
            champion.hp.addStat(self.hp_scaling[self.level])
            champion.meep = self.meep_scaling[self.level]
        else:
            if not hasattr(champion, "meep"):
                champion.meep = 0
        return 0


class Arbiter(Buff):
    levels = [0, 2, 3]
    display_name = "Arbiter"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )

    def extraParameters():
        return {"Title": "Star Levels", "Min": 1, "Max": 30, "Default": 4}

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            if champion.cause == "When an Arbiter attacks 3 times":
                champion.items.append(ArbiterAttack(self.level, self.params))
            elif champion.cause == "Every 4 seconds":
                champion.items.append(ArbiterPeriodic(self.level, self.params))
            elif champion.cause == "Combat Start: For each interest you would gain":
                champion.items.append(ArbiterInterest(self.level, self.params))
            elif champion.cause == "Combat start: If you rerolled":
                champion.items.append(ArbiterReroll(self.level, self.params))
            elif champion.cause == "When an Arbiter spends 50 mana":
                champion.items.append(ArbiterManaSpent(self.level, self.params))
            elif champion.cause == "Combat Start: For each Arbiter star level":
                champion.items.append(ArbiterStarLevel(self.level, self.params))
        return 0


class ArbiterAttack(Buff):
    levels = [2, 3]
    display_name = "Arbiter (Attack)"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["postAttack"]
        )
        self.attack_counter = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "postAttack":
            self.attack_counter += 1
            if self.attack_counter % 3 == 0:
                effect = getattr(champion, "effect", "")
                if effect == "Gain AS":
                    amt = 4 if self.level == 2 else 6
                    champion.aspd.addStat(amt)
                elif effect == "Gain AP":
                    amt = 6 if self.level == 2 else 9
                    champion.ap.addStat(amt)
        return 0


class ArbiterPeriodic(Buff):
    levels = [2, 3]
    display_name = "Arbiter (Periodic)"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["onUpdate"]
        )
        self.interval = 4.0
        self.next_trigger = 4.0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate":
            if time >= self.next_trigger:
                self.next_trigger += self.interval
                effect = getattr(champion, "effect", "")
                if effect == "Gain AS":
                    amt = 14 if self.level == 2 else 20
                    champion.aspd.addStat(amt)
                elif effect == "Gain AP":
                    amt = 10 if self.level == 2 else 15
                    champion.ap.addStat(amt)
        return 0


class ArbiterInterest(Buff):
    levels = [2, 3]
    display_name = "Arbiter (Interest)"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            multiplier = 5  # As per instructions: always assume 5 interest
            effect = getattr(champion, "effect", "")
            if effect == "Gain AS":
                amt = 8 if self.level == 2 else 12
                champion.aspd.addStat(amt * multiplier)
            elif effect == "Gain AP":
                amt = 8 if self.level == 2 else 12
                champion.ap.addStat(amt * multiplier)
        return 0


class ArbiterReroll(Buff):
    levels = [2, 3]
    display_name = "Arbiter (Reroll)"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            effect = getattr(champion, "effect", "")
            if effect == "Gain AS":
                amt = 35 if self.level == 2 else 55
                champion.aspd.addStat(amt)
            elif effect == "Gain AP":
                amt = 25 if self.level == 2 else 40
                champion.ap.addStat(amt)
        return 0


class ArbiterManaSpent(Buff):
    levels = [2, 3]
    display_name = "Arbiter (Mana Spent)"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["postAbility"]
        )
        self.manaSpent = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "postAbility":
            if champion.fullMana.stat > 0:
                self.manaSpent += champion.fullMana.stat
                while self.manaSpent >= 50:
                    self.manaSpent -= 50
                    effect = getattr(champion, "effect", "")
                    if effect == "Gain AS":
                        amt = 12 if self.level == 2 else 18
                        champion.aspd.addStat(amt)
                    elif effect == "Gain AP":
                        amt = 16 if self.level == 2 else 24
                        champion.ap.addStat(amt)
        return 0


class ArbiterStarLevel(Buff):
    levels = [2, 3]
    display_name = "Arbiter (Star Level)"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.star_levels = params

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            effect = getattr(champion, "effect", "")
            if effect == "Gain AS":
                amt = 8 if self.level == 2 else 9
                champion.aspd.addStat(amt * self.star_levels)
            elif effect == "Gain AP":
                amt = 7 if self.level == 2 else 8
                champion.ap.addStat(amt * self.star_levels)
        return 0


class Bastion(Buff):
    levels = [0, 2, 4, 6]
    display_name = "Bastion"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat", "onUpdate"]
        )
        self.bastion_scaling = {2: 16, 4: 40, 6: 60}
        self.is_bastion = 0
        self.doubled_removed = False
        self.extraBuff(params)

    def extraParameters():
        return {"Title": "Is Bastion", "Min": 0, "Max": 1, "Default": 1}

    def extraBuff(self, is_bastion):
        self.is_bastion = is_bastion

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.armor.addStat(15)
            champion.mr.addStat(15)
            if self.is_bastion and self.level >= 2:
                # Doubled during first 10 seconds of combat
                champion.armor.addStat(self.bastion_scaling[self.level] * 2)
                champion.mr.addStat(self.bastion_scaling[self.level] * 2)
            elif not self.is_bastion and self.level >= 6:
                champion.armor.addStat(20)
                champion.mr.addStat(20)
        elif phase == "onUpdate":
            if self.is_bastion and self.level >= 2 and not self.doubled_removed and time >= 10:
                self.doubled_removed = True
                bonus = self.bastion_scaling[self.level]
                champion.armor.addStat(-bonus)
                champion.mr.addStat(-bonus)
        return 0


class Shepherd(Buff):
    levels = [0]
    display_name = "Shepherd"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )

    def performAbility(self, phase, time, champion, input_=0):
        return 0


class Replicator(Buff):
    levels = [0, 2, 4]
    display_name = "Replicator"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.scaling = {0: 0, 2: 0.22, 4: 0.45}

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.replicator_scaling = self.scaling.get(self.level, 0)
        return 0


class LeblancUlt(Buff):
    levels = [1]
    display_name = "Fracture Reality"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name,
            level,
            params,
            phases=["preAttack"],
        )

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preAttack":
            # Passive: Magic damage attacks
            input_.attackType = "magical"
            input_.scaling = champion.passiveScaling

            if champion.active:
                # 5 clone attacks
                use_bolt = champion.activeAttacksLeft == 1
                scaling_func = (
                    champion.boltScaling if use_bolt else champion.cloneScaling
                )

                for _ in range(5):
                    champion.multiTargetSpell(
                        champion.opponents,
                        champion.items,
                        time,
                        1,
                        scaling_func,
                        "magical",
                    )

                champion.activeAttacksLeft -= 1
                if champion.activeAttacksLeft == 0:
                    champion.active = False
                    champion.manalockTime = time + 0.01
        return 0


class SpaceGroove(Buff):
    levels = [1, 3, 5, 7]
    display_name = "Space Groove"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.num_groovians = self.level

    def performAbility(self, phase, time, champion, input_=0):
        # Base AS is 12 per groovian (based on trait level)
        as_bonus = 12 * self.num_groovians
        ad_ap_tick = 0

        if self.level >= 5:
            ad_ap_tick = 5.0

        if self.level >= 7:
            as_bonus = as_bonus * 1.1
            ad_ap_tick = ad_ap_tick * 1.1

        champion.space_groove_params = {"as_bonus": as_bonus, "ad_ap_tick": ad_ap_tick}

        if self.level >= 3:
            champion.applyStatus(
                status.TheGrooveStatus(), self, time, 3.0, champion.space_groove_params
            )
        return 0


class FactoryNew(Buff):
    levels = [0, 1]
    display_name = "Factory New"

    def __init__(self, level=1, params=0):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preAttack"]
        )

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preAttack" and hasattr(champion, "bulletsScaling"):
            # Graves: each attack fires a volley of bullets instead of a normal auto
            input_.scaling = champion.bulletsScaling
        return input_


class StargazerHuntress(Buff):
    levels = [0, 3, 5, 7]
    display_name = "Stargazer (Huntress)"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.scaling = {3: 15, 5: 45, 7: 70}
        self.is_stargazer = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(15)
        if self.is_stargazer and self.level in self.scaling:
            champion.aspd.addStat(self.scaling[self.level])
        return 0

    def extraParameters():
        return {"Title": "Is Stargazer", "Min": 0, "Max": 1, "Default": 1}

    def extraBuff(self, is_stargazer):
        self.is_stargazer = is_stargazer


class StargazerMedallion(Buff):
    levels = [0, 3]
    display_name = "Stargazer (Medallion)"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.num_three_stars = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        amp = 0.15 + 0.05 * self.num_three_stars
        champion.dmgMultiplier.addStat(amp)
        return 0

    def extraParameters():
        return {"Title": "# 3*s", "Min": 0, "Max": 9, "Default": 0}

    def extraBuff(self, num_three_stars):
        self.num_three_stars = num_three_stars


class StargazerFountain(Buff):
    levels = [0, 3, 5]
    display_name = "Stargazer (Fountain)"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["onUpdate"]
        )
        self.scaling = {3: 4, 5: 9}
        self.next_tick = 2.0

    def performAbility(self, phase, time, champion, input_=0):
        if time >= self.next_tick:
            self.next_tick += 2.0
            amt = self.scaling[self.level]
            champion.bonus_ad.addStat(amt)
            champion.ap.addStat(amt)
        return 0


class VexUlt(Buff):
    levels = [1]
    display_name = "Lend Me a Hand, Shadow!"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name, level, params, phases=["preCombat", "onUpdate"]
        )
        self.buff_5s_applied = False
        self.buff_10s_applied = False

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            # Combat start bonus: 12 * 6 = 72
            champion.bonus_ad.addStat(72)
            champion.ap.addStat(72)
        elif phase == "onUpdate":
            if not self.buff_5s_applied and time >= 5.0:
                champion.bonus_ad.addStat(12)
                champion.ap.addStat(12)
                self.buff_5s_applied = True
            if not self.buff_10s_applied and time >= 10.0:
                champion.bonus_ad.addStat(12)
                champion.ap.addStat(12)
                self.buff_10s_applied = True
        return 0


class XayahUlt(Buff):
    levels = [1]
    display_name = "Stellar Ricochet"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preAttack"])

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preAttack" and getattr(input_, "regularAuto", True):
            champion.feathers = getattr(champion, "feathers", 0) + 1

            for target_idx, mult in ((1, 0.6), (2, 0.36)):
                if len(champion.opponents) > target_idx:
                    base = (
                        champion.atk.stat
                        * champion.bonus_ad.stat
                        * mult
                        * champion.dmgMultiplier.stat
                        * champion.extraDmgMultiplier.stat
                    )
                    champion.doDamage(
                        champion.opponents[target_idx],
                        champion.items,
                        champion.crit.stat,
                        base * champion.critDamage(),
                        base,
                        "physical",
                        time,
                    )

            ult_left = getattr(champion, "ultAttacksLeft", 0)
            if ult_left > 0:
                champion.ultAttacksLeft = ult_left - 1
                if champion.ultAttacksLeft == 0:
                    champion.doFeatherRecall(time)
                    champion.aspd.addStat(-75)
                    champion.manalockTime = time + 0.01
                    champion.manalockDuration = champion.castTime

        return input_


class KindredUlt(Buff):
    levels = [1]
    display_name = "Kindred Ult"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name, level, params, phases=["preAttack", "preAbility"]
        )

    def performAbility(self, phase, time, champion, input_=0):
        if phase in ["preAttack", "preAbility"]:
            if phase == "preAttack" and not getattr(input_, "regularAuto", True):
                return input_

            if hasattr(champion, "add_marks"):
                champion.add_marks(1, time, champion.items)
        return input_


class CorkiUlt(Buff):
    levels = [1]
    display_name = "Asteroid Blaster"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["onUpdate"])
        self.next_rocket = 0

    def performAbility(self, phase, time, champion, input_=0):
        if champion.meep > 0:
            if self.next_rocket == 0:
                self.next_rocket = time + 8 * (1 - 0.1 * champion.meep)
            if self.next_rocket <= time:
                champion.multiTargetSpell(
                    champion.opponents,
                    champion.items,
                    time,
                    champion.num_targets,
                    champion.meepScaling,
                    "physical",
                )
                self.next_rocket = time + 8 * (1 - 0.1 * champion.meep)
                print("Firing rocket at time {}".format(time))
        return 0


class MechaAurelionSolPassive(Buff):
    """Periodic passive for mecha-transformed Aurelion Sol.
    Every 0.75s: grants mana and fires fighters (1 per 0.25s during overdrive, 1 per tick otherwise).
    """

    levels = [1]
    display_name = "Mecha A-Sol Passive"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["onUpdate"])
        self.interval = 0.75
        self.next_tick = 0.75
        self.overdrive_interval = 0.25
        self.next_overdrive_fighter = 0.0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "onUpdate" and champion.opponents:
            overdrive_end = getattr(champion, "mechaOverdriveEnd", -1)
            in_overdrive = time <= overdrive_end

            if time >= self.next_tick:
                self.next_tick += self.interval
                mana_gain = 5.0 + 0.8 * champion.aspd.add / 20.0
                champion.addMana(mana_gain)

                if not in_overdrive:
                    champion.multiTargetSpell(
                        champion.opponents,
                        champion.items,
                        time,
                        1,
                        champion.fighterScaling,
                        "magical",
                    )

            if in_overdrive and time >= self.next_overdrive_fighter:
                self.next_overdrive_fighter = time + self.overdrive_interval
                champion.multiTargetSpell(
                    champion.opponents,
                    champion.items,
                    time,
                    1,
                    champion.fighterScaling,
                    "magical",
                    ability_mr_pierce=0.30,
                )
        return 0


class Mecha(Buff):
    levels = [0, 3, 4, 6]
    display_name = "Mecha"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.ad_ap_scaling = {0: 0, 3: 25, 4: 40, 6: 40}

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat" and self.level >= 3:
            amt = self.ad_ap_scaling.get(self.level, 0)
            champion.bonus_ad.addStat(amt)
            champion.ap.addStat(amt)

            if getattr(champion, "is_mecha_unit", False):
                champion.mecha_transformed = True
                champion.castTime = 3.0
                champion.manalockDuration = 3.0
                # Remove the caster-role mana regen (2/s); mana comes from passive only
                champion.manaRegen.addStat(-2)
                if not any(
                    isinstance(item, MechaAurelionSolPassive)
                    for item in champion.items
                ):
                    champion.items.append(MechaAurelionSolPassive())
        return 0


class GnarUlt(Buff):
    levels = [1]
    display_name = "Slingshot Maneuver"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name, level, params, phases=["preAbility", "onUpdate"]
        )
        self.next_meep = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preAbility":
            for i in range(champion.num_targets):
                if i < len(champion.opponents):
                    scaling_factor = 0.25**i

                    def current_scaling(level, AD, AP, sf=scaling_factor):
                        return sf * champion.abilityScaling(level, AD, AP)

                    champion.multiTargetSpell(
                        [champion.opponents[i]],
                        champion.items,
                        time,
                        1,
                        current_scaling,
                        "physical",
                    )
        elif phase == "onUpdate":
            # Deals damage per second if he has meeps
            if champion.meep > 0:
                if self.next_meep == 0:
                    self.next_meep = time + 1.0

                if time >= self.next_meep:
                    meeps = champion.meep

                    def meep_scaling(level, AD, AP):
                        # AD here is bonus_ad.stat, AP is ap.stat
                        return (
                            meeps
                            * 0.23
                            * (champion.atk.stat * AD)
                            * (1 + 0.4 * (champion.aspd.add / 100))
                        )

                    if champion.opponents:
                        champion.multiTargetSpell(
                            champion.opponents,
                            champion.items,
                            time,
                            1,
                            meep_scaling,
                            "physical",
                        )

                    self.next_meep += 1.0
        return input_

# ...existing code...
import ast

from item import Item
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
]

augments = [
    "BackupDancers",
    "Shred30",
    "Shred20",
    "BlazingSoulI",
    "BlazingSoulII",
    "MacesWill",
    "BestFriendsI",
    "BestFriendsII",
    "TrifectaI",
    "TrifectaII",
    "TinyButDeadly",
    "Moonlight",
    "FinalAscension",
    "CyberneticUplinkII",
    "CyberneticUplinkIII",
    "StandUnitedI",
    "Ascension",
    "KnowYourEnemy",
    "PumpingUpI",
    "PumpingUpII",
    "PumpingUpIII",
    "HoldTheLine",
    "AdaptiveStyle",
    "MessHall",
    "TonsOfStats",
    "LitFuseSolo",
    "LitFuseDuo",
    "LitFuseTrio",
    "WaterLotusI",
    "WaterLotusII",
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


class SupremeCells(Buff):
    levels = [0, 2, 3, 4]
    display_name = "SupremeCells"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.scaling = {2: 0.12, 3: 0.30, 4: 0.50}

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(self.scaling[self.level])
        return 0


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
        amt_to_add = self.aspd_per_yordle * self.level + self.num_three_stars * (self.aspd_per_yordle / 2)
        champion.aspd.addStat(amt_to_add)
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "# 3 Star Yordles", "Min": 0, "Max": self.level, "Default": 0}

    def extraBuff(self, num_three_stars):
        self.num_three_stars = num_three_stars


class Freljord(Buff):
    levels = [0, 3, 5, 7]
    display_name = "Freljord"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.dmgamp_scaling = {3: .1, 5: .16, 7: .22}
        self.is_freljord = 0
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        multiplier = 1.5 if self.is_freljord else 1
        value_to_add = (self.dmgamp_scaling[self.level] * multiplier)
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
        self.scaling = {2: .25, 4: .4}
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
        return {"Title": "Is Quickstriker", "Min": 0, "Max": 1, "Default": 1}

    def extraBuff(self, is_quickstriker):
        self.is_quickstriker = is_quickstriker


class Arcanist(Buff):
    levels = [0, 2, 4, 6]
    display_name = "Arcanist"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.scaling = {2: 18, 4: 25, 6: 40}
        self.arcanist_scaling = {2: 25, 4: 45, 6: 70}
        self.extraBuff(params)

    def performAbility(self, phase, time, champion, input_=0):
        amt_to_add = self.scaling[self.level] if not self.is_arcanist else self.arcanist_scaling[self.level]
        champion.ap.addStat(amt_to_add)
        return 0

    def extraParameters():
        # defining the parameters for the extra shit
        return {"Title": "Is Arcanist", "Min": 0, "Max": 1, "Default": 1}

    def extraBuff(self, is_arcanist):
        self.is_arcanist = is_arcanist


class Executioner(Buff):
    levels = [0, 2, 3, 4, 5]
    display_name = "Executioner"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.critChanceScaling = {2: 0.25, 3: 0.35, 4: 0.5, 5: 0.55}
        self.critDmgScaling = {2: 0.1, 3: 0.12, 4: 0.18, 5: 0.28}

    def performAbility(self, phase, time, champion, input=0):
        champion.canSpellCrit = True
        champion.critDmg.addStat(self.critDmgScaling[self.level])
        champion.crit.addStat(self.critChanceScaling[self.level] * 0.5)
        return 0


# Unit buffs



# AUGMENTS


class FuryBreakAlly(Buff):
    levels = [1]
    display_name = "Ally Fury Break (5s)"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name, level, params, phases=["preCombat", "onUpdate"]
        )
        self.as_scaling = 25
        self.time_bonus = 5
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


class LearnFromTheBest(Buff):
    levels = [1]
    display_name = "Learn From The Best"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])
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
    display_name = "Water Lotus I"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name,
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
    display_name = "Water Lotus II (instant mana restore)"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name,
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
    display_name = "Lit Fuse (Solo)"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["onUpdate"])
        self.activation_time = 6
        self.manaBonus = 60

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.activation_time:
            self.activation_time = 999
            champion.addMana(self.manaBonus)
        return 0


class LitFuseDuo(Buff):
    levels = [1]
    display_name = "Lit Fuse (Duo)"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["onUpdate"])
        self.activation_time = 6
        self.manaBonus = 30

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.activation_time:
            self.activation_time = 999
            champion.addMana(self.manaBonus)
        return 0


class LitFuseTrio(Buff):
    levels = [1]
    display_name = "Lit Fuse (Trio)"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["onUpdate"])
        self.activation_time = 6
        self.manaBonus = 20

    def performAbility(self, phase, time, champion, input_=0):
        if time > self.activation_time:
            self.activation_time = 999
            champion.addMana(self.manaBonus)
        return 0


class HoldTheLine(Buff):
    levels = [1]
    display_name = "HoldTheLine"

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
        champion.dmgMultiplier.addStat(0.13)
        return 0


class KnowYourEnemy(Buff):
    levels = [1]
    display_name = "Know Your Enemy"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(0.18)
        return 0


class GlassCannonII(Buff):
    levels = [1]
    display_name = "Glass Cannon II"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.dmgMultiplier.addStat(0.2)
        return 0


class Moonlight(Buff):
    levels = [1]
    display_name = "Moonlight (for 3* champs)"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        if champion.level == 3:
            champion.bonus_ad.addStat(45)
            champion.ap.addStat(45)
        return 0


class Hero101(Buff):
    levels = [1]
    display_name = "Hero101"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])
        self.scaling = 0.15

    def performAbility(self, phase, time, champion, input_=0):
        # may not interact well with other forms of scaling, watch out
        for item in champion.items:
            if "Academia" in item.name:
                champion.fullMana.mult -= self.scaling
                break
        return 0


class TinyTeam(Buff):
    levels = [1]
    display_name = "Tiny Team"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        if sum(champion.star_guardians.values()) <= 3:
            champion.tiny_team = True


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
        champion.aspd.addStat(12)
        champion.armor.addStat(12)
        return 0


class BestFriendsII(Buff):
    levels = [1]
    display_name = "Best Friends II"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(15)
        champion.armor.addStat(20)
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


class CyberneticImplantsII(Buff):
    levels = [1]
    display_name = "Cybernetic Implants II"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(20)
        return 0


class CyberneticImplantsIII(Buff):
    levels = [1]
    display_name = "Cybernetic Implants III"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(30)
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
    display_name = "No Scout no Pivot"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])
        self.scaling = 2

    def performAbility(self, phase, time, champion, input_=0):
        champion.bonus_ad.addStat(self.scaling * 5 * (champion.stage - 2))
        champion.ap.addStat(self.scaling * 5 * (champion.stage - 2))
        return 0


class BlazingSoulI(Buff):
    levels = [1]
    display_name = "Blazing Soul I"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(20)
        champion.ap.addStat(20)
        return 0


class BlazingSoulII(Buff):
    levels = [1]
    display_name = "Blazing Soul II"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        champion.aspd.addStat(35)
        champion.ap.addStat(35)
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


class FinalAscension(Buff):
    levels = [1]
    display_name = "Final Ascension"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name, level, params, phases=["preCombat", "onUpdate"]
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


class CyberneticUplinkII(Buff):
    levels = [1]
    display_name = "Cybernetic Uplink II"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])
        self.manaBonus = 2

    def performAbility(self, phase, time, champion, input_=0):
        champion.manaRegen.addStat(self.manaBonus)


class CyberneticUplinkIII(Buff):
    levels = [1]
    display_name = "Cybernetic Uplink III"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preCombat"])
        self.manaBonus = 3

    def performAbility(self, phase, time, champion, input_=0):
        champion.manaRegen.addStat(self.manaBonus)


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

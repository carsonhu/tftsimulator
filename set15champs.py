from champion import Champion
from stats import Stat, Attack
from collections import deque
from role import Role
import math
import numpy as np
import heapq
import random
import set15buffs as buffs
import status

champ_list = [
    "Ezreal",
    "Gnar",
    "Kalista",
    "Kayle",
    "Lucian",
    "Sivir",
    "Jhin",
    "Gangplank",
    "Caitlyn",
    "Malzahar",
    "Smolder",
]


class Gnar(Champion):
    def __init__(self, level):
        hp = 500
        atk = 52
        curMana = 0
        fullMana = 40
        aspd = 0.7
        armor = 25
        mr = 25
        super().__init__(
            "Gnar",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.MARKSMAN,
        )
        self.default_traits = ["Luchador", "Sniper"]
        self.items.append(buffs.GnarUlt())
        self.castTime = 0
        self.buff_duration = 6
        self.manalockDuration = self.buff_duration
        self.ad_bonus = [90, 90, 90]
        self.notes = ""

    def performAbility(self, opponents, items, time):
        self.applyStatus(
            status.ADModifier("Gnar"),
            self,
            time,
            self.buff_duration,
            self.ad_bonus[self.level - 1],
        )


class Ezreal(Champion):
    def __init__(self, level):
        hp = 500
        atk = 50
        curMana = 0
        fullMana = 50
        aspd = 0.7
        armor = 20
        mr = 20
        super().__init__(
            "Ezreal",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.CASTER,
        )
        self.default_traits = ["BattleAcademia", "Prodigy"]
        self.potential = 0
        self.castTime = 0.5
        self.buff_duration = 5 + self.castTime
        self.aspd_bonus = 25
        self.stat_per_potential = 4
        self.notes = ""

    def abilityScaling(self, level, AD, AP):
        adScale = [110, 165, 275]
        apScale = [0, 0, 0]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def magicAbilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [220, 330, 550]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical"
        )
        self.multiTargetSpell(
            opponents, items, time, 1, self.magicAbilityScaling, "magical"
        )
        if self.potential > 0:
            self.applyStatus(
                status.ASModifier("Ezreal"),
                self,
                time,
                self.buff_duration,
                self.aspd_bonus,
            )
            self.bonus_ad.addStat(self.stat_per_potential * self.potential)
            self.ap.addStat(self.stat_per_potential * self.potential)


class Kalista(Champion):
    def __init__(self, level):
        hp = 500
        atk = 55
        curMana = 10
        fullMana = 90
        aspd = 0.7
        armor = 20
        mr = 20
        super().__init__(
            "Kalista",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.CASTER,
        )
        self.default_traits = ["SoulFighter", "Executioner"]
        self.castTime = 0.5
        self.notes = "Click 'more options' button to set bonus AD"

    def abilityScaling(self, level, AD, AP):
        adScale = [400, 600, 900]
        apScale = [60, 90, 135]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical"
        )


class Kayle(Champion):
    def __init__(self, level):
        hp = 500
        atk = 30
        curMana = 0
        fullMana = -1
        aspd = 0.7
        armor = 25
        mr = 25
        super().__init__(
            "Kayle",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.CASTER,
        )
        self.num_targets = 2
        self.items.append(buffs.KayleUlt())
        self.finalAscent = False
        self.default_traits = ["Duelist"]
        self.manaGainMultiplier.base = 0
        self.notes = "modify level to modify kayle; level 9 wave is 1.5x more targets"

    def passiveAbilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [30, 45, 70]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def waveAbilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [60, 90, 140]
        return apScale[level - 1] * AP + adScale[level - 1] * AD


class Lucian(Champion):
    def __init__(self, level):
        hp = 500
        atk = 30
        curMana = 0
        fullMana = 40
        aspd = 0.7
        armor = 20
        mr = 20
        super().__init__(
            "Lucian",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.CASTER,
        )
        self.default_traits = ["Sorcerer"]
        self.projectiles = 4
        self.castTime = 0.5
        self.notes = ""

    def abilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [80, 120, 180]
        return (apScale[level - 1] * AP + adScale[level - 1] * AD) * self.projectiles

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items, time, 1, self.abilityScaling, "magical")


class Sivir(Champion):
    def __init__(self, level):
        hp = 450
        atk = 45
        curMana = 0
        fullMana = 60
        aspd = 0.7
        armor = 20
        mr = 20
        super().__init__(
            "Sivir",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.CASTER,
        )
        self.default_traits = ["Sniper"]
        self.num_targets = 2
        self.castTime = 0.5
        self.notes = "boomerang hits through each target twice"

    def abilityScaling(self, level, AD, AP):
        adScale = [160, 240, 360]
        apScale = [20, 30, 45]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        for count in range(self.num_targets * 2):
            # technically this is just hitting the 1st guy X times so we'll
            # change it if it matters
            self.multiTargetSpell(
                opponents,
                items,
                time,
                1,
                lambda x, y, z: 0.6 ** (count) * self.abilityScaling(x, y, z),
                "physical",
            )


class Jhin(Champion):
    def __init__(self, level):
        hp = 650
        atk = 64
        curMana = 0
        fullMana = -1
        aspd = 0.75
        armor = 25
        mr = 25
        super().__init__(
            "Jhin",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.MARKSMAN,
        )
        self.default_traits = ["Sniper"]
        self.items.append(buffs.JhinUlt())
        # append jhinult to items
        self.castTime = 0
        self.manaGainMultiplier.base = 0
        self.notes = "Wraith not coded yet"

    def abilityScaling(self, level, AD, AP):
        adScale = [180, 270, 415]
        apScale = [30, 45, 70]
        return apScale[level - 1] * AP + adScale[level - 1] * AD


class Gangplank(Champion):
    def __init__(self, level):
        hp = 750
        atk = 50
        curMana = 0
        fullMana = 40
        aspd = 0.8
        armor = 55
        mr = 55
        super().__init__(
            "Gangplank",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.FIGHTER,
        )
        self.default_traits = ["Duelist"]
        self.castTime = 0.5
        self.notes = ""

    def abilityScaling(self, level, AD, AP):
        adScale = [375, 565, 875]
        apScale = [0, 0, 0]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical"
        )


class Kaisa(Champion):
    def __init__(self, level):
        hp = 550
        atk = 45
        curMana = 0
        fullMana = 50
        aspd = 0.7
        armor = 25
        mr = 25
        super().__init__(
            "Kaisa",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.MARKSMAN,
        )
        self.default_traits = ["Supreme Cells", "Duelist"]
        self.projectiles = 8
        self.castTime = 1.5
        self.notes = "Click 'more options' button to set bonus AD"

    def abilityScaling(self, level, AD, AP):
        adScale = [30, 45, 70]
        apScale = [6, 8, 14]
        return (apScale[level - 1] * AP + adScale[level - 1] * AD) * self.projectiles

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical"
        )


class Caitlyn(Champion):
    def __init__(self, level):
        hp = 650
        atk = 55
        curMana = 0
        fullMana = 40
        aspd = 0.75
        armor = 30
        mr = 30
        super().__init__(
            "Caitlyn",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.CASTER,
        )
        self.default_traits = ["Battle Academia", "Sniper"]
        self.potential = 0
        self.castTime = 1
        self.notes = ""

    def abilityScaling(self, level, AD, AP):
        adScale = [340, 510, 815]
        apScale = [30, 45, 70]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def secondaryAbilityScaling(self, level, AD, AP):
        adScale = [90, 135, 210]
        apScale = [0, 0, 0]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical"
        )
        for i in range(self.potential + 1):
            self.multiTargetSpell(
                opponents,
                items,
                time,
                1,
                self.secondaryAbilityScaling,
                "physical",
            )


class Malzahar(Champion):
    def __init__(self, level):
        hp = 800
        atk = 40
        curMana = 0
        fullMana = 35
        aspd = 0.7
        armor = 30
        mr = 30
        super().__init__(
            "Malzahar",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.CASTER,
        )
        self.default_traits = ["Prodigy"]
        self.buff_duration = 15
        self.castTime = 0.5
        self.notes = "Click 'more options' button to set bonus AD"

    def dotScaling(self, level, AD, AP):
        apScale = [520, 780, 1300]
        return apScale[level - 1] * AP / self.buff_duration

    def performAbility(self, opponents, items, time):
        # self.multiTargetSpell(opponents, items,
        #                 time, 1,
        #                 self.abilityScaling,
        #                 'physical')
        opponents[0].applyStatus(
            status.DoTEffect("Malz {}".format(self.numCasts)),
            self,
            time,
            self.buff_duration,
            self.dotScaling,
        )


class Smolder(Champion):
    def __init__(self, level):
        hp = 650
        atk = 55
        curMana = 0
        fullMana = 60
        aspd = 0.75
        armor = 30
        mr = 30
        super().__init__(
            "Smolder",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.CASTER,
        )
        self.default_traits = ["MonsterTrainer"]
        self.trainer_level = 0
        self.castTime = 0.5
        self.notes = "modify mosnter level through trait"

    def abilityScaling(self, level, AD, AP):
        adScale = [350, 525, 840]
        apScale = [0, 0, 0]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def secondaryAbilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [50, 75, 120]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical"
        )
        self.multiTargetSpell(
            opponents, items, time, 3, self.secondaryAbilityScaling, "magical"
        )
        if self.trainer_level >= 15:
            if self.numCasts % 2 == 0:
                self.multiTargetSpell(
                    opponents,
                    items,
                    time,
                    1,
                    lambda x, y, z: 0.75 * self.abilityScaling(x, y, z),
                    "physical",
                )


class BaseChamp(Champion):
    def __init__(self, level):
        hp = 1000
        atk = 70
        curMana = 10
        fullMana = 100
        aspd = 0.85
        armor = 0
        mr = 0
        super().__init__(
            "Base Champ", hp, atk, curMana, fullMana, aspd, armor, mr, level
        )
        self.ap_scale = 1
        self.castTime = 0.5

    def abilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [self.ap_scale, self.ap_scale, self.ap_scale]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items, time, 1, self.abilityScaling, "magical")


class ZeroResistance(Champion):
    def __init__(self, level):
        hp = 1000
        atk = 70
        curMana = 10
        fullMana = 100
        aspd = 0.85
        armor = 0
        mr = 0
        super().__init__("Tankman", hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.castTime = 0.5

    def performAbility(self, opponents, items, time):
        return 0


class DummyTank(Champion):
    def __init__(self, level):
        hp = 1000
        atk = 70
        curMana = 10
        fullMana = 100
        aspd = 0.85
        armor = 100
        mr = 100
        super().__init__("Tankman", hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.castTime = 0.5

    def performAbility(self, opponents, items, time):
        return 0


class SuperDummyTank(Champion):
    def __init__(self, level):
        hp = 2000
        atk = 70
        curMana = 10
        fullMana = 100
        aspd = 0.85
        armor = 200
        mr = 200
        super().__init__("Tankman", hp, atk, curMana, fullMana, aspd, armor, mr, level)
        self.castTime = 0.5

    def performAbility(self, opponents, items, time):
        return 0

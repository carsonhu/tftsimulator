import heapq
import math
import random
from collections import deque

import numpy as np
import set16buffs as buffs
from role import Role
from stats import Attack, Stat

import status
from champion import Champion

champ_list = [
    # 1-cost
    "Anivia",
    "Caitlyn",
    "Sona",
    # 3-cost
    "Ahri",
    "Vayne",
    # 4-cost
    "Lux",
]


class Anivia(Champion):
    def __init__(self, level):
        hp = 500
        atk = 30
        curMana = 0
        fullMana = 45
        aspd = 0.7
        armor = 20
        mr = 20
        super().__init__(
            "Anivia",
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
        self.default_traits = ["Freljord", "Invoker"]
        self.castTime = 1
        self.notes = ""

    def abilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [325, 455, 650]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "magical"
        )


class Caitlyn(Champion):
    def __init__(self, level):
        hp = 500
        atk = 45
        curMana = 0
        fullMana = 90
        aspd = 0.7
        armor = 15
        mr = 15
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
        self.default_traits = ["Longshot"]
        self.castTime = 2
        self.notes = ""

    def abilityScaling(self, level, AD, AP):
        adScale = [475, 715, 1105]
        apScale = [40, 60, 100]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical"
        )


class Sona(Champion):
    def __init__(self, level):
        hp = 500
        atk = 20
        curMana = 0
        fullMana = 30
        aspd = 0.7
        armor = 15
        mr = 15
        super().__init__(
            "Sona",
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
        self.default_traits = ["Demacia", "Invoker"]
        self.castTime = 1
        self.notes = ""

    def abilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [120, 180, 270]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 2, self.abilityScaling, "magical"
        )


class Ahri(Champion):
    def __init__(self, level):
        hp = 650
        atk = 30
        curMana = 0
        fullMana = 30
        aspd = 0.8
        armor = 25
        mr = 25
        super().__init__(
            "Ahri",
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
        self.default_traits = ["Ionia", "Arcanist"]
        self.castTime = 1
        self.notes = ""

    def abilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [85, 130, 200]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        dmg_instances = 3 if self.numCasts % 3 != 0 else 9
        for i in range(dmg_instances):
            self.multiTargetSpell(
                opponents, items, time, 1, self.abilityScaling, "magical"
            )


class Vayne(Champion):
    def __init__(self, level):
        hp = 650
        atk = 70
        curMana = 0
        fullMana = 40
        aspd = 0.8
        armor = 25
        mr = 25
        super().__init__(
            "Vayne",
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
        self.default_traits = ["Demacia", "Longshot"]
        self.castTime = .7
        self.notes = ""

    def abilityScaling(self, level, AD, AP):
        adScale = [100, 150, 230]
        apScale = [6, 10, 15]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "true"
        )


class Lux(Champion):
    def __init__(self, level):
        hp = 800
        atk = 30
        curMana = 0
        fullMana = 50
        aspd = 0.75
        armor = 30
        mr = 30
        super().__init__(
            "Lux",
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
        self.default_traits = ["Demacia", "Arcanist"]
        self.castTime = 1.8
        self.num_targets = 2
        self.notes = "Num targets refers to number of extra targets beyond the first 2."

    def abilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [30, 45, 100]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def laserAbilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [290, 435, 1500]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def laserSecondaryScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [90, 135, 800]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 2, self.abilityScaling, "magical"
        )
        self.multiTargetSpell(
            opponents, items, time, 2, self.laserAbilityScaling, "magical"
        )
        self.multiTargetSpell(
            opponents, items, time, self.num_targets, self.laserSecondaryScaling, "magical"
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

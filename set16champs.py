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
    "Briar",
    "Caitlyn",
    "Jhin",
    "Kogmaw",
    "Lulu",
    "Qiyana",
    "Sona",
    "Viego",
    # 2-cost
    "Aphelios",
    "Ashe",
    "Bard",
    "Orianna",
    "Teemo",
    "Tristana",
    "Yasuo",
    # "TwistedFate",
    # 3-cost
    "Ahri",
    "Draven",
    "Gwen",
    "Jinx",
    "Leblanc",
    "Malzahar",
    "Milio",
    "Vayne",
    "Zoe",
    # 4-cost,
    "Kaisa",
    "Kalista",
    "Lissandra",
    "Lux",
    "MissFortuneOld",
    "MissFortune",   
    "Seraphine",
    "Veigar",
    "Yone",
    "Yunara",
    # 5-cost
    "AurelionSol",
    "Azir",
    "THex",
    
]


def create_ability_scaling(ad_values, ap_values, func_name="abilityScaling"):
    """
    Factory function to create ability scaling functions.
    
    Args:
        ad_values: List of 3 AD scaling values [level1, level2, level3]
        ap_values: List of 3 AP scaling values [level1, level2, level3]
        func_name: The name of the function to be created (must match attribute name for pickling)
    
    Returns:
        A function that calculates ability damage based on level, AD, and AP
    """
    def scaling(_self, level, AD, AP):
        return ap_values[level - 1] * AP + ad_values[level - 1] * AD
    scaling.__name__ = func_name
    return scaling


class Anivia(Champion):
    canFourStar = True
    def __init__(self, level):
        hp = 500
        atk = 30
        curMana = 0
        fullMana = 40
        aspd = 0.75
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

    # AP: 325/455/650/845
    abilityScaling = create_ability_scaling([0, 0, 0, 0], [325, 455, 650, 845])

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "magical"
        )


class Briar(Champion):
    def __init__(self, level):
        hp = 700
        atk = 42
        curMana = 0
        fullMana = 40
        aspd = 0.75
        armor = 40
        mr = 40
        super().__init__(
            "Briar",
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
        self.default_traits = ["Slayer"]
        self.castTime = .5 # unverified
        self.manalockDuration = 4
        self.buff_duration = 4
        self.aspd_scaling = [300, 300, 350]
        self.notes = ""

    def performAbility(self, opponents, items, time):
        self.applyStatus(
            status.ADModifier("BriarAD"),
            self,
            time,
            self.buff_duration,
            25,
        )
        self.applyStatus(
            status.DecayingASModifier("BriarAS {}".format(self.numCasts)),
            self,
            time,
            self.buff_duration,
            self.aspd_scaling[self.level - 1] * self.ap.stat,
        )


class Caitlyn(Champion):
    canFourStar = True
    def __init__(self, level):
        hp = 500
        atk = 45
        curMana = 0
        fullMana = 80
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
        self.castTime = 2.5
        self.notes = ""

    # AD: 475/715/1105/1495, AP: 40/60/100/140
    abilityScaling = create_ability_scaling([475, 715, 1105, 1495], [40, 60, 100, 140])

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical"
        )


class Jhin(Champion):
    def __init__(self, level):
        hp = 444
        atk = 44
        curMana = 0
        fullMana = 70
        aspd = 0.7
        armor = 24
        mr = 24
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
        self.default_traits = ["Ionia", "Gunslinger"]
        self.items.append(buffs.JhinUlt())
        self.manalockDuration = 999
        self.castTime = 0
        self.ultAutos = 0
        self.notes = ""

    # AD: 135/200/300 AP: 15/22/34
    abilityScaling = create_ability_scaling([135, 200, 300], [15, 22, 34])

    def performAbility(self, opponents, items, time):
        self.ultAutos = 4
        self.aspd.base = 1
        self.aspd.as_cap = 1



class Kogmaw(Champion):
    def __init__(self, level):
        hp = 500
        atk = 20
        curMana = 0
        fullMana = 30
        aspd = 0.7
        armor = 15
        mr = 15
        super().__init__(
            "Kogmaw",
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
        self.default_traits = ["Void", "Arcanist", "Longshot"]
        self.castTime = 1 # unverified
        self.num_targets = 2
        self.notes = "No shred included"

    # AP: 140/200/300
    abilityScaling = create_ability_scaling([0, 0, 0], [140, 200, 300])

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "magical"
        )
        if self.num_targets >= 2:
            self.multiTargetSpell(
                opponents, items, time, 1, lambda x,y,z: self.abilityScaling(x,y,z) * .5, "magical"
            )


class Lulu(Champion):
    def __init__(self, level):
        hp = 500
        atk = 25
        curMana = 20
        fullMana = 70
        aspd = 0.7
        armor = 15
        mr = 15
        super().__init__(
            "Lulu",
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
        self.default_traits = ["Yordle", "Arcanist"]
        self.castTime = 1 # unverified
        self.notes = ""

    # AP: 285/425/635
    abilityScaling = create_ability_scaling([0, 0, 0], [285, 425, 635])

    # AP: 120/180/270
    extraAbilityScaling = create_ability_scaling([0, 0, 0], [120, 180, 270])
    
    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "magical"
        )
        self.multiTargetSpell(
            opponents, items, time, 1, self.extraAbilityScaling, "magical"
        )



class Qiyana(Champion):
    def __init__(self, level):
        hp = 700
        atk = 45
        curMana = 0
        fullMana = 30
        aspd = 0.75
        armor = 40
        mr = 40
        super().__init__(
            "Qiyana",
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
        self.default_traits = ["Slayer"]
        self.castTime = 1 # unverified
        self.num_targets = 2
        self.notes = ""

    # AD: 160/240/400, AP: 20/30/45
    abilityScaling = create_ability_scaling([160, 240, 400], [20, 30, 45])

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, self.num_targets, self.abilityScaling, "physical"
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

    # AP: 120/180/270
    abilityScaling = create_ability_scaling([0, 0, 0], [120, 180, 270])

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 2, self.abilityScaling, "magical"
        )


class Viego(Champion):
    def __init__(self, level):
        hp = 700
        atk = 40
        curMana = 0
        fullMana = 30
        aspd = 0.75
        armor = 15
        mr = 15
        super().__init__(
            "Viego",
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
        self.default_traits = ["ShadowIsles", "Quickstriker"]
        self.items.append(buffs.ViegoUlt())
        self.castTime = .5
        self.notes = "need to fix for cases where AP increases over time"

    # AD: 55, 85, 125
    abilityScaling = create_ability_scaling([55, 85, 125], [0, 0, 0])

    # AP: 18, 27, 42
    def extraAbilityScaling(self, level, AD, AP):
        base_scaling = create_ability_scaling([0, 0, 0], [18, 27, 42])
        return base_scaling(None, level, AD, AP) * self.numCasts

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical"
        )


class Aphelios(Champion):
    def __init__(self, level):
        hp = 650
        atk = 20
        curMana = 0
        fullMana = 40
        aspd = 0.75
        armor = 20
        mr = 20
        super().__init__(
            "Aphelios",
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
        self.attackWindupRatio = .15
        self.default_traits = []
        self.castTime = 0
        self.items.append(buffs.ApheliosUlt())
        self.manalockDuration = 999
        self.severumAttacks = 8
        self.severumAttacksLeft = 0
        self.severumActivated = False
        # infernum, severum activated, severum
        self.notes = "Shred is just permanent"

    # AD: 70/105/175
    abilityScaling = create_ability_scaling([70, 105, 175], [0, 0, 0])

    def performAbility(self, opponents, items, time):
        self.severumAttacksLeft = round(self.severumAttacks * self.ap.stat)
        self.severumActivated = True
        self.nextAttackTime = time + .01


class Ashe(Champion):
    def __init__(self, level):
        hp = 550
        atk = 53
        curMana = 20
        fullMana = 80
        aspd = 0.7
        armor = 20
        mr = 20
        super().__init__(
            "Ashe",
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
        self.default_traits = ["Freljord", "Quickstriker"]
        self.castTime = .5
        self.num_targets = 2
        self.notes = "need to verify cast time"

    # AD: 135/195/300, AP: 15/25/35
    abilityScaling = create_ability_scaling([125, 185, 290], [15, 25, 35])

    def performAbility(self, opponents, items, time):
        # does not count as auto
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical"
        )
        if self.num_targets >= 2:
            self.multiTargetSpell(
                opponents, items, time, 1, lambda x,y,z: self.abilityScaling(x,y,z) * .33, "physical"
            )


class Bard(Champion):
    def __init__(self, level):
        hp = 750
        atk = 30
        curMana = 0
        fullMana = 55
        aspd = 0.75
        armor = 20
        mr = 20
        super().__init__(
            "Bard",
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
        self.default_traits = ["Caretaker"]
        self.num_three_stars = 0
        self.base_meeps = 6
        self.castTime = 2.5 # changes depending on # 3 stars
        self.notes = ""

    def abilityScaling(self, level, AD, AP):
        # AP: 120/170/240, multiplied by number of meeps
        base_scaling = create_ability_scaling([0, 0, 0], [120, 170, 240])
        return base_scaling(None, level, AD, AP) * (self.base_meeps + self.num_three_stars)

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "magical"
        )


class Orianna(Champion):
    def __init__(self, level):
        hp = 550
        atk = 30
        curMana = 20
        fullMana = 50
        aspd = 0.7
        armor = 20
        mr = 20
        super().__init__(
            "Orianna",
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
        self.default_traits = ["Piltover", "Invoker"]
        self.castTime = .7
        self.notes = ""

    # AP: 220/330/500
    abilityScaling = create_ability_scaling([0, 0, 0], [220, 330, 500])

    # AP: 100/150/250
    extraAbilityScaling = create_ability_scaling([0, 0, 0], [100, 150, 250], func_name="extraAbilityScaling")

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "magical"
        )
        self.multiTargetSpell(
            opponents, items, time, 1, self.extraAbilityScaling, "magical"
        )

class Teemo(Champion):
    def __init__(self, level):
        hp = 550
        atk = 25
        curMana = 0
        fullMana = 30
        aspd = 0.7
        armor = 20
        mr = 20
        super().__init__(
            "Teemo",
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
        self.default_traits = ["Yordle", "Longshot"]
        self.buff_duration = 8
        self.castTime = 1 # verified
        self.notes = ""

    # AP: 130/200/330
    abilityScaling = create_ability_scaling([0, 0, 0], [130, 200, 330])

    # AP: 35/55/100
    dotScaling = create_ability_scaling([0, 0, 0], [35, 55, 100], func_name="dotScaling")

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "magical"
        )
        opponents[0].applyStatus(
            status.DoTEffect("Teemo {}".format(self.numCasts)),
            self,
            time,
            self.buff_duration,
            (self.dotScaling, 1),
        )


class Tristana(Champion):
    def __init__(self, level):
        hp = 550
        atk = 55
        curMana = 0
        fullMana = 50
        aspd = 0.75
        armor = 20
        mr = 20
        super().__init__(
            "Tristana",
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
        self.default_traits = ["Yordle", "Gunslinger"]
        self.castTime = .6
        self.notes = ""

    # AD: 250,375,565  AP: 30,45,70
    abilityScaling = create_ability_scaling([250, 375, 565], [30, 45, 70])

    def performAbility(self, opponents, items, time):
        # does not count as auto
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical"
        )

class TwistedFate(Champion):
    def __init__(self, level):
        hp = 550
        atk = 10
        curMana = 0
        fullMana = -1
        aspd = 0.7
        armor = 20
        mr = 20
        super().__init__(
            "Twisted Fate",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.SPECIALIST,
        )
        self.default_traits = ["Bilgewater", "Quickstriker"]
        self.items.append(buffs.TwistedFateUlt()) # not implemented yet
        self.num_targets = 3
        self.notes = "Any target > 2 gets the 50% reduction. Unfinished."

    # AP: 50, 75, 115
    abilityScaling = create_ability_scaling([0, 0, 0], [33, 50, 75])

    # AP: 70/105/160
    extraAbilityScaling = create_ability_scaling([0, 0, 0], [70, 105, 160], func_name="extraAbilityScaling")



class Yasuo(Champion):
    def __init__(self, level):
        hp = 750
        atk = 45
        curMana = 0
        fullMana = 30
        aspd = 0.8
        armor = 45
        mr = 45
        super().__init__(
            "Yasuo",
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
        self.default_traits = ["Ionia", "Slayer"]
        self.castTime = .5
        self.notes = "Always hits 2 targets"

    # AD: 85, 125, 190  AP: 8, 12, 18
    abilityScaling = create_ability_scaling([85, 125, 190], [8, 12, 18])

    def performAbility(self, opponents, items, time):
        # does not count as auto
        self.multiTargetSpell(
            opponents, items, time, 2, self.abilityScaling, "physical"
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

    # AP: 82/125/195
    abilityScaling = create_ability_scaling([0, 0, 0], [82, 125, 195])

    def performAbility(self, opponents, items, time):
        dmg_instances = 3 if self.numCasts % 3 != 0 else 9
        for i in range(dmg_instances):
            self.multiTargetSpell(
                opponents, items, time, 1, self.abilityScaling, "magical"
            )


class Draven(Champion):
    def __init__(self, level):
        hp= 650
        atk = 53
        curMana = 60
        fullMana = 100
        aspd = .75
        armor = 25
        mr = 25
        super().__init__(
            "Draven",
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
        self.default_traits = ['Noxus', 'Quickstriker']
        self.castTime = 0
        self.axes = 0
        self.items.append(buffs.DravenUlt())
        self.notes = "1.3 second return time."

    # AD: 120/170/290, AP: 10/15/25
    abilityScaling = create_ability_scaling([120, 170, 290], [10, 15, 25])

    def performAbility(self, opponents, items, time):
        # he can only hold 2 axes, but this doesnt rly matter
        if self.axes < 2:
            self.axes += 1     



class Jinx(Champion):
    def __init__(self, level):
        hp = 650
        atk = 50
        curMana = 0
        fullMana = -1
        aspd = 0.75
        armor = 25
        mr = 25
        super().__init__(
            "Jinx",
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
        self.default_traits = ["Zaun", "Gunslinger"]
        self.items.append(buffs.JinxUlt())
        self.auto_threshold = [18, 18, 16]
        self.castTime = 0
        self.manaGainMultiplier.base = 0
        self.notes = ""

    # AD: 65/100/155, AP: 4/6/9
    abilityScaling = create_ability_scaling([65, 100, 155], [4, 6, 9])


class Gwen(Champion):
    def __init__(self, level):
        hp = 800
        atk = 40
        curMana = 0
        fullMana = 30
        aspd = 0.8
        armor = 50
        mr = 50
        super().__init__(
            "Gwen",
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
        self.default_traits = ["ShadowIsles", "Disruptor"]
        self.num_targets = 2
        self.base_snips = 5
        self.castTime = 1.3
        self.notes = ""

    # AP: 45/68/105
    abilityScaling = create_ability_scaling([0, 0, 0], [45, 68, 105])

    # AP: 20/30/50
    extraAbilityScaling = create_ability_scaling([0, 0, 0], [20, 30, 50], func_name="extraAbilityScaling")

    def performAbility(self, opponents, items, time):
        snips = self.base_snips + self.souls // 80
        for i in range(snips):
            self.multiTargetSpell(
                opponents, items, time, 1, self.abilityScaling, "magical"
            )
            if self.num_targets > 1:
                self.multiTargetSpell(
                    opponents, items, time, self.num_targets - 1, self.extraAbilityScaling, "magical"
                )


class Malzahar(Champion):
    def __init__(self, level):
        hp = 550
        atk = 25
        curMana = 0
        fullMana = 35
        aspd = 0.8
        armor = 20
        mr = 20
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
        self.default_traits = ["Void", "Disruptor"]
        self.buff_duration = 15
        self.castTime = .5 # verified
        self.notes = ""

    # AP: 29/43/68
    abilityScaling = create_ability_scaling([0, 0, 0], [29, 43, 68])

    def performAbility(self, opponents, items, time):
        opponents[0].applyStatus(
            status.DoTEffect("Malz bug1 {}".format(self.numCasts)),
            self,
            time,
            self.buff_duration,
            (self.abilityScaling, 1.5),
        )
        opponents[0].applyStatus(
            status.DoTEffect("Malz bug2 {}".format(self.numCasts)),
            self,
            time,
            self.buff_duration,
            (self.abilityScaling, 1.5),
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

    # AD: 100/150/230, AP: 6/10/15
    abilityScaling = create_ability_scaling([100, 150, 230], [6, 10, 15])

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "true"
        )


class Zoe(Champion):
    def __init__(self, level):
        hp = 500
        atk = 35
        curMana = 30
        fullMana = 60
        aspd = 0.8
        armor = 25
        mr = 25
        super().__init__(
            "Zoe",
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
        self.default_traits = []
        self.castTime = 1
        self.notes = "permanent shred"

    # AP: 330/500/700
    abilityScaling = create_ability_scaling([0, 0, 0], [330, 500, 700])

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 2, self.abilityScaling, "magical"
        )



class Leblanc(Champion):
    def __init__(self, level):
        hp = 650
        atk = 35
        curMana = 0
        fullMana = 60
        aspd = 0.75
        armor = 25
        mr = 25
        super().__init__(
            "Leblanc",
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
        self.default_traits = ["Invoker"]
        self.castTime = 1
        self.notes = ""

    # AP: 300/450/700
    abilityScaling = create_ability_scaling([0, 0, 0], [300, 450, 700])

    # AP: 180/270/450
    extraAbilityScaling = create_ability_scaling([0, 0, 0], [180, 270, 450])

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "magical"
        )
        self.multiTargetSpell(
            opponents, items, time, 2, self.extraAbilityScaling, "magical"
        )


class Milio(Champion):
    def __init__(self, level):
        hp = 500
        atk = 30
        curMana = 0
        fullMana = 60
        aspd = 0.75
        armor = 30
        mr = 30
        super().__init__(
            "Milio",
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
        self.default_traits = ["Invoker"]
        self.castTime = 1
        self.num_targets = 2
        self.notes = "does 3 bounces mean 4 enemies hit? num targets is for final bounce"

    # AP: 190/285/445
    abilityScaling = create_ability_scaling([0, 0, 0], [190, 285, 445])

    # AP: 160/240/375
    extraAbilityScaling = create_ability_scaling([0, 0, 0], [160, 240, 375])

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 2, self.abilityScaling, "magical"
        )
        self.multiTargetSpell(
            opponents, items, time, self.num_targets, self.extraAbilityScaling, "magical"
        )


class Kaisa(Champion):
    def __init__(self, level):
        hp = 1000
        atk = 60
        curMana = 20
        fullMana = 60
        aspd = 0.8
        armor = 20
        mr = 20
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
            Role.CASTER,
        )
        self.default_traits = ["Void", "Longshot"]
        self.missiles = [15, 15, 25]
        self.buff_duration = 5
        self.items.append(buffs.KaisaUlt())
        self.ad_version = True
        self.ultActive = False
        self.castTime = 2
        self.notes = ""

    # AD: 39/63/150  AP: 6/9/20
    abilityScaling = create_ability_scaling([39, 63, 150], [6, 9, 20])

    # AP: 60, 90, 500
    empoweredAbilityScaling = create_ability_scaling([0, 0, 0], [60, 90, 500], func_name="empoweredAbilityScaling")

    # AP: 250, 400, 1600
    empoweredAbilityScaling2 = create_ability_scaling([0, 0, 0], [250, 400, 1600], func_name="empoweredAbilityScaling2")

    def performAbility(self, opponents, items, time):
        if self.ad_version:
            for i in range(self.missiles[self.level - 1]):
                self.multiTargetSpell(
                    opponents, items, time, 1, self.abilityScaling, "physical"
                )
        else:
            self.aspd.addStat(20)
            self.applyStatus(status.UltActivator("Kaisa ult"),
                    self, time, self.buff_duration)



class Kalista(Champion):
    def __init__(self, level):
        hp = 800
        atk = 50
        curMana = 20
        fullMana = 65
        aspd = 0.85
        armor = 30
        mr = 30
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
        self.default_traits = ["ShadowIsles", "Vanquisher"]
        self.castTime = 1.5
        self.notes = "No armor shred"

    # AD: 32/48/450, AP: 3/5/15
    def abilityScaling(self, level, AD, AP):
        spears = 20 + self.souls // 25
        base_scaling = create_ability_scaling([32, 48, 450], [3, 5, 15])
        return base_scaling(None, level, AD, AP) * spears

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical"
        )


class Lissandra(Champion):
    def __init__(self, level):
        hp = 500
        atk = 30
        curMana = 0
        fullMana = 80
        aspd = 0.75
        armor = 30
        mr = 30
        super().__init__(
            "Lissandra",
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
        self.castTime = .6
        self.notes = "no chill interaction yet"

    # AP: 275, 415, 2500
    abilityScaling = create_ability_scaling([0, 0, 0], [275, 415, 2500])

    # AP: 415, 625, 2800
    extraAbilityScaling = create_ability_scaling([0, 0, 0], [415, 625, 2800], func_name="extraAbilityScaling")

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "magical"
        )
        self.multiTargetSpell(
            opponents, items, time, 1, self.extraAbilityScaling, "magical"
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

    # AP: 30/45/100
    abilityScaling = create_ability_scaling([0, 0, 0], [30, 45, 100])
    
    # AP: 290/435/1500
    laserAbilityScaling = create_ability_scaling([0, 0, 0], [290, 435, 1500])
    
    # AP: 90/135/800
    laserSecondaryScaling = create_ability_scaling([0, 0, 0], [90, 135, 800])

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


class MissFortuneOld(Champion):
    def __init__(self, level):
        hp = 800
        atk = 55
        curMana = 0
        fullMana = 30
        aspd = 0.75
        armor = 30
        mr = 30
        super().__init__(
            "Miss Fortune (Old)",
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
        self.default_traits = ["Bilgewater", "Gunslinger"]
        self.items.append(buffs.MissFortuneUlt())
        self.castTime = 1
        self.notes = "Bilgewater; add AD / AS as needed. passive not included yet"

    # AD: 145, 220, 3000, AP: 15, 25, 70
    abilityScaling = create_ability_scaling([145, 220, 3000], [15, 25, 70])

    def extraAbilityScaling(self, level, AD, AP):
        return self.abilityScaling(level, AD, AP) * 0.65

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical"
        )
        for i in range(self.numCasts // 3 + 1):
            self.multiTargetSpell(
                opponents, items, time, 1, self.extraAbilityScaling, "physical"
            )


class MissFortune(Champion):
    def __init__(self, level):
        hp = 800
        atk = 55
        curMana = 0
        fullMana = 30
        aspd = 0.75
        armor = 30
        mr = 30
        super().__init__(
            "Miss Fortune",
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
        self.default_traits = ["Bilgewater", "Gunslinger"]
        self.items.append(buffs.MissFortuneUlt())
        self.castTime = 1
        self.notes = "Bilgewater; add AD / AS as needed. passive not included yet"

    # AD: 230, 345, 3000, AP: 15, 25, 70
    abilityScaling = create_ability_scaling([230, 345, 3000], [15, 25, 70])

    def extraAbilityScaling(self, level, AD, AP):
        return self.abilityScaling(level, AD, AP) * 0.4

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical"
        )
        for i in range(self.numCasts // 3 + 1):
            self.multiTargetSpell(
                opponents, items, time, 1, self.extraAbilityScaling, "physical"
            )


class Seraphine(Champion):
    def __init__(self, level):
        hp = 800
        atk = 30
        curMana = 0
        fullMana = 20
        aspd = 0.75
        armor = 30
        mr = 30
        super().__init__(
            "Seraphine",
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
        self.default_traits = ["Piltover", "Disruptor"]
        self.castTime = .7
        self.num_targets = 3
        self.musicNotes = 0
        self.notes = ""

    # AP: 35/55/200
    def abilityScaling(self, level, AD, AP):
        base_scaling = create_ability_scaling([0, 0, 0], [35, 55, 200])
        return base_scaling(None, level, AD, AP) * self.musicNotes

    # AP: 270/405/2200
    extraAbilityScaling = create_ability_scaling([0, 0, 0], [270, 405, 2200])

    def performAbility(self, opponents, items, time):
        if self.musicNotes < 12:
            self.musicNotes += 3
            self.multiTargetSpell(
                opponents, items, time, 1, self.abilityScaling, "magical"
            )
            self.castTime = .7
        else:
            for count in range(self.num_targets):
                self.multiTargetSpell(
                    opponents,
                    items,
                    time,
                    1,
                    lambda x, y, z: 0.7 ** (count) * self.extraAbilityScaling(x, y, z),
                    "magical",
                )
                self.castTime = 1
            self.musicNotes = 0


class Veigar(Champion):
    def __init__(self, level):
        hp = 800
        atk = 33
        curMana = 0
        fullMana = 60
        aspd = 0.75
        armor = 30
        mr = 30
        super().__init__(
            "Veigar",
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
        self.default_traits = ["Yordle", "Arcanist"]
        self.items.append(buffs.VeigarUlt())
        self.num_missiles = [12, 12, 24]
        self.castTime = 1.5

        self.notes = "Edit bonus AP in extra options"

    # AP: 62/93/199
    abilityScaling = create_ability_scaling([0, 0, 0], [62, 93, 199])

    def performAbility(self, opponents, items, time):
        for i in range(self.num_missiles[self.level - 1]):
            self.multiTargetSpell(
                opponents, items, time, 1, self.abilityScaling, "magical"
            )


class Yone(Champion):
    def __init__(self, level):
        hp = 800
        atk = 20
        curMana = 30
        fullMana = 100
        aspd = 0.9
        armor = 60
        mr = 60
        super().__init__(
            "Yone",
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
        self.default_traits = ["Ionia", "Slayer"]
        self.items.append(buffs.YoneUlt())
        self.num_targets = 3
        self.castTime = 1
        self.notes = ""

    # AD: 80/120/800
    def adAutoAbilityScaling(self, level, AD, AP):
        base_scaling = create_ability_scaling([80, 120, 800], [0, 0, 0])
        return base_scaling(None, level, AD, AP)

    # AP: 140/210/1400
    def apAutoAbilityScaling(self, level, AD, AP):
        base_scaling = create_ability_scaling([0, 0, 0], [140, 210, 1400])
        return base_scaling(None, level, AD, AP)

    # AD: 40/60/240, AP: 40/60/240
    def abilityScaling(self, level, AD, AP):
        base_scaling = create_ability_scaling([40, 60, 240], [40, 60, 240])
        return base_scaling(None, level, AD, AP)

    # AD: 160/240/1080, AP: 160/240/1080
    def splitAbilityScaling(self, level, AD, AP):
        base_scaling = create_ability_scaling([160, 240, 1080], [160, 240, 1080])
        return base_scaling(None, level, AD, AP)

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, self.num_targets, self.abilityScaling, "physical"
        )
        self.multiTargetSpell(
            opponents, items, time, self.num_targets, self.abilityScaling, "magical"
        )

        # split portion
        self.multiTargetSpell(
            opponents, items, time, 1, self.splitAbilityScaling, "physical"
        )
        self.multiTargetSpell(
            opponents, items, time, 1, self.splitAbilityScaling, "magical"
        )


class Yunara(Champion):
    def __init__(self, level):
        hp = 800
        atk = 65
        curMana = 0
        fullMana = 50
        aspd = 0.75
        armor = 30
        mr = 30
        super().__init__(
            "Yunara",
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
        self.default_traits = ["Ionia", "Quickstriker"]
        self.items.append(buffs.YunaraUlt())
        self.castTime = 0
        self.manalockDuration = 4
        self.buff_duration = 4
        self.num_targets = 2
        self.ultActive = False
        self.as_ap_scaling = [75, 75, 300]
        self.notes = ""

    # AD: 80/120/425
    abilityScaling = create_ability_scaling([80, 120, 425], [0, 0, 0])

    def performAbility(self, opponents, items, time):
        self.applyStatus(status.ASModifier("Yunara"),
                    self, time, self.buff_duration, self.as_ap_scaling[self.level-1] * self.ap.stat)
        self.applyStatus(status.UltActivator("Yunara ult"),
                         self, time, self.buff_duration)
        

class AurelionSol(Champion):
    def __init__(self, level):
        hp = 1100
        atk = 50
        curMana = 0
        fullMana = 85
        aspd = 0.8
        armor = 40
        mr = 40
        super().__init__(
            "Aurelion Sol",
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
        self.default_traits = ["StarForger"]
        self.stardust = 0
        self.num_targets = 2
        self.castTime = 1
        self.notes = "25 Shockwave: hits num targets + 2. 140 shockwave: hits num targets + 4. 300 shockwave: hits 8 targets."

    # AP: 480/800/5000
    abilityScaling = create_ability_scaling([0, 0, 0], [480, 800, 5000])

    # AP: 100/150/1000
    shockwaveAbilityScaling = create_ability_scaling([0, 0, 0], [100, 150, 1000])

    # AP: 500/750/9999
    meteorAbilityScaling = create_ability_scaling([0, 0, 0], [500, 750, 9999])

    def performAbility(self, opponents, items, time):
        dmgMult = 1
        if self.stardust >= 60:
            dmgMult = 1.15
        
        # star crash
        self.multiTargetSpell(
            opponents, items, time, self.num_targets, lambda x, y, z: self.abilityScaling(x, y, z) * dmgMult, "magical"
        )
        if self.stardust >= 475:
            self.multiTargetSpell(
                opponents, items, time, self.num_targets, lambda x, y, z: self.abilityScaling(x, y, z) * dmgMult * .33, "true"
            )   
        
        # Shockwave
        shockwave_targets = self.num_targets + 2
        if self.stardust >= 140:
            shockwave_targets = self.num_targets + 4
        if self.stardust >= 300:
            shockwave_targets = 8
        if self.stardust >= 25:
            self.multiTargetSpell(
                        opponents, items, time, shockwave_targets, self.shockwaveAbilityScaling, "magical"
            )   

        # Meteor
        if self.stardust >= 750:
            self.multiTargetSpell(
                opponents, items, time, self.num_targets, self.meteorAbilityScaling, "magical"
            )


class Azir(Champion):
    def __init__(self, level):
        hp = 800
        atk = 35
        curMana = 20
        fullMana = 40
        aspd = 0.8
        armor = 30
        mr = 30
        super().__init__(
            "Azir",
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
        self.default_traits = ["Shurima", "Disruptor"]
        self.items.append(buffs.AzirUlt())
        self.castTime = 1
        self.soldiers = 0
        self.soldier_intervals = [-1, -1]
        self.notes = ""

    # AP: 100/150/3000
    abilityScaling = create_ability_scaling([0, 0, 0], [100, 150, 3000])

    # AP: 70/105/5000
    extraAbilityScaling = create_ability_scaling([0, 0, 0], [70, 105, 5000])

    def performAbility(self, opponents, items, time):
        if self.soldiers < 2:
            self.soldier_intervals[self.soldiers] = self.numAttacks + 2
            self.soldiers += 1
            self.multiTargetSpell(
                opponents, items, time, 1, self.abilityScaling, "magical"
            )
        else:
            self.multiTargetSpell(
                opponents, items, time, self.soldiers, self.extraAbilityScaling, "magical"
            )


class BaronNashor(Champion):
    def __init__(self, level):
        hp = 3000
        atk = 120
        curMana = 0
        fullMana = 50
        aspd = 0.5
        armor = 85
        mr = 85
        super().__init__(
            "Baron Nashor",
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
        self.default_traits = ["Void"]
        self.num_targets = 3
        self.items.append(buffs.BaronNashorUlt())
        self.castTime = 3.2
        self.notes = "Autoattacks will hit 2 targets."

    # AD: 250/375/20000, AP: 30/45/500
    abilityScaling = create_ability_scaling([250, 375, 20000], [30, 45, 500])

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, self.num_targets, self.abilityScaling, "physical"
        )

        for i in range(10):
            self.multiTargetSpell(
                opponents, items, time, 1, lambda x, y, z: .5 * self.abilityScaling(x, y, z), "physical"
            )


class THex(Champion):
    def __init__(self, level):
        hp = 1400
        atk = 85
        curMana = 30
        fullMana = 100
        aspd = 0.9
        armor = 70
        mr = 70
        super().__init__(
            "T-Hex",
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
        self.default_traits = ["HexMech", "Piltover", "Gunslinger"]
        self.items.append(buffs.THexUlt())
        self.castTime = 0

        # ult variables
        self.nextDrain = -1
        self.missilesPerTick = 0
        self.firstMissile = False

        self.num_targets = 5
        self.ultActive = False
        self.notes = ""


    # divided by 4 since it procs every .25s
    def abilityScaling(self, level, AD, AP):
        # AD: 145/250/2000, AP: 10/15/150
        base_scaling = create_ability_scaling([145, 250, 2000], [10, 15, 150])
        return base_scaling(None, level, AD, AP) / 4

    # multiplied by 4 since this is based off per-second damage
    def extraAbilityScaling(self, level, AD, AP):
        return self.abilityScaling(level, AD, AP) * .25  * 4

    def performAbility(self, opponents, items, time):
        if not self.ultActive:
            print("Activating THex ult: {}".format(time))

            self.ultActive = True
            self.nextDrain = time
            self.firstMissile = True
            self.nextAttackTime = 9999
            self.missilesPerTick = (4 + self.aspd.stat // 4) / 4
            # self.curMana = self.fullMana.stat # shouldn't proc another cast
            print("mana: {}".format(self.curMana))


class Ziggs(Champion):
    def __init__(self, level):
        hp = 650
        atk = 10
        curMana = 0
        fullMana = 60
        aspd = 0.75
        armor = 25
        mr = 25
        super().__init__(
            "Leblanc",
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
        self.default_traits = ["Invoker"]
        self.castTime = 1
        self.notes = ""

    # AP: 300/450/700
    abilityScaling = create_ability_scaling([0, 0, 0], [300, 450, 700])

    # AP: 180/270/450
    extraAbilityScaling = create_ability_scaling([0, 0, 0], [180, 270, 450])

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "magical"
        )
        self.multiTargetSpell(
            opponents, items, time, 2, self.extraAbilityScaling, "magical"
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
        # Dynamic AP scaling based on self.ap_scale
        base_scaling = create_ability_scaling([0, 0, 0], [self.ap_scale, self.ap_scale, self.ap_scale])
        return base_scaling(None, level, AD, AP)

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

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
    "Jhin",
    "Sona",
    "Viego",
    # 2-cost
    "Bard",
    "Orianna",
    "Teemo",
    "Tristana",
    "TwistedFate",
    # 3-cost
    "Ahri",
    "Draven",
    "Gwen",
    "Jinx",
    "Vayne",
    # 4-cost,
    "Kaisa",
    "Kalista",
    "Lissandra",
    "Lux",
    "MissFortune",
    "Seraphine",
    "Veigar",
    "Yunara",
    # 5-cost
    "THex",
    
]


def create_ability_scaling(ad_values, ap_values):
    """
    Factory function to create ability scaling functions.
    
    Args:
        ad_values: List of 3 AD scaling values [level1, level2, level3]
        ap_values: List of 3 AP scaling values [level1, level2, level3]
    
    Returns:
        A function that calculates ability damage based on level, AD, and AP
    """
    def scaling(_self, level, AD, AP):
        return ap_values[level - 1] * AP + ad_values[level - 1] * AD
    return scaling


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

    # AP: 325/455/650
    abilityScaling = create_ability_scaling([0, 0, 0], [325, 455, 650])

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
        self.castTime = 2.5
        self.notes = ""

    # AD: 475/715/1105, AP: 40/60/100
    abilityScaling = create_ability_scaling([475, 715, 1105], [40, 60, 100])

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical"
        )


class Jhin(Champion):
    def __init__(self, level):
        hp = 444
        atk = 48
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

    # AD: 125, 190, 280  AP: 15, 22, 34
    abilityScaling = create_ability_scaling([125, 190, 280], [15, 22, 34])

    def performAbility(self, opponents, items, time):
        self.ultAutos = 4



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
        # AP: 105/160/240, multiplied by number of meeps
        base_scaling = create_ability_scaling([0, 0, 0], [105, 160, 240])
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
        fullMana = 60
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
    extraAbilityScaling = create_ability_scaling([0, 0, 0], [100, 150, 250])

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

    # AP: 125/185/285
    abilityScaling = create_ability_scaling([0, 0, 0], [125, 185, 285])

    # AP: 30, 45, 70
    dotScaling = create_ability_scaling([0, 0, 0], [30, 45, 70])

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "magical"
        )
        opponents[0].applyStatus(
            status.DoTEffect("Teemo {}".format(self.numCasts)),
            self,
            time,
            self.buff_duration,
            self.dotScaling,
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

    # AD: 250, 375, 565  AP: 30, 45, 70
    abilityScaling = create_ability_scaling([0, 0, 0], [250, 375, 565])

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
        self.notes = "Any target > 2 gets the 50% reduction"

    # AP: 33, 50, 75
    abilityScaling = create_ability_scaling([0, 0, 0], [33, 50, 75])

    # AP: 70/105/160
    extraAbilityScaling = create_ability_scaling([0, 0, 0], [70, 105, 160])



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

    # AP: 85/130/200
    abilityScaling = create_ability_scaling([0, 0, 0], [85, 130, 200])

    def performAbility(self, opponents, items, time):
        dmg_instances = 3 if self.numCasts % 3 != 0 else 9
        for i in range(dmg_instances):
            self.multiTargetSpell(
                opponents, items, time, 1, self.abilityScaling, "magical"
            )


class Draven(Champion):
    def __init__(self, level):
        hp= 650
        atk = 45
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

    # AD: 140/210/350, AP: 10/15/25
    abilityScaling = create_ability_scaling([140, 210, 350], [10, 15, 25])

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

    # AD: 38/57/100, AP: 4/6/9
    abilityScaling = create_ability_scaling([38, 57, 100], [4, 6, 9])


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
    extraAbilityScaling = create_ability_scaling([0, 0, 0], [20, 30, 50])

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


class Kaisa(Champion):
    def __init__(self, level):
        hp = 1000
        atk = 55
        curMana = 0
        fullMana = 70
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
        self.castTime = 1.5
        self.notes = ""

    # AD: 38, 57, 135  AP: 6, 9, 20
    abilityScaling = create_ability_scaling([38, 57, 135], [6, 9, 20])

    # AP: 60, 90, 500
    empoweredAbilityScaling = create_ability_scaling([0, 0, 0], [60, 90, 500])

    # AP: 265, 400, 1600
    empoweredAbilityScaling2 = create_ability_scaling([0, 0, 0], [265, 400, 1600])

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
        fullMana = 70
        aspd = 0.8
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
        self.castTime = 1
        self.notes = "no chill interaction yet"

    # AP: 275, 415, 2500
    abilityScaling = create_ability_scaling([0, 0, 0], [275, 415, 2500])

    # AP: 415, 625, 2800
    abilityScaling2 = create_ability_scaling([0, 0, 0], [415, 625, 2800])

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "magical"
        )
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling2, "magical"
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


class MissFortune(Champion):
    def __init__(self, level):
        hp = 800
        atk = 50
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
        self.castTime = 1
        self.notes = "Bilgewater; add AD / AS as needed"

    # AD: 125, 190, 1000, AP: 15, 25, 70
    abilityScaling = create_ability_scaling([125, 190, 1000], [15, 25, 70])

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
        self.musicNotes = 0
        self.notes = ""

    # AP: 25/40/200
    def abilityScaling(self, level, AD, AP):
        base_scaling = create_ability_scaling([0, 0, 0], [25, 40, 200])
        return base_scaling(None, level, AD, AP) * self.musicNotes

    def extraAbilityScaling(self, level, AD, AP):
        return self.abilityScaling(level, AD, AP) * 0.65

    def performAbility(self, opponents, items, time):
        if self.musicNotes < 12:
            self.musicNotes += 3
            self.multiTargetSpell(
                opponents, items, time, 1, self.abilityScaling, "magical"
            )
        else:
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

    # AP: 60/90/135
    abilityScaling = create_ability_scaling([0, 0, 0], [60, 90, 135])

    def performAbility(self, opponents, items, time):
        for i in range(self.num_missiles[self.level - 1]):
            self.multiTargetSpell(
                opponents, items, time, 1, self.abilityScaling, "magical"
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
        self.buff_duration = 4
        self.num_targets = 2
        self.ultActive = False
        self.as_ap_scaling = [75, 75, 300]
        self.notes = ""

    # AD: 85/130/450
    abilityScaling = create_ability_scaling([85, 130, 450], [0, 0, 0])

    def performAbility(self, opponents, items, time):
        self.applyStatus(status.ASModifier("Yunara"),
                    self, time, self.buff_duration, self.as_ap_scaling[self.level-1] * self.ap.stat)
        self.applyStatus(status.UltActivator("Yunara ult"),
                         self, time, self.buff_duration)


class THex(Champion):
    def __init__(self, level):
        hp = 1400
        atk = 75
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
        # AD: 120/200/2000, AP: 10/15/150
        base_scaling = create_ability_scaling([120, 200, 2000], [10, 15, 150])
        return base_scaling(None, level, AD, AP) / 4

    # multiplied by 4 since this is based off per-second damage
    def extraAbilityScaling(self, level, AD, AP):
        return self.abilityScaling(level, AD, AP) * .3 * 4

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

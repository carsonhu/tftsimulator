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
    "KaiSa",
    "Kayle",
    "KennenHERO",
    "Lucian",
    "Sivir",
    "Syndra",
    "DrMundoHERO",
    "ShenHERO",
    "Jhin",
    "Gangplank",
    "Katarina",
    "Caitlyn",
    "KogMaw",
    "Malzahar",
    "Yasuo",
    "Karma",
    "Ryze",
    "Senna",
    "Smolder",
    "Ashe",
    "Jinx",
    "Samira",
    "Yuumi",
    "Ziggs",
    "Viego",
    "TwistedFate",
]


class Gnar(Champion):
    def __init__(self, level):
        hp = 500
        atk = 50
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
        self.notes = "AS bonus does not reset, care when comparing with other champs"

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
        self.castTime = 0.8
        self.secondaryCastTime = 1.1  # when he has to blink
        self.buff_duration = 5 + self.castTime
        self.aspd_bonus = 25
        self.stat_per_potential = 4
        self.notes = "AS bonus lasts slightly too long with mage in sims"

    def abilityScaling(self, level, AD, AP):
        adScale = [115, 175, 300]
        apScale = [0, 0, 0]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def magicAbilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [230, 350, 600]
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
        adScale = [380, 570, 900]
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
            Role.SPECIALIST,
        )
        self.num_targets = 2
        self.items.append(buffs.KayleUlt())
        self.finalAscent = False
        self.default_traits = ["Duelist"]
        self.manaGainMultiplier.base = 0
        self.notes = "modify level to modify kayle; level 9 wave is 1.5x more targets"

    def passiveAbilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [33, 50, 75]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def waveAbilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [55, 75, 110]
        return apScale[level - 1] * AP + adScale[level - 1] * AD


class KennenHERO(Champion):
    def __init__(self, level):
        hp = 700
        atk = 45
        curMana = 20
        fullMana = 60
        aspd = 0.7
        armor = 40
        mr = 40
        super().__init__(
            "KennenHERO",
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
        self.default_traits = ["SupremeCells", "Sorcerer"]
        self.items.append(buffs.KennenUlt())
        self.num_targets = 2
        self.castTime = 0.5
        self.notes = ""

    def abilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [160, 240, 360]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def passiveAbilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [30, 45, 70]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        for count in range(self.num_targets):
            # technically this is just hitting the 1st guy X times so we'll
            # change it if it matters
            self.multiTargetSpell(
                opponents,
                items,
                time,
                2,
                lambda x, y, z: 0.65 ** (count) * self.abilityScaling(x, y, z),
                "magical",
            )


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
        apScale = [85, 130, 225]
        return (apScale[level - 1] * AP + adScale[level - 1] * AD) * self.projectiles

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items, time, 1, self.abilityScaling, "magical")


class Sivir(Champion):
    def __init__(self, level):
        hp = 450
        atk = 50
        curMana = 0
        fullMana = 50
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
        adScale = [170, 255, 385]
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


class Syndra(Champion):
    def __init__(self, level):
        hp = 450
        atk = 40
        curMana = 0
        fullMana = 30
        aspd = 0.7
        armor = 20
        mr = 20
        super().__init__(
            "Syndra",
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
        self.castTime = 0.6
        self.chaosScaling = 0.06
        self.notes = "No MR shred, gimme a second to code SG in"

    def abilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [215, 325, 485]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def chaosAbilityScaling(self, level, AD, AP):
        return self.abilityScaling(level, AD, AP) * self.chaosScaling

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items, time, 1, self.abilityScaling, "magical")


class DrMundoHERO(Champion):
    def __init__(self, level):
        hp = 800
        atk = 60
        curMana = 30
        fullMana = 60
        aspd = 0.75
        armor = 40
        mr = 40
        super().__init__(
            "DrMundoHERO",
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
        self.default_traits = ["Luchador"]
        self.items.append(buffs.MundoUlt())
        self.num_targets = 2
        self.castTime = 1.3
        self.notes = "Mundo Hero. Num targets is # secondary units hit."

    def passiveAbilityScaling(self, level, AD, bonus_AD, AP):
        # this is for attack scaling
        hpScale = 0.07
        return AD * bonus_AD + self.hp.stat * hpScale

    def abilityScaling(self, level, AD, AP):
        adScale = [140, 210, 330]
        apScale = [0, 0, 0]
        hpScale = 0.3
        return (
            apScale[level - 1] * AP + adScale[level - 1] * AD + self.hp.stat * hpScale
        )

    def splashAbilityScaling(self, level, AD, AP):
        apScale = 0.25
        return self.abilityScaling(level, AD, AP) * apScale * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents,
            items,
            time,
            1,
            self.abilityScaling,
            "physical",
        )
        self.multiTargetSpell(
            opponents,
            items,
            time,
            self.num_targets,
            self.splashAbilityScaling,
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
        self.ultMultiplier = 1
        self.manaGainMultiplier.base = 0
        self.notes = "Wraith not coded yet"

    def abilityScaling(self, level, AD, AP):
        adScale = [190, 285, 440]
        apScale = [30, 45, 70]
        return (apScale[level - 1] * AP + adScale[level - 1] * AD) * self.ultMultiplier


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
        self.castTime = 1
        self.notes = ""

    def abilityScaling(self, level, AD, AP):
        adScale = [285, 430, 775]
        apScale = [0, 0, 0]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical", 1
        )


class Katarina(Champion):
    def __init__(self, level):
        hp = 800
        atk = 35
        curMana = 0
        fullMana = 30
        aspd = 0.75
        armor = 55
        mr = 55
        super().__init__(
            "Katarina",
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
        self.default_traits = ["BattleAcademia", "Executioner"]
        self.potential = 0
        self.num_targets = 2
        self.castTime = 0.7
        self.secondaryCastTime = 1.1
        self.notes = ""

    def abilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [130, 200, 300]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def potentialAbilityScaling(self, level, AD, AP):
        potentialScaling = 0.13
        return self.abilityScaling(level, AD, AP) * potentialScaling * self.potential

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, self.num_targets, self.abilityScaling, "magical"
        )
        if self.potential > 0:
            self.multiTargetSpell(
                opponents,
                items,
                time,
                self.num_targets,
                self.potentialAbilityScaling,
                "magical",
            )


class KaiSa(Champion):
    def __init__(self, level):
        hp = 550
        atk = 45
        curMana = 0
        fullMana = 50
        aspd = 0.7
        armor = 25
        mr = 25
        super().__init__(
            "KaiSa",
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
        self.default_traits = ["SupremeCells", "Duelist"]
        self.projectiles = 8
        self.castTime = 1.5
        self.notes = "Click 'more options' button to set bonus AD"

    def abilityScaling(self, level, AD, AP):
        adScale = [32, 48, 75]
        apScale = [6, 8, 14]
        return (apScale[level - 1] * AP + adScale[level - 1] * AD) * self.projectiles

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical", 2
        )


class ShenHERO(Champion):
    def __init__(self, level):
        hp = 800
        atk = 60
        curMana = 0
        fullMana = 50
        aspd = 0.75
        armor = 55
        mr = 55
        super().__init__(
            "ShenHERO",
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
        self.default_traits = ["Bastion", "Edgelord"]
        self.ultAutos = 0
        self.items.append(buffs.ShenUlt())
        self.manalockDuration = 999
        self.castTime = 0
        self.notes = "Crew not coded; Shen Hero augment"

    def abilityScaling(self, level, AD, AP):
        mrScale = [0.75, 1.15, 1.75]
        apScale = [70, 105, 170]
        return apScale[level - 1] * AP + mrScale[level - 1] * self.mr.stat

    def performAbility(self, opponents, items, time):
        self.ultAutos = 3


class Caitlyn(Champion):
    def __init__(self, level):
        hp = 650
        atk = 55
        curMana = 0
        fullMana = 60
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
        self.default_traits = ["BattleAcademia", "Sniper"]
        self.potential = 0
        self.castTime = 2.5  # semi-verified
        self.notes = ""

    def abilityScaling(self, level, AD, AP):
        adScale = [330, 495, 790]
        apScale = [30, 45, 70]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def secondaryAbilityScaling(self, level, AD, AP):
        adScale = [85, 130, 205]
        apScale = [0, 0, 0]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical", 1
        )
        for i in range(self.potential):
            self.multiTargetSpell(
                opponents,
                items,
                time,
                1,
                self.secondaryAbilityScaling,
                "physical",
            )


class KogMaw(Champion):
    def __init__(self, level):
        hp = 650
        atk = 15
        curMana = 0
        fullMana = 40
        aspd = 0.75
        armor = 30
        mr = 30
        super().__init__(
            "KogMaw",
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
        self.default_traits = ["MonsterTrainer"]
        self.items.append(buffs.KogmawUlt())
        self.nextAutoEnhanced = False
        self.castTime = 0
        self.notes = ""

    def passiveAbilityScaling(self, level, AD, AP):
        apScale = [36, 55, 87]
        adScale = [0, 0, 0]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def abilityScaling(self, level, AD, AP):
        apScale = [55, 85, 130]
        adScale = [0, 0, 0]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.nextAutoEnhanced = True
        if self.trainer_level >= 15:
            self.aspd.addStat(15)


class Malzahar(Champion):
    def __init__(self, level):
        hp = 800
        atk = 40
        curMana = 0
        fullMana = 30
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
        self.castTime = 0.5  # Verified
        self.notes = ""

    def dotScaling(self, level, AD, AP):
        apScale = [515, 775, 1315]
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


class Senna(Champion):
    def __init__(self, level):
        hp = 650
        atk = 55
        curMana = 0
        fullMana = 60
        aspd = 0.75
        armor = 30
        mr = 30
        super().__init__(
            "Senna",
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
        self.default_traits = ["Executioner"]
        self.castTime = 2.4  # semi-verified
        self.notes = "No mana refund"

    def abilityScaling(self, level, AD, AP):
        adScale = [360, 540, 875]
        apScale = [40, 60, 95]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def secondaryAbilityScaling(self, level, AD, AP):
        scale = 0.22
        return scale * self.abilityScaling(level, AD, AP)

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical"
        )
        if self.num_targets > 1:
            self.multiTargetSpell(
                opponents,
                items,
                time,
                self.num_targets - 1,
                self.secondaryAbilityScaling,
                "physical",
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
        self.castTime = 1  # verified
        self.notes = "Smolder passive burn not included"

    def abilityScaling(self, level, AD, AP):
        adScale = [225, 340, 540]
        apScale = [0, 0, 0]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def secondaryAbilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [50, 75, 120]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical", 1
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


class Viego(Champion):
    def __init__(self, level):
        hp = 850
        atk = 30
        curMana = 0
        fullMana = 40
        aspd = 0.9
        armor = 60
        mr = 60
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
        self.default_traits = ["SoulFighter", "Duelist"]
        self.items.append(buffs.ViegoUlt())
        self.ult_phase = 0  # for the ult
        self.manalockDuration = 999
        self.castTime = 0
        self.notes = "not sure how viego's cast time works, temporarily at 0"

    def autoAbilityScaling(self, level, AD, AP):
        # AD scaling is defined in the buff ViegoUlt
        apScale = [30, 45, 80]
        return apScale[level - 1] * AP

    def abilityScaling(self, level, AD, AP):
        # jank as fuck: Ability sets it to 1, and the buff increments it.
        # 1st attack Ult phase is at 2
        # 2nd attack ult phase is at 3
        # 3rd attack ult phase is at 0 to make sure this func isn't called again
        apScale = [0, 0, 0]
        if self.ult_phase == 2 or self.ult_phase == 3:
            apScale = [100, 150, 270]
        elif self.ult_phase == 0:
            apScale = [210, 315, 560]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.ult_phase = 1


class Yasuo(Champion):
    def __init__(self, level):
        hp = 850
        atk = 70
        curMana = 0
        fullMana = 40
        aspd = 0.75
        armor = 60
        mr = 60
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
        self.default_traits = ["Mentor", "Edgelord"]
        self.castTime = 1
        self.notes = "4 mentor not in"

    def abilityScaling(self, level, AD, AP):
        adScale = [180, 270, 430]
        apScale = [0, 0, 0]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 3, self.abilityScaling, "physical"
        )


class Ziggs(Champion):
    def __init__(self, level):
        hp = 650
        atk = 20
        curMana = 0
        fullMana = 90
        aspd = 0.75
        armor = 30
        mr = 30
        super().__init__(
            "Ziggs",
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
        self.default_traits = ["Strategist"]
        self.items.append(buffs.ZiggsUlt())
        self.num_targets = 2
        self.castTime = 0.5
        self.notes = ""

    def autoAbilityScaling(self, level, AD, AP):
        apScale = [50, 75, 120]
        return apScale[level - 1] * AP

    def abilityScaling(self, level, AD, AP):
        apScale = [230, 345, 550]
        return apScale[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, self.num_targets, self.abilityScaling, "magical"
        )


class Ashe(Champion):
    def __init__(self, level):
        hp = 850
        atk = 65
        curMana = 0
        fullMana = 80
        aspd = 0.8
        armor = 35
        mr = 35
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
            Role.MARKSMAN,
        )
        self.items.append(buffs.AsheUlt())
        self.base_projectiles = 8  # special case for bullet hell
        self.projectile_multiplier = 1  # for bullet hell
        self.manalockDuration = 999
        self.default_traits = ["Duelist"]
        self.ultAutos = 0
        self.castTime = 0
        self.notes = ""

    def abilityScaling(self, level, AD, AP):
        adScale = [14, 21, 100]
        apScale = [1, 2, 10]
        num_arrows = round(
            (self.base_projectiles + 4 * ((self.aspd.add + 100) / 125 - 0.8))
            * self.projectile_multiplier
        )
        return (apScale[level - 1] * AP + adScale[level - 1] * AD) * num_arrows

    def performAbility(self, opponents, items, time):
        self.ultAutos = 8


class Jinx(Champion):
    def __init__(self, level):
        hp = 850
        atk = 70
        curMana = 10
        fullMana = 80
        aspd = 0.75
        armor = 35
        mr = 35
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
            Role.CASTER,
        )
        self.default_traits = ["StarGuardian", "Sniper"]
        self.items.append(buffs.JinxUlt())
        self.castTime = 1.25
        self.notes = " "

    def abilityScaling(self, level, AD, AP):
        adScale = [200, 300, 900]
        apScale = [0, 0, 0]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def aoeAbilityScaling(self, level, AD, AP):
        adScale = [575, 875, 4000]
        apScale = [0, 0, 0]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 1, self.abilityScaling, "physical")
        self.multiTargetSpell(
            opponents, items, time, 1, self.aoeAbilityScaling, "physical"
        )


class Karma(Champion):
    def __init__(self, level):
        hp = 850
        atk = 40
        curMana = 0
        fullMana = 65
        aspd = 0.75
        armor = 35
        mr = 35
        super().__init__(
            "Karma",
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
        self.num_targets = 1
        self.castTime = 1.5
        self.cast_ticks = 12
        self.notes = "A lot of things i'm not sure on with karma yet. Cast split into 12 ticks for strikers calculation"

    def abilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [1050, 1575, 6500]
        return (apScale[level - 1] * AP + adScale[level - 1] * AD) / self.cast_ticks

    def performAbility(self, opponents, items, time):
        for _ in range(self.cast_ticks):
            self.multiTargetSpell(
                opponents, items, time, self.num_targets, self.abilityScaling, "magical"
            )


class Ryze(Champion):
    def __init__(self, level):
        hp = 850
        atk = 50
        curMana = 10
        fullMana = 60
        aspd = 0.8
        armor = 35
        mr = 35
        super().__init__(
            "Ryze",
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
        self.default_traits = ["Mentor", "Executioner", "Strategist"]
        self.upgraded = False
        self.num_targets = 2
        self.castTime = 4  # verified
        self.notes = ""

    def abilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [770, 1155, 6000] if not self.upgraded else [800, 1200, 6000]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def secondaryAbilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [110, 165, 1200]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def waveScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [45, 65, 450]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items, time, 1, self.abilityScaling, "magical")
        if self.num_targets > 1:
            self.multiTargetSpell(
                opponents,
                items,
                time,
                self.num_targets - 1,
                self.secondaryAbilityScaling,
                "magical",
            )
        if self.upgraded:
            for i in range(6):
                self.multiTargetSpell(
                    opponents,
                    items,
                    time,
                    1,
                    self.waveScaling,
                    "magical",
                )


class Samira(Champion):
    def __init__(self, level):
        hp = 850
        atk = 50
        curMana = 0
        fullMana = 15
        aspd = 0.75
        armor = 45
        mr = 45
        super().__init__(
            "Samira",
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
        self.default_traits = ["SoulFighter", "Edgelord"]
        self.num_targets = 3
        self.ultAutos = 0
        self.stacks = 0
        self.castTime = 0.5
        self.notes = "Edgelord is coded to give fixed 20% AS."

    def abilityScaling(self, level, AD, AP):
        adScale = [105, 160, 650]
        apScale = [0, 0, 0]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def spinAbilityScaling(self, level, AD, AP):
        adScale = [230, 345, 2200]
        apScale = [50, 75, 225]
        return apScale[level - 1] * AP + adScale[level - 1] * AD

    def performAbility(self, opponents, items, time):
        self.stacks += 1
        if self.stacks == 5:
            self.stacks = 0
            self.castTime = 3
            self.multiTargetSpell(
                opponents,
                items,
                time,
                self.num_targets,
                self.spinAbilityScaling,
                "physical",
                2,
            )
        else:
            self.castTime = 0.5
            self.multiTargetSpell(
                opponents, items, time, 1, self.abilityScaling, "physical", 1
            )


class Yuumi(Champion):
    def __init__(self, level):
        hp = 850
        atk = 40
        curMana = 0
        fullMana = 40
        aspd = 0.75
        armor = 35
        mr = 35
        super().__init__(
            "Yuumi",
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
        self.castTime = 2.4
        self.projectiles = 15
        self.projectile_multiplier = 1
        self.potential = 0
        self.notes = ""

    def abilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [24, 36, 150]
        return (apScale[level - 1] * AP + adScale[level - 1] * AD) * math.ceil(
            self.projectiles * self.projectile_multiplier
        )

    def extraAbilityScaling(self, level, AD, AP):
        adScale = [0, 0, 0]
        apScale = [24, 36, 150]
        potentialScaling = 0.32
        return (
            (apScale[level - 1] * AP + adScale[level - 1] * AD)
            * potentialScaling
            * self.potential
            * math.ceil((self.projectiles // 5) * self.projectile_multiplier)
        )

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(opponents, items, time, 1, self.abilityScaling, "magical")
        if self.potential > 0:
            self.multiTargetSpell(
                opponents, items, time, 1, self.extraAbilityScaling, "true"
            )
        self.projectiles += 5


class TwistedFate(Champion):
    def __init__(self, level):
        hp = 900
        atk = 30
        curMana = 40
        fullMana = 120
        aspd = 0.85
        armor = 40
        mr = 40
        super().__init__(
            "TwistedFate",
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
        self.default_traits = []
        self.items.append(buffs.TwistedFateUlt())
        self.marks = 0
        self.percent_popped_marks = 1
        self.castTime = 1.5
        self.notes = " "

    def autoAbilityScaling(self, level, AD, AP):
        # AD scaling is defined in the buff ViegoUlt
        apScale = [35, 55, 999]
        return apScale[level - 1] * AP

    def abilityScalingPhysical(self, level, AD, AP):
        adScale = [200, 300, 9999]
        return adScale[level - 1] * AD

    def abilityScalingMagical(self, level, AD, AP):
        apScale = [15, 25, 500]
        return apScale[level - 1] * AP * round(self.marks * self.percent_popped_marks)

    def performAbility(self, opponents, items, time):
        self.multiTargetSpell(
            opponents, items, time, 4, self.abilityScalingPhysical, "physical"
        )
        self.multiTargetSpell(
            opponents, items, time, 4, self.abilityScalingMagical, "magical"
        )
        self.marks = 0


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

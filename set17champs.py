import heapq
import math
import random
from collections import deque

import numpy as np
import set17buffs as buffs
from role import Role
from stats import Attack, Stat

import status
from champion import Champion

champ_list = ["Caitlyn", "Ezreal", "Jinx", "Pyke", "MasterYi", "Kaisa", "MissFortuneConduit", "Viktor", "Corki", "Leblanc", "Lissandra", "Nami",
             "Karma", "TwistedFate", "Bard", "Veigar", "Sona", "Vex", "Milio"]

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


class Caitlyn(Champion):
    def __init__(self, level):
        hp = 500
        atk = 65
        curMana = 0
        fullMana = -1
        aspd = 0.55
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
            Role.SPECIALIST,
        )
        self.default_traits = ["NOVA", "Fateweaver"]
        self.items.append(buffs.CaitlynUlt())
        self.notes = "NOVA strike, emblems not active yet."

    # AD: 170/255/510, AP: 20/30/45
    abilityScaling = create_ability_scaling([170, 255, 510], [20, 30, 45])


class Ezreal(Champion):
    def __init__(self, level):
        hp = 450
        atk = 40
        curMana = 0
        fullMana = 30
        aspd = 0.70
        armor = 15
        mr = 15
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
        self.default_traits = ["Timebreaker", "Sniper"]
        self.castTime = 1.0 # 1 second cast time
        
    abilityScaling = create_ability_scaling([160, 240, 365], [14, 21, 32])
    droneScaling = create_ability_scaling([8, 12, 18], [0, 0, 0])

    def performAbility(self, opponents, items, time):
        # Initial hit
        self.multiTargetSpell(opponents, items, time, 1, self.abilityScaling, "physical")
        
        # Drones
        drones = getattr(self, 'takedowns', 0) // 8
        if drones > 0:
            for _ in range(drones):
                self.multiTargetSpell(opponents, items, time, 1, self.droneScaling, "physical")
                

class Jinx(Champion):
    def __init__(self, level):
        hp = 550
        atk = 55
        curMana = 20 # 20/80
        fullMana = 80
        aspd = 0.75
        armor = 20
        mr = 20
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
        self.default_traits = ["Anima", "Challenger"]
        self.castTime = 2.0
        self.notes = "Challenger is 1.25x the given value to account for dash"
    abilityScaling = create_ability_scaling([29, 44, 65], [3, 5, 7])

    def performAbility(self, opponents, items, time):
        # Rockets: 15 + 1 per 35% bonus AS
        num_rockets = 16 + int(self.aspd.add / 35.0)
        
        # Fires num_rockets rockets using multiTargetSpell
        # Counts as 3 attacks (numAttacks=3)
        # Pass numAttacks=3 to the first rocket call
        for i in range(num_rockets):
            na = 3 if i == 0 else 0
            self.multiTargetSpell(opponents, items, time, 1, self.abilityScaling, "physical", numAttacks=na)


class Pyke(Champion):
    def __init__(self, level):
        hp = 700
        atk = 45
        curMana = 0
        fullMana = 40
        aspd = 0.80
        armor = 40
        mr = 40
        super().__init__(
            "Pyke",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.ASSASSIN,
        )
        self.default_traits = ["Psionic", "Voyager"]
        self.castTime = 2.5 # 2.5 second cast time
        self.num_targets = 2
        
    harpoonScaling = create_ability_scaling([0, 0, 0], [60, 90, 135])
    cleaveScaling = create_ability_scaling([240, 360, 720], [0, 0, 0])
    areaScaling = create_ability_scaling([120, 180, 360], [0, 0, 0])

    def performAbility(self, opponents, items, time):
        # 3 parts to ability
        # Harpoon
        self.multiTargetSpell(opponents, items, time, 1, self.harpoonScaling, "physical")
        # Cleave
        self.multiTargetSpell(opponents, items, time, 1, self.cleaveScaling, "physical")
        # Area
        num_hits = getattr(self, 'num_targets', 2)
        self.multiTargetSpell(opponents, items, time, num_hits, self.areaScaling, "physical")


class PsiStrikesStatus(status.Status):
    def __init__(self, name="Psi Strikes", projectionScaling=None):
        super().__init__(name)
        self.projectionScaling = projectionScaling
        self.interval = 0.5
        self.next_proc = 0

    def applicationEffect(self, champion, time, duration, params):
        champion.ultActive = True
        champion.aspd.add += 70
        champion.omnivamp.addStat(0.15)
        # Projections only start 0.5s after the channel is complete
        self.next_proc = time + champion.castTime + self.interval
        return True

    def wearoffEffect(self, champion, time):
        champion.ultActive = False
        champion.aspd.add -= 70
        champion.omnivamp.addStat(-0.15)
        return True

    def update(self, champion, time):
        if self.active and time >= self.next_proc:
            # fire projection
            champion.multiTargetSpell(
                champion.opponents,
                champion.items,
                time,
                1,
                self.projectionScaling,
                "physical",
                numAttacks=0
            )
            self.next_proc += self.interval
        super().update(champion, time)


class PsionicStormStatus(status.Status):
    def __init__(self, name="Psionic Storm", scaling=None, num_targets=2):
        super().__init__(name)
        self.scaling = scaling
        self.num_targets = num_targets
        self.interval = 1.0
        self.next_proc = 0
        self.ticks_remaining = 4

    def applicationEffect(self, champion, time, duration, params):
        self.next_proc = time + 1.0
        self.ticks_remaining = 4
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        self.next_proc = time + 1.0
        self.ticks_remaining = 4
        return True

    def update(self, champion, time):
        if self.active and self.ticks_remaining > 0 and time >= self.next_proc:
            if champion.opponents:
                # 1. Primary target (First opponent in the list)
                champion.multiTargetSpell(
                    [champion.opponents[0]], champion.items, time, 1, self.scaling, "magical"
                )
                
                # 2. Secondary targets (all others up to num_targets)
                num_to_hit = self.num_targets
                if len(champion.opponents) > 1 and num_to_hit > 1:
                    def secondary_scaling(level, bonusAD, AP):
                        return 0.6 * self.scaling(level, bonusAD, AP)
                    
                    champion.multiTargetSpell(
                        champion.opponents[1:num_to_hit], 
                        champion.items, 
                        time, 
                        num_to_hit - 1, 
                        secondary_scaling, 
                        "magical"
                    )
            
            self.ticks_remaining -= 1
            self.next_proc += self.interval
        super().update(champion, time)


class UltraFriendlyObjectStatus(status.Status):
    def __init__(self, name="Ultra Friendly Object", baseScaling=None, splashScaling=None):
        super().__init__(name)
        self.baseScaling = baseScaling
        self.splashScaling = splashScaling
        self.interval = 1.0
        self.next_proc = 0
        self.ticks_remaining = 4

    def applicationEffect(self, champion, time, duration, params):
        self.next_proc = time + 1.0
        self.ticks_remaining = 4
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        self.next_proc = time + 1.0
        self.ticks_remaining = 4
        return True

    def update(self, champion, time):
        if self.active and self.ticks_remaining > 0 and time >= self.next_proc:
            if champion.opponents:
                # Deal damage to primary target: base followed by splash
                champion.multiTargetSpell(
                    [champion.opponents[0]], champion.items, time, 1, self.baseScaling, "magical"
                )
                champion.multiTargetSpell(
                    [champion.opponents[0]], champion.items, time, 1, self.splashScaling, "magical"
                )
            
            self.ticks_remaining -= 1
            self.next_proc += self.interval
        super().update(champion, time)


class MeepBonusStatus(status.Status):
    def __init__(self, name="Meep Bonus", scaling=None):
        super().__init__(name)
        self.scaling = scaling
        self.next_proc = 0

    def applicationEffect(self, champion, time, duration, params):
        meeps = getattr(champion, "meep", 0)
        self.interval = 8 * (1 - 0.1 * meeps)
        self.next_proc = time + self.interval
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        meeps = getattr(champion, "meep", 0)
        self.interval = 8 * (1 - 0.1 * meeps)
        self.next_proc = time + self.interval
        return True

    def update(self, champion, time):
        if self.active and time >= self.next_proc:
            # print(f"DEBUG: Meep Bonus fired at {time}, next_proc was {self.next_proc}, meeps: {getattr(champion, 'meep', 0)}")
            meeps = getattr(champion, "meep", 0)
            if meeps > 0 and champion.opponents:
                # Every 8 seconds (reduced by 10% per meep), launch an Explosive Meep at the target, 
                # dealing 120/180/900 physical damage in a one hex radius on impact.
                # Hits primary target and 1 secondary target (num_targets=2)
                champion.multiTargetSpell(
                    champion.opponents,
                    champion.items,
                    time,
                    2, 
                    self.scaling,
                    "physical"
                )
            self.interval = 8 * (1 - 0.1 * meeps)
            self.next_proc += self.interval
        super().update(champion, time)


class Corki(Champion):
    def __init__(self, level):
        hp = 850
        atk = 45
        curMana = 0
        fullMana = 60
        aspd = 0.80
        armor = 30
        mr = 30
        super().__init__(
            "Corki",
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
        self.default_traits = ["Meeple", "Fateweaver"]
        self.castTime = 4.0
        self.manalockDuration = 3.5
        self.missile_counter = 0

        # Apply Meep Bonus status at start of combat
        self.applyStatus(MeepBonusStatus(scaling=self.meepScaling), self, 0, 999, 0)

    abilityScaling = create_ability_scaling([30, 44, 280], [5, 7, 24], func_name="corkiAbilityScaling")
    standardMissileScaling = abilityScaling
    meepScaling = create_ability_scaling([120, 180, 900], [0, 0, 0], func_name="meepScaling")

    def megaMissileScaling(self, level, AD, AP):
        return 3.5 * self.standardMissileScaling(level, AD, AP)

    def performAbility(self, opponents, items, time):
        p = 0.2
        if getattr(self, "luckyAbility", False):
            # lucky_chance(0.2) = 1 - 0.8^2 = 0.36
            p = 0.36
            
        for _ in range(21):
            is_mega = False
            self.missile_counter += p
            if self.missile_counter >= 1.0:
                is_mega = True
                self.missile_counter -= 1.0
            
            scaling = self.megaMissileScaling if is_mega else self.standardMissileScaling
            self.multiTargetSpell(opponents, items, time, 1, scaling, "physical")


class MasterYi(Champion):
    def __init__(self, level):
        hp = 1100
        atk = 60
        curMana = 30
        fullMana = 70
        aspd = 0.85
        armor = 65
        mr = 65
        super().__init__(
            "Master Yi",
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
        self.default_traits = ["Psionic", "Marauder"]
        self.castTime = 1.0
        self.manalockDuration = 6.0 # 5s active + 1s meditation
        self.attack_counter = 0

    passiveScaling = create_ability_scaling([70, 105, 550], [0, 0, 0])
    projectionScaling = create_ability_scaling([50, 75, 600], [20, 30, 200])

    def startAttack(self, opponents, items, time):
        self.attack_counter += 1
        if self.attack_counter % 3 == 0:
            # bonus physical damage
            self.multiTargetSpell(opponents, items, time, 1, self.passiveScaling, "physical", numAttacks=0)
        super().startAttack(opponents, items, time)

    def performAbility(self, opponents, items, time):
        # 1s meditation + 5s active = 6s duration
        self.applyStatus(PsiStrikesStatus(projectionScaling=self.projectionScaling), self, time, 6, 0)


class Kaisa(Champion):
    def __init__(self, level):
        hp = 650
        atk = 45
        curMana = 0
        fullMana = 50
        aspd = 0.80
        armor = 25
        mr = 25
        super().__init__(
            "Kai'Sa",
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
        self.default_traits = ["Dark Star", "Rogue"]
        self.castTime = 2.0 # 2 second cast time
        
    abilityScaling = create_ability_scaling([36, 54, 86], [4, 6, 10])

    def performAbility(self, opponents, items, time):
        # 16 missiles on primary target
        for _ in range(16):
            self.multiTargetSpell(
                opponents, items, time, 1, self.abilityScaling, "physical"
            )


class MissFortuneConduit(Champion):
    def __init__(self, level):
        hp = 650
        atk = 50
        curMana = 0
        fullMana = 100
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
        self.default_traits = ["Conduit"]
        self.castTime = 3.0
        self.manalockDuration = 2.5

    abilityScaling = create_ability_scaling(
        [72, 108, 173], [10, 15, 25]
    )

    def performAbility(self, opponents, items, time):
        # Hits nearest 2 enemies with a 2.5s burst at the start of the cast
        burst_multiplier = 2.5
        def burst_scaling(level, bonusAD, AP):
            return burst_multiplier * self.abilityScaling(level, bonusAD, AP)

        self.multiTargetSpell(
            opponents, items, time, 2, burst_scaling, "physical"
        )


class Viktor(Champion):
    def __init__(self, level):
        hp = 650
        atk = 30
        curMana = 20
        fullMana = 80
        aspd = 0.80
        armor = 25
        mr = 25
        super().__init__(
            "Viktor",
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
        self.default_traits = ["Psionic", "Conduit"]
        self.castTime = 4.5
        self.manalockDuration = 4.0
        self.num_targets = 3

    abilityScaling = create_ability_scaling([0, 0, 0], [185, 275, 475])

    def performAbility(self, opponents, items, time):
        # 4 damage ticks over 4 seconds, starting 1s after cast starts
        self.applyStatus(
            PsionicStormStatus(
                scaling=self.abilityScaling, num_targets=self.num_targets
            ),
            self,
            time,
            5.0, # duration to cover 4 ticks starting at +1s
            0,
        )


class Leblanc(Champion):
    def __init__(self, level):
        hp = 850
        atk = 0 # passive handles it
        curMana = 0
        fullMana = 40
        aspd = 0.8
        armor = 30
        mr = 30
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
            Role.MARKSMAN,
        )
        self.default_traits = ["Arbiter", "Shepherd"]
        self.castTime = 0.6
        self.manalockDuration = 999
        self.items.append(buffs.LeblancUlt())
        self.activeAttacks = 5
        self.activeAttacksLeft = 0
        self.active = False
        self.notes = ""

    def passiveScaling(self, level, baseAD, AD, AP):
        values = [62, 93, 250]
        return values[level - 1] * AP

    # AP: 25/25/150%
    def cloneScaling(self, level, AD, AP):
        values = [25, 25, 150]
        return values[level - 1] * AP

    # AP: 70/105/750
    def boltScaling(self, level, AD, AP):
        values = [70, 105, 750]
        return values[level - 1] * AP

    def performAbility(self, opponents, items, time):
        self.activeAttacksLeft = self.activeAttacks
        self.active = True
        self.nextAttackTime = time + .01
        return 0


class Karma(Champion):
    def __init__(self, level):
        hp = 850
        atk = 40
        curMana = 0
        fullMana = 55
        aspd = 0.8
        armor = 30
        mr = 30
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
        self.default_traits = ["Dark Star", "Voyager"]
        self.castTime = 2

    abilityScaling = create_ability_scaling(
        [0, 0, 0], [570 / 3, 855 / 3, 5000 / 3], func_name="karmaPrimaryScaling"
    )
    secondaryScaling = create_ability_scaling(
        [0, 0, 0], [120, 180, 1000], func_name="karmaSecondaryScaling"
    )

    def performAbility(self, opponents, items, time):
        # 1. Primary Cast
        # Primary target
        self.multiTargetSpell(opponents, items, time, 3, self.abilityScaling, "magical")

        self.multiTargetSpell(
            opponents,
            items,
            time,
            1,
            self.secondaryScaling,
            "magical",
        )


class Lissandra(Champion):
    def __init__(self, level):
        hp = 450
        atk = 30
        curMana = 0
        fullMana = 30
        aspd = 0.70
        armor = 15
        mr = 15
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
        self.default_traits = ["Dark Star", "Shepherd", "Replicator"]
        self.castTime = 1.5
        self.num_targets = 2

    abilityScaling = create_ability_scaling(
        [0, 0, 0], [250, 375, 600], func_name="lissandraPrimaryScaling"
    )
    secondaryScaling = create_ability_scaling(
        [0, 0, 0], [50, 75, 115], func_name="lissandraSecondaryScaling"
    )

    def performAbility(self, opponents, items, time):
        # 1. Primary Cast
        # Primary target
        self.multiTargetSpell(opponents, items, time, 1, self.abilityScaling, "magical")

        # Secondary targets
        num_secondary = self.num_targets - 1
        if num_secondary > 0 and len(opponents) > 1:
            self.multiTargetSpell(
                opponents[1:],
                items,
                time,
                num_secondary,
                self.secondaryScaling,
                "magical",
            )

        # 2. Replicator Cast
        scaling = getattr(self, "replicator_scaling", 0)
        if scaling > 0:
            def scaled_primary(level, bonusAD, AP):
                return scaling * self.abilityScaling(level, bonusAD, AP)

            def scaled_secondary(level, bonusAD, AP):
                return scaling * self.secondaryScaling(level, bonusAD, AP)

            # Fire another multitargetspell
            self.multiTargetSpell(opponents, items, time, 1, scaled_primary, "magical")
            if num_secondary > 0 and len(opponents) > 1:
                self.multiTargetSpell(
                    opponents[1:],
                    items,
                    time,
                    num_secondary,
                    scaled_secondary,
                    "magical",
                )
        return 0


class Nami(Champion):
    def __init__(self, level):
        hp = 850
        atk = 40
        curMana = 25
        fullMana = 70
        aspd = 0.80
        armor = 30
        mr = 30
        super().__init__(
            "Nami",
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
        self.default_traits = ["Space Groove", "Replicator"]
        self.castTime = 1.0
        self.notes = "TODO: verify whether groove count starts at cast start or cast end"

    abilityScaling = create_ability_scaling(
        [0, 0, 0], [410, 615, 5000], func_name="namiPrimaryScaling"
    )
    secondaryScaling = create_ability_scaling(
        [0, 0, 0], [110, 165, 1000], func_name="namiSecondaryScaling"
    )

    def performAbility(self, opponents, items, time):
        # Apply The Groove
        groove_params = getattr(self, "space_groove_params", {"as_bonus": 0, "ad_ap_tick": 0})
        self.applyStatus(status.TheGrooveStatus(), self, time, 3.0, groove_params)

        # Primary Cast
        if opponents:
            self.multiTargetSpell(opponents, items, time, 1, self.abilityScaling, "magical")

        # Secondary targets: explosion sends 3 globs towards nearby enemies
        num_secondary = 3
        if len(opponents) > 1:
            self.multiTargetSpell(
                opponents[1:],
                items,
                time,
                num_secondary,
                self.secondaryScaling,
                "magical",
            )
            
        # Replicator Cast
        scaling = getattr(self, "replicator_scaling", 0)
        if scaling > 0:
            def scaled_primary(level, bonusAD, AP):
                return scaling * self.abilityScaling(level, bonusAD, AP)

            def scaled_secondary(level, bonusAD, AP):
                return scaling * self.secondaryScaling(level, bonusAD, AP)

            if opponents:
                self.multiTargetSpell(opponents, items, time, 1, scaled_primary, "magical")
                
            if len(opponents) > 1:
                self.multiTargetSpell(
                    opponents[1:],
                    items,
                    time,
                    num_secondary,
                    scaled_secondary,
                    "magical",
                )
        
        return 0


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


class Bard(Champion):
    def __init__(self, level):
        hp = 900
        atk = 30
        curMana = 0
        fullMana = 65
        aspd = 0.85
        armor = 40
        mr = 40
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
        self.default_traits = ["Meeple", "Conduit"]
        self.castTime = 4.5
        self.manalockDuration = 4.5
        self.notes = "30\% bonus dmg to tanks not included"

    abilityScaling = create_ability_scaling([0, 0, 0], [220, 330, 3000], func_name="bardAbilityScaling")
    splashScaling = create_ability_scaling([0, 0, 0], [135, 205, 1500], func_name="bardSplashScaling")
    bardAbilityScaling = abilityScaling
    bardSplashScaling = splashScaling

    def totalScaling(self, level, bonusAD, AP):
        return self.abilityScaling(level, bonusAD, AP) + self.splashScaling(level, bonusAD, AP)

    def performAbility(self, opponents, items, time):
        # 4 damage ticks over 4 seconds, starting 1s after cast starts
        self.applyStatus(
            UltraFriendlyObjectStatus(
                baseScaling=self.abilityScaling,
                splashScaling=self.splashScaling
            ),
            self,
            time,
            5.0, # duration to cover 4 ticks starting at +1s
            0,
        )


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


class TwistedFate(Champion):
    def __init__(self, level):
        hp = 500
        atk = 30
        curMana = 0
        fullMana = 50
        aspd = 0.70
        armor = 15
        mr = 15
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
            Role.CASTER,
        )
        self.default_traits = ["Stargazer", "Fateweaver"]
        self.castTime = 1.0
        self.notes = "Damage is based on expected dice roll value"

    def cardScaling(self, level, bonusAD, AP, roll=5.0):
        min_vals = [190, 285, 430]
        max_vals = [380, 570, 860]

        base_min = min_vals[level - 1]
        base_max = max_vals[level - 1]

        # damage(roll) = min + (roll - 1) * (max - min) / 8
        damage_base = base_min + (roll - 1) * (base_max - base_min) / 8.0
        return damage_base * AP

    def performAbility(self, opponents, items, time):
        # Average roll
        roll = 5.0
        if getattr(self, "luckyAbility", False):
            # Checking twice and taking the better outcome: E[max(X1, X2)] for X ~ U{1..9}
            roll = 175.0 / 27.0  # ~6.48148148

        def tf_scaling(level, bonusAD, AP):
            return self.cardScaling(level, bonusAD, AP, roll=roll)

        self.multiTargetSpell(opponents, items, time, 1, tf_scaling, "magical")
        return 0


class Veigar(Champion):
    def __init__(self, level):
        hp = 500
        atk = 30
        curMana = 10
        fullMana = 50
        aspd = 0.70
        armor = 15
        mr = 15
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
        self.default_traits = ["Meeple", "Replicator"]
        self.castTime = 1.0

    abilityScaling = create_ability_scaling([0, 0, 0], [310, 465, 700])
    miniMeepScaling = create_ability_scaling([0, 0, 0], [31, 47, 70])

    def performAbility(self, opponents, items, time):
        # 1. Main cast
        self.multiTargetSpell(opponents, items, time, 1, self.abilityScaling, "magical")

        # 2. Meep bonus: Fires off if he has meeps
        meeps = getattr(self, "meep", 0)
        for m in range(meeps):
            self.multiTargetSpell(opponents, items, time, 2, self.miniMeepScaling, "magical")

        # 3. Replicator bonus: Duplicates the main cast (not the meep bonus)
        scaling = getattr(self, "replicator_scaling", 0)
        if scaling > 0:
            def scaled_scaling(level, bonusAD, AP):
                return scaling * self.abilityScaling(level, bonusAD, AP)
            self.multiTargetSpell(opponents, items, time, 1, scaled_scaling, "magical")
        
        return 0


class Sona(Champion):
    def __init__(self, level):
        hp = 900
        atk = 35
        curMana = 0
        fullMana = 25
        aspd = 0.90
        armor = 40
        mr = 40
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
        self.default_traits = ["Psionic", "Shepherd"]
        self.castTime = 1.5
        self.manalockDuration = 0.5

    abilityScaling = create_ability_scaling([0, 0, 0], [280, 420, 999], func_name="sonaAbilityScaling")
    ripScaling = create_ability_scaling([0, 0, 0], [120, 180, 999], func_name="sonaRipScaling")
    slamScaling = create_ability_scaling([0, 0, 0], [680, 1050, 9999], func_name="sonaSlamScaling")

    def performAbility(self, opponents, items, time):
        # numCasts is incremented before performAbility is called
        if self.numCasts % 5 != 0:
            # Casts 1-4
            self.castTime = 1.5
            self.manalockDuration = 0.5
            self.multiTargetSpell(opponents, items, time, 1, self.abilityScaling, "magical")
        else:
            # Cast 5
            self.castTime = 2.5
            self.manalockDuration = 1.5
            # Deal rip damage to 4 targets
            self.multiTargetSpell(opponents, items, time, 4, self.ripScaling, "magical")
            # Then deal slam damage to 1 target
            self.multiTargetSpell(opponents, items, time, 1, self.slamScaling, "magical")
        
        return 0


class Vex(Champion):
    def __init__(self, level):
        hp = 900
        atk = 15
        curMana = 0
        fullMana = 60
        aspd = 0.80
        armor = 40
        mr = 40
        super().__init__(
            "Vex",
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
        self.default_traits = ["Doomer"]
        self.castTime = 0
        self.shadow_counter = 0
        self.notes = "Gains 72 AD/AP at start, then 12 AD/AP at 5s and 10s. Shadow doublestrike procs every 5 times shadow attacks."

        # Apply the passive buff via VexUlt item
        self.items.append(buffs.VexUlt())

    passiveScaling = create_ability_scaling([0, 0, 0], [30, 45, 250], func_name="vexPassiveScaling")
    activeScaling = create_ability_scaling([0, 0, 0], [130, 195, 1000], func_name="vexActiveScaling")

    def fireShadowStrike(self, opponents, items, time, scaling):
        if not opponents:
            return

        # Hit 1 target with shadow
        self.multiTargetSpell(opponents, items, time, 1, scaling, "magical")

        # Increment counter
        self.shadow_counter += 1

        # Every 5 hits, strike again
        if self.shadow_counter >= 5:
            self.shadow_counter -= 5
            # Bonus hit uses passive scaling
            self.fireShadowStrike(opponents, items, time, self.passiveScaling)

    def startAttack(self, opponents, items, time):
        # Call base attack
        super().startAttack(opponents, items, time)
        # Trigger passive shadow strike
        self.fireShadowStrike(opponents, items, time, self.passiveScaling)

    def performAbility(self, opponents, items, time):
        # Launch three empowered strikes
        for _ in range(3):
            self.fireShadowStrike(opponents, items, time, self.activeScaling)
        return 0


class Milio(Champion):
    def __init__(self, level):
        hp = 550
        atk = 30
        curMana = 0
        fullMana = 30
        aspd = 0.70
        armor = 20
        mr = 20
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
        self.default_traits = ["Timebreaker", "Fateweaver"]
        self.castTime = 1.0
        self.bounce_counter = 0.0
        self.notes = "Without lucky: 1.64 expected bounces, with lucky: 2.16 expected bounces"

    abilityScaling = create_ability_scaling([0, 0, 0], [255, 380, 575], func_name="milioAbilityScaling")
    bounceScaling = create_ability_scaling([0, 0, 0], [85, 130, 190], func_name="milioBounceScaling")

    def performAbility(self, opponents, items, time):
        # Base expected bounces
        # Without Lucky: 1 + 0.5 + 0.125 + 0.015625 + ... = 1.6416325606551538
        # With Lucky: 2.1649329148705205
        expected_bounces = 1.6416325606551538
        if getattr(self, "luckyAbility", False):
            expected_bounces = 2.1649329148705205

        self.bounce_counter += expected_bounces
        bounces_this_cast = int(self.bounce_counter)
        self.bounce_counter -= bounces_this_cast

        # 1. Primary Cast
        self.multiTargetSpell(opponents, items, time, 1, self.abilityScaling, "magical")

        # 2. Bounces
        for _ in range(bounces_this_cast):
            self.multiTargetSpell(opponents, items, time, 1, self.bounceScaling, "magical")
            
        return 0



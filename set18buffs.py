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
    "Rapidfire",
    "Blossom",
    "Executioner",
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


class Rapidfire(Buff):
    levels = [0, 2, 3, 4, 5]
    display_name = "Rapidfire"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}",
            level,
            params,
            phases=["preCombat", "postAttack"],
        )
        self.per_attack_scaling = {0: 0, 2: 3, 3: 5, 4: 9, 5: 15}
        self.max_stacks = 10
        self.stacks = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            # Team gains 10% Attack Speed
            champion.aspd.addStat(10)
        if phase == "postAttack":
            # Rapidfire champions gain more on every attack, up to 10 stacks
            if self.stacks < self.max_stacks and self._is_rapidfire(champion):
                self.stacks += 1
                champion.aspd.addStat(self.per_attack_scaling[self.level])
        return 0

    def _is_rapidfire(self, champion):
        # A Rapidfire Emblem makes its holder a full trait member too, not
        # just an innate Rapidfire champion (default_traits).
        if "Rapidfire" in getattr(champion, "default_traits", []):
            return True
        return any(getattr(item, "trait", None) == "Rapidfire" for item in champion.items)


class Blossom(Buff):
    levels = [0, 3, 5, 7, 9, 11]
    display_name = "Blossom"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        # "After combat, your Wisps are empowered" and the shop-side Wisp
        # mechanics are out of scope for a combat simulator -- only the
        # AD/AP grant is modeled.
        self.scaling = {0: 0, 3: 12, 5: 30, 7: 45, 9: 60, 11: 100}

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            amt = self.scaling[self.level]
            champion.bonus_ad.addStat(amt)
            champion.ap.addStat(amt)
        return 0


class Executioner(Buff):
    levels = [0, 2, 3, 4]
    display_name = "Executioner"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}",
            level,
            params,
            phases=["preCombat", "PostOnDealDamage"],
        )
        self.crit_bonus = 0.35
        # (2) grants Precision + crit only; bleed starts at (3)
        self.bleed_scaling = {0: 0, 2: 0, 3: 0.30, 4: 0.50}
        self.bleed_duration = 3.0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            if self.level >= 2:
                champion.crit.addStat(self.crit_bonus)
                champion.addPrecision()
        if phase == "PostOnDealDamage":
            bleed_pct = self.bleed_scaling.get(self.level, 0)
            target = champion.lastDamagedOpponent
            if bleed_pct > 0 and target is not None and input_:
                target.applyStatus(
                    status.ExecutionerBleedStatus(),
                    champion,
                    time,
                    self.bleed_duration,
                    input_[0] * bleed_pct,
                )
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

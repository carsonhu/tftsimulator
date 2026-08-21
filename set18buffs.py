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
    "Riftbeast",
    "Summoner",
    "Spellweaver",
    "Adaptor",
    "Ravager",
    "Blackthorn",
]

augments = [
    "Shred30",
    "Shred20",
    "TinyButDeadly",
    "StandUnitedI",
    "Ascension",
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

wisps = [
    "Flow",
    "ProlificPower",
    "UltraAscension",
    "CrystalBall",
    "Hummingbird",
    "Rain",
    "Downpour",
    "TatteredArmor",
    "MarksmensGale",
    "Supercritical",
    "BackrowStar",
]


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

    def extraParameters():
        return {"Title": "Is Rapidfire", "Min": 0, "Max": 1, "Default": 1}

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            # Team gains 10% Attack Speed
            champion.aspd.addStat(10)
        if phase == "postAttack":
            # Rapidfire champions gain more on every attack, up to 10 stacks.
            # extraParams ("Is Rapidfire") == 1 flags this holder as a full
            # trait member rather than just a teammate benefiting from the
            # flat 10% aura.
            if self.stacks < self.max_stacks and self.params == 1:
                self.stacks += 1
                champion.aspd.addStat(self.per_attack_scaling[self.level])
        return 0


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
            # Wisps (below) read this during postPreCombat to decide whether
            # their Blossom-upgraded values apply -- postPreCombat runs after
            # every item's preCombat phase, so it's the earliest point a Wisp
            # can reliably see this regardless of item ordering.
            champion.blossom_level = self.level
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


class Riftbeast(Buff):
    levels = [0, 3, 7]
    display_name = "Riftbeast"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat", "onUpdate"]
        )
        # (5) shop-overrun and (10) +2 team size are meta/shop mechanics,
        # out of scope for a combat simulator -- only (3) and (7) are modeled.
        self.stat_scaling = 5  # AD/AS/AP %
        self.resist_scaling = 3  # Armor/MR
        self.hp_scaling = 50
        self.mana_regen_scaling = 1
        self.interval = 5
        self.next_bonus = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            if self.level >= 3:
                # (3) Alpha Mark grants its holder a champion-specific unique
                # buff. Only the boolean flag is modeled here -- the actual
                # unique buffs (e.g. Mama Beak's Orange Buff armor shred) are
                # unimplemented for now (see set18champs.MamaBeak).
                champion.riftbeast_alpha_mark = True
        elif phase == "onUpdate":
            if self.level >= 7 and time >= self.next_bonus:
                self.next_bonus += self.interval
                champion.bonus_ad.addStat(self.stat_scaling)
                champion.aspd.addStat(self.stat_scaling)
                champion.ap.addStat(self.stat_scaling)
                champion.armor.addStat(self.resist_scaling)
                champion.mr.addStat(self.resist_scaling)
                champion.hp.addStat(self.hp_scaling)
                champion.manaRegen.addStat(self.mana_regen_scaling)
        return 0


class Summoner(Buff):
    levels = [0, 2, 3]
    display_name = "Summoner"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        # Yorick (+30% Health) is unimplemented for now -- Zyra's extra
        # plant attacks and Mama Beak/Azir's +45% Damage are modeled.
        self.zyra_bonus_attacks = {0: 0, 2: 4, 3: 6}
        # (3) improves (2)'s +45% by 50% -> +67.5%, not a flat +45%*2. Same
        # formula for both Mama Beak's Tiny Beaks and Azir's soldiers, so
        # they share this one multiplier.
        self.dmg_mult = {0: 1.0, 2: 1.45, 3: 1 + 0.45 * 1.5}

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.summoner_bonus_attacks = self.zyra_bonus_attacks.get(self.level, 0)
            champion.summoner_dmg_mult = self.dmg_mult.get(self.level, 1.0)
        return 0


class Spellweaver(Buff):
    levels = [0, 2, 4, 6]
    display_name = "Spellweaver"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}",
            level,
            params,
            phases=["preCombat", "postAbility"],
        )
        # The team-wide half doesn't scale with the breakpoint: everyone gets a
        # flat 10 AP at every tier. Only the Spellweavers' own grant scales,
        # and it stacks on top of the aura -- a Spellweaver at (4) holds
        # 10 + 30 = 40, not 30.
        self.team_ap = 10
        # extraParams ("Is Spellweaver") == 1 flags this holder as an actual
        # Spellweaver unit rather than a teammate benefiting from the aura.
        self.spellweaver_ap = {0: 0, 2: 10, 4: 30, 6: 55}
        self.ap_per_cast = {0: 0, 2: 1, 4: 1, 6: 2}

    def extraParameters():
        return {"Title": "Is SWeaver", "Min": 0, "Max": 1, "Default": 1}

    def performAbility(self, phase, time, champion, input_=0):
        is_spellweaver = self.params == 1
        if phase == "preCombat":
            champion.ap.addStat(self.team_ap)
            if is_spellweaver:
                champion.ap.addStat(self.spellweaver_ap.get(self.level, 0))
        elif phase == "postAbility" and is_spellweaver:
            champion.ap.addStat(self.ap_per_cast.get(self.level, 0))
        return 0


def resolveAdaptorVersion(champion):
    """Decide (once) whether an Adaptor unit is on its AD or AP version.

    Cached on the champion so the Adaptor trait's stat grant and the unit's own
    ability can never disagree, whichever of them runs first within
    postPreCombat. The grant can't flip the answer anyway -- it always feeds
    whichever stat is already ahead -- but pinning it keeps that guarantee from
    depending on item ordering.

    Which version an untouched Adaptor starts on is per-unit, not a single
    rule: Gromp and Nidalee tie to AP, Master Yi, Kog'Maw and Akali tie to AD.
    Units advertise it as adaptor_ties_to_ad; anything that doesn't set the
    attribute gets the AD default.
    """
    if not getattr(champion, "adaptor_resolved", False):
        if champion.bonus_ad.stat == champion.ap.stat:
            champion.ad_version = getattr(champion, "adaptor_ties_to_ad", True)
        else:
            champion.ad_version = champion.bonus_ad.stat > champion.ap.stat
        champion.adaptor_resolved = True
    return champion.ad_version


class Adaptor(Buff):
    """Adaptor: gain AP or AD, whichever of the two is already higher.

    The innate half of the trait (which version of the ability an Adaptor
    casts) is handled by AdaptorInnate, which sits on the unit rather than
    here -- an Adaptor unit switches its ability based on its own stats
    whether or not enough Adaptors are fielded to hit a breakpoint.

    Runs on postPreCombat, not preCombat: every other trait/item/augment AD and
    AP grant lands in preCombat, so postPreCombat is the earliest phase where
    the comparison sees final combat-start stats regardless of item order --
    the same reasoning the Wisps use for reading blossom_level.
    """

    levels = [0, 2, 3, 4]
    display_name = "Adaptor"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["postPreCombat"]
        )
        self.scaling = {0: 0, 2: 25, 3: 35, 4: 55}

    def performAbility(self, phase, time, champion, input_=0):
        # No "Is Adaptor" param: unlike Rapidfire/Spellweaver there's no
        # team-wide half of this trait, so only Adaptors ever hold it.
        amount = self.scaling.get(self.level, 0)
        if amount:
            if resolveAdaptorVersion(champion):
                champion.bonus_ad.addStat(amount)
            else:
                champion.ap.addStat(amount)
        return 0


class Ravager(Buff):
    """Ravager: flat bonus damage, multiplicative with damage amplification.

    Ravager-only, like Adaptor -- there's no team-wide half, so no
    "Is Ravager" param.

    The bonus lands on extraDmgMultiplier rather than dmgMultiplier because
    it's a separate multiplier in game: dmgMultiplier is the additive amp pool
    every item and augment feeds (Giant Slayer, Rabadon's, Glass Cannon...),
    and Ravager multiplies against the total of that pool instead of joining
    it. extraDmgMultiplier was unused before this, so nothing else competes
    for the slot -- worth knowing that two sources sharing it WOULD be
    additive with each other, so a second multiplicative amp needs its own
    multiplier rather than this one.

    The "doubled against units below 50% Health" half is not modeled: the
    sim's opponents are damage sponges whose HP the frame loop never
    decrements, so there's no health percentage to threshold on.
    """

    levels = [0, 2, 4, 6]
    display_name = "Ravager"

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )
        self.scaling = {0: 0, 2: 0.12, 4: 0.25, 6: 0.40}
        # Cosmetic here -- omnivamp is tracked and displayed but heals nothing,
        # since nothing in the sim damages the champion being measured.
        self.omnivamp_bonus = 0.10

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preCombat":
            champion.extraDmgMultiplier.addStat(self.scaling.get(self.level, 0))
            champion.omnivamp.addStat(self.omnivamp_bonus)
        return 0


class Blackthorn(Buff):
    """Blackthorn: the ally on the Blackthorn hex is sacrificed before combat.

    Two halves: a flat Health grant, plus the stat package the sacrifice hands
    over. Which package that is depends on its Role, and how big it is depends
    on its Star Level and Cost -- all three read off the champion
    (blackthorn_role/_star/_cost, set by the sidebar's Blackthorn selector),
    like the set-17 Arbiter's cause/effect. The final number is

        base value  x  sacrifice_scaling[cost][star]  x  bonus_scaling[level]

    An empty hex (role "None", the default) is no sacrifice at all, so neither
    half applies.

    A Tank sacrifice (17% Health, 17 Armor/MR) is not modeled: it does nothing
    to a DPS number here, since nothing in the sim damages the champion being
    measured, and sacrificing a Tank is rare enough not to be worth a row.

    The reference bin disagrees with the champion card here: it has (4) at a
    0.25 StatMultiplier and (6) at 350 Health with a whole different effect
    ("the sacrifice doesn't die"), i.e. it is a patch behind. The card's
    175/300/550 and 0%/30%/60% are used instead, per request. The sacrifice
    base values and the star/cost scaling table are not in the bin at all.
    """

    levels = [0, 2, 4, 6]
    display_name = "Blackthorn"

    # Health granted to your whole team.
    team_health = {0: 0, 2: 175, 4: 300, 6: 550}
    # "Bonus is X% stronger" -- multiplies the sacrifice's stats only.
    bonus_scaling = {0: 1.0, 2: 1.0, 4: 1.3, 6: 1.6}

    ROLE_NONE = "None"
    ROLE_MAGIC = "Magic"
    ROLE_ATTACK = "Attack"
    # Roles a sacrifice can actually have. ROLE_NONE is the empty hex -- no
    # sacrifice, so no Health and no stat package, whatever star level and
    # cost are set to. It is a selectable option, not a role, hence the two
    # lists.
    roles = [ROLE_MAGIC, ROLE_ATTACK]
    selectable_roles = [ROLE_NONE, ROLE_MAGIC, ROLE_ATTACK]

    # Sacrifice base values, before either scaling.
    magic_mana_regen = 1.7
    magic_amp = 0.14  # damage amp
    attack_ad = 24  # % AD
    attack_aspd = 12  # % Attack Speed

    star_levels = [1, 2, 3, 4]
    # 0 is the "No Tier" row -- a sacrifice with no cost tier scales at 1.0
    # whatever its star level.
    costs = [1, 2, 3, 4, 5, 0]
    sacrifice_scaling = {
        1: {1: 0.6, 2: 1.0, 3: 1.75, 4: 2.5},
        2: {1: 0.7, 2: 1.4, 3: 2.8, 4: 5.0},
        3: {1: 0.8, 2: 1.8, 3: 3.3, 4: 8.0},
        4: {1: 1.1, 2: 2.25, 3: 50.0, 4: 500.0},
        5: {1: 1.5, 2: 3.0, 3: 100.0, 4: 999.0},
        0: {1: 1.0, 2: 1.0, 3: 1.0, 4: 1.0},
    }
    # Only a 1-cost realistically reaches 3 or 4 stars, so the rest of the
    # table's high-star rows (the 50/500/100/999 placeholders included) are
    # kept as data but never offered. Per request.
    max_star_by_cost = {1: 4}
    default_max_star = 2

    def __init__(self, level, params):
        super().__init__(
            f"{self.display_name} {level}", level, params, phases=["preCombat"]
        )

    @classmethod
    def costLabel(cls, cost):
        return "No Tier" if cost == 0 else f"{cost} cost"

    @classmethod
    def starLabel(cls, star):
        return f"{star}*"

    @classmethod
    def starLevels(cls, cost):
        """Star levels a sacrifice of this cost can actually turn up at."""
        cap = cls.max_star_by_cost.get(cost, cls.default_max_star)
        return [star for star in cls.star_levels if star <= cap]

    def sacrificeScaling(self, champion):
        """Star/cost multiplier for the sacrifice sitting on the hex."""
        cost = getattr(champion, "blackthorn_cost", 1)
        star = getattr(champion, "blackthorn_star", 1)
        return self.sacrifice_scaling.get(cost, {}).get(star, 1.0)

    def performAbility(self, phase, time, champion, input_=0):
        if phase != "preCombat":
            return 0
        role = getattr(champion, "blackthorn_role", self.ROLE_NONE)
        if role == self.ROLE_NONE:
            # Nothing on the hex: no sacrifice, so not even the Health.
            return 0
        champion.hp.addStat(self.team_health.get(self.level, 0))
        scale = self.sacrificeScaling(champion) * self.bonus_scaling.get(self.level, 1.0)
        if role == self.ROLE_ATTACK:
            champion.bonus_ad.addStat(self.attack_ad * scale)
            champion.aspd.addStat(self.attack_aspd * scale)
        else:
            champion.manaRegen.addStat(self.magic_mana_regen * scale)
            champion.dmgMultiplier.addStat(self.magic_amp * scale)
        return 0


# WISPS
#
# Single-copy combat buffs from the Wisp bag (as opposed to the Blossom
# trait's own count-scaled levels above). Several of them get stronger
# values once the holder's Blossom trait is at level 3+ ("blossom_level",
# set by Blossom.performAbility). All of them read that on postPreCombat --
# by the time that phase runs, every item's preCombat phase (including
# Blossom's) has already resolved, so this doesn't depend on item order.


def _is_blossom_upgraded(champion):
    return getattr(champion, "blossom_level", 0) >= 3


class Flow(Buff):
    levels = [1]
    display_name = "Flow"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["postPreCombat"])
        # Unstoppable (CC immunity) is out of scope -- this simulator doesn't
        # model crowd control.
        self.as_bonus = 15
        self.duration = 10
        self.duration_upgraded = 15

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "postPreCombat":
            duration = (
                self.duration_upgraded
                if _is_blossom_upgraded(champion)
                else self.duration
            )
            champion.applyStatus(
                status.ASModifier("Flow"), champion, time, duration, self.as_bonus
            )
        return 0


class ProlificPower(Buff):
    levels = [1]
    display_name = "Prolific Power"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["postPreCombat"])
        self.scaling = 8
        self.scaling_upgraded = 15

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "postPreCombat":
            amt = (
                self.scaling_upgraded
                if _is_blossom_upgraded(champion)
                else self.scaling
            )
            champion.bonus_ad.addStat(amt)
            champion.ap.addStat(amt)
        return 0


class UltraAscension(Buff):
    levels = [1]
    display_name = "Ultra Ascension"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name, level, params, phases=["postPreCombat", "onUpdate"]
        )
        self.dmg_bonus = 3.0
        self.trigger_time = 25
        self.trigger_time_upgraded = 23
        self.next_bonus = None

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "postPreCombat":
            self.next_bonus = (
                self.trigger_time_upgraded
                if _is_blossom_upgraded(champion)
                else self.trigger_time
            )
        elif phase == "onUpdate":
            if self.next_bonus is not None and time >= self.next_bonus:
                self.next_bonus = None
                champion.dmgMultiplier.addStat(self.dmg_bonus)
        return 0


class CrystalBall(Buff):
    levels = [1]
    display_name = "Crystal Ball"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["postPreCombat"])
        # Revealing the next opponent has no effect on a 1v1 combat sim.
        self.as_bonus = 12
        self.as_bonus_upgraded = 18

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "postPreCombat":
            amt = (
                self.as_bonus_upgraded
                if _is_blossom_upgraded(champion)
                else self.as_bonus
            )
            champion.aspd.addStat(amt)
        return 0


class Hummingbird(Buff):
    levels = [1]
    display_name = "Hummingbird"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["postPreCombat"])
        self.as_bonus = 20
        self.as_bonus_upgraded = 35

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "postPreCombat":
            amt = (
                self.as_bonus_upgraded
                if _is_blossom_upgraded(champion)
                else self.as_bonus
            )
            champion.aspd.addStat(amt)
        return 0


class Rain(Buff):
    levels = [1]
    display_name = "Rain"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["postPreCombat"])
        self.mana_regen = 1
        self.mana_regen_upgraded = 2

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "postPreCombat":
            amt = (
                self.mana_regen_upgraded
                if _is_blossom_upgraded(champion)
                else self.mana_regen
            )
            champion.manaRegen.addStat(amt)
        return 0


class Downpour(Buff):
    levels = [1]
    display_name = "Downpour"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["postPreCombat"])
        self.mana_regen = 2
        self.mana_regen_upgraded = 3

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "postPreCombat":
            amt = (
                self.mana_regen_upgraded
                if _is_blossom_upgraded(champion)
                else self.mana_regen
            )
            champion.manaRegen.addStat(amt)
        return 0


class TatteredArmor(Buff):
    levels = [1]
    display_name = "Tattered Armor"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["postPreCombat"])
        # Shred = Armor reduction, Sunder = MR reduction.
        self.shred_mult = 0.7
        self.duration = 10
        self.duration_upgraded = 15

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "postPreCombat":
            duration = (
                self.duration_upgraded
                if _is_blossom_upgraded(champion)
                else self.duration
            )
            for opponent in champion.opponents:
                opponent.applyStatus(
                    status.ArmorReduction("Tattered Armor - Armor"),
                    champion,
                    time,
                    duration,
                    self.shred_mult,
                )
                opponent.applyStatus(
                    status.MRReduction("Tattered Armor - MR"),
                    champion,
                    time,
                    duration,
                    self.shred_mult,
                )
        return 0


class MarksmensGale(Buff):
    levels = [1]
    display_name = "Marksmen's Gale"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name, level, params, phases=["postPreCombat", "postAttack"]
        )
        self.as_per_attack = 3
        self.as_per_attack_upgraded = 5
        # Role can still change during postPreCombat (e.g. Kaisa's ult
        # swapping to ATTACK_MARKSMAN), so this is checked there rather than
        # preCombat, same as the blossom-upgrade check.
        self.is_marksman = False

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "postPreCombat":
            self.is_marksman = champion.role.archetype == "Marksman"
        elif phase == "postAttack" and self.is_marksman:
            amt = (
                self.as_per_attack_upgraded
                if _is_blossom_upgraded(champion)
                else self.as_per_attack
            )
            champion.aspd.addStat(amt)
        return 0


class Supercritical(Buff):
    levels = [1]
    display_name = "Supercritical"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["postPreCombat"])
        # "Allies with Precision" -- Precision is modeled in this simulator
        # as champion.canSpellCrit (set by addPrecision(), see Executioner/
        # JeweledLotusI/II above).
        self.crit_dmg_bonus = 0.25
        self.crit_dmg_bonus_upgraded = 0.40

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "postPreCombat" and champion.canSpellCrit:
            amt = (
                self.crit_dmg_bonus_upgraded
                if _is_blossom_upgraded(champion)
                else self.crit_dmg_bonus
            )
            champion.critDmg.addStat(amt)
        return 0


class BackrowStar(Buff):
    levels = [1]
    display_name = "Backrow Star"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["postPreCombat"])
        # Ignoring the "random back row champion" targeting -- applies
        # directly to the buff holder.
        self.as_bonus = 75
        self.as_bonus_upgraded = 100
        self.duration = 7
        self.duration_upgraded = 8

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "postPreCombat":
            upgraded = _is_blossom_upgraded(champion)
            as_bonus = self.as_bonus_upgraded if upgraded else self.as_bonus
            duration = self.duration_upgraded if upgraded else self.duration
            champion.applyStatus(
                status.ASModifier("Backrow Star"), champion, time, duration, as_bonus
            )
        return 0


# Unit buffs


class AdaptorInnate(Buff):
    """Adaptor's innate: lock in the AD or AP version of the unit's ability.

    Lives on the unit rather than on the Adaptor trait buff so it still fires
    when the trait isn't fielded at all (or sits at level 0) -- an Adaptor's
    ability always adapts, the trait levels only add the stat grant.

    postPreCombat for the same reason as the Adaptor trait: it's the first
    phase where every preCombat AD/AP source has resolved.

    Also applies the base-AD swap for the Adaptors whose two versions don't
    share a base AD (Master Yi 70/15, Akali 40/30). They advertise it as
    ap_base_atk, already star-scaled; units whose versions share a base AD
    just don't set the attribute.
    """

    levels = [1]
    display_name = "Adaptor Innate"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["postPreCombat"])

    def performAbility(self, phase, time, champion, input_=0):
        if not resolveAdaptorVersion(champion) and hasattr(champion, "ap_base_atk"):
            champion.atk.base = champion.ap_base_atk
        return 0


class GrompPurpleBuff(Buff):
    """Gromp's Riftbeast unique buff: every 5s, +25% of his adaptive stat.

    Unlocked by Riftbeast (3)'s Alpha Mark, so this checks the
    riftbeast_alpha_mark flag that Riftbeast.performAbility sets on preCombat
    (which runs before any onUpdate frame) instead of being appended
    conditionally. Which stat it feeds follows the same AD-vs-AP split as the
    ability itself.
    """

    levels = [1]
    display_name = "Purple Buff"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["onUpdate"])
        self.interval = 5.0
        self.amount = 25
        self.next_tick = 5.0

    def performAbility(self, phase, time, champion, input_=0):
        if not getattr(champion, "riftbeast_alpha_mark", False):
            return 0
        if time >= self.next_tick:
            self.next_tick += self.interval
            if getattr(champion, "ad_version", False):
                champion.bonus_ad.addStat(self.amount)
            else:
                champion.ap.addStat(self.amount)
        return 0


class TinyBeaksBuff(Buff):
    levels = [1]
    display_name = "Flock Family"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name, level, params, phases=["postAbility", "postAttack"]
        )
        self.num_beaks = 4
        self.duration = 5
        self.active_until = -1

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "postAbility":
            # Duration scales with AP the same way this file's other
            # ap_values do (ap.stat is ~1.0 at 0 bonus AP), per Mama Beak's
            # card ("5" shown with the AP-scaling droplet icon).
            self.active_until = time + self.duration * champion.ap.stat
        elif phase == "postAttack" and time < self.active_until:
            # Summoner (2)/(3): Tiny Beak damage is boosted +45%/+67.5%.
            mult = getattr(champion, "summoner_dmg_mult", 1.0)

            def scaling(level, AD, AP, mult=mult):
                return mult * champion.beakScaling(level, AD, AP)

            for _ in range(self.num_beaks):
                champion.multiTargetSpell(
                    champion.opponents,
                    champion.items,
                    time,
                    1,
                    scaling,
                    "physical",
                )
        return 0


class AriseBuff(Buff):
    levels = [1]
    display_name = "Arise!"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name,
            level,
            params,
            phases=["postAbility", "preAttack", "postAttack"],
        )
        self.as_bonus = 150
        self.num_soldier_attacks = 6
        self.num_targets = 2
        self.attacks_remaining = 0
        self.active = False

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "postAbility":
            champion.aspd.addStat(self.as_bonus)
            self.attacks_remaining = self.num_soldier_attacks
            self.active = True
            # Manalocked until all num_soldier_attacks land -- pinned far
            # ahead rather than duration-estimated, since the AS gain (and
            # so attack cadence) changes the instant this fires. Unlocked
            # explicitly in postAttack below once the count hits zero.
            champion.manalockTime = time + 9999
        elif phase == "preAttack" and self.active:
            # Replace the attack with a 2-target magic "soldier command",
            # matching how the rest of this file swaps an Attack's
            # scaling/canCrit/attackType from preAttack (see e.g.
            # DravenUlt/JhinUlt) rather than bypassing performAttack.
            input_.canOnHit = True
            input_.canCrit = champion.canSpellCrit
            input_.attackType = "magical"
            # Summoner (2)/(3): soldier damage is boosted +45%/+67.5%.
            mult = getattr(champion, "summoner_dmg_mult", 1.0)
            input_.scaling = (
                ChampionAbilityScaling(champion)
                if mult == 1.0
                else ScaledChampionAbilityScaling(champion, mult)
            )
            input_.numTargets = self.num_targets
        elif phase == "postAttack" and self.active:
            # Runs after performAttack's own mana-gen check for this same
            # attack, so ending Arise here (rather than in preAttack) means
            # the 6th empowered attack still generates no mana and only the
            # 7th (first normal attack after) does.
            self.attacks_remaining -= 1
            if self.attacks_remaining <= 0:
                self.active = False
                champion.aspd.addStat(-self.as_bonus)
                champion.manalockTime = time
                # startAttack() (caller of performAttack, still on the
                # stack above this hook) does
                # `attack_progress = max(0.0, attack_progress - 1.0)`
                # right after this returns, carrying any overshoot past
                # 1.0 into the next swing's timer -- that overshoot was
                # accrued while still under the +150% AS, in the frames
                # leading up to this attack. Clamping to 1.0 here (instead
                # of leaving the accrued value, which can be >1.0) zeroes
                # that carryover out so the wait for the 7th attack starts
                # fresh, fully under normal AS with no leftover head start.
                champion.attack_progress = min(champion.attack_progress, 1.0)
        return 0


class CaitlynHeadshotBuff(Buff):
    levels = [1]
    display_name = "Headshot"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["preAttack"])
        self.attack_count = 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preAttack" and input_.regularAuto:
            self.attack_count += 1
            if self.attack_count % 3 == 0:
                input_.scaling = ChampionAbilityScaling(champion)
                input_.canCrit = champion.canSpellCrit
        return input_


class MasterYiUlt(Buff):
    """Wuju Style: every third attack is a Double Strike that hits twice.

    Not a real cast -- Master Yi is built with fullMana=-1 (canCast() is never
    true), so the whole passive lives here, counting attacks the same way
    CaitlynHeadshotBuff does.

    The two hits are the auto itself plus one replay of it (queued in
    preAttack, fired in postAttack so it lands after the original), and each
    Adaptor version then gets its own per-hit rider:
      AP: bonus magic damage per hit (the heal off it isn't modeled -- nothing
          in the sim damages the champion being measured).
      AD: stacking AS per hit -- a flat 12% plus 3% that scales with AP, i.e.
          the 15% the card shows at Master Yi's 100 base AP.

    The AP version's much weaker base AD (15 instead of 70) is applied by
    AdaptorInnate, not here.
    """

    levels = [1]
    display_name = "Wuju Style"

    def __init__(self, level=1, params=0):
        super().__init__(
            self.display_name,
            level,
            params,
            phases=["preAttack", "postAttack"],
        )
        self.attack_count = 0
        self.attacks_per_strike = 3
        self.hits_per_strike = 2
        # AD version, per Double Strike hit: 12% AS flat + 3% AP-scaled.
        self.as_per_hit = 12
        self.as_per_hit_scaling = 3
        # Set in preAttack, consumed in postAttack; the Attack object it holds
        # is created fresh per performAttack, so replaying it can't outlive the
        # swing it belongs to.
        self.pending_strike = None

    def performAbility(self, phase, time, champion, input_=0):
        if phase == "preAttack" and input_.regularAuto:
            self.attack_count += 1
            if self.attack_count % self.attacks_per_strike == 0:
                # Every other item's preAttack has already run (champion.items
                # sit last in the simulator's list), so this is the finished
                # attack -- replaying it in postAttack repeats it exactly.
                self.pending_strike = input_
        elif phase == "postAttack" and self.pending_strike is not None:
            attack = self.pending_strike
            self.pending_strike = None
            # Second hit. doAttack, not performAttack: a Double Strike is one
            # attack that lands twice, so this must not re-enter preAttack
            # (which would advance the count) or generate mana.
            champion.doAttack(attack, champion.items, time)
            if champion.ad_version:
                champion.aspd.addStat(
                    self.hits_per_strike
                    * (self.as_per_hit + self.as_per_hit_scaling * champion.ap.stat)
                )
            else:
                for _ in range(self.hits_per_strike):
                    champion.multiTargetSpell(
                        champion.opponents,
                        champion.items,
                        time,
                        1,
                        champion.abilityScaling,
                        "magical",
                    )
        return input_


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


class ClockworkAccelerator(Buff):
    levels = [1]
    display_name = "Clockwork Accelerator"

    def __init__(self, level=1, params=0):
        super().__init__(self.display_name, level, params, phases=["onUpdate"])
        self.asBonus = 10
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
                # After 12 seconds, increase to 3 (so add 2 more)
                champion.manaRegen.addStat(2)
                self.stage_2_active = True
        return 0

from role import Role

import status
from champion import Champion
from set18buffs import (
    AdaptorInnate,
    AriseBuff,
    CaitlynHeadshotBuff,
    GrompPurpleBuff,
    MasterYiUlt,
    TinyBeaksBuff,
)

champ_list = [
    "Varus",
    "Yunara",
    "LeBlanc",
    "MamaBeak",
    "Cassiopeia",
    "Zyra",
    "Azir",
    "Caitlyn",
    "Ahri",
    "Gromp",
    "Karma",
    "MasterYi",
    "Akali",
    "Ezreal",
    "Warwick",
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
        base_scaling = create_ability_scaling(
            [0, 0, 0], [self.ap_scale, self.ap_scale, self.ap_scale]
        )
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


class Varus(Champion):
    def __init__(self, level):
        hp = 500
        atk = 40
        curMana = 30
        fullMana = 120
        aspd = 0.7
        armor = 25
        mr = 25
        super().__init__(
            "Varus",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.ATTACK_CASTER,
        )
        self.default_traits = ["Rapidfire"]
        self.castTime = 2.0
        self.num_targets = 2

    abilityScaling = create_ability_scaling([350, 525, 790], [30, 45, 70])

    def performAbility(self, opponents, items, time):
        # Piercing Arrow: hits the first num_targets enemies in line; damage is
        # reduced by 40% for each enemy already pierced (minimum 40% of base).
        pierce_multiplier = 1.0
        for opponent in opponents[: self.num_targets]:
            mult = pierce_multiplier

            def pierce_scaling(level, AD, AP, mult=mult):
                return mult * self.abilityScaling(level, AD, AP)

            self.multiTargetSpell([opponent], items, time, 1, pierce_scaling, "physical")
            pierce_multiplier = max(0.4, pierce_multiplier * 0.6)


class Yunara(Champion):
    def __init__(self, level):
        hp = 550
        atk = 42
        curMana = 0
        fullMana = 35
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
            Role.ATTACK_CASTER,
        )
        self.default_traits = ["Blossom", "Executioner"]
        # Full dash + orb-throw duration: maps directly to the real
        # cast-trigger-to-next-attack gap (no separate windup on top -- see
        # champion.py's post-cast attack_progress reset). Measured ~1.27-1.49s
        # for near-zero-distance dashes and ~1.8s for a full-board dash;
        # 1.8s assumes medium/long dashes are the common case. Revisit if
        # short dashes turn out to be more frequent in practice.
        self.castTime = 1.8

    abilityScaling = create_ability_scaling([170, 255, 400], [10, 15, 25])
    splash_ratio = 0.35
    splash_targets = 2

    def performAbility(self, opponents, items, time):
        # Cultivation of Spirit: dash, then launch an orb dealing physical
        # damage to the current target, splitting 35% of that damage to
        # splash_targets nearby enemies. Always 1 main target + 2 splash --
        # not user-adjustable, so no num_targets/num_extra_targets here.
        # numAttacks=1 on the main hit makes the cast count as an attack for
        # on-attack effects (e.g. Rapidfire's per-attack AS stacking),
        # without a redundant basic-attack hit or extra manaPerAttack
        # generation (the cast's own mana reset already handles that).
        if not opponents:
            return
        self.multiTargetSpell(
            opponents[:1], items, time, 1, self.abilityScaling, "physical", numAttacks=1
        )

        def splash_scaling(level, AD, AP):
            return self.splash_ratio * self.abilityScaling(level, AD, AP)

        self.multiTargetSpell(
            opponents[1:], items, time, self.splash_targets, splash_scaling, "physical"
        )


class LeBlanc(Champion):
    def __init__(self, level):
        hp = 550
        atk = 30
        curMana = 0
        fullMana = 40
        aspd = 0.7
        armor = 30
        mr = 30
        super().__init__(
            "LeBlanc",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.MAGIC_CASTER,
        )
        self.default_traits = ["Elderwood", "Spellweaver"]
        # Measured directly off video frames in 2026-08-04 14-01-14.mkv:
        # mana hits 0 (cast start) at 05:34.166, next attack-windup twirl
        # starts at 05:35.266 -- a 1.1s raw gap, with the extra ~0.1s inside
        # attack-windup/frame-rounding slop rather than the cast itself.
        # Matches the standard 1.0s TFT mage cast time. Supersedes the
        # earlier 1.2s estimate from 5fps OCR sampling (see
        # verify_leblanc_mana.py) -- that was undersampled, this is exact.
        self.castTime = 1.0
        self.num_targets = 2

    abilityScaling = create_ability_scaling([0, 0, 0], [250, 375, 565])
    splashScaling = create_ability_scaling(
        [0, 0, 0], [85, 130, 190], func_name="splashScaling"
    )

    def performAbility(self, opponents, items, time):
        # Mirror Image: full damage to current target, reduced damage to
        # num_targets-1 adjacent enemies. Passive (ally clone on takedown)
        # ignored per request -- board-composition dependent, out of scope.
        if not opponents:
            return
        self.multiTargetSpell(opponents[:1], items, time, 1, self.abilityScaling, "magical")
        self.multiTargetSpell(
            opponents[1:], items, time, self.num_targets - 1, self.splashScaling, "magical"
        )


class MamaBeak(Champion):
    def __init__(self, level):
        hp = 650
        atk = 60
        curMana = 30
        fullMana = 70
        aspd = 0.75
        armor = 35
        mr = 35
        super().__init__(
            "Mama Beak",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.ATTACK_MARKSMAN,
        )
        self.default_traits = ["Riftbeast", "Summoner", "Rapidfire"]
        # Tentative, needs investigating.
        self.castTime = 0
        # Always-on (not an opt-in buff-bar selection): every attack while
        # active summons Tiny Beak hits, which is core to her kit rather
        # than a togglable ultimate.
        self.items.append(TinyBeaksBuff())

    beakScaling = create_ability_scaling([25, 38, 60], [0, 0, 0], func_name="beakScaling")

    def performAbility(self, opponents, items, time):
        # Flock Family: the cast itself deals no damage -- it just opens the
        # Tiny Beaks window, handled by TinyBeaksBuff (see __init__) via
        # postAbility/postAttack. Riftbeast's Orange Buff (armor shred on
        # physical damage) is unimplemented for now.
        return 0


class Cassiopeia(Champion):
    def __init__(self, level):
        hp = 650
        atk = 30
        curMana = 0
        fullMana = 30
        aspd = 0.75
        armor = 35
        mr = 35
        super().__init__(
            "Cassiopeia",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.MAGIC_CASTER,
        )
        # Coven ignored per request.
        self.default_traits = ["Spellweaver"]
        self.castTime = 1
        self.poison_duration = 15

    abilityScaling = create_ability_scaling([0, 0, 0], [400, 600, 960])

    def performAbility(self, opponents, items, time):
        # Noxious Blast: poison target 1 and target 2 for total magic damage
        # over poison_duration, ticking once per second. Real ability picks
        # "nearest non-poisoned enemy" for the 2nd target; per request this
        # always uses opponents[1] instead. Poisons stack, so each cast gets
        # its own uniquely named status (see CassiopeiaPoisonStatus) rather
        # than refreshing/replacing whatever's already ticking.
        total_damage = self.abilityScaling(self.level, self.bonus_ad.stat, self.ap.stat)
        for i, opponent in enumerate(opponents[:2]):
            opponent.applyStatus(
                status.CassiopeiaPoisonStatus(
                    f"Cassiopeia Poison {id(self)} {self.numCasts} {i}"
                ),
                self,
                time,
                self.poison_duration,
                total_damage,
            )


class Zyra(Champion):
    def __init__(self, level):
        hp = 850
        atk = 40
        curMana = 0
        fullMana = 45
        aspd = 0.75
        armor = 40
        mr = 40
        super().__init__(
            "Zyra",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.MAGIC_CASTER,
        )
        self.default_traits = ["Thornmaiden", "Summoner"]
        # Measured from 2026-08-04 14-01-14.mkv, t=715-736s: 5/5 clean
        # cast-reset-to-next-attack gaps all landed at exactly 1.2s (no
        # variance), overriding the 1.0s tentative guess. Frame-perfect
        # verification (like LeBlanc got) would sharpen this further.
        self.castTime = 1.2
        self.num_plants = 2
        self.plant_attacks = 10
        self.plant_interval = 0.8

    plantScaling = create_ability_scaling([0, 0, 0], [33, 50, 225], func_name="plantScaling")

    def performAbility(self, opponents, items, time):
        # Rampant Growth: spawn num_plants plants, each independently
        # attacking the caster's current first target every plant_interval
        # seconds for plant_attacks hits (+ Summoner's bonus, see
        # set18buffs.Summoner). Modeled as self-applied ticking statuses
        # (DoTEffect-style: the caster deals damage to its own current
        # first target each tick) rather than tracking plants as separate
        # entities.
        total_attacks = self.plant_attacks + getattr(self, "summoner_bonus_attacks", 0)
        duration = self.plant_interval * total_attacks + self.plant_interval
        for i in range(self.num_plants):
            self.applyStatus(
                status.ZyraPlantStatus(f"Zyra Plant {id(self)} {self.numCasts} {i}"),
                self,
                time,
                duration,
                (self.plantScaling, self.plant_interval, total_attacks),
            )


class Azir(Champion):
    def __init__(self, level):
        hp = 650
        atk = 30
        curMana = 0
        fullMana = 35
        aspd = 0.75
        armor = 35
        mr = 35
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
            Role.MAGIC_MARKSMAN,
        )
        self.default_traits = ["Blackthorn", "Executioner", "Summoner"]
        self.castTime = 0.5
        self.items.append(AriseBuff())

    abilityScaling = create_ability_scaling([0, 0, 0], [48, 72, 115])

    def performAbility(self, opponents, items, time):
        # Arise!: no direct cast damage -- AriseBuff (see __init__) handles
        # the AS gain, the manalock-until-6-attacks gate, and replacing the
        # next 6 attacks with 2-target magic soldier commands.
        return 0


class Caitlyn(Champion):
    def __init__(self, level):
        hp = 550
        atk = 50
        curMana = 0
        # -1 disables casting entirely (canCast() requires fullMana.stat >
        # -1) -- her 3rd attack is a passive attack replacement, not a real
        # spell cast, per request.
        fullMana = -1
        aspd = 0.7
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
            Role.ATTACK_SPECIALIST,
        )
        # Coven ignored per request.
        self.default_traits = ["Hunter"]
        self.items.append(CaitlynHeadshotBuff())

    # Physical damage row: 190/285/450 AD-scaled + 20/30/45 AP-scaled.
    abilityScaling = create_ability_scaling([190, 285, 450], [20, 30, 45])

    def performAbility(self, opponents, items, time):
        # Never actually called -- fullMana=-1 keeps canCast() False.
        # Headshot triggers off attack count (CaitlynHeadshotBuff, see
        # __init__), not mana.
        return 0


class Ahri(Champion):
    def __init__(self, level):
        hp = 850
        atk = 40
        curMana = 20
        fullMana = 100
        aspd = 0.8
        armor = 40
        mr = 40
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
            Role.MAGIC_CASTER,
        )
        self.default_traits = ["Blossom", "Spellweaver"]
        # Measured from 2026-08-04 14-01-14.mkv, t=872-911s: 7/7 clean
        # cast-reset-to-next-attack gaps all landed at exactly 1.8s (no
        # variance) -- matches the tentative guess exactly.
        self.castTime = 1.8
        self.num_targets = 5

    abilityScaling = create_ability_scaling([0, 0, 0], [485, 735, 3500])

    def performAbility(self, opponents, items, time):
        # Spirit Bomb: 1 target at the epicenter (full damage), the next 2
        # at -20%, everyone else at -40% -- including any beyond the base
        # 5 (overflow just extends the -40% ring). Fewer than num_targets
        # enemies truncates this list from the end (outermost ring drops
        # first), which falls out naturally from only iterating over
        # however many opponents actually exist.
        for i, opponent in enumerate(opponents[: self.num_targets]):
            if i == 0:
                mult = 1.0
            elif i <= 2:
                mult = 0.8
            else:
                mult = 0.6

            def scaling(level, AD, AP, mult=mult):
                return mult * self.abilityScaling(level, AD, AP)

            self.multiTargetSpell([opponent], items, time, 1, scaling, "magical")


class Gromp(Champion):
    def __init__(self, level):
        hp = 550
        atk = 45
        curMana = 0
        fullMana = 45
        aspd = 0.7
        armor = 30
        mr = 30
        super().__init__(
            "Gromp",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.MAGIC_CASTER,
        )
        self.default_traits = ["Riftbeast", "Adaptor"]
        self.castTime = 1
        self.num_targets = 2
        self.splash_duration = 3
        # Set at combat start by AdaptorInnate; True = the physical version.
        self.ad_version = False
        self.adaptor_resolved = False
        # Gromp is one of the two Adaptors (with Nidalee) that starts on its
        # AP version when nothing has pushed either stat ahead.
        self.adaptor_ties_to_ad = False
        # Always-on rather than opt-in buff-bar picks: Belchy Bubble adapts
        # on every Gromp, and the Purple Buff no-ops on its own unless
        # Riftbeast (3) has set the Alpha Mark flag.
        self.items.append(AdaptorInnate())
        self.items.append(GrompPurpleBuff())
        self.notes = "Defaults AP"

    # AP version: burst on the current target, 3s splash DoT on the rest.
    apAbilityScaling = create_ability_scaling(
        [0, 0, 0], [225, 340, 535], func_name="apAbilityScaling"
    )
    apSplashScaling = create_ability_scaling(
        [0, 0, 0], [145, 220, 345], func_name="apSplashScaling"
    )
    # AD version: burst on the current target, instant splash on the rest.
    adAbilityScaling = create_ability_scaling(
        [305, 460, 725], [30, 45, 70], func_name="adAbilityScaling"
    )
    adSplashScaling = create_ability_scaling(
        [100, 150, 240], [0, 0, 0], func_name="adSplashScaling"
    )

    def performAbility(self, opponents, items, time):
        # Belchy Bubble: full damage to the current target, splash to
        # num_targets-1 enemies within a hex of the explosion. Which of the
        # two versions fires was pinned at combat start by AdaptorInnate.
        if not opponents:
            return 0
        num_splash = self.num_targets - 1
        if self.ad_version:
            self.multiTargetSpell(
                opponents[:1], items, time, 1, self.adAbilityScaling, "physical"
            )
            self.multiTargetSpell(
                opponents[1:], items, time, num_splash, self.adSplashScaling, "physical"
            )
        else:
            self.multiTargetSpell(
                opponents[:1], items, time, 1, self.apAbilityScaling, "magical"
            )
            # Splash is a DoT, so it goes out as a status on each victim
            # (see status.GrompBubbleStatus) rather than an instant hit.
            total = self.apSplashScaling(self.level, self.bonus_ad.stat, self.ap.stat)
            # multiTargetSpell would have applied these to an instant hit;
            # applied here so the two versions' splash amps stay comparable.
            total *= self.dmgMultiplier.stat * self.extraDmgMultiplier.stat
            for opponent in opponents[1 : 1 + num_splash]:
                opponent.applyStatus(
                    status.GrompBubbleStatus(),
                    self,
                    time,
                    self.splash_duration,
                    total,
                )
        return 0


class Karma(Champion):
    def __init__(self, level):
        hp = 500
        atk = 25
        curMana = 0
        fullMana = 40
        aspd = 0.7
        armor = 25
        mr = 25
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
            Role.MAGIC_CASTER,
        )
        self.default_traits = ["Blossom", "Spellweaver"]
        # Per request. Longer than the 1.5s tether, so a recast can never
        # land while the previous tether is still ticking.
        self.castTime = 3.0
        self.num_targets = 2
        self.tether_duration = 1.5
        self.tether_interval = 0.5

    tetherScaling = create_ability_scaling(
        [0, 0, 0], [280, 420, 630], func_name="tetherScaling"
    )
    burstScaling = create_ability_scaling(
        [0, 0, 0], [120, 180, 270], func_name="burstScaling"
    )

    def performAbility(self, opponents, items, time):
        # Karmic Bond: tether the current target for tether_duration, dealing
        # the tether total to it alone in even ticks, then burst on it and
        # the enemies within a hex -- num_targets counts the tethered target
        # itself, so the default 2 is "target + 1 neighbour". The tether and
        # the delayed burst both live in KarmaTetherStatus (see status.py).
        if not opponents:
            return 0
        ticks = max(1, round(self.tether_duration / self.tether_interval))
        opponents[0].applyStatus(
            # Unique per cast, like Cassiopeia's poison: refreshing a shared
            # status would drop a burst that hadn't fired yet if castTime
            # were ever lowered below the tether's duration.
            status.KarmaTetherStatus(f"Karma Tether {id(self)} {self.numCasts}"),
            self,
            time,
            self.tether_duration,
            (
                self.tetherScaling,
                self.tether_interval,
                ticks,
                self.burstScaling,
                self.num_targets,
            ),
        )
        return 0


class MasterYi(Champion):
    # The AD version's base AD; the AP version is a much weaker autoattacker.
    AD_VERSION_ATK = 70
    AP_VERSION_ATK = 15

    def __init__(self, level):
        hp = 850
        atk = self.AD_VERSION_ATK
        curMana = 0
        # -1 disables casting entirely (canCast() requires fullMana.stat >
        # -1) -- the third-attack Double Strike is a passive, not a cast, so
        # it lives in MasterYiUlt instead.
        fullMana = -1
        aspd = 0.8
        armor = 60
        mr = 60
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
            Role.ATTACK_SPECIALIST,
        )
        self.default_traits = ["Blossom", "Adaptor"]
        # Base AD to switch to if the AP version wins the Adaptor comparison.
        # Scaled off self.atk.base so the star-level multiplier Champion
        # already applied carries over instead of being re-derived here.
        self.ap_base_atk = self.atk.base * self.AP_VERSION_ATK / self.AD_VERSION_ATK
        # Set at combat start by AdaptorInnate; True = the physical version,
        # which is also where an untouched one lands (unlike Gromp).
        self.ad_version = False
        self.adaptor_resolved = False
        self.adaptor_ties_to_ad = True
        self.items.append(AdaptorInnate())
        self.items.append(MasterYiUlt())

    # AP version: bonus magic damage on each of the two Double Strike hits.
    abilityScaling = create_ability_scaling([0, 0, 0], [155, 235, 375])

    def performAbility(self, opponents, items, time):
        # Never actually called -- fullMana=-1 keeps canCast() False. Wuju
        # Style triggers off attack count (MasterYiUlt, see __init__).
        return 0


class Akali(Champion):
    # The AD version's base AD; the AP version trades 10 of it away.
    AD_VERSION_ATK = 40
    AP_VERSION_ATK = 30

    def __init__(self, level):
        hp = 650
        atk = self.AD_VERSION_ATK
        curMana = 0
        fullMana = 30
        aspd = 0.75
        armor = 35
        mr = 35
        super().__init__(
            "Akali",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.ATTACK_FIGHTER,
        )
        # Inferno isn't in the buff list yet, so it isn't preselected.
        self.default_traits = ["Adaptor", "Ravager"]
        # Guess: Kunai Strike is still a bin placeholder (its 0.25s is the
        # unauthored-spell template default, shared by every other unauthored
        # set-18 spell), so this uses the 1.0s the set's other single-target
        # casters measured out at.
        self.castTime = 1.0
        # Base AD to switch to if the AP version wins the Adaptor comparison.
        # Scaled off self.atk.base so the star-level multiplier Champion
        # already applied carries over instead of being re-derived here.
        self.ap_base_atk = self.atk.base * self.AP_VERSION_ATK / self.AD_VERSION_ATK
        # Set at combat start by AdaptorInnate; True = the physical version,
        # which is also where an untouched one lands (unlike Gromp).
        self.ad_version = False
        self.adaptor_resolved = False
        self.adaptor_ties_to_ad = True
        self.items.append(AdaptorInnate())
        # Inferno's Burn is what makes a target Burning, and Inferno is
        # unimplemented, so the AD version's Burning rider is assumed live
        # rather than driven by it. Flip this off to price the dry case.
        self.assume_burning = True

    # AD version, assuming Burning: 145/220/345 AD + 10/15/25 AP for the
    # volley, plus 35/52/80 AD for the Burning rider. Kept as separate rows
    # (as the card shows them) but summed into one damage instance -- same
    # target, same damage type, so splitting would only double-count spell
    # crit rolls.
    adAbilityScaling = create_ability_scaling(
        [145, 220, 345], [10, 15, 25], func_name="adAbilityScaling"
    )
    adBurningScaling = create_ability_scaling(
        [35, 52, 80], [0, 0, 0], func_name="adBurningScaling"
    )
    # AP version: pure AP, no AD row on the card.
    apAbilityScaling = create_ability_scaling(
        [0, 0, 0], [140, 210, 340], func_name="apAbilityScaling"
    )
    # "Increased by if they're a Tank" -- the exact number isn't published, so
    # per request this is a flat 1.5x against a Tank-archetype target.
    ap_tank_multiplier = 1.5

    def performAbility(self, opponents, items, time):
        # Kunai Strike: single target either way. Which of the two versions
        # fires was pinned at combat start by AdaptorInnate.
        if not opponents:
            return 0
        if self.ad_version:
            burning = self.assume_burning

            def ad_scaling(level, AD, AP, burning=burning):
                total = self.adAbilityScaling(level, AD, AP)
                if burning:
                    total += self.adBurningScaling(level, AD, AP)
                return total

            self.multiTargetSpell(
                opponents[:1], items, time, 1, ad_scaling, "physical"
            )
        else:
            # The ChampionSelector's enemy is a DummyTank, so this is the
            # normal case there rather than the exception.
            mult = (
                self.ap_tank_multiplier
                if opponents[0].role.archetype == "Tank"
                else 1.0
            )

            def ap_scaling(level, AD, AP, mult=mult):
                return mult * self.apAbilityScaling(level, AD, AP)

            self.multiTargetSpell(
                opponents[:1], items, time, 1, ap_scaling, "magical"
            )
        return 0


class Ezreal(Champion):
    # Forest's Flurry: three blinks, then a piercing blast on the fourth cast.
    blink_cast_time = 1.0
    blast_cast_time = 2.25
    casts_per_blast = 4

    def __init__(self, level):
        hp = 850
        atk = 45
        curMana = 0
        fullMana = 30
        aspd = 0.75
        armor = 40
        mr = 40
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
            Role.ATTACK_CASTER,
        )
        self.default_traits = ["Elderwood", "Executioner"]
        # Swapped to blast_cast_time on the blast cast itself (see
        # performAbility) -- update() reads castTime after performAbility
        # returns, so setting it there applies to the cast that just fired.
        self.castTime = self.blink_cast_time
        # Enemies the blast passes through, per request.
        self.num_targets = 4
        # Running total of the Attack Speed handed out by the blinks, so the
        # blast can hand exactly that much back.
        self.natures_wrath_aspd = 0.0

    abilityScaling = create_ability_scaling([235, 355, 1200], [0, 0, 0])
    blastScaling = create_ability_scaling(
        [385, 580, 2500], [0, 0, 0], func_name="blastScaling"
    )
    # Attack Speed per blink at 100 AP; scaled by the AP ratio at cast time.
    aspd_per_blink = [25, 25, 100]
    # The blast loses 25% of its damage per enemy pierced, floored at 50%.
    # Multiplicative per enemy, matching Varus's Piercing Arrow.
    blast_falloff = 0.75
    blast_minimum = 0.5

    def performAbility(self, opponents, items, time):
        if not opponents:
            return 0
        # numCasts is incremented before performAbility runs, so this is the
        # 1-indexed number of the cast being fired.
        if self.numCasts % self.casts_per_blast == 0:
            self.castTime = self.blast_cast_time
            # Blast through the largest group of enemies, damage reduced for
            # each one already pierced.
            pierce_multiplier = 1.0
            for opponent in opponents[: self.num_targets]:
                mult = pierce_multiplier

                def pierce_scaling(level, AD, AP, mult=mult):
                    return mult * self.blastScaling(level, AD, AP)

                self.multiTargetSpell(
                    [opponent], items, time, 1, pierce_scaling, "physical"
                )
                pierce_multiplier = max(
                    self.blast_minimum, pierce_multiplier * self.blast_falloff
                )
            # The blast consumes the Attack Speed the blinks granted.
            self.aspd.addStat(-self.natures_wrath_aspd)
            self.natures_wrath_aspd = 0.0
        else:
            self.castTime = self.blink_cast_time
            self.multiTargetSpell(
                opponents[:1], items, time, 1, self.abilityScaling, "physical"
            )
            gained = self.aspd_per_blink[self.level - 1] * self.ap.stat
            self.aspd.addStat(gained)
            self.natures_wrath_aspd += gained
        return 0


class Warwick(Champion):
    def __init__(self, level):
        hp = 750
        atk = 40
        curMana = 0
        fullMana = 40
        aspd = 0.75
        armor = 45
        mr = 45
        super().__init__(
            "Warwick",
            hp,
            atk,
            curMana,
            fullMana,
            aspd,
            armor,
            mr,
            level,
            Role.ATTACK_FIGHTER,
        )
        self.default_traits = ["Blackthorn", "Ravager"]
        self.castTime = 1.0  # per request

    abilityScaling = create_ability_scaling([200, 300, 450], [0, 0, 0])
    # Flat on the card -- the only AP-scaled number on it is the heal.
    aspd_per_cast = 20

    def performAbility(self, opponents, items, time):
        # Bite the current target, then keep the Attack Speed for good.
        if not opponents:
            return 0
        self.multiTargetSpell(
            opponents[:1], items, time, 1, self.abilityScaling, "physical"
        )
        self.aspd.addStat(self.aspd_per_cast)
        return 0

from role import Role

from champion import Champion

champ_list = [
    "Varus",
    "Yunara",
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
        baseDmg = self.abilityScaling(self.level, self.bonus_ad.stat, self.ap.stat)
        baseCritDmg = baseDmg
        if self.canSpellCrit:
            baseCritDmg *= self.critDamage()
        critChance = self.crit.stat if self.canSpellCrit else 0

        pierce_multiplier = 1.0
        for opponent in opponents[: self.num_targets]:
            dmgMult = (
                pierce_multiplier * self.dmgMultiplier.stat * self.extraDmgMultiplier.stat
            )
            self.doDamage(
                opponent,
                items,
                critChance,
                baseCritDmg * dmgMult,
                baseDmg * dmgMult,
                "physical",
                time,
                is_spell=True,
            )
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
        self.num_targets = 1
        self.num_extra_targets = 2

    abilityScaling = create_ability_scaling([170, 255, 400], [10, 15, 25])
    splash_ratio = 0.35

    def performAbility(self, opponents, items, time):
        # Cultivation of Spirit: dash, then launch an orb dealing physical
        # damage to the current target, splitting 35% of that damage to
        # num_extra_targets nearby enemies.
        if not opponents:
            return
        baseDmg = self.abilityScaling(self.level, self.bonus_ad.stat, self.ap.stat)
        baseCritDmg = baseDmg
        if self.canSpellCrit:
            baseCritDmg *= self.critDamage()
        critChance = self.crit.stat if self.canSpellCrit else 0
        dmgMult = self.dmgMultiplier.stat * self.extraDmgMultiplier.stat

        self.doDamage(
            opponents[0],
            items,
            critChance,
            baseCritDmg * dmgMult,
            baseDmg * dmgMult,
            "physical",
            time,
            is_spell=True,
        )
        splash_dmg = baseDmg * dmgMult * self.splash_ratio
        splash_crit_dmg = baseCritDmg * dmgMult * self.splash_ratio
        for opponent in opponents[1 : 1 + self.num_extra_targets]:
            self.doDamage(
                opponent,
                items,
                critChance,
                splash_crit_dmg,
                splash_dmg,
                "physical",
                time,
                is_spell=True,
            )

        # The cast itself counts as an attack for on-attack effects (e.g.
        # Rapidfire's per-attack AS stacking), per design -- just the
        # attack-accounting side effects, not a redundant basic-attack hit
        # or extra manaPerAttack generation (the cast's own mana reset
        # below already handles that).
        self.numAttacks += 1
        for item in items:
            item.ability("postAttack", time, self)

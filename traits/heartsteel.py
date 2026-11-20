"""The Heartsteel trait."""
from registry import register
from traits.base import BuildTrait, pct


@register("trait")
class Heartsteel(BuildTrait):
    """Heartsteel (DA_Heartsteel19): "(1) Heartsteel members grant your team bonuses. (3) Choose a Bias, empowering
    their Ability. (5) Choose a 2nd Bias. (7) Heartsteel champions gain an additional 150% of active Heartsteel
    bonuses." (B21)

    GA_Heartsteel19_BonusManager tags the army with <Name>Active for each member fielded (one bonus however many
    copies), and the (1) tier gives every ally (TFTAddAllAlliesTargetRule) each active member's SelflessBonus, Channel1:
    Kayn AttackDamage + KaynAD (7%), Alune AbilityPower + AluneAP (7%), Aphelios AttackSpeed x (1 + ApheliosAS (6%)),
    Ezreal CritChance + EzrealCritChance (10%); Sett, K'Sante, Yone and Sona give HP, armor/MR, omnivamp and healing,
    which change nothing against dummies. The (7) tier gives Heartsteel members each active member's StanBonus as well:
    the row x StanPercentIncrease (1.5 at level 4). Ezreal's StanBonus reads the plain 10% (DamageAmpCalc1, not
    TrueDamageCalc1); the owner ruled (2026-11-17) to follow the tooltip, +15%. The (3) and (5) tiers give a member
    chosen as Bias the SpellUpgradeTierIsActive + Selected tags its spell checks (`champion.heartsteel_bias`, e.g.
    Ezreal). The two (7) tiers are the same level with and without the Prismatic quest; its car is not modelled.

    Which members are fielded, and whether this unit is a Bias, are tick boxes (the parameter's bits). A unit always
    counts itself as fielded.
    """
    KEY = "DA_Heartsteel19"
    display_name = "Heartsteel"
    # tick box -> (champion, curve row, attribute, op); the row is the bonus: + v, or MultiplyAdditive (1 + v)
    MEMBERS = [
        ("Kayn", "DA_Kayn19", "KaynAD", "AttackDamage", "+"),
        ("Alune", "DA_Alune19", "AluneAP", "AbilityPower", "+"),
        ("Aphelios", "DA_Aphelios19", "ApheliosAS", "AttackSpeed", "MultiplyAdditive"),
        ("Ezreal", "DA_Ezreal19", "EzrealCritChance", "CritChance", "+"),
    ]
    BIAS = len(MEMBERS)  # the bit after the members

    @staticmethod
    def extraParameters():
        names = [m[0] for m in Heartsteel.MEMBERS] + ["Bias"]
        # default: Ezreal fielded and a Bias (the one Heartsteel champion implemented)
        return {"Title": "Fielded", "Min": 0, "Max": 2 ** len(names) - 1, "Default": (1 << 3) | (1 << Heartsteel.BIAS),
                "Flags": names, "TeamFlags": len(Heartsteel.MEMBERS)}

    def applyStats(self, champion):
        if getattr(champion, "trait_tiers", None) is None:
            champion.trait_tiers = {}
        # trait level = distinct breakpoints reached: (7) is level 4 with or without its Prismatic quest
        champion.trait_tiers[self.KEY] = sum(1 for t in self.levels[1:] if self.level >= t)
        tier = champion.trait_tier(self.KEY)
        champion.heartsteel_bias = False
        if tier == 0:
            return
        member = self.KEY in (champion.data.d.get("trait_keys") or [])
        stan = champion.trait_value(self.KEY, "StanPercentIncrease") if member else 0
        fielded = [m for bit, m in enumerate(self.MEMBERS)
                   if (self.params >> bit) & 1 or getattr(champion, "KEY", None) == m[1]]
        bias = member and tier >= 2 and bool((self.params >> self.BIAS) & 1)
        # Big Solo / Small Squad (augments/combat.py): an extra share of the bonuses
        extra = sum(i.heartsteel_extra(champion, bias, len(fielded)) for i in getattr(champion, "items", None) or []
                    if getattr(i, "level", 0) and hasattr(i, "heartsteel_extra"))
        for name, key, row, attr, op in fielded:
            v = champion.trait_value(self.KEY, row) * (1 + stan + extra)
            champion.attribute(attr).modify(op, 1 + v if op == "MultiplyAdditive" else v)
        champion.heartsteel_bias = member and tier >= 2 and bool((self.params >> self.BIAS) & 1)

    # Levels whose effect differs (owner, 2026-11-19): (1)-(5) differ only in whether a Bias can be chosen (3+; a
    # 2nd Bias is another unit), (7) adds StanPercentIncrease. So 0, 3 (a Bias, no 150%) and 7 cover them.
    SWEEP_LEVELS = (0, 3, 7)
    BIAS_LEVEL = 3

    @classmethod
    def sweep_rows(cls, level, params, member, champ_key=None):
        """[(level, params, label)]: the table rows worth running from this setup.

        A member (the buff bar, Trait tab): the other levels of SWEEP_LEVELS; the Bias ticked or not (at the level,
        or (3) below it); each other member fielded or not. A non-member (Team Traits): each member fielded or not;
        the level changes nothing for them.
        """
        params = int(params or 0)
        name = cls.display_name
        rows = []
        if member:
            rows += [(lvl, params, f"{name} {lvl}") for lvl in cls.SWEEP_LEVELS if lvl != level]
            bias_at = level if level >= cls.BIAS_LEVEL else cls.BIAS_LEVEL
            flipped = params ^ (1 << cls.BIAS)
            rows.append((bias_at, flipped, f"{name} {bias_at} ({'Bias' if flipped >> cls.BIAS & 1 else 'No Bias'})"))
        member_level = level or next(lvl for lvl in cls.levels if lvl)
        for bit, (unit, key, *_rest) in enumerate(cls.MEMBERS):
            if key == champ_key:
                continue  # a unit always counts itself as fielded
            flipped = params ^ (1 << bit)
            sign = "+" if flipped >> bit & 1 else "-"
            label = f"{name} {member_level} ({sign}{unit})" if member else f"{name} ({sign}{unit})"
            rows.append((member_level if member else level or member_level, flipped, label))
        return rows

    @classmethod
    def team_card(cls, build):
        t = build.trait(cls.KEY)
        tags = {"AttackDamage": "AD", "AbilityPower": "AP", "AttackSpeed": "AS", "CritChance": "CritChance"}
        return {"text": "Each Heartsteel member you field grants your team a bonus (once, however many copies):",
                "rows": [{"label": f"{name}:", "stats": [[pct(t.row(row, col=1)), tags[attr]]]}
                         for name, key, row, attr, op in cls.MEMBERS]}


Heartsteel.levels = [0] + sorted(set(Heartsteel.breakpoints()))

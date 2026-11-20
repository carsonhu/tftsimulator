"""The Beach Pop trait."""
from registry import register
from timing import ticks_up
from traits.base import BuildTrait


@register("trait")
class BeachPop(BuildTrait):
    """Beach Pop (DA_OceanSong19): "Gain placeable instruments that empower adjacent allies. Empowered allies
    regenerate 2% Health every 3 seconds. Empowered Beach Pop champions gain Attack Speed and also regenerate Mana
    every 3 seconds." CT_OceanSong19 by trait level 1-3: AttackSpeed (20/35/35%), ManaRegen (5/8/8), RegenEveryXSeconds
    (3), OceanBreezeAfterXSeconds (10), OceanBreezeMana (0/0/40).

    The build's tier list is a placeholder (threshold 0), so the units each tier needs are not in the data; they are
    the game's tooltip (VOD5 2:14, owner): (3) 1 Instrument; 20% AS, 5 mana, (5) 2 Instruments; 35% AS, 8 mana,
    (7) AND every 10 seconds an ocean breeze (BREAKPOINTS). The page's level is units on the board, as for every
    trait. Every Beach Pop member is taken as empowered, next to an instrument (owner, 2026-11-20: no toggle).
    Empowered members: AttackSpeed MultiplyAdditive + AttackSpeed (the instrument's effect, as the text says) and
    GA_Oceansong19_HealthRegenHandler: WaitDelay(RegenEveryXSeconds), then TickRegen: ManaRegen mana (and a heal,
    nothing against dummies), repeating: +5/8/8 mana at 3, 6, 9, ... s. Level 3 (GA_Oceansong19_7Piece_ManaAndHeal):
    a looping K2_SetTimerDelegate(OceanBreezeAfterXSeconds) gives Beach Pop units OceanBreezeMana (40) every 10 s
    (and a heal). Instrument uniques (Rainstick, Maracas, ...) are augment content, not modelled.
    """
    KEY = "DA_OceanSong19"
    display_name = "Beach Pop"
    team_trait = False
    BREAKPOINTS = [3, 5, 7]  # the tooltip (VOD5 2:14); the build's tier list is a placeholder
    levels = [0, 3, 5, 7]
    REPEATS = 99

    def __init__(self, level=0, params=0):
        super().__init__(level, params, phases=["preCombat"])

    INSTRUMENTS = {3: "1 Instrument", 5: "2 Instruments"}  # the tooltip (VOD5 2:14)

    @classmethod
    def card_tiers(cls, build):
        """The card's breakpoints: the build's tier list is a placeholder ("Placeholder so validation lets me chuck it
        in"), so they are the tooltip's (VOD5 2:14) with the build's numbers (owner, 2026-11-20)."""
        t = build.trait(cls.KEY)
        tiers = []
        for col, threshold in enumerate(cls.BREAKPOINTS, start=1):
            if t.row("OceanBreezeMana", col=col):
                text = (f"({threshold}) AND every {t.row('OceanBreezeAfterXSeconds', col=col):g} seconds, an ocean "
                        f"breeze gives Beach Pop champions {t.row('OceanBreezeMana', col=col):g} Mana and heals them")
            else:
                text = (f"({threshold}) {cls.INSTRUMENTS[threshold]}; {t.row('AttackSpeed', col=col) * 100:g}%AS, "
                        f"{t.row('ManaRegen', col=col):g} Mana")
            tiers.append({"threshold": threshold, "text": text})
        return tiers

    def applyStats(self, champion):
        tiers = getattr(champion, "trait_tiers", None)
        if tiers is None:
            tiers = champion.trait_tiers = {}
        tiers[self.KEY] = sum(int(self.level) >= b for b in self.BREAKPOINTS)  # the tooltip's breakpoints
        if self.level and self._empowered_member(champion):
            champion.aspd.modify("MultiplyAdditive", 1 + champion.trait_value(self.KEY, "AttackSpeed"))

    def _empowered_member(self, champion):
        return champion.has_trait(self.KEY)  # every member is empowered (owner, 2026-11-20)

    def performAbility(self, phase, time, champion, input_=0):
        if not self.level or not champion.has_trait(self.KEY):
            return input_
        if self._empowered_member(champion):
            every, mana = champion.trait_value(self.KEY, "RegenEveryXSeconds"), champion.trait_value(self.KEY, "ManaRegen")
            for k in range(1, self.REPEATS):
                champion.schedule_tick(champion.tick + ticks_up(k * every), lambda: champion.addMana(mana))
        breeze = champion.trait_value(self.KEY, "OceanBreezeMana")
        if breeze:
            every = champion.trait_value(self.KEY, "OceanBreezeAfterXSeconds")
            for k in range(1, self.REPEATS):
                champion.schedule_tick(champion.tick + ticks_up(k * every), lambda: champion.addMana(breeze))
        return input_

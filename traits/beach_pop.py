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

    The build's tier list is a placeholder (threshold 0), so the units each level needs are not in the data: the
    page's level here IS the trait level (1-3; the game's panel shows the first at 3 units). Whether the simulated
    unit stands next to an instrument is the parameter (default: yes).
    Empowered members: AttackSpeed MultiplyAdditive + AttackSpeed (the instrument's effect, as the text says) and
    GA_Oceansong19_HealthRegenHandler: WaitDelay(RegenEveryXSeconds), then TickRegen: ManaRegen mana (and a heal,
    nothing against dummies), repeating: +5/8/8 mana at 3, 6, 9, ... s. Level 3 (GA_Oceansong19_7Piece_ManaAndHeal):
    a looping K2_SetTimerDelegate(OceanBreezeAfterXSeconds) gives Beach Pop units OceanBreezeMana (40) every 10 s
    (and a heal). Instrument uniques (Rainstick, Maracas, ...) are augment content, not modelled.
    """
    KEY = "DA_OceanSong19"
    display_name = "Beach Pop"
    team_trait = False
    levels = [0, 1, 2, 3]
    PLACES = ["Next to an instrument", "Not empowered"]
    REPEATS = 99

    def __init__(self, level=0, params=0):
        super().__init__(level, params, phases=["preCombat"])

    @staticmethod
    def extraParameters():
        return {"Title": "Empowered", "Min": 0, "Max": 1, "Default": 0, "Options": BeachPop.PLACES}

    def applyStats(self, champion):
        tiers = getattr(champion, "trait_tiers", None)
        if tiers is None:
            tiers = champion.trait_tiers = {}
        tiers[self.KEY] = int(self.level)  # the level is the trait level (no breakpoints in the build)
        if self.level and self._empowered_member(champion):
            champion.aspd.modify("MultiplyAdditive", 1 + champion.trait_value(self.KEY, "AttackSpeed"))

    def _empowered_member(self, champion):
        return self.PLACES[int(self.params or 0)] == self.PLACES[0] and \
            self.KEY in (champion.data.d.get("trait_keys") or [])

    def performAbility(self, phase, time, champion, input_=0):
        if not self.level or self.KEY not in (champion.data.d.get("trait_keys") or []):
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

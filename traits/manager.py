"""The Manager trait."""
from registry import register
from timing import ticks_up
from traits.base import BuildTrait


@register("trait")
class Manager(BuildTrait):
    """Manager (DA_Manager19): "Gain a Spotlight Hex. The ally who starts combat in it gains bonuses at Combat Start
    and every 5 seconds." CT_Manager19 by tier: ADAP (6%), Mana (0/8/8), Interval (5), HexStatMultiplier (1), Gold
    (0/0/1), HealthPercent (15/20/25%). Tooltip: (2) 6% AD AP, (3) AND 8 Mana, (4) AND they drop 1 Gold.

    Whoever stands in the hex gets it, member or not (Alune, the member, is not implemented), so it is a team trait;
    the parameter is whether the simulated unit starts in the Spotlight Hex (default: yes).
    GA_Manager19_StatGain (build ga_scripts.zip), triggered at combat start (Combat.Event.Passive): RepeatAction(
    Interval, 99), first action at once (A1), each action applying at the trait level GE_Manager19_ADAP (Infinite, no
    stacking rule: every pulse is another instance; AttackDamage and AbilityPower + PhysicalDamageCalc1 = ADAP x
    HexStatMultiplier, Channel1: bonus AD and AP like an item's) and GE_Manager19_AddMana (ManaApplication of
    ManaCalc1 = Mana x HexStatMultiplier). So +6% AD and AP at 0, 5, 10, ... s, plus 8 mana each time from (3).
    The (4) gold and HealthPercent change no damage against dummies and are not modelled.
    """
    KEY = "DA_Manager19"
    display_name = "Manager"
    team_trait = True
    PLACES = ["Yes", "No"]  # starts combat in the Spotlight Hex
    REPEATS = 99

    def __init__(self, level=0, params=0):
        super().__init__(level, params, phases=["preCombat"])

    @staticmethod
    def extraParameters():
        return {"Title": "In the Spotlight Hex", "Min": 0, "Max": 1, "Default": 0, "Options": Manager.PLACES}

    def performAbility(self, phase, time, champion, input_=0):
        if champion.trait_tier(self.KEY) == 0 or self.PLACES[int(self.params or 0)] != "Yes":
            return input_
        mult = champion.trait_value(self.KEY, "HexStatMultiplier")
        adap = champion.trait_value(self.KEY, "ADAP") * mult
        mana = champion.trait_value(self.KEY, "Mana") * mult
        every = champion.trait_value(self.KEY, "Interval")

        def pulse():
            champion.bonus_ad.modify("+", adap)
            champion.ap.modify("+", adap)
            if mana:
                champion.addMana(mana)

        pulse()  # combat start: RepeatAction's first action is immediate
        for k in range(1, self.REPEATS):
            champion.schedule_tick(champion.tick + ticks_up(k * every), pulse)
        return input_


Manager.levels = [0] + Manager.breakpoints()

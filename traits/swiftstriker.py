"""The Swiftstriker trait."""
from registry import register
from timing import ticks_up
from traits.base import BuildTrait, pct


@register("trait")
class Swiftstriker(BuildTrait):
    """Swiftstriker (DA_Swiftstriker19): "Your team gains 10% Attack Speed. Swiftstrikers gain more every 2 seconds,
    up to 5 times." CT_Swiftstriker19 at the tier: TeamAS, SwiftieAS, Period, Stacks.

    Team: GE_Swiftstriker19_AttackSpeed_Team, AttackSpeed MultiplyAdditive 1 + TeamAS, infinite, on every unit of the
    team (members or not), already shown in planning (VOD2 Yunara 0.77 = 0.7 x 1.1).
    Members (GA_Swiftstriker19, triggered at combat start by Combat.Event.Passive): TaskWaitDelay(Period), then
    RepeatAction(Period, Stacks) whose first action is immediate: GE_Swiftstriker19_AttackSpeed_Selfish (MultiplyAdditive
    1 + SwiftieAS) at Period, 2 Period, ..., Stacks x Period (2, 4, 6, 8, 10 s) (B15).
    """
    KEY = "DA_Swiftstriker19"
    display_name = "Swiftstriker"
    team_trait = True  # its team-wide half reaches non-members: offered in Team Traits (owner, 2026-11-19)

    def __init__(self, level=0, params=0):
        super().__init__(level, params, phases=["preCombat"])

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.trait_tier(self.KEY) > 0:
            champion.aspd.modify("MultiplyAdditive", 1 + champion.trait_value(self.KEY, "TeamAS"))

    def performAbility(self, phase, time, champion, input_=0):
        if not champion.has_trait(self.KEY) or champion.trait_tier(self.KEY) == 0:
            return input_
        period = champion.trait_value(self.KEY, "Period")
        bonus = 1 + champion.trait_value(self.KEY, "SwiftieAS")  # one MultiplyAdditive instance per stack
        for k in range(1, int(champion.trait_value(self.KEY, "Stacks")) + 1):
            champion.schedule_tick(champion.tick + ticks_up(k * period), lambda: champion.aspd.modify("MultiplyAdditive", bonus))
        return input_

    @classmethod
    def team_card(cls, build):
        return {"text": "Your team gains Attack Speed.",
                "rows": [{"stats": [[pct(build.trait(cls.KEY).row("TeamAS", col=1)), "AS"]]}]}


Swiftstriker.levels = [0] + Swiftstriker.breakpoints()

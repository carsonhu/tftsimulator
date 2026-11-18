"""The IonicSpark trait."""
from registry import register
from timing import ticks_up
from traits.base import BuildTrait


@register("trait")
class IonicSpark(BuildTrait):
    """Ionic Spark (DA_IonicSpark19): "Fans cheer on Ionic Spark members with gifts every 4 seconds. (3) Letters that
    restore 2% Health and grant 7% AS. (5) Personalized gifts that grant 25% AD or 25% AP. (7) gold and consumables.
    (10) Fans rush the stage!" (B22)

    Letters, (3)+ (GA_IonicSpark19_LetterFan): RepeatAction(LetterFrequency (4 s), 99) from the army's arrival
    (OnReinforcementArmyTravelEnd); action 0 sends nothing (ActionNumber > 0, 0x2c8), each later one sends
    Set19.Trait.IonicSpark.SendLetters, and GA_IonicSpark19_FansManager throws a letter to every member in combat
    (GetFansAndMembersForLetterGranting: the fans round-robin). On arrival, GE_IonicSpark19_LetterAS (AttackSpeed
    MultiplyAdditive AttackSpeedCalc1 = LetterASGain + 1, infinite for the combat, no stack limit) and a heal (nothing
    against dummies). So +7% AS at 4, 8, 12, ... s; the letter's flight from the fans is not modelled.
    Gifts, (5)+ (GA_IonicSpark19_BigGiftFan): RepeatAction(LetterFrequency, 99) whose first action is immediate picks
    DetermineNextIonicSparkMemberToBuff (members, Tanks last (TR_Sort_ByRoleWeighted TankWeight 0), then by items
    equipped, without Set19.Trait.IonicSpark.GiftRecieved) and throws a gift: Role.Attack gets GE_IonicSpark19_Gift_
    Attack (AttackDamage + PersonalGiftAD 25%), Role.Magic or Role.Hybrid GE_IonicSpark19_Gift_Magic (AbilityPower +
    PersonalGiftAP 25%), once per combat. Which gift this unit gets is the 'Gift' option (1st at 0 s, 2nd at 4 s, 3rd
    at 8 s, or none); the throw and flight are not modelled. Bonus Health, (7)'s economy and (10)'s waves of fans
    (damage to enemies, not modelled) aside.
    """
    KEY = "DA_IonicSpark19"
    display_name = "Ionic Spark"
    team_trait = False  # members only: the gift order is about this unit
    GIFTS = ["1st", "2nd", "3rd", "None"]
    ACTIONS = 99  # RepeatAction's count (both fans)

    def __init__(self, level=0, params=0):
        super().__init__(level, params, phases=["preCombat"])

    @staticmethod
    def extraParameters():
        return {"Title": "Gift", "Min": 0, "Max": len(IonicSpark.GIFTS) - 1, "Default": 0, "Options": IonicSpark.GIFTS}

    def performAbility(self, phase, time, champion, input_=0):
        tier = champion.trait_tier(self.KEY)
        if tier == 0 or self.KEY not in (champion.data.d.get("trait_keys") or []):
            return input_
        period = champion.trait_value(self.KEY, "LetterFrequency")
        letter = champion.trait_value(self.KEY, "LetterASGain") * 100
        for k in range(1, self.ACTIONS):
            champion.schedule_tick(champion.tick + ticks_up(k * period), lambda: champion.aspd.addStat(letter))
        if tier >= 2 and self.GIFTS[self.params] != "None":
            attack = champion.role.key.startswith("Attack")
            stat = champion.bonus_ad if attack else champion.ap
            gift = champion.trait_value(self.KEY, "PersonalGiftAD" if attack else "PersonalGiftAP") * 100
            champion.schedule_tick(champion.tick + ticks_up(self.params * period), lambda: stat.addStat(gift))
        return input_


IonicSpark.levels = [0] + IonicSpark.breakpoints()

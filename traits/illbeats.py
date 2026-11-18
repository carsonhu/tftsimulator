"""The Illbeats trait."""
from registry import register
from traits.base import BuildTrait


@register("trait")
class Illbeats(BuildTrait):
    """Illbeats (DA_Illbeats19): "Open the Illbeats Mixer to allocate Decibels. Illbeats champions receive different
    stats based on your mix. Your team gains 50% of the mix." (B20)

    The tier grants GE_Illbeats19_GrantStats to members and GE_Illbeats19_GrantSelflessStats to everyone else; each
    grants one GA_Illbeats19_UpdateStat per channel (HP Stack, AD Stack2, AP Stack3, gold Stack4). CalculateStatAmount
    sums CT_Illbeats19_PercentAtEachTick's row at ticks 1..n (n = the channel's decibels), times StatMult at the trait
    level (1 / 1 / 1.5), times SelflessStatMult (0.5) for non-members, and applies it as the channel's effect:
    GE_Illbeats19_PercentAttackDamage / PercentAbilityPower (AttackDamage / AbilityPower +, Channel1). Decibels: Remix
    (10 / 14 / 18) in all, at most MaxRemixPerChannel (10) per channel. Applied while planning (the stat is not
    changed in combat), so in the static-stats pass. HP and gold chance change nothing against dummies.

    The mix is the parameter (Options): every decibel the option doesn't spend on AD or AP goes to HP or gold.
    """
    KEY = "DA_Illbeats19"
    display_name = "Illbeats"
    TABLE = "CT_Illbeats19_PercentAtEachTick"
    MIXES = ["All AD", "All AP", "Split AD/AP", "No AD/AP"]

    @staticmethod
    def extraParameters():
        return {"Title": "Mix", "Min": 0, "Max": len(Illbeats.MIXES) - 1, "Default": 0, "Options": Illbeats.MIXES}

    def ticks(self, champion):
        """(AD decibels, AP decibels) of the chosen mix at the board's tier."""
        total = int(champion.trait_value(self.KEY, "Remix"))
        cap = int(champion.trait_value(self.KEY, "MaxRemixPerChannel"))
        mix = self.MIXES[self.params]
        if mix == "All AD":
            return min(cap, total), 0
        if mix == "All AP":
            return 0, min(cap, total)
        if mix == "Split AD/AP":
            ad = min(cap, (total + 1) // 2)
            return ad, min(cap, total - ad)
        return 0, 0

    def channel_value(self, champion, row, n):
        """The channel's stat at n decibels for a member: CalculateStatAmount's sum x StatMult."""
        from build_champion import curve_at  # build_champion imports this module
        pts = champion.build.trait(self.KEY).table_row(self.TABLE, row)
        total = sum(curve_at(pts, i, "Linear") for i in range(1, n + 1))
        return total * champion.trait_value(self.KEY, "StatMult")

    def applyStats(self, champion):
        super().applyStats(champion)
        if champion.trait_tier(self.KEY) == 0:
            return
        member = self.KEY in (champion.data.d.get("trait_keys") or [])
        share = 1 if member else champion.trait_value(self.KEY, "SelflessStatMult")
        ad, ap = self.ticks(champion)
        champion.bonus_ad.modify("+", self.channel_value(champion, "PercentAD", ad) * share)
        champion.ap.modify("+", self.channel_value(champion, "PercentAP", ap) * share)


Illbeats.levels = [0] + Illbeats.breakpoints()

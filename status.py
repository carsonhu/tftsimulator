import math

from stats import FastDeepCopy


class Status(FastDeepCopy):
    """Holds champion status effects:
    1. name
    2. wearoff time
    3. application effect
    4. wearoff effect
    """

    # Earliest time update() could do anything. The frame loop polls every
    # status on all ~900 frames of a combat, and most statuses (a 30s shred
    # applied at combat start, say) are only waiting to expire, so there is
    # nothing to look at until wearoff_time. -1 means "poll every frame",
    # which is what any subclass with its own update() gets.
    next_update = -1

    def __init__(self, name):
        self.wearoff_time = -1
        self.name = name
        self.active = False
        self.opponent = None

    def _reschedule(self):
        """Recompute next_update after wearoff_time changes."""
        if type(self).update is Status.update:
            self.next_update = self.wearoff_time
        else:
            # Subclass does periodic work of its own; keep polling it.
            self.next_update = -1

    def application(self, champion, opponent, time, duration, params):
        # opponent applies the status
        self.opponent = opponent
        self.active = True
        self.wearoff_time = time + duration
        self.applicationEffect(champion, time, duration, params)
        self._reschedule()

    def applicationEffect(self, champion, time, duration, params):
        return 0

    def reapplication(self, champion, opponent, time, duration, params):
        self.opponent = opponent
        self.active = True
        if self.reapplicationEffect(champion, time, duration, params):
            self.wearoff_time = time + duration
        self._reschedule()

    def reapplicationEffect(self, champion, time, duration, params):
        return 0

    def wearoff(self, champion, time):
        self.active = False
        self.wearoffEffect(champion, time)
        self.opponent = None
        if type(self).update is Status.update:
            # Nothing left to do unless it gets reapplied.
            self.next_update = float("inf")

    def wearoffEffect(self, champion, time):
        return 0

    def update(self, champion, time):
        if time > self.wearoff_time and self.active:
            self.wearoff(champion, time)

        # if status not in dict, put it in
        # applyeeffect: if inactive, application
        # else, reapplication



def zero_scaling(x, y, z):
    """Default zero scaling function for DoT effects."""
    return 0


class DoTEffect(Status):
    # apply damage once per second. in-game it's at least every half-second
    # but this is chill for clarity
    def __init__(self, name):
        super().__init__("DoT {}".format(name))
        self.scaling = zero_scaling
        self.next_proc = 0

    def applicationEffect(self, champion, time, duration, params):
        # params: (scaling function, interval)
        self.scaling = params[0]
        self.interval = params[1]
        self.next_proc = math.floor(time) + self.interval
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        return True

    def wearoffEffect(self, champion, time):
        self.next_proc = 999
        return True

    def update(self, champion, time):
        if time > self.next_proc:
            # do damage
            self.opponent.multiTargetSpell(
                self.opponent.opponents,
                self.opponent.items,
                time,
                1,
                self.scaling,
                "magical",
            )

            self.next_proc += self.interval
        super().update(champion, time)


class DoTEffectNoItems(Status):
    # bad code but this is for fairy tail
    # no scaling, just raw damage
    def __init__(self, name):
        super().__init__("DoT {}".format(name))
        self.damage = 0
        self.next_proc = 0

    def applicationEffect(self, champion, time, duration, params):
        self.damage = params / duration
        self.next_proc = math.floor(time) + 1
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        return True

    def wearoffEffect(self, champion, time):
        self.next_proc = 999
        return True

    def update(self, champion, time):
        if time > self.next_proc:
            # do damage
            self.opponent.doDamage(
                self.opponent.opponents[0],
                [],
                0,
                self.damage,
                self.damage,
                "magical",
                time,
            )

            self.next_proc += 1
        super().update(champion, time)


class UltActivator(Status):
    def __init__(self, name):
        super().__init__("Ult Active {}".format(name))

    def applicationEffect(self, champion, time, duration, params):
        champion.ultActive = True
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        return True

    def wearoffEffect(self, champion, time):
        champion.ultActive = False
        return True


class SilverBolts(Status):
    def __init__(self, wearoff_time=999):
        super().__init__("Silver Bolt", wearoff_time=wearoff_time)
        self.stacks = 0

    def applicationEffect(self, champion, time, duration, params):
        self.stacks += 1
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        self.stacks += 1
        if self.stacks == 3:
            self.opponent.performAbility([champion], self.opponent.items, time)
            self.stacks = 0
        return True

    def wearoffEffect(self, champion, time):
        self.stacks = 0
        return True


class ADModifier(Status):
    # increase AS by %
    # NOTE: does not work with stacking
    def __init__(self, name):
        super().__init__("AD Modifier {}".format(name))
        self.toAdd = 0

    def applicationEffect(self, champion, time, duration, params):
        self.toAdd = params
        champion.bonus_ad.addStat(self.toAdd)
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True

    def wearoffEffect(self, champion, time):
        champion.bonus_ad.addStat(-1 * self.toAdd)
        return True


class AsheUlt(Status):
    # increase AS by %
    # NOTE: does not work with stacking
    def __init__(self, name):
        super().__init__("Ashe Ult {}".format(name))

    def applicationEffect(self, champion, time, duration, params):
        champion.ultsActive += 1
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True

    def wearoffEffect(self, champion, time):
        champion.ultsActive -= 1
        return True


class ASMultModifier(Status):
    # increase AS by %
    # NOTE: does not work with stacking
    def __init__(self, wearoff_time):
        super().__init__("AS Multiplicative Modifier", wearoff_time=wearoff_time)
        self.addition = 1

    def applicationEffect(self, champion, time, duration, params):
        champion.aspd.mult += params
        self.addition = params
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True

    def wearoffEffect(self, champion, time):
        champion.aspd.mult -= self.addition
        return True


class ManaRegenModifier(Status):
    # increase Mana Regen
    # NOTE: does not work with stacking
    def __init__(self, name):
        super().__init__(f"Mana Regen Modifier {name}")
        self.addition = 1

    def applicationEffect(self, champion, time, duration, params):
        champion.manaRegen.addStat(params)
        self.addition = params
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True

    def wearoffEffect(self, champion, time):
        champion.manaRegen.addStat(self.addition * -1)
        return True


class DmgMultiplierModifier(Status):
    # increase AS by %
    # NOTE: does not work with stacking
    def __init__(self, name):
        super().__init__("AS Multiplicative Modifier {}".format(name))
        self.addition = 1

    def applicationEffect(self, champion, time, duration, params):
        champion.dmgMultiplier.addStat(params)
        self.addition = params
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True

    def wearoffEffect(self, champion, time):
        champion.dmgMultiplier.addStat(self.addition * -1)
        return True


class KogASModifier(Status):
    # increase AS by %
    # NOTE: does not work with stacking
    def __init__(self, wearoff_time):
        super().__init__("AS Modifier", wearoff_time=wearoff_time)
        self.addition = 1

    def applicationEffect(self, champion, time, duration, params):
        champion.aspd.add += params
        champion.ultActive = True
        self.addition = params
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True

    def wearoffEffect(self, champion, time):
        champion.ultActive = False
        champion.aspd.add -= self.addition
        return True


class KaisaBuff(Status):
    # increase AS by %
    # idea is each buff has new name
    def __init__(self, count, wearoff_time):
        super().__init__("Kaisa Buff {}".format(count), wearoff_time=wearoff_time)
        self.addition = 1

    def applicationEffect(self, champion, time, duration, params):
        champion.aspd.add += params
        self.addition = params
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True

    def wearoffEffect(self, champion, time):
        champion.aspd.add -= self.addition
        return True


class DecayingASModifier(Status):
    # increase AS by %
    # NOTE: does not work with stacking
    def __init__(self, name):
        super().__init__("Decaying AS Modifier {}".format(name))
        self.addition = 1
        self.duration = 0

    def applicationEffect(self, champion, time, duration, params):
        champion.aspd.add += params
        self.addition = params
        self.amount_to_decrease = self.addition / (duration / (1 / 30))
        self.duration = duration
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True

    def wearoffEffect(self, champion, time):
        # champion.aspd.add  -= self.addition
        return True

    def update(self, champion, time):
        # NOTE: thsi will get fucked up with frame time
        if time <= self.wearoff_time and self.active:
            champion.aspd.add -= self.amount_to_decrease
            self.addition -= self.amount_to_decrease
        if time > self.wearoff_time and self.addition > 0:
            champion.aspd.add -= self.addition
            self.addition = 0
        super().update(champion, time)


class CritModifier(Status):
    # increase crit by %
    def __init__(self, name):
        super().__init__("Crit Modifier {}".format(name))
        self.addition = 0

    def applicationEffect(self, champion, time, duration, params):
        champion.crit.addStat(params)
        self.addition = params
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True

    def wearoffEffect(self, champion, time):
        champion.aspd.addStat(-1 * self.addition)
        return True


class DmgAmpModifier(Status):
    # increase crit by %
    def __init__(self, name):
        super().__init__("Dmg Amp Modifier {}".format(name))
        self.addition = 0

    def applicationEffect(self, champion, time, duration, params):
        champion.dmgMultiplier.addStat(params)
        self.addition = params
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True

    def wearoffEffect(self, champion, time):
        champion.dmgMultiplier.addStat(-1 * self.addition)
        return True


class ASModifier(Status):
    # increase AS by %
    # NOTE: does not work with stacking
    def __init__(self, name):
        super().__init__("AS Modifier {}".format(name))
        self.addition = 1

    def applicationEffect(self, champion, time, duration, params):
        champion.aspd.add += params
        self.addition = params
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        # champion.aspd.add += params
        # self.addition = params
        return True

    def wearoffEffect(self, champion, time):
        champion.aspd.add -= self.addition
        return True


class ArmorReduction(Status):
    # reduce armor by N%
    def __init__(self, name):
        super().__init__("Armor Reduction {}".format(name))
        self.reduction = 1

    def applicationEffect(self, champion, time, duration, params):
        # if it's not a bigger shred, do nothing
        champion.armor.mult = min(champion.armor.mult, params)
        self.reduction = params
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        if self.reduction >= params:
            champion.armor.mult = min(champion.armor.mult, self.reduction)
            return True
        else:
            # if it's weaker, doesnt work
            return False

    def wearoffEffect(self, champion, time):
        # iterate through champ statuses
        champion.armor.mult = 1
        for status_name, status in list(champion.statuses.items()):
            if "Armor Reduction" in status_name and status.active:
                champion.armor.mult = min(champion.armor.mult, status.reduction)
        return True


class MRReduction(Status):
    # reduce MR by N%
    def __init__(self, name):
        super().__init__("MR Reduction {}".format(name))
        self.reduction = 1

    def applicationEffect(self, champion, time, duration, params):
        champion.mr.mult = min(champion.mr.mult, params)
        self.reduction = params
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        if self.reduction >= params:
            champion.mr.mult = min(champion.mr.mult, self.reduction)
            return True
        else:
            # if it's weaker, doesnt work
            return False

    def wearoffEffect(self, champion, time):
        champion.mr.mult = 1
        for status_name, status in list(champion.statuses.items()):
            if (
                "MR Reduction" in status_name
                and status.active
                and status_name != self.name
            ):
                champion.mr.mult = min(champion.mr.mult, status.reduction)
        return True


class CorrosionStatus(Status):
    def __init__(self):
        super().__init__("Corrosion")
        self.amount = 4
        self.interval = 2
        self.next_proc = 2
        self.total_reduction = 0

    def applicationEffect(self, champion, time, duration, params):
        self.next_proc = time + self.interval
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        return True

    def wearoffEffect(self, champion, time):
        # champion.armor.addStat(self.total_reduction)
        # champion.mr.addStat(self.total_reduction)
        return True

    def _reschedule(self):
        # Ticks on a fixed interval and deliberately has no wearoff, so the
        # next tick is the only time it needs looking at. Corrosion sits on
        # every opponent for whole fights, so polling it every frame was one of
        # the most expensive things in the simulator.
        self.next_update = self.next_proc

    def update(self, champion, time):
        if time >= self.next_proc:
            champion.armor.addStat(-self.amount)
            champion.mr.addStat(-self.amount)
            self.total_reduction += self.amount
            self.next_proc += self.interval
        self.next_update = self.next_proc
        super().update(champion, time)


class AccelerationGateStatus(Status):
    def __init__(self):
        super().__init__("AccelerationGateStatus")
        self.scaling = zero_scaling
        self.next_proc = 0
        self.ticks_remaining = 0
        self.mana_per_tick = 0

    def applicationEffect(self, champion, time, duration, params):
        self.mana_per_tick = (0.35 * champion.fullMana.stat) / 4
        self.next_proc = time + 0.5
        self.ticks_remaining = 4
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        self.ticks_remaining = 4
        self.mana_per_tick = (0.35 * champion.fullMana.stat) / 4
        self.next_proc = time + 0.5
        return True

    def update(self, champion, time):
        if self.active and time >= self.next_proc and self.ticks_remaining > 0:
            champion.addMana(self.mana_per_tick)
            self.next_proc += 0.5
            self.ticks_remaining -= 1
        
        super().update(champion, time)


class AkaliNovaStrikeStatus(Status):
    # N.O.V.A. Strike: after the power surge, Akali slices all enemies with a
    # bleed dealing physical damage each second for the rest of combat.
    def __init__(self, name="N.O.V.A. Strike"):
        super().__init__(name)
        self.scaling = zero_scaling
        self.num_targets = 0
        self.interval = 1.0
        self.next_proc = 0

    def applicationEffect(self, champion, time, duration, params):
        self.scaling, self.num_targets = params
        self.next_proc = time + self.interval
        return True

    def update(self, champion, time):
        if self.active and time >= self.next_proc:
            if champion.opponents:
                champion.multiTargetSpell(
                    champion.opponents,
                    champion.items,
                    time,
                    self.num_targets,
                    self.scaling,
                    "physical",
                )
            self.next_proc += self.interval
        super().update(champion, time)


class TheGrooveStatus(Status):
    def __init__(self):
        super().__init__("The Groove")
        self.as_bonus = 0
        self.ad_ap_per_tick = 0
        self.next_proc = 0
        self.total_ad_ap_added = 0

    def applicationEffect(self, champion, time, duration, params):
        self.as_bonus = params.get("as_bonus", 0)
        self.ad_ap_per_tick = params.get("ad_ap_tick", 0)
        
        champion.aspd.add += self.as_bonus
        self.next_proc = time + 1.0
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        return True

    def wearoffEffect(self, champion, time):
        champion.aspd.add -= self.as_bonus
        return True

    def update(self, champion, time):
        if self.active and time >= self.next_proc:
            if self.ad_ap_per_tick > 0:
                champion.bonus_ad.addStat(self.ad_ap_per_tick)
                champion.ap.addStat(self.ad_ap_per_tick)
                self.total_ad_ap_added += self.ad_ap_per_tick
            self.next_proc += 1.0
        super().update(champion, time)


class ExecutionerBleedStatus(Status):
    # Executioner: any damage the source deals bleeds the target for a % of
    # that hit's damage, split evenly as true damage over `duration`. Each
    # new hit's bleed replaces whatever's left of the current one rather
    # than stacking, since Yunara can retrigger this every attack/cast.
    def __init__(self):
        super().__init__("Executioner Bleed")
        self.damage_per_tick = 0
        self.interval = 1.0
        self.next_proc = 0

    def applicationEffect(self, champion, time, duration, params):
        # params: total bleed damage, to be split over `duration`
        self.damage_per_tick = params / duration * self.interval
        self.next_proc = time + self.interval
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        self.damage_per_tick = params / duration * self.interval
        self.next_proc = time + self.interval
        return True

    def update(self, champion, time):
        if self.active and time >= self.next_proc:
            if self.opponent is not None:
                self.opponent.doDamage(
                    champion, [], 0,
                    self.damage_per_tick, self.damage_per_tick,
                    "true", time,
                )
            self.next_proc += self.interval
        super().update(champion, time)

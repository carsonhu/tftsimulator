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


class DmgAmpModifier(Status):
    """Damage amp for the status's duration (Striker's Flail's buff): its own keyed modifier, removed at wearoff."""

    def __init__(self, name):
        super().__init__("Dmg Amp Modifier {}".format(name))

    def applicationEffect(self, champion, time, duration, params):
        champion.dmgMultiplier.modify("+", params, key=self.name)
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        return True

    def wearoffEffect(self, champion, time):
        champion.dmgMultiplier.remove(self.name)
        return True


def _reduction(attr, key):
    """The Channel2 multiplier a reduction status keeps on `attr` (1 = none)."""
    return next((m[2] for m in attr.mods if m[3] == key), 1)


class _Reduction(Status):
    """Armor or MR x reduction for the duration; only the strongest active one counts (I7): all of a kind share one
    keyed Channel2 MultiplyCompound on the target."""
    KIND = None  # the status-name prefix, also the modifier's key
    ATTR = None  # the target's attribute field

    def __init__(self, name):
        super().__init__("{} {}".format(self.KIND, name))
        self.reduction = 1

    def _set(self, champion, value):
        attr = getattr(champion, self.ATTR)
        if value == 1:
            attr.remove(self.KIND)
        else:
            attr.modify("MultiplyCompound", value, channel=2, key=self.KIND)

    def applicationEffect(self, champion, time, duration, params):
        # if it's not a bigger reduction, it changes nothing
        self._set(champion, min(_reduction(getattr(champion, self.ATTR), self.KIND), params))
        self.reduction = params
        return True

    def reapplicationEffect(self, champion, time, duration, params):
        if self.reduction >= params:
            self._set(champion, min(_reduction(getattr(champion, self.ATTR), self.KIND), self.reduction))
            return True
        return False  # a weaker one doesn't renew it

    def wearoffEffect(self, champion, time):
        strongest = 1
        for status_name, status in list(champion.statuses.items()):
            if self.KIND in status_name and status.active and status_name != self.name:
                strongest = min(strongest, status.reduction)
        self._set(champion, strongest)
        return True


class ArmorReduction(_Reduction):
    KIND, ATTR = "Armor Reduction", "armor"


class MRReduction(_Reduction):
    KIND, ATTR = "MR Reduction", "mr"

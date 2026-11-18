from copy import deepcopy as _deepcopy

# Values that can be shared between a copy and its original instead of being
# recursed into. Functions are included because scaling callables are stateless
# and copy.deepcopy already returns them unchanged.
_IMMUTABLE_TYPES = frozenset(
    (int, float, bool, str, bytes, complex, type(None), type(_deepcopy))
)


class FastDeepCopy(object):
    """Mixin providing a cheaper copy.deepcopy for plain attribute containers.

    Every simulation deep-copies a champion, its ~18 Stat objects and 8
    opponents, which made copy.deepcopy's generic __reduce_ex__ machinery the
    single most expensive thing in the simulator. Copying __dict__ directly and
    passing scalars through by reference does the same job for these classes.
    The memo is still threaded through so shared references stay shared in
    the copy.
    """

    __slots__ = ()

    def __deepcopy__(self, memo):
        cls = self.__class__
        new = cls.__new__(cls)
        memo[id(self)] = new
        new_dict = new.__dict__
        for key, value in self.__dict__.items():
            if type(value) in _IMMUTABLE_TYPES:
                new_dict[key] = value
            else:
                new_dict[key] = _deepcopy(value, memo)
        return new


# Modifier operations, named as the build names them ("+" is AddBase, "=" is Override).
OPS = ("+", "MultiplyAdditive", "DivideAdditive", "MultiplyCompound", "AddFinal", "=", "at least", "at most")


class Attribute(FastDeepCopy):
    """A unit attribute, evaluated the way the game evaluates it (GAS; ledger I5).

    A modifier is (channel, op, value), as the build lists it. Channel 0 starts from the attribute's base; each
    channel's result is the next channel's input. Per channel:

        ((input + sum of AddBase) x (1 + sum of (MultiplyAdditive - 1)) / (1 + sum of (DivideAdditive - 1))
         x product of MultiplyCompound) + sum of AddFinal

    then an Override ("=") replaces the result and bounds clamp it ("at least" is a minimum, "at most" a maximum).
    Items, roles and traits sit on Channel1; Channel2 comes after them (caps, Overrides such as Silvermere Dawn's,
    debuffs on the target).

    Values are in game units: AttackDamage and AbilityPower are multipliers (1.0 = the unit's own; Deathblade's 55%
    is +0.55), AttackSpeed is attacks per second, crit chance, crit damage, omnivamp and damage amp are fractions,
    the rest flat. A modifier given a `key` replaces any earlier one with that key and can be removed by it.
    """

    def __init__(self, base):
        self._base = base
        self.mods = []  # (channel, op, value, key), in the order applied
        self._value = base  # cached result; None = stale

    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, value):
        self._base = value
        self._value = None

    def modify(self, op, value, channel=1, key=None):
        if op not in OPS:
            raise ValueError(f"unknown modifier op {op!r}")
        if key is not None:
            self.mods = [m for m in self.mods if m[3] != key]
        self.mods.append((channel, op, value, key))
        self._value = None

    def remove(self, key):
        self.mods = [m for m in self.mods if m[3] != key]
        self._value = None

    def total(self, op, channel=1):
        """One channel's combined `op` term: the sum for AddBase, AddFinal, MultiplyAdditive and DivideAdditive
        (the last two as sum of (v - 1)), the product for MultiplyCompound."""
        t = 1.0 if op == "MultiplyCompound" else 0.0
        for c, o, x, _ in self.mods:
            if c == channel and o == op:
                if op == "MultiplyCompound":
                    t *= x
                elif op in ("MultiplyAdditive", "DivideAdditive"):
                    t += x - 1
                else:
                    t += x
        return t

    @property
    def stat(self):
        if self._value is None:
            self._value = self._evaluate()
        return self._value

    def _evaluate(self):
        v = self._base
        for ch in sorted({m[0] for m in self.mods}):  # a channel without modifiers changes nothing
            add = ma = da = af = 0.0
            mc = 1.0
            over = lo = hi = None
            for c, op, x, _ in self.mods:
                if c != ch:
                    continue
                if op == "+":
                    add += x
                elif op == "MultiplyAdditive":
                    ma += x - 1
                elif op == "DivideAdditive":
                    da += x - 1
                elif op == "MultiplyCompound":
                    mc *= x
                elif op == "AddFinal":
                    af += x
                elif op == "=":
                    over = x
                elif op == "at least":
                    lo = x if lo is None else max(lo, x)
                else:
                    hi = x if hi is None else min(hi, x)
            v = (v + add) * (1 + ma) / (1 + da) * mc + af
            if over is not None:
                v = over
            if lo is not None:
                v = max(v, lo)
            if hi is not None:
                v = min(v, hi)
        return v


# ---------------------------------------------------------------- the old Stat API, while callers move over
# (docs/RESTRUCTURE.md step 3, first pass). Each answers .addStat, .add and .mult in the old units and turns them
# into modifiers; removed once nothing calls them.
class _Legacy(Attribute):
    @property
    def mult(self):
        """The old final multiplier: a Channel2 MultiplyCompound."""
        return next((m[2] for m in self.mods if m[3] == "legacy mult"), 1)

    @mult.setter
    def mult(self, value):
        self.modify("MultiplyCompound", value, channel=2, key="legacy mult")

    @property
    def add(self):
        return self.total("+")

    @add.setter
    def add(self, value):
        self.addStat(value - self.add)

    def addStat(self, add):
        self.modify("+", add)


class LegacyFlat(_Legacy):
    """HP, mana, crit, crit damage, omnivamp, damage amp: added as they are."""


class LegacyResist(_Legacy):
    """Armor and MR: added as they are, never below 0."""

    def __init__(self, base):
        super().__init__(base)
        self.modify("at least", 0, channel=2, key="floor")


class LegacyMultiplier(_Legacy):
    """AD and AP: added in percent points (55 for +0.55); addMultiplier is the old Deathblade / Rabadon's factor
    on every bonus, as MultiplyAdditive (1 + f) with AddFinal -f (I5)."""

    def __init__(self):
        super().__init__(1.0)

    @property
    def add(self):
        return self.total("+") * 100

    @add.setter
    def add(self, value):
        self.addStat(value - self.add)

    def addStat(self, add):
        self.modify("+", add / 100)

    @property
    def addMultiplier(self):
        return 1 + self.total("MultiplyAdditive")

    @addMultiplier.setter
    def addMultiplier(self, value):
        delta = value - self.addMultiplier
        self.modify("MultiplyAdditive", 1 + delta)
        self.modify("AddFinal", -delta)


class LegacyAspd(_Legacy):
    """Attack speed: added in percent points as MultiplyAdditive; capped (as_cap) and overridden on Channel2."""

    def __init__(self, base):
        super().__init__(base)
        self.as_cap = 5

    @property
    def add(self):
        return self.total("MultiplyAdditive") * 100

    @add.setter
    def add(self, value):
        self.addStat(value - self.add)

    def addStat(self, add):
        self.modify("MultiplyAdditive", 1 + add / 100)

    @property
    def as_cap(self):
        return next(m[2] for m in self.mods if m[3] == "cap")

    @as_cap.setter
    def as_cap(self, value):
        self.modify("at most", value, channel=2, key="cap")

    @property
    def override(self):
        return next((m[2] for m in self.mods if m[3] == "override"), None)

    @override.setter
    def override(self, value):
        if value is None:
            self.remove("override")
        else:
            self.modify("=", value, channel=2, key="override")


class Stat(FastDeepCopy):
    """Object for each stat, (AD, HP, Armor, etc.)

    Attributes:
        add (double): Additive modifier
        base (double): Base modifier
        mult (double): Multiplier
    """

    def __init__(self, base, multModifier, addModifier):
        self.base = base
        self.mult = multModifier
        self.add = addModifier

    @property
    def stat(self):
        # ad: (base + add)* mult
        # i.e 15% AS is base AS * .15
        return self.mult * (self.base + self.add)

    def addStat(self, add):
        self.add += add


class ArmorPierce(Stat):
    # If you have 50% armor shred and 40% armor shred on same unit,
    # they shuold multiply to be 70% armor shred
    def __init__(self, base, multModifier, addModifier):
        super().__init__(base, multModifier, addModifier)

    def addStat(self, add):
        # If 50%, 40%: .5 + .4 - .5 * .4 = .7
        # if 50%, 0%: .5
        # if 40%, 0%: .4
        self.add = add + self.add - add * self.add

    @property
    def stat(self):
        return self.base + self.add


def default_scaling(level, baseAD, AD, AP=0):
    """Default scaling function for attacks."""
    return baseAD * AD


class Attack(object):
    # stores details on an attack
    def __init__(
        self,
        opponents=None,
        scaling=None,
        canCrit=True,
        canOnHit=True,
        multiplier=Stat(0, 1, 0),
        attackType="physical",
        numTargets=1,
        regularAuto=True,
    ):
        self.opponents = opponents
        self.scaling = scaling if scaling is not None else default_scaling
        self.canCrit = canCrit
        self.canOnHit = canOnHit
        self.multiplier = multiplier
        self.attackType = attackType
        self.numTargets = numTargets
        self.regularAuto = regularAuto

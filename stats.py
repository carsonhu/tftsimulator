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


class AttributeBased(FastDeepCopy):
    """A modifier's magnitude read from another attribute each time it is needed (GAS AttributeBased, not snapshot):
    coefficient x (that attribute + pre) + post, the attribute evaluated through channel `up_to`
    (AttributeMagnitudeEvaluatedUpToChannel; None = its final value). Jhin's AS -> AD converter (champions/Jhin.md)."""

    def __init__(self, attribute, coefficient, post=0.0, pre=0.0, up_to=None):
        self.attribute = attribute
        self.coefficient, self.post, self.pre, self.up_to = coefficient, post, pre, up_to

    def value(self):
        return self.coefficient * (self.attribute.evaluate(self.up_to) + self.pre) + self.post


def _magnitude(x):
    return x.value() if isinstance(x, AttributeBased) else x


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
        if isinstance(value, AttributeBased):
            self.dynamic = True  # never cached: the other attribute can change at any time

    def remove(self, key):
        self.mods = [m for m in self.mods if m[3] != key]
        self._value = None

    def total(self, op, channel=1):
        """One channel's combined `op` term: the sum for AddBase, AddFinal, MultiplyAdditive and DivideAdditive
        (the last two as sum of (v - 1)), the product for MultiplyCompound."""
        t = 1.0 if op == "MultiplyCompound" else 0.0
        for c, o, x, _ in self.mods:
            x = _magnitude(x)
            if c == channel and o == op:
                if op == "MultiplyCompound":
                    t *= x
                elif op in ("MultiplyAdditive", "DivideAdditive"):
                    t += x - 1
                else:
                    t += x
        return t

    dynamic = False  # True once a modifier is AttributeBased

    @property
    def stat(self):
        if self.dynamic:
            return self._evaluate()
        if self._value is None:
            self._value = self._evaluate()
        return self._value

    def evaluate(self, up_to=None):
        """The value through channel `up_to` (None: every channel)."""
        return self._evaluate(up_to)

    def _evaluate(self, up_to=None):
        v = self._base
        for ch in sorted({m[0] for m in self.mods}):  # a channel without modifiers changes nothing
            if up_to is not None and ch > up_to:
                break
            add = ma = da = af = 0.0
            mc = 1.0
            over = lo = hi = None
            for c, op, x, _ in self.mods:
                if c != ch:
                    continue
                x = _magnitude(x)
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


class Stat(FastDeepCopy):
    """The old stat object, kept only for Attack.multiplier (set18's Runaan's hook, always x1; step 4 replaces
    attacks) and the pierce stats.

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

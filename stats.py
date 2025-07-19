class Stat(object):
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


class AD(Stat):
    # AD shouldnt be modified
    def __init__(self, base):
        super().__init__(base, 1, 0)
        self.addMultiplier = 1  # used for Attack Expert

    def addStat(self, add):
        # if u get 6 AD, mult is +6
        self.mult += add / 100

    @property
    def stat(self):
        return self.base


class JhinBonusAD(Stat):
    # AP needs a slightly different calcualtion
    def __init__(self, base, multModifier, addModifier, aspd):
        super().__init__(base, multModifier, addModifier)
        # temporary
        self.aspd = aspd
        self.base = 100
        self.addMultiplier = 1  # only for ahri

    @property
    def stat(self):
        return (
            self.mult
            * (self.base + (self.add + self.aspd.add * 0.8) * self.addMultiplier)
            / 100
        )


class Aspd(Stat):
    # AS needs a slightly different calc and a cap
    def __init__(self, base, multModifier, addModifier):
        super().__init__(base, multModifier, addModifier)
        self.as_cap = 5

    @property
    def stat(self):
        return min(self.mult * self.base * (1 + self.add / 100), self.as_cap)


class AP(Stat):
    # AP needs a slightly different calcualtion
    def __init__(self, base, multModifier, addModifier):
        super().__init__(base, multModifier, addModifier)
        # temporary
        self.base = 100
        self.addMultiplier = 1  # only for ahri

    @property
    def stat(self):
        return self.mult * (self.base + self.add * self.addMultiplier) / 100


class Resist(Stat):
    # just make sure you can't go negative
    @property
    def stat(self):
        return max(self.mult * (self.base + self.add), 0)


class Attack(object):
    # stores details on an attack
    def __init__(
        self,
        opponents=None,
        scaling=lambda level, baseAD, AD, AP=0: baseAD * AD,
        canCrit=True,
        canOnHit=True,
        multiplier=Stat(0, 1, 0),
        attackType="physical",
        numTargets=1,
        regularAuto=True,
    ):
        self.opponents = opponents
        self.scaling = scaling
        self.canCrit = canCrit
        self.canOnHit = canOnHit
        self.multiplier = multiplier
        self.attackType = attackType
        self.numTargets = numTargets
        self.regularAuto = regularAuto

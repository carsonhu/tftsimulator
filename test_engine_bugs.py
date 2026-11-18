"""Engine review bugs E8 and E9 (docs/ASSUMPTIONS.md)."""
from champion import Champion
from item import Item
import stats
from stats import Stat
from test_timing import dummy


class Spy(Item):
    def __init__(self):
        super().__init__(name='Spy', phases=['preAttack', 'onCrit'])
        self.attacks, self.crits = [], 0

    def performAbility(self, phase, time, champion, input_=0):
        if phase == 'preAttack':
            self.attacks.append(input_)
        else:
            self.crits += 1


def unit():
    c = Champion('Unit', 1000, 100, 0, 30, 1.0, 0, 0, 1)
    c.items = []
    return c


def test_spell_attacks_carry_their_fields_in_the_right_places():
    # E8: multiTargetSpell's simulated attacks were built positionally: scaling=Stat, canCrit="physical", canOnHit=1
    c, spy = unit(), Spy()
    c.multiTargetSpell([dummy()], [spy], 0, 1, lambda lvl, ad, ap: 100, numAttacks=1)
    a = spy.attacks[0]
    assert a.scaling is stats.default_scaling and a.canCrit is True and a.canOnHit is True
    assert a.attackType == 'physical' and a.numTargets == 1 and isinstance(a.multiplier, Stat)
    assert a.regularAuto is False


def test_crit_effects_fire_from_the_first_crit():
    # E9: at 100% crit the first hit is a crit; '> 1' fired its effects one hit late
    c, spy = unit(), Spy()
    c.crit.base = 1.0
    c.doDamage(dummy(), [spy], 1.0, 140, 100, 'physical', 0)
    assert spy.crits == 1
    # 50%: effects on the 2nd and 4th hits
    c2, spy2 = unit(), Spy()
    fired = []
    for i in range(4):
        c2.doDamage(dummy(), [spy2], 0.5, 140, 100, 'physical', 0)
        fired.append(spy2.crits)
    assert fired == [0, 1, 1, 2]

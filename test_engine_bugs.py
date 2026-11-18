"""Engine review bugs E8 and E9 (docs/ASSUMPTIONS.md), on the combat events (events.py)."""
from champion import Champion
from events import CRIT, DAMAGE_POST, IS_ATTACK, ON_HIT, ON_SPELL, ONHIT_PRE, UNIT
from item import Item
from stats import Attack
from test_timing import dummy


class Spy(Item):
    LISTENS = {CRIT: frozenset(), DAMAGE_POST: frozenset(), ONHIT_PRE: frozenset()}

    def __init__(self):
        super().__init__(name='Spy')
        self.crits, self.seen = 0, []

    def performAbility(self, phase, time, champion, input_=0):
        if phase == CRIT:
            self.crits += 1
        else:
            self.seen.append((phase, input_.target, input_.dtype, input_.tags))


def unit():
    c = Champion('Unit', 1000, 100, 0, 30, 1.0, 0, 0, 1)
    c.items = []
    return c


def test_spell_and_attack_damage_carry_their_tags():
    # E8 was multiTargetSpell's simulated attacks built with fields in the wrong places; that path is gone, and what
    # tells a listener what hit is now the event: spell damage is the unit's spell, an attack's the unit's on-hit
    c, spy, d = unit(), Spy(), dummy()
    c.multiTargetSpell([d], [spy], 0, 1, lambda lvl, ad, ap: 100)
    (moment, target, dtype, tags), = spy.seen
    assert (moment, target, dtype) == (DAMAGE_POST, d, 'magical') and {UNIT, ON_SPELL} <= tags and IS_ATTACK not in tags
    spy.seen.clear()
    c.doAttack(Attack(opponents=[d]), [spy], 0)
    assert [s[0] for s in spy.seen] == [ONHIT_PRE, DAMAGE_POST]
    assert all(s[1] is d and {UNIT, IS_ATTACK, ON_HIT} <= s[3] for s in spy.seen)


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

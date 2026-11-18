"""Combat events (docs/RESTRUCTURE.md step 4): what items and traits react to, with the game's tags.

Every damage instance, attack release and hit is a CombatEvent. An item or trait listens by declaring
`LISTENS = {moment: tags}`: it hears an event at that moment when the event carries every one of those tags, the way
its script waits with WaitForDealDamage(required tags) or WaitGameplayEvent; it reacts in `on_event(moment, event,
champion)`. Listeners are told in the order of the champion's item list (items, then buffs, then the role).

Moments, each fired where the engine always fired it:
    LAUNCH         an attack releases, or a spell simulates one (Combat.Event.LaunchAttack; G11)
    ONHIT_PRE      before an attack's damage (PreApply): Titanic Hydra, Trickshot
    CRIT           the averaged crit counter passes 1 (I6), before that damage
    DAMAGE_POST    after each damage instance (PostApply): sunder, shred, True Damage's bonus
    ONHIT_AFTER    after an attack's damage and its mana: Wit's End, Lich Bane, Hellfire Hatchet
"""

LAUNCH = "Combat.Event.LaunchAttack"
ONHIT_PRE = "OnHit.PreApply"
CRIT = "Crit"
DAMAGE_POST = "DealDamage.PostApply"
ONHIT_AFTER = "OnHit.After"

# tags (the game's names, except where marked)
UNIT = "Damage.Source.Unit"
ITEM = "Damage.Source.Item"
TRAIT = "Damage.Source.Trait"  # engine label: True Damage's bonus, which nothing hears (B19)
IS_ATTACK = "AppliesOnHit.IsAttack"
ON_HIT = "OnHitDamage"  # the attack's own hit (not a Trickshot ricochet, which applies no on-hit effects)
ON_SPELL = "AppliesOnSpell"
SIMULATED = "Combat.Event.LaunchAttack.SimulateTriggersOnly"
TYPES = {"physical": "Damage.Type.Physical", "magical": "Damage.Type.Magic", "true": "Damage.Type.True"}


class CombatEvent(object):
    """One event: who caused it, at whom, how much (after resistances; None before the damage is known), its damage
    type, its tags, the time (seconds) and, for an on-hit damage, its on-hit effectiveness
    (Damage.SetByCaller.OnHitEffectivenessMultiplier: 1 for an attack; Ashe's flurry arrows 0.6; I11)."""
    __slots__ = ("source", "target", "amount", "dtype", "tags", "time", "effectiveness")

    def __init__(self, source, target=None, amount=None, dtype=None, tags=frozenset(), time=0.0, effectiveness=1.0):
        self.source = source
        self.target = target
        self.amount = amount
        self.dtype = dtype
        self.tags = tags
        self.time = time
        self.effectiveness = effectiveness


def damage_tags(dtype, *tags):
    """A damage instance's tags: its type and the given ones."""
    return frozenset((TYPES[dtype],) + tags)

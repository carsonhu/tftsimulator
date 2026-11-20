"""The fight viewer's recorder: everything one fight does, tick by tick, for the page to replay.

A Tracer is attached to one champion (`champion.tracer`) for one run; the table's runs never have one, and every
hook in the engine is a single `is not None` check. It records:

- damage: each instance (tick, target, amount after resistances, type, what dealt it);
- projectiles: launch tick, arrival tick, from and to (a unit, or a point in world units);
- marks: attack launches, casts (with their locks) and spell visuals (an area, a beam, a dash);
- a snapshot of the champion's and the dummies' stats as each tick ends, stored as changes only.

Units are numbered as the page draws them: 0 is the champion, 1.. the dummies in placement order (1 = the target).
"""

import sys

from events import IS_ATTACK, ITEM, ON_HIT, ON_SPELL
from timing import TPS

# Engine functions a damage instance passes through on its way to doDamage: the label is what called them
_PLUMBING = {"doDamage", "multiTargetSpell", "doAttack", "performAttack", "<lambda>", "fly", "_run_events",
             "schedule_tick", "update", "fire_attack", "on_event", "emit", "ability", "performAbility"}
# A champion's own overrides, by what they are: its spell, and passives riding on its attacks
_NAMED = {"performAbility": "cast", "performAttack": "passive", "onLaunch": "passive", "fire_attack": "empowered attack"}


def _r(x, n=4):
    return round(float(x), n)


class Tracer:
    def __init__(self, champion, opponents):
        self.champion = champion
        self.units = [champion] + list(opponents)
        self.damage_events = []
        self.projectiles = []
        self.marks = []
        self.snapshots = []  # (tick, {changed field: value}); the first holds every field
        self._last = {}

    # ------------------------------------------------------------------ recording
    def unit(self, u):
        """A unit's number on the page (0 the champion, 1.. the dummies), or a world point [x, y] as given."""
        if isinstance(u, (tuple, list)):
            return [_r(u[0], 1), _r(u[1], 1)]
        for i, x in enumerate(self.units):
            if x is u:
                return i
        return None

    def _source(self):
        """What dealt the damage being recorded: an item or trait by name, else the step of the champion's own code
        (e.g. 'record lands', 'burst', 'cast'), else None for the plain attack (champion.py's own functions)."""
        items = self.champion.items
        f = sys._getframe(2)
        for _ in range(16):
            if f is None:
                break
            owner = f.f_locals.get("self")
            if owner is not None and owner is not self.champion and any(owner is it for it in items):
                return getattr(owner, "name", type(owner).__name__)
            code = f.f_code
            path = code.co_filename.replace("\\", "/")
            if path.endswith("/champion.py") and code.co_name == "doAttack":
                return None  # an attack's own damage (or an attack ricochet): the kind says which
            if path.endswith("/set19champs.py"):
                # a lambda or closure: the innermost named function it sits in (co_qualname, Python 3.11+)
                parts = [p for p in getattr(code, "co_qualname", code.co_name).split(".")
                         if p not in ("<lambda>", "<locals>")]
                name = parts[-1] if parts else code.co_name
                if name in _NAMED:
                    return _NAMED[name]
                if name not in _PLUMBING:
                    return name.strip("_").replace("_", " ")
            f = f.f_back
        return None

    def damage(self, tick, target, amount, dtype, tags, crit_chance):
        if ITEM in tags:
            kind = "item"
        elif ON_SPELL in tags:
            kind = "spell"
        elif IS_ATTACK in tags:
            kind = "attack" if ON_HIT in tags else "ricochet"
        else:
            kind = "spell"
        self.damage_events.append({"t": tick, "to": self.unit(target), "v": _r(amount, 2), "type": dtype,
                                   "kind": kind, "by": self._source(), "crit": _r(crit_chance, 3)})

    def projectile(self, t0, t1, source, target, name):
        self.projectiles.append({"t0": t0, "t1": t1, "from": self.unit(source), "to": self.unit(target),
                                 "name": name})

    def mark(self, tick, kind, **data):
        out = {"t": tick, "kind": kind}
        for k, v in data.items():
            if isinstance(v, (list, tuple)) and v and not isinstance(v[0], (int, float)):
                out[k] = [self.unit(x) for x in v]
            elif hasattr(v, "hex"):
                out[k] = self.unit(v)
            elif isinstance(v, float):
                out[k] = _r(v)
            else:
                out[k] = v
        self.marks.append(out)

    # ------------------------------------------------------------------ snapshots
    @staticmethod
    def _mods(attr):
        return [[op, _r(value.value() if hasattr(value, "value") else value), key]  # AttributeBased: its value now
                for channel, op, value, key in attr.mods if key not in ("cap", "floor")]

    def _state(self, tick):
        c = self.champion
        s = {
            "ad": _r(c.atk.stat * c.bonus_ad.stat, 2), "adMult": _r(c.bonus_ad.stat), "ap": _r(c.ap.stat),
            "as": _r(c.aspd.stat), "crit": _r(min(c.crit.stat, 1)), "critDmg": _r(c.critDamage()),
            "amp": _r(c.dmgMultiplier.stat * c.extraDmgMultiplier.stat),
            "mana": _r(c.curMana, 2), "maxMana": _r(c.fullMana.stat, 2), "regen": _r(c.manaRegen.stat),
            "mpa": _r(c.manaPerAttack.stat), "manaMult": _r(c.manaGainMultiplier.stat),
            "armorPen": _r(c.armorPierce.stat), "mrPen": _r(c.mrPierce.stat), "omnivamp": _r(c.omnivamp.stat),
            "casting": tick < c.busy_until, "lockedUntil": c.mana_locked_until if tick < c.mana_locked_until else None,
            "busyUntil": c.busy_until if tick < c.busy_until else None,
            "attacks": c.numAttacks, "casts": c.numCasts,
            "effects": sorted(c.effects),
            "mods": {name: self._mods(getattr(c, attr)) for name, attr in (
                ("ad", "bonus_ad"), ("ap", "ap"), ("as", "aspd"), ("crit", "crit"), ("critDmg", "critDmg"),
                ("amp", "dmgMultiplier"), ("regen", "manaRegen"), ("mpa", "manaPerAttack"))},
        }
        for i, d in enumerate(self.units[1:], 1):
            s[f"d{i}"] = {"armor": _r(d.armor.stat, 2), "mr": _r(d.mr.stat, 2), "effects": sorted(d.effects)}
        return s

    def snapshot(self, tick):
        state = self._state(tick)
        changed = {k: v for k, v in state.items() if self._last.get(k) != v}
        if changed or not self.snapshots:
            self.snapshots.append([tick, changed])
        self._last = state

    # ------------------------------------------------------------------ out
    def to_dict(self, ticks):
        c = self.champion
        units = [{"name": c.name, "hex": list(c.hex), "champion": True}]
        for i, d in enumerate(self.units[1:], 1):
            units.append({"name": "Target" if i == 1 else f"Dummy {i}", "hex": list(d.hex),
                          "inPlay": bool(getattr(d, "in_play", True)), "hp": d.hp.stat})
        return {
            "tps": TPS, "ticks": ticks, "units": units, "range": c.attack_range,
            # what the champion carries: items, and the traits and augments that are on (a trait at level 0 is off;
            # one that says itself, active_for: Heartsteel with no member ticked on a non-member)
            "items": [getattr(it, "name", type(it).__name__) for it in c.items
                      if getattr(it, "name", "NoItem") not in ("NoItem", "NoBuff", "Role")
                      and (it.active_for(c) if hasattr(it, "active_for") else getattr(it, "level", 1) != 0)],
            "damage": self.damage_events, "projectiles": self.projectiles, "marks": self.marks,
            "snapshots": self.snapshots,
        }

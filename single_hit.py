"""One attack or one cast, at fixed stats: the page's Hit table (owner, 2026-11-19).

"If this champion attacked or cast at this moment, how much damage would it deal, with each item?" No fight is run:
the champion is set up as a fight starts (sim_entry._build_champion: level, bonuses, buff bar, items), plus the row's
item, on the page's dummies (layout.py), and then does one thing:

- an attack: one released attack (fire_attack, the champion's own: its passive on-hit damage counts), or
- a cast: the champion's spell (`_cast`) as it is at combat start (owner: the first cast, e.g. Ahri's 6 fox-fires),

after which everything the spell set in motion plays out (its scheduled hits, DoT ticks, the timed effects it
applies end on time), with no mana, attacks or item timers in between. The damage is every hit on every dummy,
summed (owner: all targets, as primary and secondary targets take different amounts), averaged over crit as the
simulator does.

Assumptions (owner, 2026-11-19): Last Whisper's sunder and Void Staff's shred are already on every dummy;
Striker's Flail has its full stacks; Archangel's Staff has the stacks of the slider's time; Kraken's Fury is left out
(its stacks need a fight). A champion can count per unit instead of per cast (HIT_PER: Jinx per rocket, Viego per
sword) or run its cast its own way (hit_cast); a cast that empowers the next attacks (Ashe's flurries, Olaf's axes,
Briar's slashes: HIT_EMPOWERED names the counter) includes them; a passive that fires every n-th attack (Kai'Sa's
missiles, Gnar's rock, Jhin's 4th shot: hit_attack_cycle) makes "an attack" the average over the n.
"""
import copy

from effects import expire_effects
from events import CRIT, LAUNCH, CombatEvent
from layout import Layout
from simulator import Simulator
from stats import Stat

FOREVER = 10 ** 9  # an assumed debuff or buff lasts the whole hit
MAX_TICKS = 60 * 30  # a spell's effects end well within a minute


def _assume(champion, dummies, items, seconds):
    """The table's assumptions, on the champion set up for the fight (its items include the row's)."""
    import set19items
    for item in items:
        if isinstance(item, set19items.ArchangelsStaff):  # the stacks of `seconds` (StackingItem timer)
            item.next_k = 1
            while seconds >= item.next_k * item.period_seconds(champion) - 1e-9:
                item.per_stack(champion)
                item.next_k += 1
        elif isinstance(item, set19items.StrikersFlail):  # full stacks, held for the whole hit
            for _ in range(int(item.row(champion, "MaxStacks"))):
                item.performAbility(CRIT, 0, champion)
            for name, effect in champion.effects.items():
                if name.startswith("StrikersFlail"):
                    effect.last_tick = FOREVER
        elif isinstance(item, (set19items.LastWhisper, set19items.VoidStaff)):  # already sundered / shredded
            for d in dummies:
                item.debuff(champion, d, 0, item.param_row(champion, item.LEVEL_PARAM), FOREVER / 30)


def setup(champion, enemy, extra, is_buff, layout=None, seconds=0.0):
    """A copy of the configured champion with the row's extra, on copies of the enemy placed by `layout`, its stats
    applied as a fight starts (Simulator.simulate's setup), and the table's assumptions. Returns (champion, dummies)."""
    layout = layout or Layout()
    champ = copy.deepcopy(champion)
    dummies = [copy.deepcopy(enemy) for _ in range(layout.count)]
    extra = copy.deepcopy(extra)
    items = ([] if is_buff else [extra]) + ([extra] if is_buff else []) + champ.items
    champ.items = items
    champ.opponents = dummies
    layout.place(champ, dummies)
    Simulator().itemStats(items, champ)
    champ.prepare_timing()
    champ.onUpdateItems = []  # no item timers run during the hit (Archangel's is set by _assume)
    for d in dummies:
        d.opponents = champ
    champ.tick = 0
    _assume(champ, dummies, items, seconds)
    return champ, dummies


def play_out(champ, dummies):
    """Run what the attack or cast scheduled, tick by tick, until nothing is pending: timed effects end on time (a
    buff whose end starts a finale, Kayle) and dummies' debuffs too."""
    tick = champ.tick
    while tick < MAX_TICKS and (champ.events or _pending_effects(champ)):
        tick += 1
        champ.tick = tick
        for d in dummies:
            if d.effects:
                expire_effects(d, tick)
        if champ.effects:
            expire_effects(champ, tick)
        champ._run_events()


def _pending_effects(champ):
    return any(e.last_tick < FOREVER for e in champ.effects.values())


def launch(champ, dummies):
    """One attack released the way the fight releases it (Champion._release, without the rhythm or mana): the
    animation it plays, the launch count and LaunchAttack, then the champion's own attack, played out."""
    if hasattr(champ, "_next_animation"):
        champ._next_animation()
    champ.launches += 1
    champ.onLaunch(dummies, champ.items)
    champ.emit(LAUNCH, CombatEvent(champ, time=champ.tick / 30), champ.items)
    champ.fire_attack(dummies, champ.items, "release", True)
    play_out(champ, dummies)


def attack(champ, dummies):
    """One attack; over a passive's cycle, the cycle's attacks (damage() divides by their number)."""
    for _ in range(hit_attack_cycle(champ)):
        launch(champ, dummies)


def hit_attack_cycle(champ):
    cycle = getattr(champ, "hit_attack_cycle", None)
    return int(cycle()) if cycle else 1


def cast(champ, dummies):
    """The champion's first cast, from a full bar, played out, with the attacks it empowers. Returns where its damage
    starts in dmgVector (after the cast itself for HIT_EMPOWERED_ONLY: Briar's slashes without the dash)."""
    start = len(champ.dmgVector)
    hook = getattr(champ, "hit_cast", None)
    if hook is not None:
        hook(dummies, champ.items)
    else:
        champ.curMana = champ.fullMana.stat
        champ._cast(dummies, champ.items, 0)
    play_out(champ, dummies)
    counter = getattr(champ, "HIT_EMPOWERED", None)
    if getattr(champ, "HIT_EMPOWERED_ONLY", False):
        start = len(champ.dmgVector)
    while counter and getattr(champ, counter) > 0:
        launch(champ, dummies)
    return start


def special(champ, dummies, mode):
    """A hit of the champion's own (HIT_MODES beyond attack and cast, e.g. Gnar's rock): hit_<mode>() readies the
    champion, then one attack is launched."""
    getattr(champ, f"hit_{mode}")()
    launch(champ, dummies)


CAST_ONLY = ("Magic Caster", "Magic Fighter")


def modes(champ):
    """The hits the table offers: attack and cast, except a Magic Caster or Magic Fighter, who only casts (owner,
    2026-11-19: Attack Casters such as Ezreal attack too; Magic Fighters such as Katarina don't). HIT_MODES overrides
    it (no spell: Gnar, Jhin; a spell that only gives attack speed: Kai'Sa) and can add its own (Gnar's rock)."""
    own = getattr(champ, "HIT_MODES", None)
    if own:
        return tuple(own)
    return ("cast",) if champ.role and champ.role.name in CAST_ONLY else ("attack", "cast")


def default_mode(champ):
    """The hit the table opens on: a Caster's cast, anyone else's first."""
    offered = modes(champ)
    return "cast" if "cast" in offered and champ.role and champ.role.archetype == "Caster" else offered[0]


def uses_ap(champ):
    """The AP item list for a "Magic ..." role, the AD list otherwise (owner, 2026-11-19)."""
    return bool(champ.role and champ.role.name.startswith("Magic"))


def item_lists(champ):
    """Which lists the table compares: "ad", "ap" or "both" (HIT_ITEMS = 'both': Yone, truly hybrid, owner)."""
    own = getattr(champ, "HIT_ITEMS", None)
    return own if own else ("ap" if uses_ap(champ) else "ad")


class _Recorder:
    """Every damage call of the hit (Champion.doDamage), split into its factors: the damage before amp (the amped
    damage over the champion's amp at that moment), the amp, the crit average and the armor/MR multiplier. The four
    multiply back to the damage done, hit by hit."""

    def __init__(self, champ, dummies):
        self.hits = []
        self.champ, self.dummies = champ, dummies
        original = champ.doDamage

        def do_damage(opponent, items, critChance, damageIfCrit, damage, dtype, time, *args, **kwargs):
            at = len(champ.dmgVector)
            amp = champ.dmgMultiplier.stat * champ.extraDmgMultiplier.stat
            crit = min(1, critChance)
            original(opponent, items, critChance, damageIfCrit, damage, dtype, time, *args, **kwargs)
            done = sum(row[1][0] for row in champ.dmgVector[at:])
            self.hits.append({"at": at, "target": next((i for i, d in enumerate(dummies) if d is opponent), -1),
                              "dtype": dtype, "amped": damage, "raw": damage / amp if amp else damage,
                              "avg": damage * (1 - crit) + damageIfCrit * crit, "done": done})

        champ.doDamage = do_damage

    def explain(self, before, divisor):
        """The hit's math: its stats as it starts, then damage = before amp x amp x crit x resists (sums over every
        hit from dmgVector index `before`, divided by `divisor` as the table divides: per rocket, per attack of a
        cycle)."""
        hits = [h for h in self.hits if h["at"] >= before]
        raw, amped, avg, done = (sum(h[k] for h in hits) for k in ("raw", "amped", "avg", "done"))
        resists = {}
        for dtype, stat in (("physical", "armor"), ("magical", "mr")):
            mine = [h for h in hits if h["dtype"] == dtype and h["avg"] > 0 and h["done"] > 0]
            if mine:  # the resist the damage met: 100 / multiplier - 100, damage-weighted
                mult = sum(h["done"] for h in mine) / sum(h["avg"] for h in mine)
                resists[stat] = round(100 / mult - 100, 1)
        c = self.champ
        return {
            "stats": {"ad": round(c.atk.stat * c.bonus_ad.stat, 1), "ap": round(c.ap.stat, 4),
                      "amp": round(c.dmgMultiplier.stat * c.extraDmgMultiplier.stat - 1, 4),
                      "crit": round(min(1, c.crit.stat), 4), "critdmg": round(c.critDamage(), 4),
                      "spellcrit": bool(c.canSpellCrit)},
            "hits": len(hits), "targets": len({h["target"] for h in hits}),
            "types": sorted({h["dtype"] for h in hits}),
            "raw": round(raw / divisor, 2),
            "amp": round(amped / raw, 4) if raw else 1, "crit": round(avg / amped, 4) if amped else 1,
            "resist": round(done / avg, 4) if avg else 1, "resists": resists,
        }


def damage(champion, enemy, extra, is_buff, mode, layout=None, seconds=0.0, explain=False):
    """The hit's damage after mitigation, every dummy summed (per HIT_PER unit when the champion counts one). With
    `explain`, (damage, its math: _Recorder.explain)."""
    champ, dummies = setup(champion, enemy, extra, is_buff, layout, seconds)
    recorder = _Recorder(champ, dummies) if explain else None
    stats = recorder and recorder.explain(len(champ.dmgVector), 1)["stats"]  # as the hit starts
    before = len(champ.dmgVector)
    if mode == "attack":
        attack(champ, dummies)
    elif mode == "cast":
        before = cast(champ, dummies)
    else:
        special(champ, dummies, mode)
    total = sum(row[1][0] for row in champ.dmgVector[before:])
    divisor = 1
    if mode == "attack":
        divisor = hit_attack_cycle(champ)
    per = getattr(champ, "hit_per", None)
    if mode == "cast" and per is not None:
        divisor = max(1, per())
    total /= divisor
    if recorder is None:
        return total
    math = recorder.explain(before, divisor)
    math["stats"] = stats
    math["divisor"] = divisor
    return total, math

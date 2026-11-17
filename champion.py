import heapq
import math
import random

import set18roles
import utils
from role import Role
from stats import AD, AP, ArmorPierce, Aspd, Attack, FastDeepCopy, Resist, Stat
from timing import TPS, Timing, ticks, ticks_up

import status


def _round_half_up(x):
    # tftFightSim rounds release times half away from zero (Rust f32::round); Python's round() is banker's
    return math.floor(x + 0.5)


class Champion(FastDeepCopy):
    canFourStar = False
    # set18 compat: the Set 18 content still in this repo times its champions with these (castTime and
    # manalockDuration are instance attributes below). A Set 19 champion sets self.timing instead (timing.Timing,
    # normally Timing.from_build). The tick rules are in update(); see docs/ASSUMPTIONS.md T1-T6.
    attackWindup = 0  # set18: post-cast attack start -> hit; becomes Timing.launch (no stretch)
    attackWindupRepeat = 0  # set18: > 0 marks a ranged unit with attack-start mana
    fillingAttackLead = 0  # set18: > 0 marks a ranged unit with on-hit mana (Karma, LeBlanc, ...)

    def __init__(
        self,
        name,
        hp,
        atk,
        curMana,
        fullMana,
        aspd,
        armor,
        mr,
        level,
        role=Role.ATTACK_TANK,
    ):
        self.name = name
        levels = [1, 1.5, 1.5**2, 1.5**3, 1.5**4]
        hp_levels = [1, 1.8, 1.8**2, 1.8**3, 1.8**4]
        self.hp = Stat(hp * hp_levels[level - 1], 1, 0)
        self.bonus_ad = AP(0, 1, 0)
        self.atk = AD(atk * levels[level - 1])
        self.curMana = curMana
        self.fullMana = Stat(fullMana, 1, 0)
        self.startingMana = 0
        self.aspd = Aspd(aspd, 1, 0)
        self.ap = AP(0, 1, 0)
        self.armor = Resist(armor, 1, 0)
        self.mr = Resist(mr, 1, 0)
        self.manaPerAttack = Stat(0, 1, 0)
        self.manaRegen = Stat(0, 1, 0)
        self.manaGainMultiplier = Stat(1, 1, 0)
        self.level = level
        self.dmgMultiplier = Stat(1, 1, 0)
        # 2nd damage multiplier, multiplied against dmgMultiplier rather than
        # summed into it -- for amps that stack multiplicatively with the
        # item/augment amp pool (Ravager). Sources here are still additive with
        # each other, so a third independent multiplier needs its own Stat.
        self.extraDmgMultiplier = Stat(1, 1, 0)
        self.crit = Stat(0.25, 1, 0)
        self.critDmg = Stat(1.4, 1, 0)
        self.omnivamp = Stat(0, 1, 0)
        # crit chance over 100% becomes crit damage at this ratio (set18 0.5; Set 19 data: CT_ExtraCritChanceToCritDamage)
        self.excess_crit_ratio = 0.5

        if not isinstance(role, Role):
            self.role = Role.ATTACK_TANK
        self.role = role

        # mana regen is paid in 0.25 s steps from t = 0 (G17: inherited from set18, open); index of the next step
        self.next_regen = 0

        self.armorPierce = ArmorPierce(0, 1, 0)
        self.mrPierce = ArmorPierce(0, 1, 0)

        self.canCrit = True
        self.canSpellCrit = False
        self.manalockDuration = 0  # set18 compat: mana lock in seconds (0 = castTime)
        self.castTime = 0  # set18 compat: cast lock in seconds
        self.base_aspd = aspd  # attack speed before items, for locks that scale with AS (G7)
        self.attack_range = 1  # hexes; Set 19 champions set it from the build
        self.timing = None  # timing.Timing; None = built from the set18 compat attributes at combat start
        self._compat_timing = False
        # tick state (update() is the only writer; everything is in whole ticks, T1)
        self.tick = 0
        self.busy_until = 0  # no attack starts before this tick (cast lock, T5)
        self.mana_locked_until = 0  # no mana gain before this tick (mana lock, T5)
        self.attacking = False  # an attack rhythm is under way
        self.attack_start_tick = -1  # start of the current or next attack
        self.release_tick = -1  # its release (ranged) or hit (melee)
        self.release_exact = 0.0  # exact release time in ticks: repeat attacks keep the fraction (T2)
        self.attacks_started = 0
        self._paid = False  # the current attack's mana is already paid
        self.full_since = None  # tick the bar became full; a cast comes one tick later (T4)
        self.events = []  # heap of (tick, seq, fn): projectile hits, delayed spell effects (T6)
        self._event_seq = 0
        self.items = [set18roles.ChampRole()]

        self.statuses = {}  # current statuses
        # Earliest next_update across self.statuses; lets the frame loop skip
        # the whole status pass while everything is just waiting.
        self.nextStatusUpdate = -1
        self.opponents = []
        self.dmgVector = []
        self.dmgDealt = 0 # no need to serialize
        self.alive = True
        self.lastDamagedOpponent = None

        # notes for user
        self.notes = ""

        # Takedowns
        self.takedowns = 0
        
        # Arbiter
        self.cause = ""
        self.effect = ""
        
        # Meep
        self.meep = 0

        # Blackthorn: the sacrificed ally on the hex. Role/Star Level/Cost
        # decide which stat package the trait hands over and how big it is;
        # set by class_utilities.blackthorn_selector. Cost 0 is "No Tier";
        # role "None" is an empty hex, i.e. no sacrifice and no effect.
        self.blackthorn_role = "None"
        self.blackthorn_star = 1
        self.blackthorn_cost = 1

        # Augments
        self.seraphim = False
        self.retribution = False
        self.embiggen = False

        self.tactician_level = 4
        self.first_takedown = 5  # time of first takedown
        self.stage = 2  # 2, 3, 4, 5, 6

        self.num_targets = 0
        self.num_extra_targets = 0
        self.item_count = 0  # number of craftables
        # Trait-count-scaling buffs read this. The Champion Selector page sets
        # it from a widget, but other pages don't, so it needs a default or
        # those buffs raise AttributeError.
        self.num_traits = 6

        self.critCounter = 0
        self.numAttacks = 0
        self.numCasts = 0
        self.luckyAbility = False
        self.luckyCrit = False

        # G18 (inherited from set18, open): a unit casts only after starting an attack since its last cast
        self.attacksOnLastCast = -1

        # Items subscribed to the "onUpdate" phase. Filled in by the Simulator
        # once combat starts; None means "ask every item", which is what
        # callers outside the simulator loop get.
        self.onUpdateItems = None

    def hashFunction(self):
        # Hash to cache champion data
        items_tuple = tuple(item.hashFunction() for item in self.items)
        stat_tuple = (
            self.name,
            self.hp.stat,
            self.atk.stat,
            self.aspd.stat,
            self.ap.stat,
            self.armor.stat,
            self.curMana,
            self.fullMana.stat,
            self.mr.stat,
            self.bonus_ad.stat,
            self.manaPerAttack.stat,
            self.manaRegen.stat,
            self.manaGainMultiplier.stat,
            self.level,
            self.dmgMultiplier.stat,
            self.crit.stat,
            self.critDmg.stat,
            self.omnivamp.stat,
            self.canCrit,
            self.canSpellCrit,
            self.castTime,
            self.tactician_level,
            self.first_takedown,
            self.takedowns,
            self.seraphim,
            self.retribution,
            self.embiggen,
            self.stage,
            self.num_targets,
            self.num_extra_targets,
            self.item_count,
            self.luckyAbility,
            self.cause,
            self.effect,
            self.meep,
            self.blackthorn_role,
            self.blackthorn_star,
            self.blackthorn_cost,
        )
        # return stat_tuple
        return items_tuple + stat_tuple

    def __hash__(self):
        # used for caching
        return hash(self.hashFunction())

    def applyStatus(self, status, champion, time, duration, params=0):
        """Apply status to self.

        Args:
            status (Status): Status to apply
            champion (Champion): Opponent who applied the status
            time (int): time of application
            duration (int): How long to apply for
            params (??): any extra params
        """
        if status.name not in self.statuses:
            self.statuses[status.name] = status
            self.statuses[status.name].application(
                self, champion, time, duration, params
            )
        else:
            if not self.statuses[status.name].active:
                self.statuses[status.name].application(
                    self, champion, time, duration, params
                )
            else:
                self.statuses[status.name].reapplication(
                    self, champion, time, duration, params
                )
        # Schedule changed; make the next frame look at the statuses again.
        self.nextStatusUpdate = -1

    def addPrecision(self):
        if self.canSpellCrit:
            self.critDmg.addStat(0.1)
        self.canSpellCrit = True

    # get basic stats from items
    def addStats(self, item) -> None:
        self.hp.addStat(item.hp)
        self.bonus_ad.addStat(item.ad)  # now we have multipicative AD only
        self.ap.addStat(item.ap)
        self.aspd.addStat(item.aspd)
        # self.curMana = min(self.curMana + item.mana, self.fullMana.stat)
        self.manaRegen.addStat(item.manaRegen)
        self.armor.addStat(item.armor)
        self.mr.addStat(item.mr)
        self.crit.addStat(item.crit / 100)
        self.dmgMultiplier.addStat(item.dmgMultiplier)
        self.omnivamp.addStat(item.omnivamp)

    def addStat(self, stat, amount):
        # separate function good for bad luck + holobow
        getattr(self, stat).addStat(amount)

    # ---------------------------------------------------------------- set18 compat views of the tick state
    @property
    def manalockTime(self):
        return self.mana_locked_until / TPS

    @manalockTime.setter
    def manalockTime(self, value):
        self.mana_locked_until = max(0, math.ceil(value * TPS - 1e-6))

    @property
    def nextAttackTime(self):
        return self.busy_until / TPS

    @nextAttackTime.setter
    def nextAttackTime(self, value):
        # set18 content holds attacks off (time + 9999) and releases them (time): the next attack starts fresh
        self.busy_until = max(0, math.ceil(value * TPS - 1e-6))
        self.attacking = False

    @property
    def attack_progress(self):
        return 1.0

    @attack_progress.setter
    def attack_progress(self, value):
        pass  # set18's continuous swing progress has no meaning on the tick engine

    @property
    def ranged(self):
        if self._compat_timing:
            return self.attackWindupRepeat > 0 or self.fillingAttackLead > 0
        return self.attack_range > 1

    # ---------------------------------------------------------------- casting and mana
    def canCast(self, time=None):
        """A full bar casts one tick after it filled (T4), never during a cast lock, and (G18, inherited) only after
        an attack has started since the last cast."""
        return (
            self.curMana >= self.fullMana.stat
            and self.fullMana.stat > -1
            and self.tick >= self.busy_until
            and self.full_since is not None
            and self.tick > self.full_since
            and self.attacks_started > self.attacksOnLastCast
        )

    def canAttack(self, time=None):
        return self.tick >= self.busy_until

    def addMana(self, amount, time=None) -> None:
        """Mana from any source, times the mana multiplier; none during a cast lock or a mana lock (T5)."""
        if self.tick >= self.busy_until and self.tick >= self.mana_locked_until:
            self.curMana += amount * self.manaGainMultiplier.stat

    def abilityScaling(self, level):
        # Abstract method
        return 0

    def __str__(self):
        return ",".join(
            (
                str(p)
                for p in (
                    self.hp.stat,
                    self.atk.stat,
                    self.aspd.stat,
                    self.ap.stat,
                )
            )
        )

    def attackTime(self):
        return 1 / self.aspd.stat

    def period_exact(self):
        """Attack period now, in exact (fractional) ticks."""
        return TPS / max(self.aspd.stat, 0.05)

    def period_ticks(self):
        return max(1, _round_half_up(self.period_exact()))

    def schedule(self, delay_seconds, fn):
        """Run fn() on the tick a client event `delay_seconds` from now lands on (T6). For spell effects that come
        after the cast starts (e.g. a second hit at 0.833 s): fn runs before this tick's cast and attack checks."""
        self.schedule_tick(self.tick + ticks_up(delay_seconds), fn)

    def schedule_tick(self, tick, fn):
        self._event_seq += 1
        heapq.heappush(self.events, (tick, self._event_seq, fn))

    def _run_events(self):
        while self.events and self.events[0][0] <= self.tick:
            _, _, fn = heapq.heappop(self.events)
            fn()

    def performAttack(
        self,
        opponents,
        items,
        time,
        multiplier=None,
        generateMana=True,
    ):
        """One attack's effects: 'preAttack' items, the damage, attack mana (when generateMana), 'postAttack' items.
        The engine calls this when the attack lands, with generateMana only if the mana is due on the hit (T3)."""
        newAttack = Attack(
            opponents=opponents,
            multiplier=multiplier if multiplier is not None else Stat(0, 1, 0),
            canCrit=True,
            canOnHit=True,
            attackType="physical",
            numTargets=1,
        )
        for item in items:
            item.ability("preAttack", time, self, newAttack)

        self.doAttack(newAttack, items, time)

        if generateMana:
            self.addMana(self.manaPerAttack.stat)

        for item in items:
            item.ability("postAttack", time, self)

    def performAbility(self, opponents, items, time):
        # abstract method
        return 0

    def startAttack(self, opponents, items, time):
        """set18 compat: an extra attack that lands at once, outside the attack rhythm, with its mana."""
        self.numAttacks += 1
        self.attacks_started += 1
        self.performAttack(opponents, items, time, Stat(0, 1, 0))

    # ---------------------------------------------------------------- the attack rhythm (T2, T3)
    def _mana_moment(self):
        return self.timing.mana_moment(self.ranged)

    def _begin_attack(self, items, time):
        """An attack starts this tick: count it and pay start mana (T3). A ranged unit whose mana comes later pays
        at the start an attack whose mana fills the bar (T3, Set 18: Karma, LeBlanc, Veigar, Cinderling,
        Cassiopeia); returns True if this attack's mana is paid."""
        self.attacks_started += 1
        moment = self._mana_moment()
        gain = self.manaPerAttack.stat * self.manaGainMultiplier.stat
        if moment == 'start' or (self.ranged and self.curMana + gain >= self.fullMana.stat > -1):
            self.addMana(self.manaPerAttack.stat)
            return True
        return False

    def _start_fresh_attack(self, items, time):
        """Combat start, the end of a cast lock, or an attack reset: a fresh attack starts now and releases one
        windup later (G2, T5)."""
        self.attacking = True
        self.attack_start_tick = self.tick
        self.release_tick = self.tick + self.timing.release_ticks(self.period_ticks())
        self.release_exact = float(self.release_tick)
        self._paid = self._begin_attack(items, time)

    def _release(self, opponents, items, rhythm=True, paid=None):
        """The attack releases (ranged) or hits (melee) this tick. With `rhythm`, the next attack is scheduled one
        exact period after this release (T2). `paid`: whether this attack's mana is already paid (default: the
        current attack's flag; an attack kept through a cast passes its own)."""
        paid = self._paid if paid is None else paid
        moment = self._mana_moment()
        if moment == 'release' and not paid:
            self.addMana(self.manaPerAttack.stat)
            paid = True
        if rhythm:
            tick = self.tick
            base = self.release_exact if tick == self.release_tick else float(tick)
            self.release_exact = base + self.period_exact()
            self.release_tick = max(_round_half_up(self.release_exact), tick + 1)
            self.attack_start_tick = max(tick + 1, self.release_tick - self.timing.release_ticks(self.period_ticks()))
            self._paid = False
        flight = self.timing.flight_ticks(self.attack_range)

        def land():
            self.numAttacks += 1
            self.performAttack(opponents, items, self.tick / TPS, Stat(0, 1, 0),
                               generateMana=(moment == 'hit' and not paid))

        if flight == 0:
            land()
        else:
            self.schedule_tick(self.tick + flight, land)

    def _attack_phase(self, opponents, items, time):
        if self.tick < self.busy_until:
            return
        if not self.attacking:
            self._start_fresh_attack(items, time)
        elif self.tick == self.attack_start_tick:
            self._paid = self._begin_attack(items, time)
        if self.tick == self.release_tick:
            self._release(opponents, items)

    def _cast(self, opponents, items, time):
        self.numCasts += 1
        for item in items:
            item.ability("preAbility", time, self)
        self.performAbility(opponents, items, time)
        if self._compat_timing:
            self.timing.cast_lock = self.castTime
            self.timing.mana_lock = self.manalockDuration if self.manalockDuration > 0 else None
        cast_lock, mana_lock = self.timing.scaled_locks(self.base_aspd, self.aspd.stat)
        tick = self.tick
        self.busy_until = tick + max(1, ticks(cast_lock))
        self.mana_locked_until = tick + ticks(mana_lock)
        # overflow mana is kept (G10, inherited, open); startingMana is the bar after a cast (some champions)
        self.curMana = self.curMana - self.fullMana.stat + self.startingMana
        self.full_since = None
        self.attacksOnLastCast = self.attacks_started
        if self.attacking:
            # T4: a ranged attack already under way still releases during the cast (unless the cast cancels it);
            # any other attack in progress is lost. The rhythm restarts with a fresh attack after the cast lock.
            under_way = self.attack_start_tick <= tick < self.release_tick
            if under_way and self.ranged and not self.timing.cast_cancels_attack:
                kept_paid = self._paid
                self.schedule_tick(self.release_tick,
                                   lambda: self._release(opponents, items, rhythm=False, paid=kept_paid))
            self.attacking = False
        for item in items:
            item.ability("postAbility", time, self)

    def prepare_timing(self):
        """Called once at combat start: set18 content gets a Timing from its compat attributes."""
        if self.timing is None:
            self._compat_timing = True
            self.timing = Timing(
                launch=self.attackWindup, cast_lock=self.castTime,
                mana_lock=self.manalockDuration if self.manalockDuration > 0 else None,
                mana_at=('hit' if self.fillingAttackLead > 0 else ('start' if self.attackWindupRepeat > 0 else 'hit')),
                source={'all': 'set18 compat attributes'})

    def updateStatuses(self, time):
        """Tick this champion's statuses and nothing else.

        The opponents in a simulation are inert damage sponges: the simulator
        pushes their next attack past the end of combat, they hold no items, and
        nothing reads their mana or attack counters. Shred/corrosion/DoT
        statuses on them still have to tick, so this is the only part of
        update() they need.
        """
        # List copy to avoid RuntimeError: dictionary changed size during iteration
        for statusa in list(self.statuses.values()):
            if time >= statusa.next_update:
                statusa.update(self, time)

        # Recompute from the live dict: a status that just ticked has moved its
        # own schedule on, and one may have added another status.
        soonest = float("inf")
        for statusa in self.statuses.values():
            if statusa.next_update < soonest:
                soonest = statusa.next_update
        self.nextStatusUpdate = soonest

    def update(self, opponents, items, time):
        """One tick (T1). Order: statuses, mana regen, onUpdate items, scheduled events (projectile hits, spell
        effects), the cast check, the attack rhythm. A bar that fills during a tick casts on the next one (T4)."""
        self.tick = _round_half_up(time * TPS)
        self.opponents = opponents
        if self.statuses and time >= self.nextStatusUpdate:
            self.updateStatuses(time)

        # mana regen in 0.25 s steps from t = 0 (G17, inherited), each paid on the first tick at or after its time
        while self.tick >= math.ceil(self.next_regen * 0.25 * TPS - 1e-9):
            self.next_regen += 1
            self.addMana(self.manaRegen.stat / 4)

        for item in self.onUpdateItems if self.onUpdateItems is not None else items:
            item.ability("onUpdate", time, self)
        self._run_events()

        if self.full_since is None and self.curMana >= self.fullMana.stat > -1:
            self.full_since = self.tick
        if opponents and self.canCast(time):
            self._cast(opponents, items, time)
        if opponents:
            self._attack_phase(opponents, items, time)
        if self.full_since is None and self.curMana >= self.fullMana.stat > -1:
            self.full_since = self.tick

    def baseAtkDamage(self, attack, multiplier):
        # just an extra method for abilities which attack for a % of your AD,
        # like Runaans
        # Probably does result in some niche buggy interactions

        return (attack + multiplier.add) * multiplier.mult

    def doAttack(self, attack, items, time):
        # Activating onhits
        # onAttack is currently unused
        if attack.canOnHit:
            for item in items:
                item.ability("onAttack", time, self, attack.opponents)

        baseDmg = self.baseAtkDamage(
            attack.scaling(self.level, self.atk.stat, self.bonus_ad.stat, self.ap.stat),
            attack.multiplier,
        )
        baseCritDmg = baseDmg
        if attack.canCrit:
            baseCritDmg *= self.critDamage()
        baseDmg *= self.dmgMultiplier.stat * self.extraDmgMultiplier.stat
        baseCritDmg *= self.dmgMultiplier.stat * self.extraDmgMultiplier.stat
        crit_chance = self.crit.stat if attack.canCrit else 0 # only increment crit if we can actually crit
        for target in range(attack.numTargets):
            self.doDamage(
                attack.opponents[target],
                items,
                crit_chance,
                baseCritDmg,
                baseDmg,
                attack.attackType,
                time,
            )

    def critDamage(self):
        # Crit chance < 1: critdmg.stat
        # Crit chance > 1: add half the overfill crit chance to dmg
        return self.critDmg.stat + max(0, (self.crit.stat - 1) * self.excess_crit_ratio)

    def doDamage(
        self,
        opponent,
        items,
        critChance,
        damageIfCrit,
        damage,
        dtype,
        time,
        is_spell=False,
        source_item=None,
        ability_armor_pierce=0,
        ability_mr_pierce=0,
    ):
        """Actually doing damage: consider
            average of damage if crit and damage

        Args:
            opponent (Champion): opp to do dmg to
            items (List[item]): List of active items/buffs
            critChance (float)
            damageIfCrit (float)
            damage (float): dmg if not crit
            dtype (str): "physical", "magical", "true"
            time (int)
            is_spell (bool, optional): is it spell damage?
        """
        #
        # if not crit
        critChance = min(1, critChance)
        if getattr(self, "luckyCrit", False):
            critChance = utils.lucky_chance(critChance)
        self.critCounter += critChance
        if self.critCounter > 1:
            for item in items:
                if item != source_item:
                    # pass whether it's spell for holobow
                    item.ability("onCrit", time, self, is_spell)
            self.critCounter -= 1

        preDmg = damage
        preCritDmg = damageIfCrit

        avgDmg = preDmg * (1 - critChance) + preCritDmg * critChance
        # if anything needs to modify the damage dealt
        for item in items:
            avgDmg = item.ability("onDealDamage", time, self, avgDmg)
        # if only spell dmg needs to be modified (Arcana Xerath)
        if is_spell:
            for item in items:
                avgDmg = item.ability("onDealSpellDamage", time, self, avgDmg)

        avgDmg = self.damage(avgDmg, dtype, opponent, ability_armor_pierce, ability_mr_pierce)
        self.dmgDealt += avgDmg[0]
        # PostOnDealDamage's input_ carries the damage amount but not who it
        # hit; on-hit effects that need the specific target (e.g. Executioner
        # applying a bleed) read this instead of threading a new param
        # through every item.ability() call.
        self.lastDamagedOpponent = opponent
        for item in items:
            # if you need to track how much dmg was actually dealt
            item.ability("PostOnDealDamage", time, self, avgDmg)

        if is_spell:
            for item in items:
                item.ability("PostOnDealSpellDamage", time, self, avgDmg)

        if avgDmg:
            # record (Time, Damage Dealt, current AS, current Mana, full Mana)
            self.dmgVector.append(
                (time, avgDmg, self.aspd.stat, self.curMana, self.fullMana.stat)
            )


    def multiTargetSpell(
        self,
        opponents,
        items,
        time,
        targets,
        scaling,
        type="magical",
        numAttacks=0,
        ability_armor_pierce=0,
        ability_mr_pierce=0,
    ):
        """Cast a damage-dealing spell

        Args:
            opponents (List[Champion]): List of opponents
            items (List[item]): active items & buffs
            time (float): current float
            targets (int): # targets
            scaling (func): damage func(level, AD, AP)
            type (str, optional): physical, magical, true
            numAttacks (int, optional): # of attacks to apply for guinsoo/runaans
        """
        baseDmg = scaling(self.level, self.bonus_ad.stat, self.ap.stat)
        baseCritDmg = baseDmg
        self.numAttacks += numAttacks
        newAttack = Attack(opponents, Stat(0, 1, 0), "physical", 1, regularAuto=False)
        for attacks in range(numAttacks):
            # activate onhits, currently unused
            for item in items:
                item.ability("preAttack", time, self, newAttack)
        if self.canSpellCrit:
            baseCritDmg *= self.critDamage()

        for opponent in opponents[0:targets]:
            multipliedDmg = (
                baseDmg * self.dmgMultiplier.stat * self.extraDmgMultiplier.stat
            )
            multipliedCritDmg = (
                baseCritDmg * self.dmgMultiplier.stat * self.extraDmgMultiplier.stat
            )
            critChance = self.crit.stat if self.canSpellCrit else 0
            self.doDamage(
                opponent,
                items,
                critChance,
                multipliedCritDmg,
                multipliedDmg,
                type,
                time,
                is_spell=True,
                ability_armor_pierce=ability_armor_pierce,
                ability_mr_pierce=ability_mr_pierce,
            )

        for attacks in range(numAttacks):
            for item in items:
                item.ability("postAttack", time, self)

    def damage(self, dmg, dtype, defender, ability_armor_pierce=0, ability_mr_pierce=0):
        """deal dmg, dmg is premitigated

        Args:
            dmg (FLOAT): for basic attacks, it's just atk. sometimes
            dtype (STRING): physical/magical/true
            defender (Champion): recipient
        """
        # Pierce past 100% ignores no more than 100% does, and shred can't take
        # a resist below 0 -- so neither end can turn into bonus damage.
        if dtype == "physical":
            total_pierce = self.armorPierce.stat + ability_armor_pierce - self.armorPierce.stat * ability_armor_pierce
            defense = max(0, defender.armor.stat) * (1 - min(total_pierce, 1))
        elif dtype == "magical":
            total_pierce = self.mrPierce.stat + ability_mr_pierce - self.mrPierce.stat * ability_mr_pierce
            defense = max(0, defender.mr.stat) * (1 - min(total_pierce, 1))
        elif dtype == "true":
            defense = 0

        # also add in 'damageTaken' modifier
        dModifier = 100 / (100 + defense)
        return (dmg * dModifier, dtype)

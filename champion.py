import heapq
import math
import random

import utils
from stats import AD, AP, ArmorPierce, Aspd, Attack, FastDeepCopy, Resist, Stat
from timing import TPS, Timing, ticks, ticks_up

import status


def _round_half_up(x):
    # tftFightSim rounds release times half away from zero (Rust f32::round); Python's round() is banker's
    return math.floor(x + 0.5)


class Champion(FastDeepCopy):
    """The engine's unit. Set 19 champions subclass build_champion.BuildChampion, which fills every number from
    the selected build; this base class takes HP and AD as already scaled to the unit's star level. Timing comes
    from self.timing (timing.Timing); the tick rules are in update() (docs/ASSUMPTIONS.md T1-T9)."""
    canFourStar = False
    default_traits = []  # trait classes the UI preselects for this champion

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
    ):
        self.name = name
        # HP and AD are this star level's values (Set 19: from the build, B1); no scaling here
        self.hp = Stat(hp, 1, 0)
        self.bonus_ad = AP(0, 1, 0)
        self.atk = AD(atk)
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

        self.role = None  # build_champion.BuildRole for Set 19 champions

        # mana regen is paid in 0.25 s steps from t = 0 (G17: inherited from set18, open); index of the next step
        self.next_regen = 0

        self.armorPierce = ArmorPierce(0, 1, 0)
        self.mrPierce = ArmorPierce(0, 1, 0)

        self.canCrit = True
        self.canSpellCrit = False
        self.base_aspd = aspd  # attack speed before items, for locks that scale with AS (G7)
        self.attack_range = 1  # hexes; Set 19 champions set it from the build
        self.timing = None  # timing.Timing (BuildChampion: Timing.from_build); required before combat
        # tick state (update() is the only writer; everything is in whole ticks, T1)
        self.tick = 0
        self.busy_until = 0  # no attack starts before this tick (cast lock, T5)
        self.mana_locked_until = 0  # no mana gain before this tick (mana lock, T5)
        self.attacking = False  # an attack rhythm is under way
        self.attack_start_tick = -1  # start of the current or next attack
        self.release_tick = -1  # its release (ranged) or hit (melee)
        self.release_exact = 0.0  # exact release time in ticks: repeat attacks keep the fraction (T2)
        self.attacks_started = 0
        self.launches = 0  # attack releases this combat (LaunchAttack events; picks sequential animations, B13)
        self.start_exact = 0.0  # exact start of the current attack, for units with sequential animations (B13)
        self.last_start_exact = 0.0
        self._paid = False  # the current attack's mana is already paid
        self.full_since = None  # tick the bar became full; a cast comes one tick later (T4)
        self.events = []  # heap of (tick, seq, fn): projectile hits, delayed spell effects (T6)
        self._event_seq = 0
        self.items = []  # role effects, items and buffs (BuildChampion adds its RoleEffects)

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

        # scenario inputs the UI sets (not game data)
        self.takedowns = 0
        self.tactician_level = 4
        self.first_takedown = 5  # time of first takedown
        self.stage = 2  # 2, 3, 4, 5, 6
        self.num_targets = 0
        self.num_extra_targets = 0
        self.item_count = 0  # number of craftables

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
            self.tactician_level,
            self.first_takedown,
            self.takedowns,
            self.stage,
            self.num_targets,
            self.num_extra_targets,
            self.item_count,
            self.luckyAbility,
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

    @property
    def ranged(self):
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

    # ---------------------------------------------------------------- the attack rhythm (T2, T3)
    def _mana_moment(self):
        return self.timing.mana_moment(self.ranged)

    def _begin_attack(self, items, time):
        """An attack starts this tick: count it, and pay its mana if the unit pays at the start (T3). Returns True if
        this attack's mana is paid."""
        self.attacks_started += 1
        if self._mana_moment() == 'start':
            self.addMana(self.manaPerAttack.stat)
            return True
        return False

    def _fills_bar(self):
        gain = self.manaPerAttack.stat * self.manaGainMultiplier.stat
        return self.curMana + gain >= self.fullMana.stat > -1

    def _start_fresh_attack(self, items, time):
        """Combat start, the end of a cast lock, or an attack reset: a fresh attack starts now and releases one
        windup later (G2, T5)."""
        self.attacking = True
        self.attack_start_tick = self.tick
        self.start_exact = float(self.tick)
        self.release_tick = self.tick + self.timing.release_ticks(self.period_ticks(), *self._next_animation(),
                                                                 crit=self._animation_crit())
        self.release_exact = float(self.release_tick)
        self._paid = self._begin_attack(items, time)

    def _next_animation(self):
        """(selector, attack speed) for the attack starting next (B13): GA_ForceSequentialAttack counts launches."""
        if not self.timing.variants:
            return None, None
        return self.launches % self.timing.animations + 1, self.aspd.stat

    def _animation_crit(self):
        """The attack's crit chance, for a unit whose crits play their own animation (B17)."""
        return self.crit.stat if self.timing.crit_animation else 0.0

    def _time_next_attack(self):
        """B13: the next attack starts one period (at the current attack speed) after the last one started and
        releases its own animation's windup later."""
        tick = self.tick
        self.start_exact = self.last_start_exact + self.period_exact()
        self.release_exact = self.start_exact + self.timing.windup_seconds(
            self.period_ticks(), *self._next_animation(), crit=self._animation_crit()) * TPS
        self.release_tick = max(_round_half_up(self.release_exact), tick + 1)
        self.attack_start_tick = max(tick + 1, min(_round_half_up(self.start_exact), self.release_tick - 1))

    def onLaunch(self, opponents, items):
        """An attack releases (the LaunchAttack event). Champions whose passive counts launches override this."""

    def simulateLaunch(self, items):
        """GE_SimulateLaunchAttack (a cast's 'simulated attack'): GA_SimulateLaunchAttack sends
        Combat.Event.LaunchAttack.SimulateTriggersOnly, which every non-exact Combat.Event.LaunchAttack listener hears
        (G11; VOD4 Ezreal: Titan's Resolve stacks). Items react in their 'onLaunch' phase; the attack itself, its
        mana and the champion's own launch count are not touched."""
        for item in items:
            item.ability("onLaunch", self.tick / TPS, self)

    def _release(self, opponents, items, rhythm=True, paid=None):
        """The attack releases (ranged) or hits (melee) this tick. With `rhythm`, the next attack is scheduled one
        exact period after this release (T2). `paid`: whether this attack's mana is already paid (default: the
        current attack's flag; an attack kept through a cast passes its own)."""
        paid = self._paid if paid is None else paid
        moment = self._mana_moment()
        # T3: pay at the release; a ranged unit that pays on the hit pays at the release an attack whose mana fills
        # the bar (Set 18 replays: Karma, LeBlanc, Veigar, Cinderling, Cassiopeia, at the "Hold" event = release)
        if not paid and (moment == 'release' or (moment == 'hit' and self.ranged and self._fills_bar())):
            self.addMana(self.manaPerAttack.stat)
            paid = True
        self.launches += 1
        self.onLaunch(opponents, items)
        for item in items:
            item.ability("onLaunch", self.tick / TPS, self)  # Combat.Event.LaunchAttack listeners (Titan's Resolve)
        if rhythm and self.timing.variants:
            # B13: attack starts are one period apart and each releases its own animation's windup later, so the
            # releases of different animations are not a period apart (Kai'Sa, VOD3)
            self.last_start_exact = self.start_exact
            self._time_next_attack()
            self._paid = False
        elif rhythm:
            tick = self.tick
            base = self.release_exact if tick == self.release_tick else float(tick)
            self.release_exact = base + self.period_exact()
            self.release_tick = max(_round_half_up(self.release_exact), tick + 1)
            self.attack_start_tick = max(tick + 1, self.release_tick - self.timing.release_ticks(
                self.period_ticks(), crit=self._animation_crit()))
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
        cast_lock, mana_lock = self.timing.scaled_locks(self.base_aspd, self.aspd.stat)
        tick = self.tick
        if self.timing.cast_keeps_rhythm:
            # T12: the spell ends on activation and cancels nothing: the attack rhythm runs on (Kai'Sa, VOD3); the
            # attack after it keeps the period it was timed with (re-timing it at the new attack speed ran 6 ticks
            # early within four attacks on VOD3)
            self.mana_locked_until = tick + ticks(mana_lock)
            self.curMana = self.curMana - self.fullMana.stat + self.startingMana
            self.full_since = None
            self.attacksOnLastCast = self.attacks_started
            for item in items:
                item.ability("postAbility", time, self)
            return
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
        """Called once at combat start."""
        if self.timing is None:
            raise ValueError(f'{self.name} has no timing (BuildChampion sets it from the build)')

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
        if self.critCounter >= 1:
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
        newAttack = Attack(
            opponents=opponents, multiplier=Stat(0, 1, 0), attackType="physical", numTargets=1,
            regularAuto=False,
        )
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

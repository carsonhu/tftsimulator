"""Set 19 champions: build_champion.BuildChampion subclasses. A class is live only when it is named in champ_list.

Each champion is added after its worksheet (champions/<Name>.md) has the evidence its timing needs (decision D5).
Numbers are read from the selected build by name; what the code itself states (which event spawns which projectile,
how the damage is built) is the champion's script, cited by file and offset.
"""
import set19buffs
from build_champion import BuildChampion
from champion import Champion
from timing import TPS, Timing, projectile_ticks, ticks_up


class Neeko(BuildChampion):
    """K/DA Fan Club (champions/Neeko.md). Script: GA_Neeko19_SpellUsingVFX (build ga_scripts.zip).

    The cast timeline CD_Neeko19_CastAnimWithClone fires Throw1-Throw6; each throw plays a projectile chrono
    (script 0x18e3 switch). Throws 1, 2 and 4 spawn 'Popper' missiles at full effectiveness; throws 3, 5 and 6 spawn
    'Encore' missiles whose effectiveness is CT_Encore19 RecastEffectiveness at the Encore trait level (0 when Encore
    is inactive: those missiles then deal nothing). The Encore tier comes from the Encore trait buff
    (set19buffs.Encore). Each missile applies GE_Neeko19_Damage on arrival:
    MagicDamageCalc1 (DamageAP x AP) x effectiveness, magic, spell damage, crits only if the spell can crit.
    """
    KEY = 'DA_Neeko19'
    CAST = 'CD_Neeko19_CastAnimWithClone'
    THROWS = (  # (cast event, projectile chrono, projectile name, Encore missile?)
        ('Throw1', 'CD_Neeko19_Projectile1', 'Popper', False),
        ('Throw2', 'CD_Neeko19_Projectile2', 'Popper', False),
        ('Throw3', 'CD_Neeko19_Projectile3_Encore', 'Encore', True),
        ('Throw4', 'CD_Neeko19_Projectile4', 'Popper', False),
        ('Throw5', 'CD_Neeko19_Projectile5_Encore', 'Encore', True),
        ('Throw6', 'CD_Neeko19_Projectile6_Encore', 'Encore', True),
    )

    def __init__(self, level, build=None):
        super().__init__(level, build)
        # read every number now, so a build that lacks one fails at construction, not mid-fight
        self.throws = [(self.chrono_event(self.CAST, ev), self.chrono_projectile_speed(ch, name), encore)
                       for ev, ch, name, encore in self.THROWS]
        self.notes = ('Kill passive (+1% AP per kill) not modelled: dummies never die. Spell missiles take the '
                      'straight-line travel time at the attack range (arc height ignored, G4).')

    def missile_effectiveness(self, encore):
        if not encore:
            return 1
        return self.trait_value('DA_Encore19', 'RecastEffectiveness')  # at the board's Encore tier (B11)

    def abilityScaling(self, level, AD, AP):
        return self.row('DamageAP', star=level) * AP

    def performAbility(self, opponents, items, time):
        hexes = self.attack_range  # the target stands at attack range (G4)
        for t, speed, encore in self.throws:
            eff = self.missile_effectiveness(encore)
            if eff <= 0:
                continue  # an Encore missile without Encore applies 0 damage

            def land(eff=eff):
                self.multiTargetSpell(opponents, items, self.tick / TPS, 1,
                                      lambda level, AD, AP: self.abilityScaling(level, AD, AP) * eff, 'magical')

            self.schedule_tick(self.tick + ticks_up(t) + projectile_ticks(speed, hexes), land)


class Varus(BuildChampion):
    """One Thousand Arrows (champions/Varus.md). Script: GA_Varus19_Spell (build ga_scripts.zip).

    The cast chrono CD_Varus19_CastAnim spawns a 'HailMain' missile at its Fire point (0.4278 s) and, in its Encore
    group (plays only for an Encore unit), an 'EncoreHailMain' missile at its Encore point (0.6286 s); the other
    'Hail' missiles are visual. HailMain's arrival (OnArrived -> 0x111b -> 0x960) applies GE_Varus19_PrimaryDamage
    to the target and GE_Varus19_SecondaryDamage to enemies within AOEHexRange of it, at effectiveness 1;
    EncoreHailMain's (-> 0x121f -> 0x2e4) does the same at CT_Encore19 RecastEffectiveness (Encore tier, B11). Both
    are physical spell damage that crits only with Precision (RollIfCanSpellCrit): Primary = PhysicalDamageCalc1 =
    DamageAP x AP + DamageAD x AD; Secondary = PhysicalDamageCalc2 = AOEDamagePercent x Calc1.
    AD here is the AttackDamage attribute, a multiplier (1.0 base, items add to it), like AP.
    """
    KEY = 'DA_Varus19'
    CAST = 'CD_Varus19_CastAnim'
    MISSILES = (('HailMain', False), ('EncoreHailMain', True))  # (projectile, Encore missile?)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        # set18 convention: num_targets counts the target; the splash hits num_targets - 1 adjacent enemies
        self.num_targets = 2
        self.missiles = [(self.chrono_projectile_spawn(self.CAST, name), self.chrono_projectile_speed(self.CAST, name),
                          encore) for name, encore in self.MISSILES]
        self.splash = self.row('AOEDamagePercent')
        self.notes = ('Slow (20% AS for 4 s) not modelled: dummies never attack. Adjacent enemies hit = '
                      'targets - 1. Missiles take the straight-line travel time at the attack range (arc ignored, G4).')

    def abilityScaling(self, level, AD, AP):
        return self.row('DamageAP', star=level) * AP + self.row('DamageAD', star=level) * AD

    def performAbility(self, opponents, items, time):
        hexes = self.attack_range
        for t, speed, encore in self.missiles:
            eff = 1 if not encore else self.trait_value('DA_Encore19', 'RecastEffectiveness')
            if eff <= 0:
                continue  # without Encore the Encore missile is not spawned (its chrono group needs the tag)

            def land(eff=eff):
                now = self.tick / TPS
                self.multiTargetSpell(opponents[:1], items, now, 1,
                                      lambda level, AD, AP: self.abilityScaling(level, AD, AP) * eff, 'physical')
                if self.num_targets > 1:
                    self.multiTargetSpell(opponents[1:], items, now, self.num_targets - 1,
                                          lambda level, AD, AP: self.abilityScaling(level, AD, AP) * eff * self.splash,
                                          'physical')

            self.schedule_tick(self.tick + ticks_up(t) + projectile_ticks(speed, hexes), land)


class Draven(BuildChampion):
    """You Spin Me Round (Like An Axe) (champions/Draven.md, D1). Scripts: GA_Draven19_Spell,
    GA_Draven19_TrickshotHandler (build ga_scripts.zip).

    The cast chrono CD_Draven19_Spell throws 'Blade' at the attack target at its PlayPoint (0.6566 s) on an
    accelerating spline (1500 units/s, +2000/s, max 2500: 14 ticks over 4 hexes, P12). Its arrival (OnArrived ->
    0x0f) applies GE_Draven19_SpellBaseDamage (PhysicalDamageCalc1 = BladeDamage x AD) to the target, starts the
    vortex (CD_Draven19_BladeRiftBase -> CD_Draven19_BladeRift, both spawning at 0 and attached to the target) and
    sends the Trickshot bounce event (0x753). The vortex (0xe49) repeats every TickRate 0.5 s (the script's default)
    trunc(Duration / TickRate) = 6 times, the first at once (UAbilityTask_Repeat); each applies
    GE_Draven19_SpellSecondaryDamage x 1 / (enemies in it) to the enemies in it (the attached target alone when
    none). PhysicalDamageCalc2 (BladeRiftPerSecondAD x AD + BladeRiftPerSecondAP x AP) is a per-second value, so a
    hit is Calc2 x TickRate (owner, 2026-11-17: the tooltip's per-second damage, not double it); total per vortex
    3 x Calc2, split among identical dummies, so it is booked on the target.
    Trickshot (TrickshotHandler): ricochet k flies CD_Draven19_Spell_Trickshot's Blade (speed 2000) to the next
    enemy and does the same at MMC_TrickshotReduction = RichochetDamage^k (base hit and its own vortex), up to
    NumRichochets. All hits are physical spell damage that crits only with Precision (RollIfCanSpellCrit).
    """
    KEY = 'DA_Draven19'
    CAST = 'CD_Draven19_Spell'
    BOUNCE = 'CD_Draven19_Spell_Trickshot'
    VORTEX_TICK = 0.5  # GA_Draven19_Spell default TickRate (script literal, not a curve row)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.throw_at = self.chrono_projectile_spawn(self.CAST, 'Blade')
        self.vortex_hits = int(self.row('Duration') / self.VORTEX_TICK)
        self.notes = ("The vortex's damage is booked on the record's target: it splits among the enemies inside, which "
                      "adds up to the same total on identical dummies. Ricochets go to the next dummy, 1 hex away.")

    def record_damage(self, level, AD, AP):
        return self.row('BladeDamage', star=level) * AD

    def vortex_damage(self, level, AD, AP):
        return self.row('BladeRiftPerSecondAD', star=level) * AD + self.row('BladeRiftPerSecondAP', star=level) * AP

    def performAbility(self, opponents, items, time):
        flight = self.chrono_projectile_ticks(self.CAST, 'Blade', self.attack_range)
        self.schedule_tick(self.tick + ticks_up(self.throw_at) + flight, lambda: self._record_lands(opponents, 0))

    def _record_lands(self, opponents, k):
        """The record (k = 0) or its k-th Trickshot ricochet arrives."""
        items = self.items
        eff = self.trait_value('DA_Trickshot19', 'RichochetDamage') ** k if k else 1
        target = opponents[k % len(opponents)]
        self.multiTargetSpell([target], items, self.tick / TPS, 1,
                              lambda level, AD, AP: self.record_damage(level, AD, AP) * eff, 'physical')
        for j in range(self.vortex_hits):
            def vortex_hit():
                self.multiTargetSpell([target], items, self.tick / TPS, 1,
                                      lambda level, AD, AP: self.vortex_damage(level, AD, AP) * self.VORTEX_TICK * eff,
                                      'physical')
            self.schedule_tick(self.tick + ticks_up(j * self.VORTEX_TICK), vortex_hit)
        if k < self.trait_value('DA_Trickshot19', 'NumRichochets'):
            step = self.chrono_projectile_ticks(self.BOUNCE, 'Blade', set19buffs.bounce_hexes(opponents))
            self.schedule_tick(self.tick + step, lambda: self._record_lands(opponents, k + 1))


class Kaisa(BuildChampion):
    """Make it Rain (champions/Kaisa.md, D1). Scripts: GA_Kaisa19_Passive, GA_Kaisa19_Spell,
    GA_Kaisa19_TrickshotHandler (build ga_scripts.zip).

    Passive (GA_Kaisa19_Passive): it counts her attack launches (Combat.Event.LaunchAttack, 0x2b9a) and every
    NumAttacksForMissiles-th fires NumMissiles missiles at once (FireMissiles, 0x2c54): each plays
    CD_Kaisa19_SpellMissile ('SpellMis', speed 1900, spawning at 0). A running missile count alternates them between her
    target and up to MaxSecondaryTargets enemies within HexSearchRangeAroundCurrentTarget of it
    (1 / PercentMissilesOnCurrentTarget). Each arrival (0x33a8) applies GE_Kaisa19_MissileDamage =
    PhysicalDamageCalc1 = ADDamage x AD + APDamage x AP (physical spell damage, crits only with Precision) and sends
    the Trickshot bounce event. Ricochet k (GA_Kaisa19_TrickshotHandler) flies CD_Kaisa19_SpellMissileTrickshot (1900)
    to the next enemy for the same damage x RichochetDamage^k (B12).
    Spell (GA_Kaisa19_Spell): GE_Kaisa19_AttackSpeedBuff = AttackSpeed MultiplyAdditive (1 + ASOnCast) for ASDuration
    (60 s: the rest of combat), stacking per cast; it finishes on activation and cancels nothing (T12).
    Her attacks cycle 4 animations whose windups differ (B13).
    """
    KEY = 'DA_Kaisa19'
    MISSILE = 'CD_Kaisa19_SpellMissile'
    BOUNCE = 'CD_Kaisa19_SpellMissileTrickshot'

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.every = int(self.row('NumAttacksForMissiles'))
        self.num_missiles = int(self.row('NumMissiles'))
        self.missiles_fired = 0
        self.launch_count = 0
        self.notes = ("Missiles alternate between the target and nearby enemies (identical dummies, same total); "
                      "secondary targets are taken at her attack range. Ricochets go to the next dummy, 1 hex away.")

    def missile_damage(self, level, AD, AP):
        return self.row('ADDamage', star=level) * AD + self.row('APDamage', star=level) * AP

    def onLaunch(self, opponents, items):
        self.launch_count += 1
        if self.launch_count % self.every:
            return
        flight = self.chrono_projectile_ticks(self.MISSILE, 'SpellMis', self.attack_range)
        secondaries = opponents[1:1 + int(self.row('MaxSecondaryTargets'))] or opponents[:1]
        on_target = 1 / self.row('PercentMissilesOnCurrentTarget')
        for _ in range(self.num_missiles):
            if self.missiles_fired % on_target > 0:
                target = secondaries[self.missiles_fired // 2 % len(secondaries)]
            else:
                target = opponents[0]
            self.missiles_fired += 1
            self.schedule_tick(self.tick + flight, lambda target=target: self._missile_lands(opponents, target, 0))

    def _missile_lands(self, opponents, target, k):
        eff = self.trait_value('DA_Trickshot19', 'RichochetDamage') ** k if k else 1
        self.multiTargetSpell([target], self.items, self.tick / TPS, 1,
                              lambda level, AD, AP: self.missile_damage(level, AD, AP) * eff, 'physical')
        if k < self.trait_value('DA_Trickshot19', 'NumRichochets'):
            nxt = opponents[(opponents.index(target) + 1) % len(opponents)]
            step = self.chrono_projectile_ticks(self.BOUNCE, 'SpellMis', set19buffs.bounce_hexes(opponents))
            self.schedule_tick(self.tick + step, lambda: self._missile_lands(opponents, nxt, k + 1))

    def performAbility(self, opponents, items, time):
        # MultiplyAdditive (1 + ASOnCast): +ASOnCast x 100 attack speed points, for the rest of combat (ASDuration 60)
        self.aspd.addStat(self.row('ASOnCast') * 100)


class Yunara(BuildChampion):
    """Cultivation of Teen Spirit (champions/Yunara.md, D1). Scripts: GA_Yunara19_Spell, GA_Yunara19_Passive (build
    ga_scripts.zip).

    Spell: GE_Yunara19_EmpoweredAttack adds NumOrbsToAdd to her Stack attribute for the rest of combat (stacking per
    cast); it finishes on activation and cancels nothing (T12).
    Passive: on each attack launch (Combat.Event.LaunchAttack, 0x3587) with Stack >= 1 it plays CD_Yunara19_OrbMis at
    her attack target, fitted to a fixed duration of 0.5 / AttackSpeed (DeterminePlayrate), with MissileSelector tags
    1..min(Stack, MaxVisualOrbs 11) (AddTagsToDetermineMissiles): orb i spawns at the chrono's i-th projectile time,
    scaled to that duration, and flies at 1850 units/s. Each arrival applies GE_Yunara19_AbilityDamage =
    GetDamagePerVISUALOrb = Calc1 x (1 + (Stack - 11 if > 0) / 11), Calc1 = ADDamage x AD + APDamage x AP: in total
    Stack x Calc1 per attack. Physical spell damage, crits only with Precision.
    """
    KEY = 'DA_Yunara19'
    ORBS = 'CD_Yunara19_OrbMis'
    MAX_VISUAL_ORBS = 11  # GA_Yunara19_Passive default (script literal)
    PLAYRATE = 0.5  # DeterminePlayrate: the orb chrono lasts 0.5 / AttackSpeed s (script literal)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.stacks = 0
        ch = self.chrono(self.ORBS)
        self.orb_times = sorted(t for p in ch.get('projectiles') or [] if p['name'] == 'Yunara19_OrbMis'
                                for t in p.get('spawn_at') or [])
        self.orb_chrono_len = ch['length']
        self.notes = "Orbs fly to her target at her attack range (4 hexes); the i-th orb takes the chrono's i-th spawn time."

    def orb_damage(self, level, AD, AP):
        return self.row('ADDamage', star=level) * AD + self.row('APDamage', star=level) * AP

    def onLaunch(self, opponents, items):
        stacks = int(self.stacks)
        if stacks < 1:
            return
        visual = min(stacks, self.MAX_VISUAL_ORBS)
        per_orb = 1 + max(0, stacks - self.MAX_VISUAL_ORBS) / self.MAX_VISUAL_ORBS
        duration = self.PLAYRATE / self.aspd.stat
        flight = self.chrono_projectile_ticks(self.ORBS, 'Yunara19_OrbMis', self.attack_range)
        for t in self.orb_times[:visual]:
            spawn = t / self.orb_chrono_len * duration
            self.schedule_tick(self.tick + ticks_up(spawn) + flight, lambda: self.multiTargetSpell(
                opponents[:1], self.items, self.tick / TPS, 1,
                lambda level, AD, AP: self.orb_damage(level, AD, AP) * per_orb, 'physical'))

    def performAbility(self, opponents, items, time):
        self.stacks += self.row('NumOrbsToAdd')


class Ziggs(BuildChampion):
    """GlitterBOM3S (champions/Ziggs.md, D1). Scripts: GA_Ziggs19_Spell, GA_Ziggs19_LaunchProjectileAttack (build
    ga_scripts.zip).

    Passive: every attack applies GE_Ziggs19_AutoAttack, whose second damage application is MagicDamageCalc3
    (AADamageAP x AP) magic spell damage (AppliesOnSpell, crits only with Precision), on the same hit as the physical
    attack.
    Spell: CD_Ziggs19_CastAnim plays at rate FClamp(AttackSpeed / base AttackSpeed, 1, 2) (0x4c1-0x689), so the cast
    lock, mana lock and the 'MainBomb' spawn (0.3183 s, 1900 units/s) all shorten by that rate. The bomb's arrival
    (OnArrived -> 0xa3e) applies GE_Ziggs19_PrimaryDamage (MagicDamageCalc1 = InitialDamage x AP) to the target and
    GE_Ziggs19_SecondaryDamage (MagicDamageCalc2 = SecondaryDamageAP x AP) to the other enemies within 1 hex of it
    (0x5d). Both magic spell damage, crit only with Precision. The bomb's first OnFired applies GE_SimulateLaunchAttack
    (Combat.Event.LaunchAttack.SimulateTriggersOnly): not modelled, see notes.
    """
    KEY = 'DA_Ziggs19'
    CAST = 'CD_Ziggs19_CastAnim'
    BOMB = 'MainBomb'
    CAST_RATE_CLAMP = (1, 2)  # GA_Ziggs19_Spell 0x635: FClamp(AttackSpeed / base, 1, 2)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.timing.lock_speed_clamp = self.CAST_RATE_CLAMP
        self.timing.source['lock_speed_clamp'] = 'GA_Ziggs19_Spell 0x635 FClamp(AS / base AS, 1, 2)'
        # set18 convention (as Varus): num_targets counts the target; the splash hits num_targets - 1 adjacent enemies
        self.num_targets = 2
        self.bomb_spawn = self.chrono_projectile_spawn(self.CAST, self.BOMB)
        self.notes = ('Hyperpop (Hype levels between rounds) not modelled. The bomb\'s simulated attack (on-attack '
                      'triggers only) is not modelled: no listed item reacts to it and its role mana would fall '
                      'inside the mana lock. Adjacent enemies hit = targets - 1. The bomb flies his attack range.')

    def bomb_damage(self, level, AD, AP):
        return self.row('InitialDamage', star=level) * AP

    def splash_damage(self, level, AD, AP):
        return self.row('SecondaryDamageAP', star=level) * AP

    def passive_damage(self, level, AD, AP):
        return self.row('AADamageAP', star=level) * AP

    def performAttack(self, opponents, items, time, multiplier=None, generateMana=True):
        super().performAttack(opponents, items, time, multiplier, generateMana)
        self.multiTargetSpell(opponents[:1], items, time, 1, self.passive_damage, 'magical')

    def performAbility(self, opponents, items, time):
        rate = self.timing.cast_rate(self.base_aspd, self.aspd.stat)
        flight = self.chrono_projectile_ticks(self.CAST, self.BOMB, self.attack_range)

        def land():
            now = self.tick / TPS
            self.multiTargetSpell(opponents[:1], items, now, 1, self.bomb_damage, 'magical')
            if self.num_targets > 1:
                self.multiTargetSpell(opponents[1:], items, now, self.num_targets - 1, self.splash_damage, 'magical')

        self.schedule_tick(self.tick + ticks_up(self.bomb_spawn / rate) + flight, land)


class Senna(BuildChampion):
    """Reverberation Devastation (champions/Senna.md, D1). Script: GA_Senna19_Spell (build ga_scripts.zip).

    The cast checks the attack target for her GE_Senna19_Marker (0xf25-0x11de):
    - unmarked: FireBlast (0x17ba) plays CD_Senna19_CastAnim1; its 'SennaMis' missile (0.7859 s, 4000 units/s)
      applies GE_Senna19_Marker and GE_Senna19_Damage (PhysicalDamageCalc1 = SpellAD x AD + SpellAP x AP) on arrival
      (0x509). It also applies GE_SimulateLaunchAttack at once (0x1bfe), under the mana lock (G11: not modelled).
    - marked: CD_Senna19_CastAnim2; at its 'Damage' event (0.2851 s, 0x761 -> 0x36) the marker is removed and
      GE_Senna19_MarkerDamage (PhysicalDamageCalc2 = MarkerPercentOfSpellAD x Calc1) applied; the SoulRip projectile
      flying back to her gives GE_Senna19_Cast2Buff (OutgoingDamageMultiplier + BonusDA, infinite, no stack limit,
      0xc5b) for the rest of combat.
    The marker is infinite (its Duration row is not used), so against dummies her casts alternate blast, detonate.
    Each cast ends at its own Unlock (EndSpell: mana lock removed, FinishCasting): CastAnim1 1.1984 s, CastAnim2
    0.9864 s. Both damages are physical spell damage that crits only with Precision.
    """
    KEY = 'DA_Senna19'
    BLAST = 'CD_Senna19_CastAnim1'
    RIP = 'CD_Senna19_CastAnim2'

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.marked = False
        self.blast_spawn = self.chrono_projectile_spawn(self.BLAST, 'SennaMis')
        self.rip_damage = self.chrono_event(self.RIP, 'Damage')
        # cast lock = the Unlock event rounded up to a tick, + 1 tick; mana lock = the Unlock tick (the build's rule
        # for the spell timeline it predicts, which is CastAnim1's)
        self.locks = {name: self._locks(name) for name in (self.BLAST, self.RIP)}
        if abs(self.locks[self.BLAST][0] - self.timing.cast_lock) > 1e-3:
            raise ValueError(f'Senna: CastAnim1 lock {self.locks[self.BLAST]} differs from the build timeline '
                             f'{self.timing.cast_lock}')
        self.notes = ('True Damage and Hitmaker not modelled. The detonation buff (+8% damage amp, stacking) is '
                      'applied at the detonation: nothing of hers lands before that cast ends, so its return flight '
                      'time does not matter. Crits play a slower attack animation: the windup is weighted by crit '
                      'chance (B17).')

    def _locks(self, chrono):
        unlock = ticks_up(self.chrono_event(chrono, 'Unlock')) / TPS
        return unlock + 1 / TPS, unlock

    def blast_damage(self, level, AD, AP):
        return self.row('SpellAD', star=level) * AD + self.row('SpellAP', star=level) * AP

    def rip_damage_value(self, level, AD, AP):
        return self.row('MarkerPercentOfSpellAD', star=level) * self.blast_damage(level, AD, AP)

    def performAbility(self, opponents, items, time):
        # the spell's own timeline sets this cast's locks; Champion._cast reads them after this call
        chrono = self.RIP if self.marked else self.BLAST
        self.timing.cast_lock, self.timing.mana_lock = self.locks[chrono]
        if not self.marked:
            def land():
                self.multiTargetSpell(opponents[:1], items, self.tick / TPS, 1, self.blast_damage, 'physical')
                self.marked = True

            flight = self.chrono_projectile_ticks(self.BLAST, 'SennaMis', self.attack_range)
            self.schedule_tick(self.tick + ticks_up(self.blast_spawn) + flight, land)
        else:
            def detonate():
                self.multiTargetSpell(opponents[:1], items, self.tick / TPS, 1, self.rip_damage_value, 'physical')
                self.marked = False
                self.dmgMultiplier.addStat(self.row('BonusDA'))

            self.schedule_tick(self.tick + ticks_up(self.rip_damage), detonate)


champ_list = ['Neeko', 'Varus', 'Draven', 'Kaisa', 'Yunara', 'Ziggs', 'Senna']


class TrainingDummy(Champion):
    """The opponents: they never attack, cast or die (G9); the UI sets their HP, armor and MR."""

    def __init__(self, level=1):
        super().__init__('Training Dummy', 1800, 0, 0, -1, 0.01, 100, 100, 1)
        self.timing = Timing(source={'all': 'dummy: never attacks'})

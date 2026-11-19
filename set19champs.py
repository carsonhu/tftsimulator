"""Set 19 champions: build_champion.BuildChampion subclasses. A class is live only when it is named in champ_list.

Each champion is added after its worksheet (champions/<Name>.md) has the evidence its timing needs (decision D5).
Numbers are read from the selected build by name; what the code itself states (which event spawns which projectile,
how the damage is built) is the champion's script, cited by file and offset.
"""
import math
import layout
import set19buffs
from build_champion import BuildChampion
from buildstore import BuildDataError
from champion import Champion
from stats import Attack, AttributeBased, Stat
from items.debuffs import apply_shred
from traits.classical import captivate
from events import CRIT, IS_ATTACK, ON_HIT, ON_SPELL, ONHIT_AFTER, ONHIT_PRE, TRAIT, UNIT, CombatEvent, damage_tags
from timing import HEX_UNITS, TPS, Timing, projectile_ticks, ticks_up


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
        hexes = self.target_hexes()  # the layout's target, at attack range (G4)
        for t, speed, encore in self.throws:
            eff = self.missile_effectiveness(encore)
            if eff <= 0:
                continue  # an Encore missile without Encore applies 0 damage

            def land(eff=eff):
                self.multiTargetSpell(opponents, items, self.tick / TPS, 1,
                                      lambda level, AD, AP: self.abilityScaling(level, AD, AP) * eff, 'magical')

            self.fly(self.tick + ticks_up(t), projectile_ticks(speed, hexes), opponents[0], land, name='missile')


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
    AREA = True  # its damage depends on the page's number of targets (layout.py)
    CAST = 'CD_Varus19_CastAnim'
    MISSILES = (('HailMain', False), ('EncoreHailMain', True))  # (projectile, Encore missile?)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.aoe = int(self.row('AOEHexRange'))
        self.missiles = [(self.chrono_projectile_spawn(self.CAST, name), self.chrono_projectile_speed(self.CAST, name),
                          encore) for name, encore in self.MISSILES]
        self.splash = self.row('AOEDamagePercent')
        self.notes = ('Slow (20% AS for 4 s) not modelled: dummies never attack. The splash hits the enemies '
                      'next to the target (the layout). Missiles take the straight-line travel time at the attack range (arc ignored, G4).')

    def abilityScaling(self, level, AD, AP):
        return self.row('DamageAP', star=level) * AP + self.row('DamageAD', star=level) * AD

    def performAbility(self, opponents, items, time):
        hexes = self.target_hexes()
        for t, speed, encore in self.missiles:
            eff = 1 if not encore else self.trait_value('DA_Encore19', 'RecastEffectiveness')
            if eff <= 0:
                continue  # without Encore the Encore missile is not spawned (its chrono group needs the tag)

            def land(eff=eff):
                now = self.tick / TPS
                self.multiTargetSpell(opponents[:1], items, now, 1,
                                      lambda level, AD, AP: self.abilityScaling(level, AD, AP) * eff, 'physical')
                splash = self.nearby(opponents[0], self.aoe)  # within AOEHexRange of the target
                self.trace('area', at=opponents[0], hit=splash)
                self.multiTargetSpell(splash, items, now, len(splash),
                                      lambda level, AD, AP: self.abilityScaling(level, AD, AP) * eff * self.splash,
                                      'physical')

            self.fly(self.tick + ticks_up(t), projectile_ticks(speed, hexes), opponents[0], land, name='missile')


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
                      "adds up to the same total on identical dummies. Ricochets go to the nearest dummy not yet "
                      "hit (the layout).")

    def record_damage(self, level, AD, AP):
        return self.row('BladeDamage', star=level) * AD

    def vortex_damage(self, level, AD, AP):
        return self.row('BladeRiftPerSecondAD', star=level) * AD + self.row('BladeRiftPerSecondAP', star=level) * AP

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        flight = self.chrono_projectile_ticks(self.CAST, 'Blade', self.target_hexes(target))
        self.fly(self.tick + ticks_up(self.throw_at), flight, target, lambda: self._record_lands(target, [target], 0),
                 name='record')

    def _record_lands(self, target, hit, k):
        """The record (k = 0) or its k-th Trickshot ricochet arrives at `target`; `hit` = the enemies hit so far."""
        items = self.items
        eff = self.trait_value('DA_Trickshot19', 'RichochetDamage') ** k if k else 1
        self.multiTargetSpell([target], items, self.tick / TPS, 1,
                              lambda level, AD, AP: self.record_damage(level, AD, AP) * eff, 'physical')
        self.trace('area', at=target, hit=[], name='vortex', seconds=self.vortex_hits * self.VORTEX_TICK)
        for j in range(self.vortex_hits):
            def vortex_hit():
                self.multiTargetSpell([target], items, self.tick / TPS, 1,
                                      lambda level, AD, AP: self.vortex_damage(level, AD, AP) * self.VORTEX_TICK * eff,
                                      'physical')
            self.schedule_tick(self.tick + ticks_up(j * self.VORTEX_TICK), vortex_hit)
        if k < self.trait_value('DA_Trickshot19', 'NumRichochets'):
            nxt, hexes = self.ricochet(target, hit)
            step = self.chrono_projectile_ticks(self.BOUNCE, 'Blade', hexes)
            self.fly(self.tick, step, nxt, lambda: self._record_lands(nxt, hit + [nxt], k + 1), source=target,
                     name='ricochet')


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
                      "each missile flies its own target's distance on the dummy layout. Ricochets go to the nearest "
                      "dummy not yet hit.")

    def missile_damage(self, level, AD, AP):
        return self.row('ADDamage', star=level) * AD + self.row('APDamage', star=level) * AP

    def onLaunch(self, opponents, items):
        self.launch_count += 1
        if self.launch_count % self.every:
            return
        near = self.nearby(opponents[0], int(self.row('HexSearchRangeAroundCurrentTarget')))
        secondaries = near[:int(self.row('MaxSecondaryTargets'))] or opponents[:1]
        on_target = 1 / self.row('PercentMissilesOnCurrentTarget')
        for _ in range(self.num_missiles):
            if self.missiles_fired % on_target > 0:
                target = secondaries[self.missiles_fired // 2 % len(secondaries)]
            else:
                target = opponents[0]
            self.missiles_fired += 1
            # each missile flies its own target's distance on the layout (owner, 2026-11-17)
            flight = self.chrono_projectile_ticks(self.MISSILE, 'SpellMis', self.target_hexes(target))
            self.fly(self.tick, flight, target, lambda target=target: self._missile_lands(target, [target], 0),
                     name='missile')

    def _missile_lands(self, target, hit, k):
        eff = self.trait_value('DA_Trickshot19', 'RichochetDamage') ** k if k else 1
        self.multiTargetSpell([target], self.items, self.tick / TPS, 1,
                              lambda level, AD, AP: self.missile_damage(level, AD, AP) * eff, 'physical')
        if k < self.trait_value('DA_Trickshot19', 'NumRichochets'):
            nxt, hexes = self.ricochet(target, hit)
            step = self.chrono_projectile_ticks(self.BOUNCE, 'SpellMis', hexes)
            self.fly(self.tick, step, nxt, lambda: self._missile_lands(nxt, hit + [nxt], k + 1), source=target,
                     name='ricochet')

    def performAbility(self, opponents, items, time):
        # MultiplyAdditive (1 + ASOnCast), for the rest of combat (ASDuration 60)
        self.aspd.modify("MultiplyAdditive", 1 + self.row('ASOnCast'))


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
        flight = self.chrono_projectile_ticks(self.ORBS, 'Yunara19_OrbMis', self.target_hexes())
        for t in self.orb_times[:visual]:
            spawn = t / self.orb_chrono_len * duration
            self.fly(self.tick + ticks_up(spawn), flight, opponents[0], lambda: self.multiTargetSpell(
                opponents[:1], self.items, self.tick / TPS, 1,
                lambda level, AD, AP: self.orb_damage(level, AD, AP) * per_orb, 'physical'), name='orb')

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
    (Combat.Event.LaunchAttack.SimulateTriggersOnly): on-attack items hear it (simulateLaunch, G11).
    """
    KEY = 'DA_Ziggs19'
    AREA = True  # its damage depends on the page's number of targets (layout.py)
    CAST = 'CD_Ziggs19_CastAnim'
    BOMB = 'MainBomb'
    CAST_RATE_CLAMP = (1, 2)  # GA_Ziggs19_Spell 0x635: FClamp(AttackSpeed / base, 1, 2)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.timing.lock_speed_clamp = self.CAST_RATE_CLAMP
        self.timing.source['lock_speed_clamp'] = 'GA_Ziggs19_Spell 0x635 FClamp(AS / base AS, 1, 2)'
        self.bomb_spawn = self.chrono_projectile_spawn(self.CAST, self.BOMB)
        self.notes = ('The bomb\'s simulated attack triggers on-attack items (Titan\'s Resolve); its role mana '
                      'would fall inside the mana lock. The splash hits the enemies next to the target (the '
                      'layout). The bomb flies his attack range.')

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
        flight = self.chrono_projectile_ticks(self.CAST, self.BOMB, self.target_hexes())

        def land():
            now = self.tick / TPS
            self.multiTargetSpell(opponents[:1], items, now, 1, self.bomb_damage, 'magical')
            splash = self.nearby(opponents[0], 1)  # the other enemies within 1 hex (0x5d)
            self.trace('area', at=opponents[0], hit=splash)
            self.multiTargetSpell(splash, items, now, len(splash), self.splash_damage, 'magical')

        spawn = self.tick + ticks_up(self.bomb_spawn / rate)
        self.schedule_tick(spawn, lambda: self.simulateLaunch(items))  # 0x9f5: the bomb's first OnFired (G11)
        self.fly(spawn, flight, opponents[0], land, name='bomb')


class Senna(BuildChampion):
    """Reverberation Devastation (champions/Senna.md, D1). Script: GA_Senna19_Spell (build ga_scripts.zip).

    The cast checks the attack target for her GE_Senna19_Marker (0xf25-0x11de):
    - unmarked: FireBlast (0x17ba) plays CD_Senna19_CastAnim1; its 'SennaMis' missile (0.7859 s, 4000 units/s)
      applies GE_Senna19_Marker and GE_Senna19_Damage (PhysicalDamageCalc1 = SpellAD x AD + SpellAP x AP) on arrival
      (0x509). It also applies GE_SimulateLaunchAttack at once (0x1bfe): on-attack items hear it (G11).
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

            flight = self.chrono_projectile_ticks(self.BLAST, 'SennaMis', self.target_hexes())
            self.fly(self.tick + ticks_up(self.blast_spawn), flight, opponents[0], land, name='blast')
            self.simulateLaunch(items)  # 0x1bfe: the blast's GE_SimulateLaunchAttack, at once (G11)
        else:
            def detonate():
                self.multiTargetSpell(opponents[:1], items, self.tick / TPS, 1, self.rip_damage_value, 'physical')
                self.marked = False
                self.dmgMultiplier.modify("+", self.row('BonusDA'))

            self.schedule_tick(self.tick + ticks_up(self.rip_damage), detonate)


class Ezreal(BuildChampion):
    """Bite the Bullet (champions/Ezreal.md, D1). Script: GA_Ezreal19_Spell (build ga_scripts.zip).

    Stage 1 (0x1247): CD_Ezreal19_CastAnim fires 'SpellMis' (the mark: CD_Ezreal19_Spell1_Tar, no damage). Its Unlock
    event (0.6663 s) calls FireAtTarget (0x16ba), which plays CD_Ezreal19_CastAnim2: its root 'SpellMis' (0.1729 s,
    2200 units/s) detonates on arrival (0x66 -> 0x382): GE_Ezreal19_DamagePrimary = PhysicalDamageCalc1 (ADDamage x
    AD + APDamage x AP) on the target and GE_Ezreal19_DamageSecondary = PhysicalDamageCalc2 (AoEPercentDamage x Calc1)
    on the other enemies within 1 hex. With the Set19.Trait.Encore tag the chrono's SecondCast group adds a second
    'SpellMis' (0.319 s): FirstCastHit, set by the first detonation of the cast, makes it deal x CT_Encore19
    RecastEffectiveness (DetermineDamageForSpell). CastAnim2's Unlock ends the spell (the build's 36-tick cast lock,
    35-tick mana lock). Physical spell damage, crits only with Precision.
    Each stage applies GE_SimulateLaunchAttack (0x168a, 0x1ce5 -> 0xf): on-attack items hear both (G11; VOD4: two
    Titan's Resolve stacks per cast).
    Heartsteel upgrade (IsHeartsteelUpgradeActive: the SpellUpgradeTierIsActive and Selected tags, i.e. a Bias at
    Heartsteel (3)+, `heartsteel_bias`): DetermineDamageForSpell multiplies both the primary and the secondary damage
    by 1 + HeartsteelStan_PercentIncreasedAbilityDamage (0.25). Every cast first adds 1 to the combat-only spell Stack
    (GE_IncSpellStackBy1_CombatOnly, 0x10ed); Stack % 3 == 0 (casts 3, 6, ...) makes it a 2-hex cast (Is2HexCast,
    0x11b5): TR_Add_EnemiesWithinHexRange with HexRange 2 instead of 1 picks the secondary targets (the layout's
    enemies 2 hexes from the target join the ones next to it).
    """
    KEY = 'DA_Ezreal19'
    AREA = True  # its damage depends on the page's number of targets (layout.py)
    MARK = 'CD_Ezreal19_CastAnim'
    SHOT = 'CD_Ezreal19_CastAnim2'

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.second_stage = self.chrono_event(self.MARK, 'Unlock')
        spawns = sorted(t for p in self.chrono(self.SHOT).get('projectiles') or [] if p['name'] == 'SpellMis'
                        for t in p.get('spawn_at') or [])
        if len(spawns) != 2:
            raise ValueError(f'Ezreal: expected the root and Encore SpellMis in {self.SHOT}, got {spawns}')
        self.shot_spawn, self.encore_spawn = spawns
        self.spell_stack = 0  # the combat-only spell Stack
        self.notes = ('The splash hits the enemies next to the target (the layout); every 3rd cast of a Heartsteel '
                      'Bias also those 2 hexes away. The detonating missile flies his attack range.')

    def detonation(self, level, AD, AP):
        return self.row('ADDamage', star=level) * AD + self.row('APDamage', star=level) * AP

    def performAbility(self, opponents, items, time):
        flight = self.chrono_projectile_ticks(self.SHOT, 'SpellMis', self.target_hexes())
        stage2 = self.tick + ticks_up(self.second_stage)
        shots = [(self.shot_spawn, 1)]
        if self.trait_tier('DA_Encore19') > 0:
            shots.append((self.encore_spawn, self.trait_value('DA_Encore19', 'RecastEffectiveness')))
        splash = self.row('AoEPercentDamage')
        self.spell_stack += 1  # GE_IncSpellStackBy1_CombatOnly (0x10ed)
        bias = getattr(self, 'heartsteel_bias', False)
        boost = 1 + self.row('HeartsteelStan_PercentIncreasedAbilityDamage') if bias else 1
        # TR_Add_EnemiesWithinHexRange around the target: HexRange 1, or 2 on a 2-hex cast (0x11b5)
        splash_targets = self.nearby(opponents[0], 2 if bias and self.spell_stack % 3 == 0 else 1)
        # GE_SimulateLaunchAttack at stage 1 (0x168a) and again at stage 2 (0x1ce5 -> 0xf): VOD4, Titan's stacks
        self.simulateLaunch(items)
        self.schedule_tick(stage2, lambda: self.simulateLaunch(items))
        for spawn, eff in shots:
            def land(eff=eff * boost, splash_targets=splash_targets):
                now = self.tick / TPS
                self.multiTargetSpell(opponents[:1], items, now, 1,
                                      lambda level, AD, AP: self.detonation(level, AD, AP) * eff, 'physical')
                if splash_targets:
                    self.trace('area', at=opponents[0], hit=splash_targets)
                    self.multiTargetSpell(splash_targets, items, now, len(splash_targets),
                                          lambda level, AD, AP: self.detonation(level, AD, AP) * splash * eff,
                                          'physical')

            self.fly(stage2 + ticks_up(spawn), flight, opponents[0], land, name='shot')


class Lux(BuildChampion):
    """Lux Lux Beam! (champions/Lux.md, D1). Script: GA_Lux19_Spell (build ga_scripts.zip).

    The cast applies the mana lock (GE_ManaLock, 0x1876) and plays CD_Lux19_Spell_new at her target's hex. Its
    'Prism' event (0.3137 s) tosses the prism (CD_Lux19_Prism, visual); at 'DamageAndBeam' (1.0416 s, 0x28b) she
    takes her attack target and the NumSecondaryTargets enemies nearest her, the target left out
    (TR_Add_N_NearestEnemiesWithoutTags from her own position, SortByRowDistance; when there is none, the target
    again: 0x5b4), and at once applies GE_Lux19_PrimaryDamage (MagicDamageCalc1 = PrimaryDamageAP x AP) to the target
    and GE_Lux19_SecondaryDamage (MagicDamageCalc2 = SecondaryDamageAP x AP) to each secondary; the beam chronos are
    visual. Both are magic spell damage that crits only with Precision (RollIfCanSpellCrit). Her 'Unlock' event
    (1.5625 s, 0xc75) removes the mana lock and finishes the cast; ManaRefundOnKill needs a kill (dummies never die).
    The build's spell timeline has no lock for her, so the locks are read from the chrono as for Senna: mana lock =
    the Unlock tick, cast lock one tick later.
    """
    KEY = 'DA_Lux19'
    CAST = 'CD_Lux19_Spell_new'

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.beam_at = self.chrono_event(self.CAST, 'DamageAndBeam')
        unlock = ticks_up(self.chrono_event(self.CAST, 'Unlock')) / TPS
        self.timing.cast_lock, self.timing.mana_lock = unlock + 1 / TPS, unlock
        self.timing.source['cast_lock'] = self.timing.source['mana_lock'] = f'{self.CAST} Unlock (GA_Lux19_Spell 0xc75)'
        self.num_secondaries = int(self.row('NumSecondaryTargets'))
        self.notes = ('The secondary beam hits the enemy nearest Lux other than her target (the target again when '
                      'there is none). Mana refund on kill not modelled: dummies never die.')

    def primary_damage(self, level, AD, AP):
        return self.row('PrimaryDamageAP', star=level) * AP

    def secondary_damage(self, level, AD, AP):
        return self.row('SecondaryDamageAP', star=level) * AP

    def performAbility(self, opponents, items, time):
        def beam():
            target = opponents[0]
            others = self.nearest(self.num_secondaries, exclude=[target]) or [target]
            # GetRepeatingListFromTargetData: the list repeated to NumSecondaryTargets entries
            secondaries = [others[i % len(others)] for i in range(self.num_secondaries)]
            now = self.tick / TPS
            self.trace('beam', at=target, hit=secondaries)
            self.multiTargetSpell([target], items, now, 1, self.primary_damage, 'magical')
            self.multiTargetSpell(secondaries, items, now, len(secondaries), self.secondary_damage, 'magical')

        self.schedule_tick(self.tick + ticks_up(self.beam_at), beam)


class Gnar(BuildChampion):
    """Hard Rock (champions/Gnar.md, D1). Scripts: GA_Gnar19_Passive, GA_Gnar19_TrickshotHandler (build ga_scripts.zip).

    His mana bar is Ammo (max 3, no role mana) and he has no spell. GA_Gnar19_Passive, on each attack launch
    (Combat.Event.LaunchAttack, 0x1720): Ammo 0 -> +1; Ammo 1 -> +1 and GE_Gnar19_UseEmpoweredAttack, whose tag
    ChronoTags.Dynamic.CustomAttack.1 makes the next attack play the attack chrono's SpecialAttack group
    (CustomLaunchAttack1 at 0.38 s in a 1.2333 s animation, rate-scaled like the others, instead of LaunchAttack at
    0.2678 s in 1.9667 s). So every 3rd attack is the empowered one. Its Combat.Event.LaunchAttack.Custom.1 (0x4fe):
    +1 Ammo, GE_Gnar19_AttackSpeedBuff (AttackSpeed MultiplyAdditive AttackSpeedCalc1 = 0.09 x AP + 1, infinite,
    stacking) and the rock, CD_Gnar19_Projectile's 'SpellProjectile' (1800 units/s) at his target; 0.3 / AS later the
    Ammo resets. The custom launch is not one of the events GA_LaunchProjectileAttack fires a projectile on, so the
    rock replaces the attack. On arrival (0x1c66 -> 0x1371): GE_Gnar19_PhysicalDamage = PhysicalDamageCalc1
    (ADDamage x AD, AD the AttackDamage multiplier), physical, tagged AppliesOnHit.IsAttack and AppliesOnSpell (on-hit
    effects apply), crits only with Precision (RollIfCanSpellCrit); then the Trickshot bounce event.
    Trickshot (GA_Gnar19_TrickshotHandler): the rock ricochets k = 1..NumRichochets to the nearest enemy not yet hit
    (CD_Gnar19_Projectile_TrickshotBounce, 1800) for the same damage x RichochetDamage^k; its on-hit effects at
    RichochetDamage^k are not modelled (as for attack ricochets, B12). His other attacks ricochet as every Trickshot's
    (B12). Assumed: the attack rhythm of units with several attack animations (B13: starts a period apart).
    """
    KEY = 'DA_Gnar19'
    ATTACK = 'CD_Gnar19__Attack'
    ROCK = 'CD_Gnar19_Projectile'
    BOUNCE = 'CD_Gnar19_Projectile_TrickshotBounce'
    EVERY = 3  # Ammo max 3: two attacks fill it to 2, the third is empowered (GA_Gnar19_Passive 0x1720)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        t = self.timing
        # the attack chrono's SpecialAttack group (CustomAttack.1): CustomLaunchAttack1 in a module ending at the
        # chrono's length (1.2333 s); the SequentialAttack modules are the build's attack timeline
        special = {'selector': self.EVERY, 'min_as': None, 'launch': self.chrono_event(self.ATTACK, 'CustomLaunchAttack1'),
                   'length': self.chrono(self.ATTACK)['length']}
        t.variants = [{'selector': s, 'min_as': None, 'launch': t.launch, 'length': t.attack_len}
                      for s in range(1, self.EVERY)] + [special]
        t.animations = self.EVERY
        t.source['variants'] = f'{self.ATTACK} SequentialAttack x2 + SpecialAttack (GA_Gnar19_Passive Ammo, every 3rd)'
        self.rock_speed = self.chrono_projectile_speed(self.ROCK, 'SpellProjectile')
        self.notes = ('Every 3rd attack is the rock (its own, slower windup); each rock gives +9% x AP attack speed '
                      'for the rest of combat. Items that give mana add no Ammo.')

    def canCast(self, time=None):
        return False  # no spell: the bar is Ammo, spent by the passive; mana from items adds no Ammo (owner, 2026-11-18)

    def rock_damage(self, level, AD, AP):
        return self.row('ADDamage', star=level) * AD

    def _empowered(self):
        """Is the attack released just now (launches already counted) the empowered one?"""
        return (self.launches - 1) % self.EVERY == self.EVERY - 1

    def onLaunch(self, opponents, items):
        if self._empowered():
            # GE_Gnar19_AttackSpeedBuff at the custom launch: MultiplyAdditive 0.09 x AP + 1, stacking
            self.aspd.modify("MultiplyAdditive", self.row('AttackSpeedAP') * self.ap.stat + 1)

    def fire_attack(self, opponents, items, moment, paid):
        if not self._empowered():
            return super().fire_attack(opponents, items, moment, paid)
        target = opponents[0]
        flight = self.chrono_projectile_ticks(self.ROCK, 'SpellProjectile', self.target_hexes(target))
        self.fly(self.tick, flight, target, lambda: self._rock_lands(target, [target], 0), name='rock')

    def _rock_lands(self, target, hit, k):
        """The rock (k = 0) or its k-th Trickshot ricochet arrives at `target`."""
        items, now = self.items, self.tick / TPS
        eff = self.trait_value('DA_Trickshot19', 'RichochetDamage') ** k if k else 1
        dmg = self.rock_damage(self.level, self.bonus_ad.stat, self.ap.stat) * eff
        crit_dmg = dmg * self.critDamage() if self.canSpellCrit else dmg
        amp = self.dmgMultiplier.stat * self.extraDmgMultiplier.stat
        tags = damage_tags('physical', UNIT, IS_ATTACK, ON_SPELL, *((ON_HIT,) if k == 0 else ()))
        if k == 0:
            self.emit(ONHIT_PRE, CombatEvent(self, target, dtype='physical', tags=tags, time=now), items)
        self.doDamage(target, items, self.crit.stat if self.canSpellCrit else 0, crit_dmg * amp, dmg * amp,
                      'physical', now, tags=tags)
        if k == 0:
            self.emit(ONHIT_AFTER, CombatEvent(self, target, tags=tags, time=now), items)
        if self.trait_tier('DA_Trickshot19') > 0 and k < self.trait_value('DA_Trickshot19', 'NumRichochets'):
            nxt, hexes = self.ricochet(target, hit)
            step = self.chrono_projectile_ticks(self.BOUNCE, 'SpellProjectile', hexes)
            self.fly(self.tick, step, nxt, lambda: self._rock_lands(nxt, hit + [nxt], k + 1), source=target,
                     name='ricochet')


class Malzahar(BuildChampion):
    """Forbidden Cacophony (champions/Malzahar.md, D1). Script: GA_Malzahar19_SpellNew (build ga_scripts.zip).

    The cast applies the mana lock (0xb96) and plays CD_Malzahar19_CastAnim_new at his attack target. At its
    'BeginBeam' event (0.3523 s, 0x2a1) a burst goes off and the beam starts: RepeatAction(PrimaryTickRate,
    NumTicks), acting at once, NumTicks = Round(DamageOverSecondsDONTCHANGE / PrimaryTickRate + 1) = 9 (0x40a); each
    tick applies GE_Malzahar19_BeamDamageTick = MagicDamageCalc1 (DamageAP x AP) / NumTicks (SetByCaller) to the
    target, magic, DOT. Each 'Burst' event (0.9923, 1.6323, 2.2723 s) is another burst, so 4 in all: DoAOEBurst
    takes the enemies within AOEHexRange (1) of the target (TR_Add_EnemiesWithinHexRange, the target included), shreds
    them (GE_MRShred at ShredPercent 30 for ShredDuration 4 s, ShredTargets) and then applies
    GE_Malzahar19_AreaDamageTick = MagicDamageCalc2 (SecondaryDamageAP x AP), magic. All spell damage crits only with
    Precision. 'Unlock' (2.4688 s) removes the mana lock and finishes the cast (the build's timeline: 75 / 76 ticks).
    """
    KEY = 'DA_Malzahar19'
    AREA = True  # its damage depends on the page's number of targets (layout.py)
    CAST = 'CD_Malzahar19_CastAnim_new'

    def __init__(self, level, build=None):
        super().__init__(level, build)
        events = self.chrono(self.CAST).get('events') or []
        self.begin = self.chrono_event(self.CAST, 'BeginBeam')
        self.bursts = [self.begin] + sorted(t for name, t in events if name == 'Burst')
        self.tick_rate = self.row('PrimaryTickRate')
        self.beam_ticks = round(self.row('DamageOverSecondsDONTCHANGE') / self.tick_rate + 1)
        self.aoe = int(self.row('AOEHexRange'))
        self.shred_level, self.shred_duration = self.row('ShredPercent'), self.row('ShredDuration')
        self.notes = ('Beam: 9 ticks over 2 s on the target. Bursts: 4, each shredding (30% MR, 4 s) then damaging the '
                      'target and the enemies next to it (the layout).')

    def beam_damage(self, level, AD, AP):
        return self.row('DamageAP', star=level) * AP / self.beam_ticks

    def burst_damage(self, level, AD, AP):
        return self.row('SecondaryDamageAP', star=level) * AP

    def performAbility(self, opponents, items, time):
        target = opponents[0]

        def burst():
            hit = [target] + self.nearby(target, self.aoe)
            self.trace('area', at=target, hit=hit)
            for t in hit:
                apply_shred(self, t, self.shred_level, self.shred_duration)
            self.multiTargetSpell(hit, self.items, self.tick / TPS, len(hit), self.burst_damage, 'magical')

        def beam_tick():
            self.trace('beam', at=target, hit=[])
            self.multiTargetSpell([target], self.items, self.tick / TPS, 1, self.beam_damage, 'magical')

        for t in self.bursts:
            self.schedule_tick(self.tick + ticks_up(t), burst)
        for j in range(self.beam_ticks):
            self.schedule_tick(self.tick + ticks_up(self.begin + j * self.tick_rate), beam_tick)


class Samira(BuildChampion):
    """Bullets N' Roses (champions/Samira.md, D1). Scripts: GA_Samira19_Spell, GA_Samira19_TrickshotHandler,
    GA_Samira19_CaptivateCritTracker (build ga_scripts.zip).

    The cast applies the mana lock and plays CD_Samira19_CastAnim at her target. At 'BeginFire' (0.1962 s) a
    RepeatAction fires NumBullets (10) bullets TimeToShoot (0.374933 s, the script's default) / NumBullets apart, the
    first at once, alternating CD_Samira19_Mis1 / Mis2 ('Bullet', 1500 units/s) at her target. The first bullet fired
    applies GE_SimulateLaunchAttack (a DoOnce: on-attack items hear one launch per cast, G11). Each arrival applies
    GE_Samira19_BulletDamage = PhysicalDamageCalc1 (DamageAP x AP + DamageAD x AD), physical spell damage that crits
    only with Precision, and sends the Trickshot bounce: GA_Samira19_TrickshotHandler flies CD_Samira19_MisBounce
    (1500) to the nearest enemy not yet hit for the same damage x RichochetDamage^k (B12). 'Unlock' (1.3105 s) ends
    the cast (the build's 40 / 41 ticks).
    Passive (GA_Samira19_CaptivateCritTracker): any damage of hers that crits (Damage.Result.WasCrit) Captivates the
    enemy for CaptivateDuration (3 s) when the board has Classical; the engine averages crits, so a Captivate comes
    with each CRIT event (I6). Captivated enemies feed Classical's damage amp (traits/classical.py).
    """
    KEY = 'DA_Samira19'
    CAST = 'CD_Samira19_CastAnim'
    BULLETS = ('CD_Samira19_Mis1', 'CD_Samira19_Mis2')
    BOUNCE = 'CD_Samira19_MisBounce'
    TIME_TO_SHOOT = 0.374933  # GA_Samira19_Spell default TimeToShoot (script literal, not a curve row)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.begin_fire = self.chrono_event(self.CAST, 'BeginFire')
        self.num_bullets = int(self.row('NumBullets'))
        self.bullet_gap = self.TIME_TO_SHOOT / self.num_bullets
        self.captivate_duration = self.row('CaptivateDuration')
        self.notes = ('A barrage counts as one attack launch for on-attack items. Her crits Captivate (3 s) when '
                      'Classical is active, which grows the Classical damage amp.')

    def bullet_damage(self, level, AD, AP):
        return self.row('DamageAP', star=level) * AP + self.row('DamageAD', star=level) * AD

    def emit(self, moment, event, items):
        super().emit(moment, event, items)
        if moment == CRIT and event.target is not None:
            captivate(self, event.target, self.captivate_duration)

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        for k in range(self.num_bullets):
            def fire(k=k):
                if k == 0:
                    self.simulateLaunch(self.items)  # GE_SimulateLaunchAttack on the first OnFired (DoOnce)
                flight = self.chrono_projectile_ticks(self.BULLETS[k % 2], 'Bullet', self.target_hexes(target))
                self.fly(self.tick, flight, target, lambda: self._bullet_lands(target, [target], 0), name='bullet')
            self.schedule_tick(self.tick + ticks_up(self.begin_fire + k * self.bullet_gap), fire)

    def _bullet_lands(self, target, hit, k):
        eff = self.trait_value('DA_Trickshot19', 'RichochetDamage') ** k if k else 1
        self.multiTargetSpell([target], self.items, self.tick / TPS, 1,
                              lambda level, AD, AP: self.bullet_damage(level, AD, AP) * eff, 'physical')
        if self.trait_tier('DA_Trickshot19') > 0 and k < self.trait_value('DA_Trickshot19', 'NumRichochets'):
            nxt, hexes = self.ricochet(target, hit)
            step = self.chrono_projectile_ticks(self.BOUNCE, 'Bounce', hexes)
            self.fly(self.tick, step, nxt, lambda: self._bullet_lands(nxt, hit + [nxt], k + 1), source=target,
                     name='ricochet')


class Karthus(BuildChampion):
    """Requiem (champions/Karthus.md, D1). Script: GA_Karthus19_Spell (build ga_scripts.zip).

    The cast applies the mana lock (0x534) and plays CD_Karthus19_CastAnim at his attack target (CastOnTarget). At its
    'Damage' event (1.1269 s, 0x116) GE_Karthus19_Damage = MagicDamageCalc1 (APDamage x AP) x
    Max(PercentDamageOfPreviousCast ^ TimesCast, MinimumDamagePercent) (SetByCaller Multiplier), magic spell damage
    that crits only with Precision. At 'Unlock' (1.337 s, 0x361) he recasts on a new target if the hit one died;
    otherwise EndSpell removes the mana lock and finishes the cast. Dummies never die: one hit per cast, at x1. The
    build's spell timeline has no lock for him, so the locks are read from the chrono as for Lux: mana lock = the
    Unlock tick (41), cast lock one more (42).
    """
    KEY = 'DA_Karthus19'
    CAST = 'CD_Karthus19_CastAnim'

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.damage_at = self.chrono_event(self.CAST, 'Damage')
        unlock = ticks_up(self.chrono_event(self.CAST, 'Unlock')) / TPS
        self.timing.cast_lock, self.timing.mana_lock = unlock + 1 / TPS, unlock
        self.timing.source['cast_lock'] = self.timing.source['mana_lock'] = f'{self.CAST} Unlock (GA_Karthus19_Spell 0x361)'
        self.notes = 'The recast on a kill (70% of the previous hit) is not modelled: dummies never die.'

    def requiem(self, level, AD, AP):
        return self.row('APDamage', star=level) * AP

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        self.trace('area', tick=self.tick + ticks_up(self.damage_at), at=target, hit=[], name='requiem')
        self.schedule_tick(self.tick + ticks_up(self.damage_at), lambda: self.multiTargetSpell(
            [target], items, self.tick / TPS, 1, self.requiem, 'magical'))


class OlafHeroAugment(BuildChampion):
    BASE_KEY = 'DA_Olaf19'  # the unit the augment overrides: its shop cost places him in the champion menu
    """Olaf with the hero augment Axe Crescendo (DA_Olaf19_HeroAugment): the augment's unit
    DA_Olaf19_HeroAugment_Override, a separate champion (owner, 2026-11-18; champions/Olaf_HeroAugment.md, D1).
    Scripts: GA_Olaf19_HeroAugment, GA_Olaf19_EmpoweredAttack_HeroAugment (build ga_scripts.zip).

    The cast (GA_Olaf19_HeroAugment): NumAttacks = the NumAttacks row + his Stack attribute (0x3b6); the mana lock
    (0x4d3); CD_Olaf19_Empower_HeroAugment, whose 'Empower' event (0 s) applies GE_Olaf19_Empowered_HeroAugment
    (tag ChronoTags.Dynamic.CustomAttack.1, infinite) and finishes the cast (build: cast lock 1 tick). The cast
    cancels an attack in progress. Each Combat.Event.LaunchAttack.Custom.1 counts (0x1a8); at NumAttacks it applies
    GE_Olaf19_CastStacker_HeroAugment (Stack + ExtraAttacksPerCast, infinite) and ends the empower (0x7d5): the
    Empowered effect is removed and, one tick later (DelayUntilNextTick, 0xf), the mana lock. So the mana lock lasts
    until the tick after the last empowered launch, and the last empowered attack's own mana is lost.
    His attack chrono CD_Olaf19_Attack, for a unit with Augment.HeroAugment.HasHeroOverride: with the CustomAttack.1
    tag the 'Empowered' group plays (CustomLaunchAttack1 at 0.5 s in a 1.1667 s animation, rate-scaled), otherwise
    the 'Unempowered' SequentialAttack group (LaunchAttackVariant1/2 at 0.32 s in 1.0 s, rate-scaled). The custom
    launch is not one GA_LaunchProjectileAttack fires on, so the empowered attack throws only the axe
    (GA_Olaf19_EmpoweredAttack_HeroAugment: CD_Olaf19_Spell_HeroAugment's 'BigAxe', 1700 units/s, at his attack
    target). On arrival GE_Olaf19_SpellDamage_HeroAugment = PhysicalDamageCalc1 (ADDamage x AD + APDamage x AP, AD
    and AP the multipliers), physical, Damage.Source.Unit with no other tags (no on-hit), crits only with Precision.
    The base Olaf's heal passive is not on this unit.
    """
    KEY = 'DA_Olaf19_HeroAugment_Override'
    ATTACK = 'CD_Olaf19_Attack'
    AXE = 'CD_Olaf19_Spell_HeroAugment'
    EMPOWERED = 3  # the selector this class gives the empowered animation
    display_name = 'Olaf (Axe Crescendo)'

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.name = self.display_name
        t, ch = self.timing, self.chrono(self.ATTACK)
        # CD_Olaf19_Attack's modules: the unempowered ones end at the chrono's length (1.0 s), the empowered one at its
        # anim_end (1.1667 s)
        # G20: each animation's PlayRateScalingThreshold by its launch event (the build's launch_thresholds; the
        # unempowered modules set none: G2; the empowered one 0.6)
        thresholds = ch.get('launch_thresholds') or {}
        normal = [{'selector': s, 'min_as': None, 'launch': self.chrono_event(self.ATTACK, f'LaunchAttackVariant{s}'),
                   'length': ch['length'], 'rate_threshold': thresholds.get(f'LaunchAttackVariant{s}')} for s in (1, 2)]
        empowered = {'selector': self.EMPOWERED, 'min_as': None,
                     'launch': self.chrono_event(self.ATTACK, 'CustomLaunchAttack1'), 'length': ch['anim_end'],
                     'rate_threshold': thresholds.get('CustomLaunchAttack1')}
        t.variants, t.animations = normal + [empowered], 2
        t.launch, t.attack_len = normal[0]['launch'], normal[0]['length']
        t.source['variants'] = f'{self.ATTACK} HeroAugment groups: Unempowered x2, Empowered (CustomAttack.1)'
        # the mana lock ends the tick after the last empowered launch (onLaunch sets it); until then it holds
        t.mana_lock = 10 ** 6
        t.source['mana_lock'] = 'GA_Olaf19_HeroAugment: removed the tick after the last empowered launch (0x7d5, 0xf)'
        self.empowered_left = 0  # empowered attacks still to throw this cast
        self.axe_stacks = 0  # his Stack attribute: + ExtraAttacksPerCast after each cast's throws
        self._planned = 1  # the animation of the attack starting next
        self._this_empowered = False
        self.notes = ('Each cast empowers his next 2 attacks (+1 per earlier cast) into thrown axes; his mana is locked '
                      'until the last axe is thrown.')

    def axe_damage(self, level, AD, AP):
        return self.row('ADDamage', star=level) * AD + self.row('APDamage', star=level) * AP

    def _next_animation(self):
        self._planned = self.EMPOWERED if self.empowered_left > 0 else self.launches % 2 + 1
        return self._planned, self.aspd.stat

    def performAbility(self, opponents, items, time):
        self.empowered_left = int(self.row('NumAttacks') + self.axe_stacks)

    def onLaunch(self, opponents, items):
        self._this_empowered = self._planned == self.EMPOWERED
        if self._this_empowered:
            self.empowered_left -= 1
            if self.empowered_left == 0:
                self.axe_stacks += self.row('ExtraAttacksPerCast')
                self.mana_locked_until = self.tick + 1

    def fire_attack(self, opponents, items, moment, paid):
        if not self._this_empowered:
            return super().fire_attack(opponents, items, moment, paid)
        target = opponents[0]
        flight = self.chrono_projectile_ticks(self.AXE, 'BigAxe', self.target_hexes(target))
        self.fly(self.tick, flight, target, lambda: self._axe_lands(target), name='axe')

    def _axe_lands(self, target):
        items, now = self.items, self.tick / TPS
        dmg = self.axe_damage(self.level, self.bonus_ad.stat, self.ap.stat)
        crit_dmg = dmg * self.critDamage() if self.canSpellCrit else dmg
        amp = self.dmgMultiplier.stat * self.extraDmgMultiplier.stat
        self.doDamage(target, items, self.crit.stat if self.canSpellCrit else 0, crit_dmg * amp, dmg * amp,
                      'physical', now, tags=damage_tags('physical', UNIT))


class Ashe(BuildChampion):
    """Feelin' Shot Shot Shot (champions/Ashe.md, D1). Scripts: GA_Ashe19_Spell, GA_Ashe19_EmpoweredAttack (build
    ga_scripts.zip).

    The cast (GA_Ashe19_Spell) plays CD_Ashe19_CastAnim for a fixed duration, CT_Ashe19_ASToCastSpeed ASToCastTime at
    her AttackSpeed when it starts (0x3e3: 0.3333 s up to 1 AS, linear to 0.15 s at 5 AS); the cast finishes when it
    stops (a cast lock of that + 1 tick, the build's rule). It applies the mana lock (0x610) and GE_Ashe19_Empowered
    (0x65b: tag ChronoTags.Dynamic.CustomAttack.1 and AttackSpeed MultiplyAdditive AttackSpeedCalc1 = SpellASBase +
    SpellASAP x AP: +50% at AP 1, VOD5 E2: 0.93 -> 1.30). Each Combat.Event.LaunchAttack.Custom.1 counts (0xfd); at
    NumFlurryAttacks (6), one tick later (DelayUntilNextTick, 0x1ae -> 0xf), the empower and the mana lock are
    removed: her mana is locked until the tick after the 6th flurry, whose own mana is lost.
    With the tag, CD_Ashe19_Attack_new plays the 'EmpoweredAttack' group: CustomLaunchAttack1 at 0 s (the flurry
    leaves when the attack starts; the engine releases 1 tick after a start), otherwise the SequentialAttack group
    (LaunchAttack at 0.2971 s of 2.1333 s, rate-scaled). A flurry (GA_Ashe19_EmpoweredAttack: the custom launch fires
    no attack projectile) is CD_Ashe19_EmpoweredMis at her target: 'OnHitArrow' at 0 s and two 'NoOnHitArrow' at
    0.075 and 0.15 s (ArrowsPerFlurry 3), 2100 units/s. Each arrival applies PhysicalDamageCalc1 (ArrowDamageAD x AD,
    AD the multiplier), physical, AppliesOnHit and AppliesOnSpell (the first also IsAttack), crit only with
    Precision, with on-hit effects at OnHitEffectivenessPerFlurryArrow (0.6, I11).
    """
    KEY = 'DA_Ashe19'
    ATTACK = 'CD_Ashe19_Attack_new'
    FLURRY = 'CD_Ashe19_EmpoweredMis'
    CAST_TIME = ('CT_Ashe19_ASToCastSpeed', 'ASToCastTime')
    EMPOWERED = 3  # the selector this class gives the empowered animation

    def __init__(self, level, build=None):
        super().__init__(level, build)
        t, length = self.timing, self.chrono(self.ATTACK)['length']
        normal = [{'selector': s, 'min_as': None, 'launch': self.chrono_event(self.ATTACK, 'LaunchAttack'),
                   'length': length} for s in (1, 2)]
        # the empowered module's own length (1.8333 s) is not in the build; with a launch at 0 s it changes nothing
        empowered = {'selector': self.EMPOWERED, 'min_as': None,
                     'launch': self.chrono_event(self.ATTACK, 'CustomLaunchAttack1'), 'length': length}
        t.variants, t.animations = normal + [empowered], 2
        t.source['variants'] = f'{self.ATTACK}: SequentialAttack x2, EmpoweredAttack (CustomAttack.1)'
        # her attack modules' PlayRateScalingThreshold is 1.0 (the build, G20): the animation plays at the attack
        # period, shorter as well as longer (VOD5 E2: first attack 5.5 ticks after combat start at AS 0.86, G2: 9)
        t.mana_lock = 10 ** 6  # lifted the tick after the last flurry (onLaunch)
        t.source['mana_lock'] = 'GA_Ashe19_Spell: removed the tick after the last flurry launch (0x1ae, 0xf)'
        t.source['cast_lock'] = f'{self.CAST_TIME[0]} {self.CAST_TIME[1]} at her AS at the cast (GA_Ashe19_Spell 0x3e3)'
        # her script reads AttackSpeed only through that curve: the lock is not divided by the AS ratio as well
        t.lock_scales_with_as = False
        t.source['lock_scales_with_as'] = 'GA_Ashe19_Spell reads AS only for ASToCastTime (0x3e3)'
        self.arrows = [('OnHitArrow', self.chrono_projectile_spawn(self.FLURRY, 'OnHitArrow'))] + [
            ('NoOnHitArrow', s) for s in sorted(p for q in self.chrono(self.FLURRY)['projectiles']
                                                if q['name'] == 'NoOnHitArrow' for p in q['spawn_at'])]
        if len(self.arrows) != self.row('ArrowsPerFlurry'):
            raise BuildDataError(f'{self.KEY}: {self.FLURRY} spawns {len(self.arrows)} arrows, ArrowsPerFlurry is '
                                 f'{self.row("ArrowsPerFlurry")}')
        self.empowered_left = 0
        self._planned = 1
        self._this_empowered = False
        self.notes = ('Her next 6 attacks after a cast have +30% + 20% x AP attack speed and are flurries of 3 arrows; '
                      'her mana is locked until the 6th flurry.')

    def arrow_damage(self, level, AD, AP):
        return self.row('ArrowDamageAD', star=level) * AD

    def _next_animation(self):
        self._planned = self.EMPOWERED if self.empowered_left > 0 else self.launches % 2 + 1
        return self._planned, self.aspd.stat

    def performAbility(self, opponents, items, time):
        cast_end = self.table_value(*self.CAST_TIME, self.aspd.stat)  # read before the empower (0x3e3 < 0x65b)
        self.timing.cast_lock = (ticks_up(cast_end) + 1) / TPS
        self.aspd.modify('MultiplyAdditive', 1 + self.row('SpellASBase') + self.row('SpellASAP') * self.ap.stat,
                         key='ashe_empowered')
        self.empowered_left = int(self.row('NumFlurryAttacks'))

    def onLaunch(self, opponents, items):
        self._this_empowered = self._planned == self.EMPOWERED
        if self._this_empowered:
            self.empowered_left -= 1
            if self.empowered_left == 0:
                self.mana_locked_until = self.tick + 1
                self.schedule_tick(self.tick + 1, lambda: self.aspd.remove('ashe_empowered'))

    def fire_attack(self, opponents, items, moment, paid):
        if not self._this_empowered:
            return super().fire_attack(opponents, items, moment, paid)
        target = opponents[0]
        hexes = self.target_hexes(target)
        for i, (name, spawn) in enumerate(self.arrows):
            self.fly(self.tick + ticks_up(spawn), self.chrono_projectile_ticks(self.FLURRY, name, hexes), target,
                     lambda first=(i == 0): self._arrow_lands(target, first), name='arrow')

    def _arrow_lands(self, target, first):
        items, now = self.items, self.tick / TPS
        dmg = self.arrow_damage(self.level, self.bonus_ad.stat, self.ap.stat)
        crit_dmg = dmg * self.critDamage() if self.canSpellCrit else dmg
        amp = self.dmgMultiplier.stat * self.extraDmgMultiplier.stat
        eff = self.row('OnHitEffectivenessPerFlurryArrow')
        tags = damage_tags('physical', UNIT, ON_HIT, ON_SPELL, *((IS_ATTACK,) if first else ()))
        self.emit(ONHIT_PRE, CombatEvent(self, target, dtype='physical', tags=tags, time=now, effectiveness=eff), items)
        self.doDamage(target, items, self.crit.stat if self.canSpellCrit else 0, crit_dmg * amp, dmg * amp,
                      'physical', now, tags=tags)
        self.emit(ONHIT_AFTER, CombatEvent(self, target, tags=tags, time=now, effectiveness=eff), items)


class Viego(BuildChampion):
    """Singled Out (champions/Viego.md, D1). Script: GA_Viego19_Spell (build ga_scripts.zip).

    The cast commits, applies the mana lock (0xf8c) and reads the swords: NumBaseSwords (10) + GenericCalc2 (bonus
    swords from takedowns, GA_Viego19_SwordStacking: dummies never die, 0). It plays CD_Viego19_SpellCast and spawns the
    swords around his target over 0.75 s (visual). At 'FireSwords' (1.0579 s, 0x19e3 -> 0x1917) every sword plays
    CD_Viego19_SwordCollapse_Mis from its place to the target; the 'ViegoSwordCollapse' projectile is a
    TFTFixedTimeMovement with no time of its own, assumed to arrive at the module's end, the chrono's length 0.25 s
    (G21); on arrival GE_Viego19_SwordDamage = PhysicalDamageCalc1, physical, AppliesOnSpell, crit only with Precision.
    The CalcComponent builds PhysicalDamageCalc1 from DamagePerSwordAD x AbilityPower + DamagePerSwordAP x AbilityPower
    (both terms capture AbilityPower), but the owner ruled the AD row scales with AD (2026-11-18, D1):
    DamagePerSwordAD x AD + DamagePerSwordAP x AP. After starting the
    swords (0xede) one GE_SimulateLaunchAttack. 'Unlock' (1.832 s) removes the mana lock and finishes the cast (the
    build: 55 / 56 ticks).
    """
    KEY = 'DA_Viego19'
    CAST = 'CD_Viego19_SpellCast'
    COLLAPSE = 'CD_Viego19_SwordCollapse_Mis'

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.fire_at = self.chrono_event(self.CAST, 'FireSwords')
        self.collapse = self.chrono(self.COLLAPSE)['length']  # G21: a fixed-time projectile takes its module's time
        self.num_swords = int(self.row('NumBaseSwords'))
        self.notes = ('10 swords hit the target 1.31 s into the cast (the takedown swords are not modelled: dummies '
                      'never die). Each deals DamagePerSwordAD x AD + DamagePerSwordAP x AP (owner, 2026-11-18).')

    def sword_damage(self, level, AD, AP):
        # PhysicalDamageCalc1: the AD row x AD, the AP row x AP (owner, 2026-11-18; the client's CalcComponent
        # captures AbilityPower for both, D1)
        return self.row('DamagePerSwordAD', star=level) * AD + self.row('DamagePerSwordAP', star=level) * AP

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        fire = self.tick + ticks_up(self.fire_at)
        self.schedule_tick(fire, lambda: self.simulateLaunch(self.items))  # 0xede, after the swords start (G11)

        def land():
            for _ in range(self.num_swords):
                self.multiTargetSpell([target], self.items, self.tick / TPS, 1, self.sword_damage, 'physical')
        if self.tracer is not None:  # the swords, from around the target (the fight viewer)
            tx, ty = layout.world(target.hex)
            for k in range(self.num_swords):
                a = 2 * math.pi * k / self.num_swords
                self.trace_projectile(fire, fire + ticks_up(self.collapse),
                                      (tx + 170 * math.cos(a), ty + 170 * math.sin(a)), target, 'sword')
        self.schedule_tick(fire + ticks_up(self.collapse), land)


class Kayle(BuildChampion):
    """Stairway to Hell (champions/Kayle.md, D1). Scripts: GA_Kayle19_Spell_new, GA_Kayle19_RangedAttack_new (build
    ga_scripts.zip).

    Passive (GA_Kayle19_RangedAttack_new): her attack is her own projectile, DA_Kayle19_AutoAttackProjectile
    (TFTFixedSpeedMovement 2250 units/s, client asset: the snapshot doesn't read projectiles named in a champion's own
    attack script); on arrival the attack damage and GE_Kayle19_PassiveDamage (MagicDamageCalc1 = APDamage x AP,
    magic, on-spell, crit only with Precision).
    Spell: CD_Kayle19_BeginCast plays at S = FClamp(AttackSpeed / (base AttackSpeed x (1 + BonusAttackSpeed)), 1, 2)
    (ComputeASScalingForStart); the mana lock (0x2ad1). At its 'Buff' event (0.1324 s / S) GE_Kayle19_AttackSpeedBuff
    (AttackSpeed MultiplyAdditive AttackSpeedCalc1 = BonusAttackSpeed + 1, VOD5: 0.94 -> 1.58) for Duration + 0.75 x
    the chrono's duration (taken as its length / S: D1); at 'Unlock' (0.4929 s / S) the cast finishes (cast lock that
    + 1 tick; the build's G7 ratio is not applied) and every Combat.Event.LaunchAttack (exact: simulated attacks don't
    count) adds a sword. When the buff ends (WaitForGameplayEffectRemoved) she stops attacking and moving and plays
    CD_Kayle19_LaunchAllSwords at FClamp(sqrt(AttackSpeed / (base x 1.8)), 1, 1.5) (ComputeASScalingForFinale, her AS
    after the buff): at 'BigHit' (1.048 s) GE_Kayle19_AOEDamage (MagicDamageCalc2) on the enemies within AOEHexRange of
    the target, then a looping 0.1 s timer drops one sword per attack (GE_Kayle19_SingleSwordDamage, MagicDamageCalc3,
    on her target), the first 0.1 s after BigHit; at 'Unlock' (1.4532 s) FinishSpell lets her attack and removes the
    mana lock. All spell damage magic, on-spell, crit only with Precision. The Ascension rows (999) do nothing.
    """
    KEY = 'DA_Kayle19'
    AREA = True  # its damage depends on the page's number of targets (layout.py)
    BEGIN = 'CD_Kayle19_BeginCast'
    FINALE = 'CD_Kayle19_LaunchAllSwords'
    PROJECTILE_SPEED = 2250  # DA_Kayle19_AutoAttackProjectile TFTFixedSpeedMovement MoveSpeed (client asset, not in the build)
    FINALE_CLAMP = 1.5  # ComputeASScalingForFinale FMin(Sqrt(...), 1.5) (script literal)
    START_CLAMP = 2  # ComputeASScalingForStart FMin(..., 2) (script literal)
    DURATION_SHARE = 0.75  # GA_Kayle19_Spell_new 0xd1: the chrono's duration x 0.75 (script literal)
    DROP_EVERY = 0.1  # 0x100d: K2_SetTimerDelegate(0.1, looping) (script literal)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        t = self.timing
        t.proj_speed = self.PROJECTILE_SPEED
        t.source['proj_speed'] = 'DA_Kayle19_AutoAttackProjectile 2250 (client asset; not in the build)'
        t.lock_scales_with_as = False
        t.source['lock_scales_with_as'] = 'GA_Kayle19_Spell_new: its own AS clamps (ComputeASScaling*)'
        t.mana_lock = 10 ** 6  # lifted at the finale's Unlock
        t.source['mana_lock'] = 'GA_Kayle19_Spell_new: FinishSpell at CD_Kayle19_LaunchAllSwords Unlock'
        self.buff_at = self.chrono_event(self.BEGIN, 'Buff')
        self.begin_unlock = self.chrono_event(self.BEGIN, 'Unlock')
        self.begin_len = self.chrono(self.BEGIN)['length']
        self.big_hit = self.chrono_event(self.FINALE, 'BigHit')
        self.finale_unlock = self.chrono_event(self.FINALE, 'Unlock')
        self.aoe = int(self.row('AOEHexRange'))
        self.counting = False
        self.swords = 0
        self.notes = ('For 4 s after a cast: +80% attack speed and a sword per attack; then she stops for the finale: '
                      'a 2-hex blast and the swords on her target. Her mana is locked from the cast to the end of the finale.')

    def passive_damage(self, level, AD, AP):
        return self.row('APDamage', star=level) * AP

    def aoe_damage(self, level, AD, AP):
        return self.row('AOEDamageAP', star=level) * AP

    def sword_damage(self, level, AD, AP):
        return self.row('SwordAPDamage', star=level) * AP

    def performAttack(self, opponents, items, time, multiplier=None, generateMana=True):
        super().performAttack(opponents, items, time, multiplier, generateMana)
        self.multiTargetSpell(opponents[:1], items, time, 1, self.passive_damage, 'magical')

    def _speed(self, clamp, root):
        r = self.aspd.stat / (self.base_aspd * (1 + self.row('BonusAttackSpeed')))
        return min(max(r ** 0.5 if root else r, 1), clamp)

    def onLaunch(self, opponents, items):
        if self.counting:
            self.swords += 1

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        s = self._speed(self.START_CLAMP, root=False)
        self.timing.cast_lock = (ticks_up(self.begin_unlock / s) + 1) / TPS
        start = self.tick + ticks_up(self.buff_at / s)
        duration = self.row('Duration') + self.DURATION_SHARE * self.begin_len / s

        def buff():
            self.aspd.modify('MultiplyAdditive', 1 + self.row('BonusAttackSpeed'), key='kayle_buff')
            self.swords, self.counting = 0, True
            self.schedule_tick(self.tick + ticks_up(duration), finale)

        def finale():
            self.aspd.remove('kayle_buff')
            self.counting = False
            f = self._speed(self.FINALE_CLAMP, root=True)
            now, swords = self.tick, self.swords
            self.attacking = False  # GE_UnitStopAttackingMoving until the finale's Unlock
            self.busy_until = now + ticks_up(self.finale_unlock / f)
            hit = now + ticks_up(self.big_hit / f)
            area = [target] + self.nearby(target, self.aoe)  # TR_Add_EnemiesWithinHexRange, the target included
            self.trace('area', tick=hit, at=target, hit=area)
            self.schedule_tick(hit, lambda: self.multiTargetSpell(area, self.items, self.tick / TPS, len(area),
                                                                  self.aoe_damage, 'magical'))
            for k in range(1, swords + 1):
                self.schedule_tick(hit + ticks_up(k * self.DROP_EVERY), lambda: self.multiTargetSpell(
                    [target], self.items, self.tick / TPS, 1, self.sword_damage, 'magical'))
            self.schedule_tick(self.busy_until, lift)

        def lift():
            self.mana_locked_until = self.tick

        self.schedule_tick(start, buff)


class Lucian(BuildChampion):
    """Relentless Pursuit (champions/Lucian.md, D1). Script: GA_Lucian19_Spell (build ga_scripts.zip).

    The cast commits, reads Encore (IsEncoreCast = a Encore member with the trait active; EncoreDamageMult = CT_Encore19
    RecastEffectiveness at the board's tier) and applies the mana lock (0x1020). He dashes (CD_Lucian19_Dash) to the
    safest hex at least MinDashDistance away that keeps his target in range (TR_Add_SafestHexesWithinHexRange): a
    TFTFixedSpeedMovement at 2000 units/s (3400 past 700 units) whose 'Arrive' event fires the shots; the engine takes a
    MinDashDistance (1 hex) dash (D1; VOD1 suggests a little more). FireAtTarget plays CD_Lucian19_CastAnim at his
    target: 'SpellMis' at 0.1494 and 0.3282 s (1800 units/s); with Encore CD_Lucian19_CastAnim_Encore: 'SpellMis' at
    0.1009 and 0.2018 s and 'EncoreMis' at 0.2923 and 0.3834 s. Each missile's OnFired applies GE_SimulateLaunchAttack
    (G11); each arrival GE_Lucian19_Damage = PhysicalDamageCalc1 (ADDamage x AD + APDamage x AP) x the multiplier (1
    for SpellMis, EncoreDamageMult for EncoreMis), physical, on-spell, crit only with Precision. The cast chrono's
    'Unlock' (0.9298 s; Encore 0.8029 s) removes the mana lock and finishes the cast.
    """
    KEY = 'DA_Lucian19'
    DASH = 'CD_Lucian19_Dash'
    CAST, ENCORE_CAST = 'CD_Lucian19_CastAnim', 'CD_Lucian19_CastAnim_Encore'
    DASH_SPEED = 2000  # CD_Lucian19_Dash TFTFixedSpeedMovement MoveSpeed (client asset; the build has no movement modules)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.dash_hexes = self.row('MinDashDistance')
        self.dash = projectile_ticks(self.DASH_SPEED, self.dash_hexes)
        self.set_locks(self.CAST)  # the build has no cast lockout for him: the plain cast's, shown on the panel
        self.notes = ('A cast: a 1-hex dash, then 2 shots (with Encore active, 2 more at the Encore recast strength); '
                      'each shot counts as an attack for on-attack items.')

    def shot_damage(self, level, AD, AP):
        return self.row('ADDamage', star=level) * AD + self.row('APDamage', star=level) * AP

    def encore(self):
        return self.trait_tier('DA_Encore19') > 0 and 'DA_Encore19' in (self.data.d.get('trait_keys') or [])

    def set_locks(self, chrono):
        """The cast's locks: the dash, then the cast chrono's Unlock (mana lock); the next attack the tick after."""
        unlock = self.dash + ticks_up(self.chrono_event(chrono, 'Unlock'))
        self.timing.mana_lock = unlock / TPS
        self.timing.cast_lock = (unlock + 1) / TPS
        self.timing.source['cast_lock'] = self.timing.source['mana_lock'] =             f'{self.DASH} ({self.dash} ticks) + {chrono} Unlock'

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        chrono = self.ENCORE_CAST if self.encore() else self.CAST
        self.set_locks(chrono)
        mult = self.trait_value('DA_Encore19', 'RecastEffectiveness') if self.encore() else 1
        fire = self.tick + self.dash
        self.trace('dash', ticks=self.dash, hexes=self.dash_hexes)
        hexes = self.target_hexes(target)
        for name, eff in (('SpellMis', 1), ('EncoreMis', mult)):
            spawns = [t for p in self.chrono(chrono).get('projectiles') or [] if p['name'] == name
                      for t in p['spawn_at']]
            for spawn in spawns:
                at = fire + ticks_up(spawn)
                self.schedule_tick(at, lambda: self.simulateLaunch(self.items))
                land = at + self.chrono_projectile_ticks(chrono, name, hexes)
                self.trace_projectile(at, land, self, target, 'shot')
                self.schedule_tick(land, lambda eff=eff: self.multiTargetSpell(
                    [target], self.items, self.tick / TPS, 1,
                    lambda level, AD, AP: self.shot_damage(level, AD, AP) * eff, 'physical'))


class Bard(BuildChampion):
    """Come Chime with Me (champions/Bard.md, D1). Script: GA_Bard19_Spell (build ga_scripts.zip).

    The Horn of the Traveler (GA_Bard19_UniqueItem: casts give XP, attacks bonus mana ManaPerAttack, +max mana) is not
    simulated (owner, 2026-11-18): its cast (SpawnMeep, CD_Bard19_CastAnim) only applies with the horn's
    Set19.Unit.Bard.SpecialCast tag, so every cast here is the wave (WaveCast, 0x1bcc). The cast commits, sets Falloff
    = 1 and applies the mana lock (0x197d); CD_Bard19_CastAnimMeeps plays. At 'FireMeeps' (0.4381 s) it aims a 2000 x
    600 rectangle from Bard to hit the most enemies with his attack target among them
    (FindRectangleRotationFromLocationToHitActorsWithRequired, 0x4f5) and plays CD_Bard19_MeepProjectile from the board's
    edge behind him along that line to beyond the far edge: its 'MeepHitbox' moves at 1000 units/s. Each enemy it
    overlaps (0xf49) gets GE_Bard19_MeepWaveDamage with SetByCaller Falloff, then Falloff = max(Falloff x (1 -
    FalloffPerUnit), MinimumDamagePercent) (0x113f, 0x1f4): 1, 0.7, 0.49, ... down to 0.2. The effect (client asset):
    MagicDamageCalc1 (MeepsDamage x AP) x Falloff, magic, AOE, on-spell, crit only with Precision, its total spread
    over its 0.2 s duration at a 0.1 s period (bDoTotalDamageOverDuration), so two halves, the first on application.
    The cast chrono's 'Unlock' (0.8402 s) removes the mana lock and finishes the cast.

    Assumed (D1): the wave starts half a hex behind him (he stands in his back row); it meets the page's number of
    targets (owner, 2026-11-18: 2 by default), all next to the target and so in its width, and the enemy 2 hexes
    behind the target, in the line (G22).
    """
    KEY = 'DA_Bard19'
    AREA = True  # its damage depends on the page's number of targets (layout.py)
    CAST, WAVE = 'CD_Bard19_CastAnimMeeps', 'CD_Bard19_MeepProjectile'
    LENGTH, WIDTH = 2000, 600  # GA_Bard19_Spell defaults 'Line Length', 'Line Width'
    BEHIND = 0.5  # hexes from the board's back edge to Bard (assumed, D1)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.fire = self.chrono_event(self.CAST, 'FireMeeps')
        unlock = ticks_up(self.chrono_event(self.CAST, 'Unlock'))
        self.timing.mana_lock = unlock / TPS
        self.timing.cast_lock = (unlock + 1) / TPS
        self.timing.source['cast_lock'] = self.timing.source['mana_lock'] = f'{self.CAST} Unlock (WaveCast; D1)'
        speeds = {p['speed'] for p in self.chrono(self.WAVE).get('projectiles') or [] if p['name'] == 'MeepHitbox'}
        if len(speeds) != 1:
            raise BuildDataError(f'{self.KEY}: {self.WAVE} has no single MeepHitbox speed in build {self.build.version}')
        self.wave_speed = speeds.pop()
        self.halves = round(0.2 / 0.1)  # GE_Bard19_MeepWaveDamage: duration 0.2 s, period 0.1 s (client asset)
        self.notes = ('A cast: a wave of meeps along the line through his target; each enemy it meets takes 210 x AP '
                      'magic, 30% less for each one before it (at least 20%). The Horn of the Traveler is not '
                      'simulated.')

    def wave_damage(self, level, AD, AP):
        return self.row('Meeps Damage', star=level) * AP

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        fire = self.tick + ticks_up(self.fire)
        falloff, step, floor = 1.0, self.row('FalloffPerUnit'), self.row('MinimumDamagePercent')
        if self.tracer is not None:  # the wave, from behind him along the line (the fight viewer)
            (ux, uy), _ = layout.line_hits(self, target, self.opponents, self.LENGTH, self.WIDTH)
            bx, by = layout.world(self.hex)
            back = self.BEHIND * HEX_UNITS
            self.trace_projectile(fire, fire + ticks_up(self.LENGTH / self.wave_speed), (bx - ux * back, by - uy * back),
                                  (bx + ux * (self.LENGTH - back), by + uy * (self.LENGTH - back)), 'wave')
        for d, along in self.line(target, self.LENGTH, self.WIDTH):
            hit = fire + ticks_up((self.BEHIND * HEX_UNITS + along) / self.wave_speed)
            for k in range(self.halves):
                self.schedule_tick(hit + ticks_up(k * 0.1), lambda d=d, f=falloff: self.multiTargetSpell(
                    [d], self.items, self.tick / TPS, 1,
                    lambda level, AD, AP: self.wave_damage(level, AD, AP) * f / self.halves, 'magical'))
            falloff = max(falloff * (1 - step), floor)


class Syndra(BuildChampion):
    """Serve's Up (champions/Syndra.md, D1). Script: GA_Syndra19_Spell (build ga_scripts.zip).

    The cast commits (0x2bc8), plays CD_Syndra19_CastAnim at her attack target and applies the mana lock (0x290f).
    The chrono runs three phases (Default 0.7749 s, Windup 1.0240 s, FinishAnimation 0.2011 s): its 'Volleyball'
    (2400 units/s) spawns at 1.3085 s and 'Unlock' (1.99 s) removes the mana lock and finishes the cast. The ball's
    hit applies GE_Syndra19_PrimaryDamage (MagicDamageCalc1 = PrimaryDamageAP x AP) to the target, then looks for an
    enemy behind it (0xf): TR_Add_UnitsWithinExpandingCone from the hit, pointing away from Syndra, 1800 units long,
    StartingBounceAngle (120 degrees) wide and SearchAngleIncreasePerCheck (30) wider each check until one is found,
    the target excluded; sorted by distance, then farthest row first, then fewest items. The ball flies there
    (CD_Syndra19_Bounce 'Bounce', 2000 units/s) and applies GE_Syndra19_SecondaryDamage (MagicDamageCalc2 =
    SecondaryDamageAP x AP); with nobody behind, it bounces in place on the target (CD_Syndra19_BounceInPlace, a
    fixed-time 'Bounce' with no time of its own: the chrono's length, 0.4999 s, G21) and hits it again. Both
    magic, on-spell, crit only with Precision (client assets). The script reads ShredPercent and ShredDuration (0)
    but applies nothing with them.
    """
    KEY = 'DA_Syndra19'
    CAST, BOUNCE, IN_PLACE = 'CD_Syndra19_CastAnim', 'CD_Syndra19_Bounce', 'CD_Syndra19_BounceInPlace'
    CONE_LENGTH = 1800  # GA_Syndra19_Spell literal (ConeLength)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.launch = self.chrono_projectile_spawn(self.CAST, 'Volleyball')
        unlock = ticks_up(self.chrono_event(self.CAST, 'Unlock'))
        self.timing.mana_lock = unlock / TPS
        self.timing.cast_lock = (unlock + 1) / TPS
        self.timing.source['cast_lock'] = self.timing.source['mana_lock'] = f'{self.CAST} Unlock (3 phases)'
        self.in_place = self.chrono(self.IN_PLACE)['length']
        self.notes = ('A cast: a volleyball at her target, then a bounce to an enemy behind it for less (to the target '
                      'itself when nobody is behind).')

    def primary_damage(self, level, AD, AP):
        return self.row('PrimaryDamageAP', star=level) * AP

    def secondary_damage(self, level, AD, AP):
        return self.row('SecondaryDamageAP', star=level) * AP

    def bounce_target(self, target):
        """The enemy behind `target` the bounce goes to (TR_Add_UnitsWithinExpandingCone and the sorts), or None."""
        sx, sy = layout.world(self.hex)
        tx, ty = layout.world(target.hex)
        n = math.hypot(tx - sx, ty - sy) or 1
        ux, uy = (tx - sx) / n, (ty - sy) / n  # away from Syndra
        others = []
        for d in layout.in_play(self.opponents):
            if d is target:
                continue
            x, y = layout.world(d.hex)
            dx, dy = x - tx, y - ty
            dist = math.hypot(dx, dy)
            if dist <= self.CONE_LENGTH:
                angle = math.degrees(math.acos(max(-1.0, min(1.0, (dx * ux + dy * uy) / (dist or 1)))))
                others.append((d, dist, angle, dx * ux + dy * uy))
        width = self.row('StartingBounceAngle')
        while width <= 360 + 1e-9 or not others:
            found = [o for o in others if o[2] <= width / 2 + 1e-6]
            if found or width > 360:
                break
            width += self.row('SearchAngleIncreasePerCheck')
        if not found:
            return None
        return max(found, key=lambda o: (round(o[3], 6), -o[1]))[0]

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        launch = self.tick + ticks_up(self.launch)
        flight = self.chrono_projectile_ticks(self.CAST, 'Volleyball', self.target_hexes(target))

        def lands():
            now = self.tick / TPS
            self.multiTargetSpell([target], self.items, now, 1, self.primary_damage, 'magical')
            other = self.bounce_target(target)
            if other is None:
                at, victim = self.tick + ticks_up(self.in_place), target
            else:
                at = self.tick + self.chrono_projectile_ticks(self.BOUNCE, 'Bounce', layout.distance(target, other))
                victim = other
            self.fly(self.tick, at - self.tick, victim, lambda: self.multiTargetSpell(
                [victim], self.items, self.tick / TPS, 1, self.secondary_damage, 'magical'), source=target, name='bounce')

        self.fly(launch, flight, target, lands, name='volleyball')


class Briar(BuildChampion):
    """Snack Attack (champions/Briar.md, D1). Script: GA_Briar19_Spell (build ga_scripts.zip).

    The cast commits (0x2f63), reads the snack range, AOE range and NumFrenzyAttacks, and picks the snack target: the
    enemies within HexRangeSnack (3) hexes, farthest first (0x268b, 0x1edc); none: her attack target. It plays
    CD_Briar19_Windup at it and applies the mana lock (0x1e5c). 'HealOverWindup' (0 s) heals her (GE_Briar19_Heal:
    nothing against dummies); 'Kick' (0.191 s) starts the dash: CD_Briar19_CastAnim_Short when the snack target was
    under 2.5 hexes (214.5 units) away, else _Long (0xab1). The dash chrono's phases fire 'Boom' (0.31 s): GE_Briar19_
    EmpoweredBuff (AttackSpeed MultiplyAdditive 1 + FrenzyAS: +200%, and tag ChronoTags.Dynamic.CustomAttack.1);
    'Land' (Short 0.5311 s, Long 0.6731 s): GE_Briar19_DamageAOE (PhysicalDamageCalc1 = DamageAOE_AD x AD, physical,
    AOE, on-spell, crit only with Precision) on the enemies within HexRangeAOE (1) of the snack target, her attack
    target if none (0x1576); 'Unlock' (0.8003 / 0.9422 s): FinishCasting (0x19fe). The mana lock stays on.
    With the tag her attack chrono plays the Empowered sequence: CustomLaunchAttack1 at 0.4853 s of 2.6333 s, twice,
    then at 0.5099 s of 2.7667 s, rate-scaled like her other attacks. Each Combat.Event.LaunchAttack.Custom.1 is a
    slash instead of the attack (GA_LaunchMeleeAttack hears only LaunchAttack): GE_Briar19_DamageSlash on the
    attack's target (PhysicalDamageCalc2 = DamageFrenzyAD x AD, physical, AppliesOnSpell and AppliesOnHit.IsAttack:
    on-hit effects, crit only with Precision). At NumFrenzyAttacks (3) the buff comes off (0x231d) and, one tick
    later, the mana lock (DelayUntilNextTick, 0xf): her slashes' mana is lost, as Ashe's and Olaf's.
    Assumed: full health (Slayer, Briar's heal: owner, 2026-11-18). The dash's length (Short / Long) follows the
    snack target, the farthest enemy within 3 hexes; the AOE hits the page's targets (owner, 2026-11-18: the number
    of targets is the enemies an area hits, G22), the target and the enemies next to it, not the snack target's
    neighbours.
    """
    KEY = 'DA_Briar19'
    AREA = True  # its damage depends on the page's number of targets (layout.py)
    ATTACK, WINDUP = 'CD_Briar19_Attack', 'CD_Briar19_Windup'
    SHORT, LONG = 'CD_Briar19_CastAnim_Short', 'CD_Briar19_CastAnim_Long'
    FRENZY = 3  # the selector of the first frenzy animation (3, 4, 5)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        t, ch = self.timing, self.chrono(self.ATTACK)
        launch = self.chrono_event(self.ATTACK, 'LaunchAttack')
        normal_len = next(v['length'] for v in self.data.timing.get('attack_variants') or []
                          if v.get('group') == 'SequentialAttack')
        normal = [{'selector': s, 'min_as': None, 'launch': launch, 'length': normal_len} for s in (1, 2)]
        # the Empowered sequence: the two Attack1/2_Frenzy modules end at the chrono's length, Attack3_Frenzy at its
        # anim_end; their CustomLaunchAttack1 events are the build's two times, in that order
        customs = sorted(tm for n, tm in ch['events'] if n == 'CustomLaunchAttack1')
        if len(customs) != 2:
            raise BuildDataError(f'{self.KEY}: {self.ATTACK} has {len(customs)} CustomLaunchAttack1 times')
        frenzy = [(customs[0], ch['length']), (customs[0], ch['length']), (customs[1], ch['anim_end'])]
        t.variants = normal + [{'selector': self.FRENZY + i, 'min_as': None, 'launch': ln, 'length': lg}
                               for i, (ln, lg) in enumerate(frenzy)]
        t.animations = 2
        t.source['variants'] = f'{self.ATTACK}: SequentialAttack x2, EmpoweredSequence (CustomAttack.1) x3'
        t.mana_lock = 10 ** 6  # lifted the tick after the last slash (onLaunch)
        t.source['mana_lock'] = 'GA_Briar19_Spell: removed the tick after the last slash (0x231d, 0xf)'
        self.kick = ticks_up(self.chrono_event(self.WINDUP, 'Kick'))
        self.dash = {c: {e: ticks_up(self.chrono_event(c, e)) for e in ('Boom', 'Land', 'Unlock')}
                     for c in (self.SHORT, self.LONG)}
        self._set_cast_lock(self.SHORT)
        self.frenzy_left = 0
        self.frenzy_done = 0
        self._planned = 1
        self._this_frenzy = False
        self.notes = ('A cast: a dash at the farthest enemy within 3 hexes, hitting it and the enemies next to it; then '
                      'her next 3 attacks have +200% attack speed and are slashes (her mana is locked until the 3rd). '
                      'Full health assumed.')

    def _set_cast_lock(self, dash):
        self.timing.cast_lock = (self.kick + self.dash[dash]['Unlock'] + 1) / TPS
        self.timing.source['cast_lock'] = f'{self.WINDUP} Kick + {dash} Unlock'

    def aoe_damage(self, level, AD, AP):
        return self.row('DamageAOE_AD', star=level) * AD

    def slash_damage(self, level, AD, AP):
        return self.row('DamageFrenzyAD', star=level) * AD

    def snack_target(self, target):
        near = [d for d in layout.in_play(self.opponents) if layout.distance(self, d) <= self.row('HexRangeSnack')]
        return max(near, key=lambda d: layout.distance(self, d)) if near else target

    def _next_animation(self):
        self._planned = self.FRENZY + self.frenzy_done if self.frenzy_left > 0 else self.launches % 2 + 1
        return self._planned, self.aspd.stat

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        snack = self.snack_target(target)
        sx, sy = layout.world(self.hex)
        x, y = layout.world(snack.hex)
        dash = self.SHORT if math.hypot(x - sx, y - sy) / 214.5 < 2.5 else self.LONG  # 0xab1: literals
        self._set_cast_lock(dash)
        start, ev = self.tick + self.kick, self.dash[dash]
        self.trace('dash', tick=start, ticks=ev['Land'], to=snack, name=dash.rsplit('_', 1)[1].lower())

        def boom():
            self.aspd.modify('MultiplyAdditive', 1 + self.row('FrenzyAS'), key='briar_frenzy')
            self.frenzy_left, self.frenzy_done = int(self.row('NumFrenzyAttacks')), 0

        def land():
            hit = [target] + self.nearby(target, self.row('HexRangeAOE'))  # the page's targets (G22, docstring)
            self.trace('area', at=target, hit=hit)
            self.multiTargetSpell(hit, self.items, self.tick / TPS, len(hit), self.aoe_damage, 'physical')

        self.schedule_tick(start + ev['Boom'], boom)
        self.schedule_tick(start + ev['Land'], land)

    def onLaunch(self, opponents, items):
        self._this_frenzy = self.frenzy_left > 0 and self._planned >= self.FRENZY
        if self._this_frenzy:
            self.frenzy_left -= 1
            self.frenzy_done += 1
            if self.frenzy_left == 0:
                self.aspd.remove('briar_frenzy')
                self.mana_locked_until = self.tick + 1

    def fire_attack(self, opponents, items, moment, paid):
        if not self._this_frenzy:
            return super().fire_attack(opponents, items, moment, paid)
        target, now = opponents[0], self.tick / TPS
        dmg = self.slash_damage(self.level, self.bonus_ad.stat, self.ap.stat)
        crit_dmg = dmg * self.critDamage() if self.canSpellCrit else dmg
        amp = self.dmgMultiplier.stat * self.extraDmgMultiplier.stat
        tags = damage_tags('physical', UNIT, ON_HIT, IS_ATTACK, ON_SPELL)
        self.emit(ONHIT_PRE, CombatEvent(self, target, dtype='physical', tags=tags, time=now), items)
        self.doDamage(target, items, self.crit.stat if self.canSpellCrit else 0, crit_dmg * amp, dmg * amp,
                      'physical', now, tags=tags)
        self.emit(ONHIT_AFTER, CombatEvent(self, target, tags=tags, time=now), items)


class RenataGlasc(BuildChampion):
    """Hostile Measures (champions/RenataGlasc.md, D1). Script: GA_RenataGlasc19_Spell (build ga_scripts.zip).

    The cast plays CD_RenataGlasc19_Spell at her target and applies the mana lock (0xe96). At 'LaunchChains' (0.1974
    s) CD_RenataGlasc19_Projectile's 'Chain' (1800 units/s) flies to her target and CD_RenataGlasc19_Projectile2's
    'Missile' (spline, 1800) to NumSecondaryTargets (2) other enemies, the unpoisoned first. The chain's hit: the
    target gets PrimaryTargetStacks (2) applications of GE_RenataGlasc19_ToxinDamage and a Captivate
    (GE_Virtuosos19_Captivate: CaptivateDurationLong 6 s if its star level <= hers, else Short 3 s); CD_RenataGlasc19_
    SpellEnd plays and its 'Unlock' (0.6578 s) removes the mana lock and finishes the cast. (The build's 3.67 s
    timeline is the 3 s WaitDelay fallback for a chain that never lands.) Each missile: SecondaryTargetStacks (1)
    Toxin and a Captivate. GE_RenataGlasc19_ToxinDamage: HasDuration ToxinDuration (15 s), Period TickRate (0.25 s),
    no stacking (each application its own), MagicDamageCalc3 (ToxinDamageAP x AP), magic, DOT, on-spell, crit only
    with Precision. The DOT damage is spread over the duration (the tooltip's "over 15 seconds": 160 x AP / 60 a
    tick; owner, 2026-11-18: the tooltip is right) and ticks on application (bExecutePeriodicEffectOnApplication not set: Unreal's default true).
    Her Captivates feed Classical (B28): she is the simulated Classical unit.
    """
    KEY = 'DA_RenataGlasc19'
    AREA = True  # its damage depends on the page's number of targets (layout.py)
    CAST, END = 'CD_RenataGlasc19_Spell', 'CD_RenataGlasc19_SpellEnd'
    CHAIN, MISSILE = 'CD_RenataGlasc19_Projectile', 'CD_RenataGlasc19_Projectile2'
    STRICT_CAPTIVATE_FROM = 5986094  # the build whose script compares star levels with Less_IntInt (above)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.launch = self.chrono_event(self.CAST, 'LaunchChains')
        self.end_unlock = self.chrono_event(self.END, 'Unlock')
        self.period = self.row('TickRate')
        self.toxin_ticks = round(self.row('ToxinDuration') / self.period)
        self.toxin_until = {}  # id(dummy) -> the tick its last Toxin ends (unpoisoned first)
        self.notes = ('Toxin: 2 stacks on the target and 1 on each of 2 nearby enemies, each 160 x AP over 15 s; every '
                      'application Captivates (Classical).')

    def toxin_tick(self, level, AD, AP):
        # assumed: the DOT's total is spread over its ticks (D1)
        return self.row('ToxinDamageAP', star=level) * AP / self.toxin_ticks

    def _toxin(self, target, stacks):
        # the long Captivate: a target of her star level or lower (GA_RenataGlasc19_Spell LessEqual_IntInt, to
        # rls-19.1.0.5973071); only a lower one from rls-19.1.0.5986094 (Less_IntInt at 0x183c and 0x256a; the
        # 2026-11-18 PBE notes), or in a patch-notes build that says so (B33)
        strict = (self.build.changelist >= self.STRICT_CAPTIVATE_FROM
                  or 'CaptivateLongIfStarBelow' in (self.data.d.get('patch_rules') or []))
        long = target.level < self.level if strict else target.level <= self.level
        captivate(self, target, self.row('CaptivateDurationLong' if long else 'CaptivateDurationShort'))
        start = self.tick
        end = start + round(self.row('ToxinDuration') * TPS)
        self.toxin_until[id(target)] = max(self.toxin_until.get(id(target), 0), end)
        for k in range(self.toxin_ticks):
            self.schedule_tick(start + round(k * self.period * TPS), lambda: self.multiTargetSpell(
                [target], self.items, self.tick / TPS, 1,
                lambda level, AD, AP: self.toxin_tick(level, AD, AP) * stacks, 'magical'))

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        launch = self.tick + ticks_up(self.launch)
        hit = launch + self.chrono_projectile_ticks(self.CHAIN, 'Chain', self.target_hexes(target))
        unlock = hit - self.tick + ticks_up(self.end_unlock)
        self.timing.mana_lock = unlock / TPS
        self.timing.cast_lock = (unlock + 1) / TPS
        self.fly(launch, hit - launch, target, lambda: self._toxin(target, int(self.row('PrimaryTargetStacks'))),
                 name='chain')
        n = int(self.row('NumSecondaryTargets'))
        others = self.nearby(target, 99)
        others.sort(key=lambda d: self.toxin_until.get(id(d), 0) > self.tick)  # unpoisoned first, then nearest
        for d in others[:n]:
            land = launch + self.chrono_projectile_ticks(self.MISSILE, 'Missile', self.target_hexes(d))
            self.fly(launch, land - launch, d, lambda d=d: self._toxin(d, int(self.row('SecondaryTargetStacks'))),
                     name='missile')


class Zoe(BuildChampion):
    """Paddle Ball (champions/Zoe.md, D1). Script: GA_Zoe19_Spell (build ga_scripts.zip).

    The cast plays CD_Zoe19_CastAnim and applies the mana lock. At 'LaunchProjectile' (0.2884 s) the ball flies
    backwards to a point BehindDistance (300 units, ProjectDistanceThroughTarget(-300), script literal) behind her
    (CD_Zoe19_InitialProjectile, visual); at 'RedirectProjectile' (1.3167 s) CD_Zoe19_RedirectProjectile's 'Ball'
    (spawn 0.0291 s, 2500 units/s) flies from there to the farthest enemy (TR_Add_FurthestEnemyWithoutTags) and the
    first enemy it overlaps takes GE_Zoe19_SpellDamage (MagicDamageCalc1 = SpellDamageAP x AP, magic, on-spell, crit
    only with Precision). On the dummy line the first enemy on that path is her target: 300 units + her attack range.
    If it dies the ball goes on with the overkill (GE_Zoe19_OverkillDamage): dummies never die, not modelled. 'Unlock'
    (1.8147 s) ends the cast (the build: 55 / 56 ticks).
    """
    KEY = 'DA_Zoe19'
    CAST = 'CD_Zoe19_CastAnim'
    REDIRECT = 'CD_Zoe19_RedirectProjectile'
    BEHIND = 300  # GA_Zoe19_Spell 0x13dd ProjectDistanceThroughTarget(..., -300) (script literal, units)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.redirect_at = self.chrono_event(self.CAST, 'RedirectProjectile')
        self.ball_spawn = self.chrono_projectile_spawn(self.REDIRECT, 'Ball')
        self.notes = ('The ball is fired backwards, then redirected through her to her target (the first enemy on its '
                      'path on the dummy line). The overkill ricochet is not modelled: dummies never die.')

    def ball_damage(self, level, AD, AP):
        return self.row('SpellDamageAP', star=level) * AP

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        hexes = self.target_hexes(target) + self.BEHIND / HEX_UNITS
        land = (self.tick + ticks_up(self.redirect_at + self.ball_spawn)
                + self.chrono_projectile_ticks(self.REDIRECT, 'Ball', hexes))
        if self.tracer is not None:  # thrown behind her, then redirected through her to the target (the fight viewer)
            (zx, zy), (tx, ty) = layout.world(self.hex), layout.world(target.hex)
            n = math.hypot(tx - zx, ty - zy) or 1
            behind = (zx - (tx - zx) / n * self.BEHIND, zy - (ty - zy) / n * self.BEHIND)
            redirect = self.tick + ticks_up(self.redirect_at)
            self.trace_projectile(self.tick + ticks_up(self.chrono_event(self.CAST, 'LaunchProjectile')), redirect, self, behind, 'ball')
            self.trace_projectile(redirect + ticks_up(self.ball_spawn), land, behind, target, 'ball')
        self.schedule_tick(land, lambda: self.multiTargetSpell([target], self.items, self.tick / TPS, 1,
                                                               self.ball_damage, 'magical'))


class Xayah(BuildChampion):
    """Feathers Flying Like Leaves on the Wind (champions/Xayah.md, D1). Script: GA_Xayah19_Spell (build
    ga_scripts.zip); effects and chronos from the client assets (rls-19.1.0.5986094 export).

    The cast reads NumFeathers (0x1cdf), sets the spawn delay to 0.8 / NumFeathers (0x1d83), applies the mana lock
    (0x1df9) and plays CD_Xayah19_CastAnim. 'StartFeathers': one GE_SimulateLaunchAttack (0x2ba1) and wave 1 =
    RepeatAction(spawn delay, NumFeathers / 2) (0x2caa; first action at once, A1); 'MoreFeathers': wave 2, the same
    (0xfe). Each feather plays CD_Xayah19_SpellMis at Xayah's attack target from its own place
    (ComputeFeatherStartLocations: a fan behind her, 90 + i x 200 / (NumFeathers / 2) degrees from her facing, 100
    units out for wave 1 and 250 for wave 2). The chrono's first active group picks the missile: wave 1 (no tag)
    waits 0.88 s, wave 2 (MissileSelector.1) 0.4 s, then flies at 3200 units/s (both TFTFixedSpeedMovement; the delays
    are on the projectile module, which the snapshot doesn't read: typed from the asset). On reaching the target:
    GE_Xayah19_InitialDamage = PhysicalDamageCalc1 (FeatherDamage x AD + FeatherDamageAP x AP), physical, on-spell,
    crit only with Precision, and GE_Xayah19_ArmorReduction (-ArmorReduction flat Armor until combat ends: flat
    armor reduction is not modelled, owner policy). The feather then flies on behind the target (MissileSelector.2)
    and hits whoever it crosses with GE_Xayah19_SecondaryDamage (PhysicalDamageCalc2 = RetractionDamage x AD = 0):
    nothing. 'Unlock' removes the mana lock and finishes the cast (the build: 64 / 65 ticks; VOD4 confirms).
    """
    KEY = 'DA_Xayah19'
    CAST, MISSILE = 'CD_Xayah19_CastAnim', 'CD_Xayah19_SpellMis'
    SPAWN_SPREAD = 0.8  # GA_Xayah19_Spell 0x1d83: spawn delay = 0.8 / NumFeathers
    FAN_START, FAN_WIDTH = 90, 200  # ComputeFeatherStartLocations: 90 + i x 200 / (NumFeathers / 2) degrees
    WAVE_RADIUS = (100, 250)  # FeatherVectorDistance for the offsets wave 1 / wave 2 use (0x2b7b, 0x2bd1)
    WAVE_DELAY = (0.88, 0.4)  # CD_Xayah19_SpellMis 'MissileWithDelay - Wave 1' / 'MissileWithLessDelay - Wave 2'

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.wave_events = (self.chrono_event(self.CAST, 'StartFeathers'), self.chrono_event(self.CAST, 'MoreFeathers'))
        self.feather_speed = self.chrono_projectile_speed_fixed(self.MISSILE, 'FeatherMis')
        self.notes = ('A cast: 30 feathers (60 at 3 stars) gather behind her and fly at her target, each '
                      'FeatherDamage x AD + FeatherDamageAP x AP physical; they land 1.1-1.6 s into the cast. Their '
                      '-1 Armor per feather is not modelled (flat armor reduction).')

    def chrono_projectile_speed_fixed(self, chrono, projectile):
        """The speed of the chrono's fixed-speed `projectile` (CD_Xayah19_SpellMis also has the old retracting
        fixed-time missile of the same name, MissileSelector.3, which the script no longer plays)."""
        speeds = {p['speed'] for p in self.chrono(chrono).get('projectiles') or []
                  if p['name'] == projectile and p['movement'] == 'TFTFixedSpeedMovement'}
        if len(speeds) != 1:
            raise BuildDataError(f'{self.KEY}: chrono {chrono} has no single fixed speed for {projectile!r} '
                                 f'in build {self.build.version} ({sorted(speeds)})')
        return speeds.pop()

    def feather_damage(self, level, AD, AP):
        # PhysicalDamageCalc1 (VOD4 19:19 tooltip: 38 = 20 x 1.72 + 3 x 1.10)
        return self.row('FeatherDamage', star=level) * AD + self.row('FeatherDamageAP', star=level) * AP

    def feathers(self, hexes):
        """[(seconds from the cast start to the hit, (dx, dy) start offset in units along / across her facing)]
        for every feather, in spawn order."""
        n = int(self.row('NumFeathers'))
        half = int(n / 2)
        spacing = self.SPAWN_SPREAD / n
        reach = hexes * HEX_UNITS
        out = []
        for wave in (0, 1):
            for k in range(half):
                number = k + 1 if wave == 0 else half - k  # FireFeather(1, 1..half); FireFeather(2, half..1)
                angle = math.radians(self.FAN_START + (number - 1) * self.FAN_WIDTH / half)
                r = self.WAVE_RADIUS[wave]
                dx, dy = r * math.cos(angle), r * math.sin(angle)
                fly = math.hypot(reach - dx, dy) / self.feather_speed  # G4: straight line, height ignored
                out.append((self.wave_events[wave] + k * spacing + self.WAVE_DELAY[wave] + fly, (dx, dy),
                            self.wave_events[wave] + k * spacing + self.WAVE_DELAY[wave]))
        return out

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        cast = self.tick
        self.schedule_tick(cast + ticks_up(self.wave_events[0]), lambda: self.simulateLaunch(self.items))  # G11

        def hit():
            self.multiTargetSpell([target], self.items, self.tick / TPS, 1, self.feather_damage, 'physical')
        sx, sy = layout.world(self.hex)
        tx, ty = layout.world(target.hex)
        n = math.hypot(tx - sx, ty - sy) or 1
        fx, fy = (tx - sx) / n, (ty - sy) / n  # her facing
        for land, (dx, dy), launch in self.feathers(self.target_hexes(target)):
            t0, t1 = cast + ticks_up(launch), cast + ticks_up(land)
            self.fly(t0, t1 - t0, target, hit, source=(sx + dx * fx - dy * fy, sy + dx * fy + dy * fx), name='feather')


class Katarina(BuildChampion):
    """Blade Sonata (champions/Katarina.md, D1). Script: GA_Katarina19_Spell (build ga_scripts.zip).

    The cast plays CD_Katarina19_CastAnimCombined at her attack target and applies the mana lock (0x1f38). Its phases
    are Default (0.2995 s), Movement (0.6 s), MovementEnd (0.5504 s); a FirstActiveGroup picks the Movement group when
    she has the tag Set19.Unit.Katarina.ShouldMove, else NoMovement. 'Spin' (0 s): GE_Katarina19_SpinDamage on the
    enemies within AoERadius (1) hexes of her, her attack target if none (0x7a5): MagicDamageCalc1 = AoEDamageAp x AP,
    magic, AOE, on-spell, crit only with Precision. 'CheckIfMove' (0.2484 s): if her target is within her attack range
    nothing happens (0xcb1); else GE_Katarina19_MovementTag gives the tag and 'Movement' dashes her behind the target.
    NoMovement: 'Eviscerate' 0.835 s, 'Unlock' 1.2743 s; Movement: 1.285 s, 1.4251 s. 'Eviscerate':
    GE_Katarina19_EviscerateDamage on her target (MagicDamageCalc2 = TargetDamageAP x AP, magic, on-spell, crit only
    with Precision); 'Unlock' lifts the mana lock and ends the cast (0x170d). Every enemy hit is Captivated for
    CaptivateDuration (5 s) when the board has Classical (ApplyCaptivate: GE_Virtuosos19_Captivate).
    Simulated: the target stands next to her, so the NoMovement group (the build's first 'Eviscerate' and 'Unlock').
    The spin hits the page's targets (G22: the target and the enemies next to it).
    """
    KEY = 'DA_Katarina19'
    AREA = True  # its damage depends on the page's number of targets (layout.py)
    CAST = 'CD_Katarina19_CastAnimCombined'

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.spin_at = self.chrono_event(self.CAST, 'Spin')
        self.eviscerate_at = self.chrono_event(self.CAST, 'Eviscerate')  # the first: the NoMovement group's
        self.captivate_duration = self.row('CaptivateDuration')
        self.notes = ('A cast: a spin hitting her target and the enemies next to it, then a strike on her target. '
                      'Everyone hit is Captivated (5 s) when Classical is active. Her target is assumed in range '
                      '(no dash).')

    def spin_damage(self, level, AD, AP):
        return self.row('AoEDamageAp', star=level) * AP

    def eviscerate_damage(self, level, AD, AP):
        return self.row('TargetDamageAP', star=level) * AP

    def performAbility(self, opponents, items, time):
        target = opponents[0]

        def spin():
            hit = [target] + self.nearby(target, self.row('AoERadius'))  # the page's targets (G22, docstring)
            self.trace('area', at=self, hit=hit)
            for enemy in hit:
                captivate(self, enemy, self.captivate_duration)
            self.multiTargetSpell(hit, self.items, self.tick / TPS, len(hit), self.spin_damage, 'magical')

        def eviscerate():
            captivate(self, target, self.captivate_duration)
            self.multiTargetSpell([target], self.items, self.tick / TPS, 1, self.eviscerate_damage, 'magical')

        if ticks_up(self.spin_at) == 0:
            spin()  # an event scheduled now would run next tick (update: events before the cast)
        else:
            self.schedule_tick(self.tick + ticks_up(self.spin_at), spin)
        self.schedule_tick(self.tick + ticks_up(self.eviscerate_at), eviscerate)


class Kayn(BuildChampion):
    """Shadow of the Night (champions/Kayn.md, D1). Scripts: GA_Kayn19_Spell, GA_Kayn19_Heartsteel_Passive (build
    ga_scripts.zip).

    The cast commits, applies the mana lock (0x1729) and reads SpellWidth (100), SpellLength (429), SpellHexLength (2)
    and ExtraDashRangeAboveAttackRange (1). MakeDashDecision compares the enemies a SpellLength x SpellWidth rectangle
    from him toward his target holds standing still (EvalNumHitAtStandStill) with the best unoccupied hex within
    SpellHexLength of the target and within his range + 1 of him (TR_Sort_ByNumEnemiesInNHexLineThroughTarget; ties
    to the row nearest the middle): standing still hits more -> Cast(); else he dashes there first (CD_Kayn19_Dash,
    Cast() at 'FinishJump') unless he is already on it (0x1f26). Cast() plays CD_Kayn19_Spell at his target;
    'DealDamage' (0.4591 s): GE_19_KaynDamageEnemies on the enemies in the rectangle from him toward the target, the
    target if none (0x1092): PhysicalDamageCalc1 = SpellPhysicalDamage x AD + SpellMagicDamage x AP, physical,
    on-spell, crit only with Precision. The chrono's end (0.7304 s) lifts the mana lock and finishes the cast
    (CleanupAbility; the build's 22 / 23 ticks).
    Heartsteel Bias (GA_Kayn19_Heartsteel_Passive, when he has the SpellUpgradeTierIsActive and Selected tags): the
    first time his Health + Shield falls to HeartsteelStan_PercentHealthTrigger (70%) of max he becomes the Shadow
    Assassin (1 s untargetable). From then every damage of his with Damage.Source.Unit, at PreMitigation (after crit
    and amps, before resistances), adds GE_Kayn19_Heartsteel_BonusMagicDamage: that amount x
    HeartsteelStan_MagicDamagePostTransform (35%) as magic damage, Damage.Source.Trait (it triggers nothing), no tags,
    never crits.
    Simulated: he stands still (stationary dummies; the dash's length is open, champions/Kayn.md Q16). Dummies never
    hit back, so as the Bias he becomes the Shadow Assassin SHADOW_ASSASSIN_AT (5 s) into combat (owner, 2026-11-18:
    he is fronted for a while, then transforms; VOD6 crossed 70% ~4.8 s in; champions/Kayn.md Q17); the bonus is on
    damage from then on and is not amplified again (as True Damage's, B19).
    """
    KEY = 'DA_Kayn19'
    AREA = True  # the rectangle can hold enemies behind the target (layout.py)
    CAST = 'CD_Kayn19_Spell'
    SHADOW_ASSASSIN_AT = 5.0  # seconds into combat the Bias transforms (owner, 2026-11-18, Q17)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.deal_damage_at = self.chrono_event(self.CAST, 'DealDamage')
        self.notes = ('A cast: a swipe in a 2-hex line toward his target. As the Heartsteel Bias he becomes the '
                      'Shadow Assassin 5 s into combat (in game: at 70% Health), adding 35% of his damage as magic '
                      'damage from then.')

    def spell_damage(self, level, AD, AP):
        return self.row('SpellPhysicalDamage', star=level) * AD + self.row('SpellMagicDamage', star=level) * AP

    def shadow_assassin(self):
        return bool(getattr(self, 'heartsteel_bias', False)) and self.tick >= round(self.SHADOW_ASSASSIN_AT * TPS)

    def swipe_targets(self, target):
        """The dummies in the SpellLength x SpellWidth rectangle from him toward `target`
        (TR_Add_UnitsWithinRectanglePointProjection), nearest first; the target if none."""
        sx, sy = layout.world(self.hex)
        tx, ty = layout.world(target.hex)
        n = math.hypot(tx - sx, ty - sy) or 1
        ux, uy = (tx - sx) / n, (ty - sy) / n
        length, width = self.row('SpellLength'), self.row('SpellWidth')
        hit = []
        for d in layout.in_play(self.opponents):
            x, y = layout.world(d.hex)
            a, off = (x - sx) * ux + (y - sy) * uy, abs((x - sx) * uy - (y - sy) * ux)
            if -1e-9 <= a <= length + 1e-9 and off <= width / 2 + 1e-9:
                hit.append((a, d))
        return [d for _, d in sorted(hit, key=lambda h: h[0])] or [target]

    def doDamage(self, opponent, items, critChance, damageIfCrit, damage, dtype, time, tags=frozenset(),
                 ability_armor_pierce=0, ability_mr_pierce=0):
        super().doDamage(opponent, items, critChance, damageIfCrit, damage, dtype, time, tags, ability_armor_pierce,
                         ability_mr_pierce)
        if UNIT in tags and self.shadow_assassin():
            c = min(1, critChance)
            pre = damage * (1 - c) + damageIfCrit * c  # PreMitigation: after crit (averaged) and amps
            bonus = pre * self.row('HeartsteelStan_MagicDamagePostTransform')
            super().doDamage(opponent, items, 0, bonus, bonus, 'magical', time, tags=damage_tags('magical', TRAIT))

    def performAbility(self, opponents, items, time):
        target = opponents[0]

        def swipe():
            hit = self.swipe_targets(target)
            self.trace('area', at=target, hit=[d for d in hit if d is not target])
            self.multiTargetSpell(hit, self.items, self.tick / TPS, len(hit), self.spell_damage, 'physical')

        self.schedule_tick(self.tick + ticks_up(self.deal_damage_at), swipe)


class Qiyana(BuildChampion):
    """Shuffled Playlist (champions/Qiyana.md, D1). Scripts: GA_Qiyana19_Spell, GA_Qiyana19_PassiveRingRoulette
    (build ga_scripts.zip).

    Ring (the passive): every TimeRingChange (1.5 s, a looping timer from when it is granted) the ring changes to one
    of the two other colours of Red / Green / Blue, picked by RedWeight / GreenWeight / BlueWeight (1 each); in PvP
    rounds a GoldChanceIndependent (10%) roll also adds Gold (1 gold; no combat power).
    Cast: mana lock (0x2a1e); the colour tags are read at the cast (0x2779). She picks the hex within her range of
    the target that puts the most enemies in a line through it (TR_Sort_ByNumEnemiesInLineOffsetNHexBehindTarget,
    LineWidth 440): her own hex -> CD_Qiyana19_CastAnimNoMove, else she dashes (CastAnimMove). 'Fire' (NoMove 0.3498
    s): GE_SimulateLaunchAttack (on-attack items hear one launch, G11) and the 'Wave' projectile is aimed at a point
    WaveNumHexesBehindTarget x 214.5 units behind the target. The wave (spawned 0.3779 s, TFTFixedSpeedMovement 1200,
    a box 100 long and 440 wide) hits each enemy it overlaps once: her target GE_Qiyana19_PrimaryDamage
    (PhysicalDamageCalc1 = DamageAP x AP + DamageAD x AD), the others _SecondaryDamage (PhysicalDamageCalc2 =
    SecondaryDamagePercent x Calc1); physical, AOE, on-spell, crit only with Precision. Red: the _Red versions add
    Calc x RedBonusDamagePercent (20%). Green heals (nothing against dummies). 'ManaUnlock' (0.8491 s) lifts the mana
    lock and, Blue, GE_Qiyana19_ManaRefundBlue gives BlueManaRefund (10) mana; 'Unlock' (1.0912 s) ends the cast.
    Simulated: she stands still (CastAnimNoMove). The ring cycles Red -> Green -> Blue, starting Red at combat start
    and changing every TimeRingChange (owner, 2026-11-18: cycle, not a random pick; champions/Qiyana.md Q17); a cast
    takes the colour the ring shows when it starts: Red x (1 + RedBonusDamagePercent), Blue refunds BlueManaRefund.
    The refund lands at 'ManaUnlock' although the cast is still running (VOD6: +10 27 ticks after the cast). The wave
    hits the target and every dummy within 220 units of its path.
    """
    KEY = 'DA_Qiyana19'
    AREA = True  # the wave hits the enemies along and beside its path (layout.py)
    CAST = 'CD_Qiyana19_CastAnimNoMove'
    HEX = 214.5  # GA_Qiyana19_Spell 0xb3: the wave's end point, in units per hex behind the target (script literal)
    WAVE_HALF_LENGTH, WAVE_HALF_WIDTH = 50, 220  # the 'Wave' projectile's Shape BoxExtent (client asset)
    RING = ('Red', 'Green', 'Blue')  # the cycle's order and first colour (owner, Q17)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        ch = self.CAST
        wave = next(p for p in self.chrono(ch).get('projectiles') or [] if p['name'] == 'Wave')
        self.wave_spawn = wave['spawn_at'][0]
        self.wave_speed = self.chrono_projectile_speed(ch, 'Wave')
        mana_unlock, unlock = self.chrono_event(ch, 'ManaUnlock'), self.chrono_event(ch, 'Unlock')
        self.mana_unlock_ticks = ticks_up(mana_unlock)
        t = self.timing
        t.mana_lock = self.mana_unlock_ticks / TPS
        t.cast_lock = (ticks_up(unlock) + 1) / TPS  # FinishCasting at 'Unlock'; the next attack the tick after (T5)
        t.source['mana_lock'] = f'{ch} ManaUnlock'
        t.source['cast_lock'] = f'{ch} Unlock'
        self.ring_ticks = round(self.row('TimeRingChange') * TPS)
        self.notes = ('A cast: a wave through her target hitting the enemies along and beside it (others take half). '
                      'Her ring cycles Red (+20% damage), Green (a heal), Blue (10 mana back), changing every 1.5 s '
                      'from Red at combat start (in game: a random pick of the other two). She is assumed to cast '
                      'without dashing.')

    def ring_colour(self, tick):
        """The ring's colour at `tick`: RING in turn, one every TimeRingChange from combat start."""
        return self.RING[(tick // self.ring_ticks) % len(self.RING)]

    def wave_damage(self, level, AD, AP, colour='Green'):
        red = 1 + (self.row('RedBonusDamagePercent', star=level) if colour == 'Red' else 0)
        return (self.row('DamageAP', star=level) * AP + self.row('DamageAD', star=level) * AD) * red

    def wave_hits(self, target):
        """[(dummy, units along the wave's path)]: every dummy within the wave's half-width of the line from her to
        WaveNumHexesBehindTarget hexes behind the target, nearest first."""
        sx, sy = layout.world(self.hex)
        tx, ty = layout.world(target.hex)
        n = math.hypot(tx - sx, ty - sy) or 1
        ux, uy = (tx - sx) / n, (ty - sy) / n
        end = n + self.row('WaveNumHexesBehindTarget') * self.HEX
        hit = []
        for d in layout.in_play(self.opponents):
            x, y = layout.world(d.hex)
            a, off = (x - sx) * ux + (y - sy) * uy, abs((x - sx) * uy - (y - sy) * ux)
            if -1e-9 <= a <= end + 1e-9 and off <= self.WAVE_HALF_WIDTH + 1e-9:
                hit.append((d, a))
        return sorted(hit, key=lambda h: h[1])

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        cast = self.tick
        colour = self.ring_colour(cast)  # the colour tags are read at the cast (0x2779)
        self.schedule_tick(cast + ticks_up(self.chrono_event(self.CAST, 'Fire')), lambda: self.simulateLaunch(self.items))
        spawn = cast + ticks_up(self.wave_spawn)
        hits = self.wave_hits(target)
        secondary = self.row('SecondaryDamagePercent')
        if hits:
            last = spawn + ticks_up(max(0, hits[-1][1] - self.WAVE_HALF_LENGTH) / self.wave_speed)
            self.trace('dash', tick=spawn, ticks=last - spawn, to=hits[-1][0], name='wave')
        for d, along in hits:
            eff = 1 if d is target else secondary

            def land(d=d, eff=eff):
                self.multiTargetSpell([d], self.items, self.tick / TPS, 1,
                                      lambda level, AD, AP: self.wave_damage(level, AD, AP, colour) * eff, 'physical')
            self.schedule_tick(spawn + ticks_up(max(0, along - self.WAVE_HALF_LENGTH) / self.wave_speed), land)

        def refund():
            # GE_Qiyana19_ManaRefundBlue after the mana lock comes off, while the cast still runs (addMana would wait
            # for the cast lock)
            self.curMana += self.row('BlueManaRefund') * self.manaGainMultiplier.stat
        if colour == 'Blue':
            self.schedule_tick(cast + self.mana_unlock_ticks, refund)


class Seraphine(BuildChampion):
    """Livestream of Note (champions/SeraphineIndie.md, D1). Script: GA_Seraphine19_Spell (build ga_scripts.zip). Her
    three forms are three units with the same stats and rows (DA_SeraphineIndie19, _RisingStar19, _Superstar19); the
    spell reads the form (SeraphineFormIndex 1 / 2 / 3, 0x3e8c).

    The cast commits, applies the mana lock (0x4449) and plays CD_Seraphine19_CastAnim at her target. NumFires =
    Round(SpellDuration / SpellTickRate + 1) = Round(2.1 / 0.15 + 1) = 15 (script defaults, 0x3f2a).
    'BeginFire' (0.2997 s): RepeatAction(SpellTickRate, NumFires), first action at once (A1): each fire sends a note
    (CD_Seraphine19_Splines 'SpellMis', 1900 units/s) from her left speaker and, SpellTickRate / 2 later, one from her
    right (0x2929), both at her target. Each note: GE_Seraphine19_Damage = MagicDamageCalc1 (DamageAP x AP) with two
    DivideAdditive modifiers, SetByCaller NumFires and 2: magic, on-spell, crit only with Precision.
    Rising Star and Superstar (form >= 2): 'SecondFire' (1.1739 s) and 'ThirdFire' (2.0487 s) each fire bonus notes
    (FireBonusNotes): RisingStarExtraNotes - Round(it / 2) = 4, then Round(it / 2) = 4 notes, spread in turn over the
    N nearest enemies (TR_Add_N_NearestEnemiesWithoutTags, her target if none; GetRepeatingListFromTargetData), each
    CD_Seraphine19_SplinesBonus (1900) and GE_Seraphine19_DamageBonusNote = MagicDamageCalc2 (ExtraNoteDamageAP x AP).
    Superstar (form 3): 'HighNote' (0.269 s): a CD_Seraphine19_HighNoteMis ('HighNote', 1800, arc 500) at every enemy,
    GE_Seraphine19_DamageHighNote = MagicDamageCalc3 (HighNoteDamageAP x AP). 'Unlock' (2.6974 s) ends the cast
    (the build's 81 / 82 ticks).
    Each note deals MagicDamageCalc1 / (NumFires x 2) = / 30, the 30 notes the tooltip's total (owner, 2026-11-18:
    VOD6's numbers are 12 per note, the 25s two notes shown merged; champions/SeraphineIndie.md Q16). GAS's own
    rule would add the two DivideAdditive terms (1 + 14 + 1 = 16, ledger I5); the owner's reading is used.
    Flights: the target's distance at 1900 (the speakers beside her and the spline's curve not modelled, G4).
    """
    KEY = 'DA_SeraphineIndie19'
    FORM = 1
    CAST = 'CD_Seraphine19_CastAnim'
    NOTE, BONUS, HIGH = 'CD_Seraphine19_Splines', 'CD_Seraphine19_SplinesBonus', 'CD_Seraphine19_HighNoteMis'
    SPELL_DURATION, SPELL_TICK_RATE = 2.1, 0.15  # GA_Seraphine19_Spell defaults (script literals)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.cast_events = {e: self.chrono_event(self.CAST, e) for e in ('HighNote', 'BeginFire', 'SecondFire', 'ThirdFire')}
        self.num_fires = round(self.SPELL_DURATION / self.SPELL_TICK_RATE + 1)
        self.note_divisor = self.num_fires * 2  # the two DivideAdditive SetByCallers as a product (owner, Q16)
        extra = round(self.row('RisingStarExtraNotes'))
        self.bonus_volleys = (extra - round(extra / 2), round(extra / 2))  # 'SecondFire', 'ThirdFire'
        forms = {1: 'a stream of 30 notes at her target', 2: 'a stream of 30 notes at her target and 2 x 4 bonus '
                 'notes at the nearest enemies', 3: 'a high note at every enemy, a stream of 30 notes at her target '
                 'and 2 x 4 bonus notes at the nearest enemies'}
        self.notes = (f'A cast: {forms[self.FORM]}. Each stream note deals DamageAP x AP / 30, the 30 notes the '
                      f'tooltip\'s total.')

    def note_damage(self, level, AD, AP):
        return self.row('DamageAP', star=level) * AP / self.note_divisor

    def bonus_damage(self, level, AD, AP):
        return self.row('ExtraNoteDamageAP', star=level) * AP

    def high_damage(self, level, AD, AP):
        return self.row('HighNoteDamageAP', star=level) * AP

    def _note(self, at, chrono, projectile, target, damage, name):
        def land():
            self.multiTargetSpell([target], self.items, self.tick / TPS, 1, damage, 'magical')
        flight = self.chrono_projectile_ticks(chrono, projectile, self.target_hexes(target))
        self.fly(at, flight, target, land, name=name)

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        cast = self.tick

        def at(seconds, fn):
            if ticks_up(seconds) == 0:
                fn()
            else:
                self.schedule_tick(cast + ticks_up(seconds), fn)

        if self.FORM >= 3:
            def high_notes():
                for d in layout.in_play(self.opponents):
                    self._note(self.tick, self.HIGH, 'HighNote', d, self.high_damage, 'high note')
            at(self.cast_events['HighNote'], high_notes)
        for k in range(self.num_fires):
            for side in (0, 1):
                t = self.cast_events['BeginFire'] + k * self.SPELL_TICK_RATE + side * self.SPELL_TICK_RATE / 2
                at(t, lambda: self._note(self.tick, self.NOTE, 'SpellMis', target, self.note_damage, 'note'))
        if self.FORM >= 2:
            for event, n in zip(('SecondFire', 'ThirdFire'), self.bonus_volleys):
                def volley(n=n):
                    near = self.nearest(n) or [target]
                    for j in range(n):
                        self._note(self.tick, self.BONUS, 'SpellMis', near[j % len(near)], self.bonus_damage, 'bonus note')
                at(self.cast_events[event], volley)


class Yuumi(BuildChampion):
    """Girl, Put Your Records On (Your Head) (champions/Yuumi.md, D1). Scripts: GA_Yuumi19_Spell,
    GA_Yuumi19_EnemyDiscHandler, GA_Yuumi19_GESpecReceiver (build ga_scripts.zip).

    The cast commits and applies the mana lock (0x1ed8) and plays CD_Yuumi19_CastAnimLeft or _Right in turn (same
    times). 'Disk' (0.365 s): a 'Disc' (1800 units/s) at her target; on arrival GE_Yuumi19_DiscDamage =
    MagicDamageCalc1 (DoTDamageAP x AP), magic, on-spell, crit only with Precision, and a disc on the target's head
    (GE_Yuumi19_Disc, proportion 1: no damage of its own; it grants the 1 MR per second shred, not modelled: flat
    resist reduction). 'EncoreDisk' (0.4615 s), only with the Encore tag: an 'EncoreDisc' the same way, its damage and
    its disc's proportion x CT_Encore19 RecastEffectiveness at the Encore level. 'Unlock' (0.9997 s) lifts the lock
    and ends the cast.
    The target's GA_Yuumi19_EnemyDiscHandler counts her discs on it; at NumDiscsToPop + 1 (5) the stack topples: the
    discs come off, the target takes GE_Yuumi19_PoppedDiscDamage = MagicDamageCalc1 x PoppedDotPercentToMainTarget
    (0.4) x the discs' summed proportion (a self-bounce, CD_Yuumi19_ToppleNormalDiscSelfBounce, 0.5997 s), and each of
    the NumTargetsToDistributeDiscs (4) nearest other units MagicDamageCalc1 x PoppedDotPercentToOtherTargets (0.4) /
    4 x that sum (CD_Yuumi19_ToppleNormalDisc, 1450 units/s from the target).
    Simulated: one topple projectile per receiver (the game flies one per disc); discs keep their full proportion
    (DoTDuration 999 s); a disc passing on when an enemy dies is not modelled (dummies don't die).
    """
    KEY = 'DA_Yuumi19'
    AREA = True  # a topple splashes the units nearest the target
    CAST = 'CD_Yuumi19_CastAnimRight'
    SELF_BOUNCE, TOPPLE = 'CD_Yuumi19_ToppleNormalDiscSelfBounce', 'CD_Yuumi19_ToppleNormalDisc'

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.disk_at, self.encore_at = self.chrono_event(self.CAST, 'Disk'), self.chrono_event(self.CAST, 'EncoreDisk')
        unlock = ticks_up(self.chrono_event(self.CAST, 'Unlock'))
        t = self.timing
        t.mana_lock, t.cast_lock = unlock / TPS, (unlock + 1) / TPS  # FinishCasting at 'Unlock'; attack the tick after
        t.source['mana_lock'] = t.source['cast_lock'] = f'{self.CAST} Unlock'
        self.self_bounce = ticks_up(self.chrono(self.SELF_BOUNCE)['length'])
        self.stacks = {}  # id(enemy) -> [disc proportions]
        self.notes = ('A cast: a disc at her target (and an Encore disc with Encore). The 5th disc on an enemy topples '
                      'the stack: 40% of the discs\' damage to it, 40% split over the 4 nearest others. MR shred not '
                      'modelled.')

    def disc_damage(self, level, AD, AP):
        return self.row('DoTDamageAP', star=level) * AP

    def encore_effectiveness(self):
        return self.trait_value('DA_Encore19', 'RecastEffectiveness') if self.trait_tier('DA_Encore19') else 0

    def _disc_lands(self, target, prop):
        self.multiTargetSpell([target], self.items, self.tick / TPS, 1,
                              lambda level, AD, AP: self.disc_damage(level, AD, AP) * prop, 'magical')
        discs = self.stacks.setdefault(id(target), [])
        discs.append(prop)
        if len(discs) >= self.row('NumDiscsToPop') + 1:
            total = sum(discs)
            discs.clear()
            self._topple(target, total)

    def _topple(self, target, total):
        main = self.row('PoppedDotPercentToMainTarget') * total
        share = self.row('PoppedDotPercentToOtherTargets') / self.row('NumTargetsToDistributeDiscs') * total

        def hit(d, prop):
            return lambda: self.multiTargetSpell([d], self.items, self.tick / TPS, 1,
                                                 lambda level, AD, AP: self.disc_damage(level, AD, AP) * prop,
                                                 'magical')
        self.fly(self.tick, self.self_bounce, target, hit(target, main), source=target, name='topple')
        others = layout.around(target, 99, self.opponents)[:int(self.row('NumTargetsToDistributeDiscs'))]
        for d in others:
            flight = self.chrono_projectile_ticks(self.TOPPLE, 'ToppleDisc', layout.distance(target, d))
            self.fly(self.tick, flight, d, hit(d, share), source=target, name='topple')

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        cast = self.tick
        throws = [(self.disk_at, 'Disc', 1)]
        if self.trait_tier('DA_Encore19'):
            throws.append((self.encore_at, 'EncoreDisc', self.encore_effectiveness()))
        for at, name, prop in throws:
            def throw(name=name, prop=prop):
                flight = self.chrono_projectile_ticks(self.CAST, name, self.target_hexes(target))
                self.fly(self.tick, flight, target, lambda: self._disc_lands(target, prop), name='disc')
            self.schedule_tick(cast + ticks_up(at), throw)


class Yone(BuildChampion):
    """Two Sides (champions/Yone.md, D1). Scripts: GA_Yone19_Passive, GA_Yone19_LaunchMeleeAttack, GA_Yone19_Spell
    (build ga_scripts.zip).

    Form (GA_Yone19_Passive, re-checked whenever AD or AP changes): AD form while AttackDamage >= AbilityPower, else
    AP form (DA_Yone19_APOverride: role MagicFighter; attacks, strikes and the final slash use the Magic calcs).
    Attacks deal AutoAttackDamage x AD physical, or x AP magic in AP form (MagicDamageCalc3).
    Cast (GA_Yone19_Spell): commit, mana lock (0x1973), CD_Yone19_CastAnim (or _CastAnimAlt when UseAltAnims, which the
    decoded defaults set; VOD6 plays the non-Alt times, champions/Yone.md E3). 'StartStrikes' (0.4992 s):
    a strike at once and then on a looping timer GetTimeBetweenSlashes = TimeBetweenSlashes (0.085 s) / (1 +
    Min((Max(AS / base AS, 1) - 1) x SpeedUpWithAS (0.5), MaxSpeedUp (2))), until NumSpirits strikes. A strike plays
    CD_Yone19_SpellMissile (a clone) at its target: strike k even -> her attack target, odd -> the next of the
    NumBonusEnemies (2) enemies within AOERangeAroundCurrentTarget (2) hexes of the target (row distance; refilled
    when used up; the target if none) (GetSliceTarget, PercentStrikesOnTarget 0.5). At its 'Damage' event:
    GE_Yone19_Damage = PhysicalDamageCalc1 (PrimaryDamage x AD; _Magic: x AP) x TankDamageMult (1 off tanks),
    on-spell, crit only with Precision. Every NumSlashesForSimulatedAuto (3) strikes: GE_SimulateLaunchAttack. After
    the last strike: FinalSlash, CD_Yone19_CastAnim_Part2 (_Alt): 'DealDamage' (0.3453 s) GE_Yone19_FinalDamage
    (PhysicalDamageCalc2 = SecondaryDamage x AD; _Magic x AP) on the target; 'Unlock' (0.6589 s) lifts the lock and
    ends the cast.
    Heartsteel Bias (SpellUpgradeTierIsActive + Selected): HeartsteelStan_ExtraClones (2) more strikes, the slash time
    x NumSpirits / (NumSpirits + 2) (the cast lasts as long), and while casting his spell damage carries
    GE_Yone19_ArmorIgnore (Armor x GenericCalc1 = 1 - 0.25; _MRIgnore in AP form).
    Simulated: the strike damage at the SpellMissile's k mod 4-th 'Damage' time (which selector maps to which of its
    four groups isn't decoded); the timer on whole ticks from the exact times; the form at each attack and cast.
    """
    KEY = 'DA_Yone19'
    AREA = True  # odd strikes go to the enemies near the target
    # the non-Alt timelines: VOD6's casts fit them, not the Alt ones the script's defaults name (E3)
    CAST, PART2, MISSILE = 'CD_Yone19_CastAnim', 'CD_Yone19_CastAnim_Part2', 'CD_Yone19_SpellMissile'
    TIME_BETWEEN_SLASHES, SPEED_UP_WITH_AS, MAX_SPEED_UP = 0.085, 0.5, 2.0  # GA_Yone19_Spell defaults
    SLASHES_PER_LAUNCH = 3  # NumSlashesForSimulatedAuto

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.start_strikes = self.chrono_event(self.CAST, 'StartStrikes')
        self.deal, self.unlock = self.chrono_event(self.PART2, 'DealDamage'), self.chrono_event(self.PART2, 'Unlock')
        self.damage_times = sorted(t for n, t in self.chrono(self.MISSILE)['events'] if n == 'Damage')
        self.timing.lock_scales_with_as = False  # the script's own rule (GetTimeBetweenSlashes), set per cast
        self.timing.source['lock_scales_with_as'] = 'GA_Yone19_Spell GetTimeBetweenSlashes (per cast)'
        self._set_locks()
        self.notes = ('A cast: 10 strikes alternating between his target and up to 2 enemies near it, then a final '
                      'slash on the target; AP form (AP above AD) makes everything magic. As the Heartsteel Bias: 2 more '
                      'strikes in the same time and 25% armor (MR) ignored.')

    def ap_form(self):
        return self.ap.stat > self.bonus_ad.stat

    def bias(self):
        return bool(getattr(self, 'heartsteel_bias', False))

    def strikes(self):
        n = int(self.row('NumSpirits'))
        return n + (int(self.row('HeartsteelStan_ExtraClones')) if self.bias() else 0), n

    def slash_interval(self):
        n, base = self.strikes()
        speed = min((max(self.aspd.stat / self.base_aspd, 1) - 1) * self.SPEED_UP_WITH_AS, self.MAX_SPEED_UP)
        return self.TIME_BETWEEN_SLASHES * (base / n) / (1 + speed)

    def _set_locks(self):
        n, _ = self.strikes()
        end = ticks_up(self.start_strikes + (n - 1) * self.slash_interval() + self.unlock)
        self.timing.mana_lock, self.timing.cast_lock = end / TPS, (end + 1) / TPS
        self.timing.source['mana_lock'] = self.timing.source['cast_lock'] = f'{self.CAST} + {self.PART2} Unlock'

    def _scale(self, row):
        ap = self.ap_form()
        return lambda level, AD, AP: self.row(row, star=level) * (AP if ap else AD)

    def _dtype(self):
        return 'magical' if self.ap_form() else 'physical'

    def performAttack(self, opponents, items, time, multiplier=None, generateMana=True):
        if not self.ap_form():
            return super().performAttack(opponents, items, time, multiplier, generateMana)
        attack = Attack(opponents=opponents, multiplier=multiplier if multiplier is not None else Stat(0, 1, 0),
                        scaling=lambda level, baseAD, AD, AP: self.row('AutoAttackDamage', star=level) * AP,
                        attackType='magical')
        self.doAttack(attack, items, time)
        if generateMana:
            self.addMana(self.manaPerAttack.stat)
        if opponents:
            self.emit(ONHIT_AFTER, CombatEvent(self, opponents[0], tags=damage_tags('magical', UNIT, IS_ATTACK, ON_HIT),
                                               time=time), items)

    def _hit(self, targets, row):
        ignore = self.row('HeartsteelStan_ArmorIgnore') if self.bias() else 0
        ap = self.ap_form()
        self.multiTargetSpell(targets, self.items, self.tick / TPS, len(targets), self._scale(row), self._dtype(),
                              ability_armor_pierce=0 if ap else ignore, ability_mr_pierce=ignore if ap else 0)

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        cast = self.tick
        self._set_locks()  # read by _cast after this (attack speed and the Bias now)
        n, _ = self.strikes()
        interval = self.slash_interval()
        bonus = []  # the secondary targets still to strike

        def slice_target(k):
            if k % 2 == 0:
                return target
            if not bonus:
                near = [d for d in layout.around(target, self.row('AOERangeAroundCurrentTarget'), self.opponents)]
                bonus.extend(near[:int(self.row('NumBonusEnemies'))] or [target])
            return bonus.pop(0)

        for k in range(n):
            at = self.start_strikes + k * interval

            def strike(k=k):
                d = slice_target(k)
                hit_at = self.tick + ticks_up(self.damage_times[k % len(self.damage_times)])
                self.trace_projectile(self.tick, hit_at, self, d, 'strike')
                self.schedule_tick(hit_at, lambda: self._hit([d], 'PrimaryDamage'))
                if (k + 1) % self.SLASHES_PER_LAUNCH == 0:
                    self.simulateLaunch(self.items)
            self.schedule_tick(cast + ticks_up(at), strike)
        final = self.start_strikes + (n - 1) * interval
        self.schedule_tick(cast + ticks_up(final + self.deal), lambda: self._hit([target], 'SecondaryDamage'))


class Tristana(BuildChampion):
    """Head Banger (champions/Tristana.md, D1). Script: GA_Tristana19_Spell (build ga_scripts.zip).

    The cast applies the mana lock (0x2b49) and plays CD_Tristana19_CastAnim_Part1. 'Fire', 'Fire2', 'Fire3' (0.1549,
    0.1738, 0.1906 s) each throw a bomb (CD_Tristana19_CastAnim_Part1_BIGProjectile for the first, _Projectile for
    the others; fixed-time splines) at the nearest enemy not yet bombed (GetTargets: row distance; her target when
    none is left); the bombs stick. Part1's 'Unlock' (0.5454 s) starts KnockThemDown: CD_Tristana19_CastAnim_FinalShot
    at the first small bomb's enemy, then the second's, then the big bomb's (0x2bce), played at rate 1.25, 1.25, 1
    (0x1163); each shot's 'SmallBomb' / 'MainBomb' (spawned 0.1549 s / rate, 1800 units/s) detonates that bomb:
    GE_Tristana19_Damage = PhysicalDamageCalc1 (ADDamage x AD + APDamage x AP), the last GE_Tristana19_DamageBig =
    PhysicalDamageCalc2 (FinalShotPercentOfNormalShot (2) x Calc1); physical, on-spell, crit only with Precision. The
    last detonation also applies GE_SimulateLaunchAttack (0x2067). Each shot's 'Unlock' (0.6386 s / rate) starts the
    next; after the third EndSpell lifts the lock and ends the cast.
    Simulated: the big bomb on her target (the nearest), the small ones on the next nearest enemies (the target again
    when there are none); each chrono starts on the tick its predecessor's 'Unlock' lands.
    """
    KEY = 'DA_Tristana19'
    AREA = True  # the small bombs go to the enemies near her
    PART1, SHOT = 'CD_Tristana19_CastAnim_Part1', 'CD_Tristana19_CastAnim_FinalShot'
    SHOT_RATES = (1.25, 1.25, 1.0)  # KnockThemDown's play rates for the 1st, 2nd and 3rd shot (script literals)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.part1_unlock = ticks_up(self.chrono_event(self.PART1, 'Unlock'))
        self.shot_unlock = self.chrono_event(self.SHOT, 'Unlock')
        self.shot_spawn = next(p['spawn_at'][0] for p in self.chrono(self.SHOT)['projectiles'] if p['name'] == 'MainBomb')
        self.shot_starts = [self.part1_unlock]
        for rate in self.SHOT_RATES[:-1]:
            self.shot_starts.append(self.shot_starts[-1] + ticks_up(self.shot_unlock / rate))
        end = self.shot_starts[-1] + ticks_up(self.shot_unlock / self.SHOT_RATES[-1])
        t = self.timing
        t.mana_lock, t.cast_lock = end / TPS, (end + 1) / TPS
        t.source['mana_lock'] = t.source['cast_lock'] = f'{self.PART1} + 3 x {self.SHOT} (rates {self.SHOT_RATES})'
        self.notes = ('A cast: bombs on her target and the 2 enemies nearest her, then she shoots each one; the last '
                      '(her target\'s) deals double.')

    def bomb_damage(self, level, AD, AP):
        return self.row('ADDamage', star=level) * AD + self.row('APDamage', star=level) * AP

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        cast = self.tick
        others = [d for d in self.nearest(3) if d is not target][:2]
        order = [others[0] if others else target, others[1] if len(others) > 1 else target, target]
        big = self.row('FinalShotPercentOfNormalShot')
        for k, (d, start, rate) in enumerate(zip(order, self.shot_starts, self.SHOT_RATES)):
            last = k == len(order) - 1

            def shoot(d=d, last=last):
                flight = self.chrono_projectile_ticks(self.SHOT, 'MainBomb', self.target_hexes(d))

                def detonate():
                    if last:
                        self.simulateLaunch(self.items)
                    self.multiTargetSpell([d], self.items, self.tick / TPS, 1,
                                          lambda level, AD, AP: self.bomb_damage(level, AD, AP) * (big if last else 1),
                                          'physical')
                self.fly(self.tick, flight, d, detonate, name='bomb')
            self.schedule_tick(cast + start + ticks_up(self.shot_spawn / rate), shoot)


class Mel(BuildChampion):
    """Chain of Blues (champions/Mel.md, D1). Scripts: GA_Mel19_Spell, GA_Mel19_Passive (build ga_scripts.zip).

    The cast applies the mana lock (0x21c4) and plays CD_Mel19_CastAnim. 'Fire' (0.5076 s): RepeatAction(
    TimeBetweenMissiles 0.04 s, NumMissiles), first at once (A1). Missile n (from 1) goes to her target when n mod
    (1 / (1 - PercentDamageOnCurrentTarget)) = n mod 2.5 <= 1, else to the next of her secondary targets (the
    NumEnemies nearest by row distance; her target if none): 3 of every 5 on the target. Each plays CD_Mel19_SpellMissile
    ('SpellMis', 2100 units/s); arrival: GE_Mel19_TargetDamage = MagicDamageCalc1 (APDamage x AP), magic, on-spell, crit
    only with Precision, then a Blues stack (GE_Mel19_RadianceDRReduction: infinite, AggregateByTarget, for the rest of
    combat). The RepeatAction's OnFinished (one interval after the last missile, T15) plays CD_Mel19_CastAnimOut; its
    'Unlock' (0.3214 s) lifts the lock and ends the cast (62 / 63 ticks).
    Passive (GA_Mel19_Passive): her on-spell damage to an enemy with Blues stacks carries
    GE_Mel19_RadianceDRReductionForDamageInstanceOnly: the target's IncomingDamageMultiplier x (1 + GenericCalc1 x
    stacks), GenericCalc1 = NegativeDRForRadianceBundle (0.05) / RadianceStacksForNegativeDR (3): +5% per 3 stacks,
    pro rata.
    Simulated: the passive on her missiles (her only on-spell damage here); a missile's own stack comes after its
    damage.
    """
    KEY = 'DA_Mel19'
    AREA = True  # 2 of every 5 missiles go to the nearest other enemies
    CAST, OUT, MISSILE = 'CD_Mel19_CastAnim', 'CD_Mel19_CastAnimOut', 'CD_Mel19_SpellMissile'
    TIME_BETWEEN_MISSILES = 0.04  # GA_Mel19_Spell default (script literal)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.fire_at = self.chrono_event(self.CAST, 'Fire')
        self.num_missiles = int(self.row('NumMissiles'))
        # the RepeatAction's OnFinished (which plays the CastAnimOut) comes one interval after its last action (T15)
        finished = ticks_up(self.fire_at + self.num_missiles * self.TIME_BETWEEN_MISSILES)
        end = finished + ticks_up(self.chrono_event(self.OUT, 'Unlock'))
        t = self.timing
        t.mana_lock, t.cast_lock = end / TPS, (end + 1) / TPS
        t.source['mana_lock'] = t.source['cast_lock'] = f'{self.CAST} Fire + missiles + {self.OUT} Unlock'
        # MissileSelector 1-4 (the script's n mod 4) pick the TFTFixedSpeedSplineMovement modules; 5-6 (fixed time)
        # aren't used
        speeds = {p['speed'] for p in self.chrono(self.MISSILE).get('projectiles') or []
                  if p['name'] == 'SpellMis' and p['movement'] == 'TFTFixedSpeedSplineMovement'}
        if len(speeds) != 1:
            raise BuildDataError(f'{self.KEY}: {self.MISSILE} fixed-speed SpellMis speeds {speeds}')
        self.missile_speed = speeds.pop()
        self.per_stack = self.row('NegativeDRForRadianceBundle') / self.row('RadianceStacksForNegativeDR')
        self.blues = {}  # id(enemy) -> stacks
        self.notes = ('A cast: 30 missiles, 3 of every 5 at her target, the rest at the nearest others. Each adds a Blues '
                      'stack for the rest of combat; her ability deals +5% per 3 stacks to that enemy.')

    def missile_damage(self, level, AD, AP):
        return self.row('APDamage', star=level) * AP

    def _missile_lands(self, d):
        amp = 1 + self.per_stack * self.blues.get(id(d), 0)
        self.multiTargetSpell([d], self.items, self.tick / TPS, 1,
                              lambda level, AD, AP: self.missile_damage(level, AD, AP) * amp, 'magical')
        self.blues[id(d)] = self.blues.get(id(d), 0) + 1

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        cast = self.tick
        period = 1 / (1 - self.row('PercentDamageOnCurrentTarget'))
        others = []

        def pick(n):
            if n % period <= 1 + 1e-9:
                return target
            if not others:
                others.extend([d for d in self.nearest(int(self.row('NumEnemies'))) if d is not target] or [target])
            return others.pop(0)

        for n in range(1, self.num_missiles + 1):
            def fire(n=n):
                d = pick(n)
                flight = projectile_ticks(self.missile_speed, self.target_hexes(d))
                self.fly(self.tick, flight, d, lambda: self._missile_lands(d), name='missile')
            self.schedule_tick(cast + ticks_up(self.fire_at + (n - 1) * self.TIME_BETWEEN_MISSILES), fire)


class Jinx(BuildChampion):
    """Boom Boom POW POW (champions/Jinx.md, D1). Script: GA_Jinx19_Spell (build ga_scripts.zip).

    The cast applies the mana lock (0x18c6) and plays CD_Jinx19_Spell_FixedTime (speed 1). NumMissilesToFire =
    Round(AttackSpeedCalc1), a native MMC (MMC_Jinx19_AttackSpeedScaling) the tooltip spells out: BaseMissiles (16) +
    1 per BonusASPerBonusMissile (35%) bonus attack speed, the bonus counted pro rata (VOD6: 17 at +30%, E1). The
    missiles are dealt out (0x2faf): Round(N x share) each for 'AATarget' (PercentMissilesOnCurrentTarget 0.75),
    'NHexRange' (PercentMissilesOnNHexWithinTarget 0.15: an enemy within NHex (2) hexes of the target) and 'Other'
    (PercentMissilesEveryoneElse 0.1), padded with 'AATarget' to N, cut to N and shuffled. 'BeginFiring' (0.5604 s):
    RepeatAction(FireOverTime (1.2 s) / (N - 1), N), first at once; each a CD_Jinx19_Missile_new 'Rocket' (2400
    units/s); arrival: GE_Jinx19_RocketDamage = PhysicalDamageCalc1 (DamagePerMissileAD x AD + DamagePerMissileAP x
    AP), physical, on-spell, crit only with Precision. Every NumMissilesPerSimulatedAuto (5) missiles:
    GE_SimulateLaunchAttack. 'Unlock' (2.2235 s) lifts the lock and ends the cast (the build's 67 / 68 ticks).
    Simulated: the shuffle replaced by an even interleave; NHexRange missiles spread over the enemies within 2 hexes
    of the target (the target if none), Other over the rest (the NHexRange enemies, then the target, if none).
    """
    KEY = 'DA_Jinx19'
    AREA = True  # a quarter of her missiles go to the other enemies
    CAST, MISSILE = 'CD_Jinx19_Spell_FixedTime', 'CD_Jinx19_Missile_new'
    FIRE_OVER_TIME = 1.2  # GA_Jinx19_Spell default (script literal)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.begin_firing = self.chrono_event(self.CAST, 'BeginFiring')
        speeds = {p['speed'] for p in self.chrono(self.MISSILE).get('projectiles') or [] if p['name'] == 'Rocket'}
        if len(speeds) != 1:
            raise BuildDataError(f'{self.KEY}: {self.MISSILE} Rocket speeds {speeds}')
        self.rocket_speed = speeds.pop()
        self.notes = ('A cast: 16 missiles + 1 per 35% bonus attack speed over 1.2 s, 75% at her target, 15% at enemies '
                      'within 2 hexes of it, 10% at the others.')

    def num_missiles(self):
        bonus = max(0.0, self.aspd.stat / self.base_aspd - 1)
        return int(math.floor(self.row('BaseMissiles') + bonus / self.row('BonusASPerBonusMissile') + 0.5))

    def missile_damage(self, level, AD, AP):
        return self.row('DamagePerMissileAD', star=level) * AD + self.row('DamagePerMissileAP', star=level) * AP

    def plan(self, n):
        """The missiles' categories in firing order: the script's counts, its shuffle replaced by an even interleave."""
        shares = [('AATarget', self.row('PercentMissilesOnCurrentTarget')),
                  ('NHexRange', self.row('PercentMissilesOnNHexWithinTarget')),
                  ('Other', self.row('PercentMissilesEveryoneElse'))]
        total = sum(s for _, s in shares)
        logic = []
        for name, s in shares:
            logic += [name] * int(math.floor(n * s / total + 0.5))
        logic += ['AATarget'] * max(0, n - len(logic))
        logic = logic[:n]
        counts = {k: logic.count(k) for k in ('AATarget', 'NHexRange', 'Other')}
        slots = sorted(((i + 0.5) / c, k) for k, c in counts.items() for i in range(c))
        return [k for _, k in slots]

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        cast = self.tick
        n = self.num_missiles()
        near = layout.around(target, self.row('NHex'), self.opponents)
        rest = [d for d in layout.in_play(self.opponents) if d is not target and d not in near]
        pools = {'AATarget': [target], 'NHexRange': near or [target], 'Other': rest or near or [target]}
        used = {k: 0 for k in pools}
        interval = self.FIRE_OVER_TIME / (n - 1) if n > 1 else 0
        per_launch = int(self.row('NumMissilesPerSimulatedAuto'))
        for k, kind in enumerate(self.plan(n)):
            pool = pools[kind]
            d = pool[used[kind] % len(pool)]
            used[kind] += 1

            def fire(d=d, k=k):
                if (k + 1) % per_launch == 0:
                    self.simulateLaunch(self.items)
                flight = projectile_ticks(self.rocket_speed, self.target_hexes(d))
                self.fly(self.tick, flight, d, lambda: self.multiTargetSpell(
                    [d], self.items, self.tick / TPS, 1, self.missile_damage, 'physical'), name='rocket')
            self.schedule_tick(cast + ticks_up(self.begin_firing + k * interval), fire)


class Ahri(BuildChampion):
    """Burn it Down (champions/Ahri.md, D1). Script: GA_19_Ahri_Spell (build ga_scripts.zip).

    Fox-fires: BaseFoxFires (6) at combat start (the unit's Stack attribute); each basic cast's 'Unlock' adds
    FoxFiresPerCast (AddFoxFires), up to MaxFoxFires (14). The cast applies the mana lock (0x481e); with fewer than
    MaxFoxFires it plays CD_19_Ahri_CastAnim_Basic: 'StartMissiles' (0.1398 s) fires every fox-fire,
    RepeatAction(0.5 / N, N) first at once, each CD_Ahri19_FoxFireAtTarget (2100 units/s) at her target:
    GE_19_Ahri_PrimaryDamage = MagicDamageCalc1 (APDamage x AP). Its 'Unlock' (0.9981 s) adds the fox-fires; when
    that reaches the max, CD_19_Ahri_SpiritRushActivationPose plays ('PowerUp' 0.2009 s: GE_Ahri19_SpiritRush, the
    flow; 'Unlock' 0.7512 s) before the cast ends; else the cast ends there (EndSpell).
    In the flow (fox-fires at the max) she plays CD_19_Ahri_CastAnim_Empowered: a 'HeartMis' (spawned 0.3642 s, 1600)
    at her target: GE_19_Ahri_SecondaryDamage = MagicDamageCalc2 (APDamage_Secondary x AP); the fox-fires ('SpellMis',
    1600, spawned at the chrono's eight times in turn) fly PercentDistanceBeforeSplit (half) of the way and split
    (CD_Ahri19_EmpowedSpell_SpreadMissile): every other one at her target (PercentMissilesOnCurrentTarget 0.5), the
    others at enemies within HexRangeAroundTarget (2) of it (her target if none); each MagicDamageCalc1. 'Unlock'
    (0.9443 s) ends the cast. All magic, on-spell, crit only with Precision.
    Simulated: a fox-fire's whole flight at its own speed (the split's second leg at the same speed); the split's
    secondary enemies in turn.
    """
    KEY = 'DA_Ahri19'
    AREA = True  # the flow's fox-fires split to enemies within 2 hexes of the target
    BASIC, POSE, EMPOWERED = ('CD_19_Ahri_CastAnim_Basic', 'CD_19_Ahri_SpiritRushActivationPose',
                              'CD_19_Ahri_CastAnim_Empowered')
    FOX = 'CD_Ahri19_FoxFireAtTarget'
    BASIC_SPREAD = 0.5  # RepeatAction(0.5 / N, N) (script literal)
    SPLIT_EVERY = 2  # 1 / PercentMissilesOnCurrentTarget (0.5, a script default)

    def __init__(self, level, build=None):
        super().__init__(level, build)
        self.start_missiles = self.chrono_event(self.BASIC, 'StartMissiles')
        self.basic_unlock = ticks_up(self.chrono_event(self.BASIC, 'Unlock'))
        self.pose_unlock = ticks_up(self.chrono_event(self.POSE, 'Unlock'))
        self.empowered_unlock = ticks_up(self.chrono_event(self.EMPOWERED, 'Unlock'))
        proj = {p['name']: p for p in self.chrono(self.EMPOWERED).get('projectiles') or []
                if p['movement'] == 'TFTFixedSpeedMovement'}
        self.heart_spawn, self.heart_speed = proj['HeartMis']['spawn_at'][0], proj['HeartMis']['speed']
        self.split_spawns, self.split_speed = proj['SpellMis']['spawn_at'], proj['SpellMis']['speed']
        self.fox = int(self.row('BaseFoxFires'))
        self.notes = ('Casts throw her fox-fires (6, +2 a cast, up to 14) at her target; at 14 she enters the flow: a '
                      'heart at her target and the fox-fires split between it and enemies within 2 hexes.')

    def fox_damage(self, level, AD, AP):
        return self.row('APDamage', star=level) * AP

    def heart_damage(self, level, AD, AP):
        return self.row('APDamage_Secondary', star=level) * AP

    def _locks(self, end):
        self.timing.mana_lock, self.timing.cast_lock = end / TPS, (end + 1) / TPS

    def _hit(self, d, damage):
        self.multiTargetSpell([d], self.items, self.tick / TPS, 1, damage, 'magical')

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        cast = self.tick
        top = int(self.row('MaxFoxFires'))
        n = self.fox
        if n >= top:
            self._locks(self.empowered_unlock)
            self.schedule_tick(cast + ticks_up(self.heart_spawn), lambda: self.fly(
                self.tick, projectile_ticks(self.heart_speed, self.target_hexes(target)), target,
                lambda: self._hit(target, self.heart_damage), name='heart'))
            near = layout.around(target, self.row('HexRangeAroundTarget'), self.opponents) or [target]
            for k in range(n):
                d = target if k % self.SPLIT_EVERY == 0 else near[(k // self.SPLIT_EVERY) % len(near)]

                def fire(d=d):
                    self.fly(self.tick, projectile_ticks(self.split_speed, self.target_hexes(d)), d,
                             lambda: self._hit(d, self.fox_damage), name='fox-fire')
                self.schedule_tick(cast + ticks_up(self.split_spawns[k % len(self.split_spawns)]), fire)
            return
        after = min(top, n + int(self.row('FoxFiresPerCast')))
        self._locks(self.basic_unlock + (self.pose_unlock if after >= top else 0))
        for k in range(n):
            def fire():
                self.fly(self.tick, self.chrono_projectile_ticks(self.FOX, 'SpellMis', self.target_hexes(target)),
                         target, lambda: self._hit(target, self.fox_damage), name='fox-fire')
            self.schedule_tick(cast + ticks_up(self.start_missiles + k * self.BASIC_SPREAD / n), fire)

        def add():
            self.fox = after
        self.schedule_tick(cast + self.basic_unlock, add)


class Jhin(BuildChampion):
    """String Quartet (champions/Jhin.md, D1). Scripts: GA_Jhin19_Passive, GA_ForceSequentialAttack_Jhin (build
    ga_scripts.zip); effects GE_Jhin19_*.

    No spell: his bar is Ammo (4). GE_Jhin19_ASToADConverter (infinite): AttackSpeed Override 1.0 on Channel0, so
    Channel1 (items, traits) leaves AttackSpeed = 1 + every bonus; AttackDamage AddBase on Channel2 = ASToADRatio x
    (that AttackSpeed through Channel1 - 1) (AttributeMagnitudeEvaluatedUpToChannel, not snapshot: it follows every
    later bonus); AttackSpeed clamped to BaseAttackSpeed on Channel2 (0.84; 1.04 at 3 stars). So he attacks at 0.84
    and each 1% bonus AS is 0.8% AD (VOD6 E1: AS 0.84 all fight, AD 16% at +20%).
    Every launch (any Combat.Event.LaunchAttack, 0x8e9b): GE_Jhin19_AmmoTracker (-1 Ammo), attacks blocked for
    AttackLockout / (AS / 0.8) (GetJhinASScalar); then, Ammo 0 -> GE_Jhin19_Reload (+4). The block ends before his next
    attack is due, so Ammo never delays him (E2).
    The sequence (CurrentAttackCounter 1..4, advanced at each launch): each attack's start (CustomEventOnAttack1)
    spawns a violin until he ascends. Attacks 1-3 (LaunchAttack, 0.534 s): his attack plus ShootViolins(3000): every
    violin out fires CD_Jhin19_ViolinAttack's 'ViolinMis' at his target; the first to arrive applies
    GE_Jhin19_ViolinDamage = PhysicalDamageCalc1 (ViolinDamageAD x AD) x NumViolins (SetByCaller) and Captivates
    (CaptivateDuration, with Classical). Attack 4 (CustomLaunchAttack1, 0.534 s; no attack projectile): ShootViolins
    (4200) and CD_Jhin19_4thShotMis '4thShot' (4000): GE_Jhin19_4thShotDamage = PhysicalDamageCalc2, AppliesOnSpell +
    AppliesOnHit.IsAttack, crit only with Precision, Captivate; the violins then despawn. Per cycle: 1+2+3+4 violin
    hits and the empowered shot.
    Ascension: the Num4thShotsToAscend-th 4th shot, UltDelay / scalar later, stops him (GE_UnitStopAttackingMoving
    Casting) for CD_Jhin19_CastAnim; its 'Unlock' applies GE_Jhin19_UltiForm (range 44, CustomAttack.2) (E2: 54
    ticks from that shot to the next launch). From then the 4 violins stay out, launches come at 'CustomLaunchAttack2/3'
    (0.2508 s) and everything pierces: a 'PiercingMis' (GE_Jhin19_PiercingAutoAttack, his attack damage, AOE,
    IsAttack) or on the 4th a '4thPiercingMis' (Calc2), and every violin its own 'ViolinMisPierce' (Calc1, no
    NumViolins), each 4000 units/s through the target to 3000 units, a box 300 wide: per projectile the first enemy
    takes x1, each later one x max(previous x (1 - DamageReductionPerHit), MinDamagePercent) = x0.4.
    Encore (members, RecastEffectiveness r at the Encore tier): each violin attack's 'Encore' (0.494 s / scalar)
    fires again (ViolinAttackEncore: Calc1 x r x NumViolins once; piercing: per violin, x r x the multiplier); the
    4th shot fires a second one EncoreDelay / scalar later (Calc2 x r, AppliesOnHit at r). Damage terms on one
    damage component multiply (champions/Jhin.md D1: added, r + 0.4 - 1 would be negative).
    Simulated: violins fly from his hex (they float beside him); the dummies along a piercing line are those within
    150 units of it (G22 layout); on-hit effects of pierced enemies are not scaled by their x0.4.
    """
    KEY = 'DA_Jhin19'
    AREA = True  # piercing shots after ascension hit the dummies behind the target (layout.py)
    ATTACK = 'CD_Jhin19_Attack_new'
    VIOLIN = 'CD_Jhin19_ViolinAttack'
    VIOLIN_PIERCE = 'CD_Jhin19_ViolinAttack_Piercing'
    SHOT, PIERCE_SHOT, PIERCE = 'CD_Jhin19_4thShotMis', 'CD_Jhin19_4thPiercingMis', 'CD_Jhin19_PiercingMis'
    ULT = 'CD_Jhin19_CastAnim'
    # GA_Jhin19_Passive defaults and literals: EncoreDelay, UltDelay, AttackLockout (s), ShootViolins' speeds, the
    # piercing distance, GetJhinASScalar's divisor, the projectiles' half width (BoxExtent Y)
    ENCORE_DELAY, ULT_DELAY, ATTACK_LOCKOUT = 0.1, 0.6, 0.6
    VIOLIN_SPEED, FOURTH_VIOLIN_SPEED, PIERCE_LENGTH, AS_SCALAR, HALF_WIDTH = 3000, 4200, 3000, 0.8, 150
    AMMO = 4

    def __init__(self, level, build=None):
        super().__init__(level, build)
        # GE_Jhin19_ASToADConverter
        base_as = self.row('BaseAttackSpeed', star=level)
        ratio = self.row('ASToADRatio')
        self.aspd.modify('=', 1.0, channel=0)
        self.aspd.modify('at most', base_as, channel=2)
        self.aspd.modify('at least', base_as, channel=2)
        self.bonus_ad.modify('+', AttributeBased(self.aspd, ratio, post=-ratio, up_to=1), channel=2)
        self.seq, self.fourth_shots, self.ascended = 1, 0, False
        self.ammo = self.AMMO
        self.ascend_at = self.row('Num4thShotsToAscend', star=level)
        self.pierce_launch = self.chrono_event(self.ATTACK, 'CustomLaunchAttack2')
        self.violin_encore_at = self.chrono_event(self.VIOLIN, 'Encore')
        self.notes = ('No spell: every attack summons a violin; the violins out fire with each attack, the 4th is '
                      'empowered. After the 3rd empowered shot (1st at 3 stars) he ascends: 4 violins, faster '
                      'launches, everything pierces (later enemies take 40%). Bonus attack speed becomes AD (x0.8).')

    def canCast(self, time=None):
        return False  # no spell: the bar is Ammo (GE_Jhin19_AmmoTracker / _Reload)

    def violin_damage(self, level, AD, AP):
        return self.row('ViolinDamageAD', star=level) * AD

    def shot_damage(self, level, AD, AP):
        return self.row('4thShotDamageAD', star=level) * AD + self.row('4thShotDamageAP', star=level) * AP

    def scalar(self):
        return self.aspd.stat / self.AS_SCALAR  # GetJhinASScalar

    def encore(self):
        return self.trait_value('DA_Encore19', 'RecastEffectiveness') if self.trait_tier('DA_Encore19') else 0

    def pierce_hits(self, target):
        """[(dummy, units along)] within HALF_WIDTH of the line from him through `target`, PIERCE_LENGTH long."""
        sx, sy = layout.world(self.hex)
        tx, ty = layout.world(target.hex)
        n = math.hypot(tx - sx, ty - sy) or 1
        ux, uy = (tx - sx) / n, (ty - sy) / n
        hit = []
        for d in layout.in_play(self.opponents):
            x, y = layout.world(d.hex)
            a, off = (x - sx) * ux + (y - sy) * uy, abs((x - sx) * uy - (y - sy) * ux)
            if 0 < a <= self.PIERCE_LENGTH and off <= self.HALF_WIDTH + 1e-9:
                hit.append((d, a))
        return sorted(hit, key=lambda h: h[1]) or [(target, n)]

    # ------------------------------------------------------------------ the launch
    def onLaunch(self, opponents, items):
        self._shot = (self.seq, self.ascended)
        self.ammo -= 1  # GE_Jhin19_AmmoTracker
        self.curMana = self.ammo

        def reload():
            if self.ammo == 0:
                self.ammo = self.curMana = self.AMMO  # GE_Jhin19_Reload
        self.schedule_tick(self.tick + ticks_up(self.ATTACK_LOCKOUT / self.scalar()), reload)
        if self.seq == 4 and not self.ascended:
            self.fourth_shots += 1
            if self.fourth_shots >= self.ascend_at:
                self.schedule_tick(self.tick + ticks_up(self.ULT_DELAY / self.scalar()), self._ascend)
        self.seq = self.seq % 4 + 1

    def _ascend(self):
        """GE_UnitStopAttackingMovingCasting and CD_Jhin19_CastAnim; its 'Unlock' applies GE_Jhin19_UltiForm and the
        next attack starts the tick after (T5)."""
        unlock = ticks_up(self.chrono_event(self.ULT, 'Unlock'))
        self.busy_until = self.tick + unlock + 1
        self.attacking = False
        self.ascend_tick = self.tick

        def ulti_form():
            self.ascended = True
            self.timing.launch = self.pierce_launch  # CustomLaunchAttack2 / 3
        self.schedule_tick(self.tick + unlock, ulti_form)

    def fire_attack(self, opponents, items, moment, paid):
        seq, ascended = self._shot
        target = opponents[0]
        r = self.encore()
        encore_tick = self.tick + ticks_up(self.ENCORE_DELAY / self.scalar())
        if not ascended:
            if seq < 4:
                super().fire_attack(opponents, items, moment, paid)
            else:
                self._fourth_shot(target, 1, IS_ATTACK)
                if r:
                    self.schedule_tick(encore_tick, lambda: self._fourth_shot(target, r))
            self._violins(target, seq, self.FOURTH_VIOLIN_SPEED if seq == 4 else self.VIOLIN_SPEED, r)
            return
        if seq < 4:
            self._pierce(target, self.PIERCE, 'PiercingMis', self._pierced_attack)
        else:
            self._pierce(target, self.PIERCE_SHOT, '4thPiercingMis',
                         lambda d, m: self._shot_lands(d, m, IS_ATTACK, eff=m))
            if r:
                self.schedule_tick(encore_tick, lambda: self._pierce(
                    target, self.PIERCE_SHOT, '4thPiercingMis', lambda d, m: self._shot_lands(d, m * r, eff=m * r)))
        for _ in range(self.AMMO):
            self._pierce(target, self.VIOLIN_PIERCE, 'ViolinMisPierce', self._violin_pierces, name='violin')
        if r:
            def encore_violins():
                for _ in range(self.AMMO):
                    self._pierce(target, self.VIOLIN_PIERCE, 'ViolinMisPierce',
                                 lambda d, m: self._violin_pierces(d, m * r), name='violin')
            self.schedule_tick(self.tick + ticks_up(self.violin_encore_at / self.scalar()), encore_violins)

    def _violins(self, target, n, speed, r):
        """ShootViolins: n violins fire; the first arrival deals Calc1 x n (the others none); with Encore the violins
        fire again at 'Encore', the first of those dealing Calc1 x r x n."""
        flight = projectile_ticks(speed, self.target_hexes(target))

        def lands(mult):
            captivate(self, target, self.row('CaptivateDuration'))
            self.multiTargetSpell([target], self.items, self.tick / TPS, 1,
                                  lambda level, AD, AP: self.violin_damage(level, AD, AP) * mult, 'physical')
        self.fly(self.tick, flight, target, lambda: lands(n), name='violin')
        if r:
            at = self.tick + ticks_up(self.violin_encore_at / self.scalar())
            self.fly(at, flight, target, lambda: lands(r * n), name='violin')

    def _fourth_shot(self, target, mult, *extra):
        flight = self.chrono_projectile_ticks(self.SHOT, '4thShot', self.target_hexes(target))
        self.fly(self.tick, flight, target, lambda: self._shot_lands(target, mult, *extra, eff=mult), name='4th shot')

    def _shot_lands(self, target, mult, *tags, eff=1.0):
        """GE_Jhin19_4thShot*Damage: Calc2 x mult, physical, on-spell and on-hit (at `eff`), crit only with Precision."""
        items, now = self.items, self.tick / TPS
        captivate(self, target, self.row('CaptivateDuration'))
        dmg = self.shot_damage(self.level, self.bonus_ad.stat, self.ap.stat) * mult
        crit_dmg = dmg * self.critDamage() if self.canSpellCrit else dmg
        amp = self.dmgMultiplier.stat * self.extraDmgMultiplier.stat
        tags = damage_tags('physical', UNIT, ON_SPELL, ON_HIT, *tags)
        self.emit(ONHIT_PRE, CombatEvent(self, target, dtype='physical', tags=tags, time=now, effectiveness=eff), items)
        self.doDamage(target, items, self.crit.stat if self.canSpellCrit else 0, crit_dmg * amp, dmg * amp,
                      'physical', now, tags=tags)
        self.emit(ONHIT_AFTER, CombatEvent(self, target, tags=tags, time=now, effectiveness=eff), items)

    def _pierce(self, target, chrono, projectile, land, name='pierce'):
        """A projectile through `target`: each dummy on its line when the box's front reaches it, x1 then x0.4."""
        speed = self.chrono_projectile_speed(chrono, projectile)
        reduction, floor = self.row('DamageReductionPerHit'), self.row('MinDamagePercent')
        mult = 1.0
        hits = self.pierce_hits(target)
        self.trace_projectile(self.tick, self.tick + ticks_up(hits[-1][1] / speed), self, hits[-1][0], name)
        for d, along in hits:
            self.schedule_tick(self.tick + ticks_up(max(0, along - 50) / speed), lambda d=d, m=mult: land(d, m))
            mult = max(mult * (1 - reduction), floor)

    def _violin_pierces(self, d, mult):
        captivate(self, d, self.row('CaptivateDuration'))
        self.multiTargetSpell([d], self.items, self.tick / TPS, 1,
                              lambda level, AD, AP: self.violin_damage(level, AD, AP) * mult, 'physical')

    def _pierced_attack(self, d, mult):
        """GE_Jhin19_PiercingAutoAttack: his attack's damage x mult, an attack hit (on-hit effects, normal crits)."""
        self.numAttacks += 1
        self.performAttack([d], self.items, self.tick / TPS, Stat(0, mult, 0), generateMana=False)


class SeraphineRisingStar(Seraphine):
    """Seraphine's Rising Star form (DA_SeraphineRisingStar19): the stream plus the bonus notes (see Seraphine)."""
    KEY = 'DA_SeraphineRisingStar19'
    FORM = 2
    display_name = 'Seraphine (Rising Star)'


class SeraphineSuperstar(Seraphine):
    """Seraphine's Superstar form (DA_SeraphineSuperstar19): high notes, the stream and the bonus notes."""
    KEY = 'DA_SeraphineSuperstar19'
    FORM = 3
    display_name = 'Seraphine (Superstar)'


champ_list = ['Neeko', 'Varus', 'Draven', 'Kaisa', 'Yunara', 'Ziggs', 'Senna', 'Ezreal', 'Lux', 'Gnar', 'Malzahar', 'Samira', 'Karthus',
              'OlafHeroAugment', 'Ashe', 'Viego', 'Kayle', 'Lucian', 'RenataGlasc', 'Zoe', 'Bard',
              'Syndra', 'Briar', 'Xayah', 'Katarina', 'Kayn', 'Qiyana', 'Seraphine', 'SeraphineRisingStar',
              'SeraphineSuperstar', 'Yuumi', 'Yone', 'Tristana', 'Mel', 'Jinx', 'Ahri', 'Jhin']


class TrainingDummy(Champion):
    """The opponents: they never attack, cast or die (G9); the UI sets their HP, armor and MR."""

    def __init__(self, level=1):
        super().__init__('Training Dummy', 1800, 0, 0, -1, 0.01, 100, 100, 1)
        self.timing = Timing(source={'all': 'dummy: never attacks'})

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
from items.debuffs import apply_shred
from traits.classical import captivate
from events import CRIT, IS_ATTACK, ON_HIT, ON_SPELL, ONHIT_AFTER, ONHIT_PRE, UNIT, CombatEvent, damage_tags
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
        # the long Captivate: a target of her star level or lower (the script); from the 2026-11-18 PBE notes only a
        # lower one (a patch-notes rule in the build, B33)
        strict = 'CaptivateLongIfStarBelow' in (self.data.d.get('patch_rules') or [])
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


champ_list = ['Neeko', 'Varus', 'Draven', 'Kaisa', 'Yunara', 'Ziggs', 'Senna', 'Ezreal', 'Lux', 'Gnar', 'Malzahar', 'Samira', 'Karthus',
              'OlafHeroAugment', 'Ashe', 'Viego', 'Kayle', 'Lucian', 'RenataGlasc', 'Zoe', 'Bard',
              'Syndra', 'Briar']


class TrainingDummy(Champion):
    """The opponents: they never attack, cast or die (G9); the UI sets their HP, armor and MR."""

    def __init__(self, level=1):
        super().__init__('Training Dummy', 1800, 0, 0, -1, 0.01, 100, 100, 1)
        self.timing = Timing(source={'all': 'dummy: never attacks'})

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
        hexes = self.target_hexes()  # the layout's target, at attack range (G4)
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
                self.multiTargetSpell(splash, items, now, len(splash),
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
                      "adds up to the same total on identical dummies. Ricochets go to the nearest dummy not yet "
                      "hit (the layout).")

    def record_damage(self, level, AD, AP):
        return self.row('BladeDamage', star=level) * AD

    def vortex_damage(self, level, AD, AP):
        return self.row('BladeRiftPerSecondAD', star=level) * AD + self.row('BladeRiftPerSecondAP', star=level) * AP

    def performAbility(self, opponents, items, time):
        target = opponents[0]
        flight = self.chrono_projectile_ticks(self.CAST, 'Blade', self.target_hexes(target))
        self.schedule_tick(self.tick + ticks_up(self.throw_at) + flight, lambda: self._record_lands(target, [target], 0))

    def _record_lands(self, target, hit, k):
        """The record (k = 0) or its k-th Trickshot ricochet arrives at `target`; `hit` = the enemies hit so far."""
        items = self.items
        eff = self.trait_value('DA_Trickshot19', 'RichochetDamage') ** k if k else 1
        self.multiTargetSpell([target], items, self.tick / TPS, 1,
                              lambda level, AD, AP: self.record_damage(level, AD, AP) * eff, 'physical')
        for j in range(self.vortex_hits):
            def vortex_hit():
                self.multiTargetSpell([target], items, self.tick / TPS, 1,
                                      lambda level, AD, AP: self.vortex_damage(level, AD, AP) * self.VORTEX_TICK * eff,
                                      'physical')
            self.schedule_tick(self.tick + ticks_up(j * self.VORTEX_TICK), vortex_hit)
        if k < self.trait_value('DA_Trickshot19', 'NumRichochets'):
            nxt, hexes = self.ricochet(target, hit)
            step = self.chrono_projectile_ticks(self.BOUNCE, 'Blade', hexes)
            self.schedule_tick(self.tick + step, lambda: self._record_lands(nxt, hit + [nxt], k + 1))


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
            self.schedule_tick(self.tick + flight, lambda target=target: self._missile_lands(target, [target], 0))

    def _missile_lands(self, target, hit, k):
        eff = self.trait_value('DA_Trickshot19', 'RichochetDamage') ** k if k else 1
        self.multiTargetSpell([target], self.items, self.tick / TPS, 1,
                              lambda level, AD, AP: self.missile_damage(level, AD, AP) * eff, 'physical')
        if k < self.trait_value('DA_Trickshot19', 'NumRichochets'):
            nxt, hexes = self.ricochet(target, hit)
            step = self.chrono_projectile_ticks(self.BOUNCE, 'SpellMis', hexes)
            self.schedule_tick(self.tick + step, lambda: self._missile_lands(nxt, hit + [nxt], k + 1))

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
    (Combat.Event.LaunchAttack.SimulateTriggersOnly): on-attack items hear it (simulateLaunch, G11).
    """
    KEY = 'DA_Ziggs19'
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
            self.multiTargetSpell(splash, items, now, len(splash), self.splash_damage, 'magical')

        spawn = self.tick + ticks_up(self.bomb_spawn / rate)
        self.schedule_tick(spawn, lambda: self.simulateLaunch(items))  # 0x9f5: the bomb's first OnFired (G11)
        self.schedule_tick(spawn + flight, land)


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
            self.schedule_tick(self.tick + ticks_up(self.blast_spawn) + flight, land)
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
                    self.multiTargetSpell(splash_targets, items, now, len(splash_targets),
                                          lambda level, AD, AP: self.detonation(level, AD, AP) * splash * eff,
                                          'physical')

            self.schedule_tick(stage2 + ticks_up(spawn) + flight, land)


champ_list = ['Neeko', 'Varus', 'Draven', 'Kaisa', 'Yunara', 'Ziggs', 'Senna', 'Ezreal']


class TrainingDummy(Champion):
    """The opponents: they never attack, cast or die (G9); the UI sets their HP, armor and MR."""

    def __init__(self, level=1):
        super().__init__('Training Dummy', 1800, 0, 0, -1, 0.01, 100, 100, 1)
        self.timing = Timing(source={'all': 'dummy: never attacks'})

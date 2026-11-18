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


champ_list = ['Neeko', 'Varus', 'Draven']


class TrainingDummy(Champion):
    """The opponents: they never attack, cast or die (G9); the UI sets their HP, armor and MR."""

    def __init__(self, level=1):
        super().__init__('Training Dummy', 1800, 0, 0, -1, 0.01, 100, 100, 1)
        self.timing = Timing(source={'all': 'dummy: never attacks'})

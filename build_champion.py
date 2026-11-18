"""Set 19 champions whose numbers come from a client build (docs/ASSUMPTIONS.md E11-E13, B1-B8).

    class Ahri(BuildChampion):
        KEY = 'DA_Ahri19'

        def performAbility(self, opponents, items, time):
            dmg = self.row('APDamage')          # this star's value from the selected build
            ...

    Ahri(level=2)                          # newest imported build
    Ahri(level=2, build=load_build(v))     # a specific build

Base stats, HP and AD per star, mana, attack speed (and its cap), range, role mana and timing are read here and
never typed into champion code. `self.sources` records where each value came from; a value the build lacks is
either a loud BuildDataError or a documented default listed in `self.sources`.
"""
import set19buffs
from buildstore import BuildDataError, load_build
from champion import Champion
from item import Item
from timing import Timing, accelerating_projectile_ticks, projectile_ticks

# Base crit is in no shared asset (native defaults). The owner confirmed on 2026-11-17 that Set 19 keeps
# 25% chance / 140% damage (E12).
BASE_CRIT_CHANCE = 0.25
BASE_CRIT_DAMAGE = 1.4


def curve_at(points, t, interp='Constant'):
    """Value of [[time, value], ...] at t (step or linear, flat outside the points)."""
    if not points:
        return None
    if t <= points[0][0]:
        return points[0][1]
    if t >= points[-1][0]:
        return points[-1][1]
    for (k0, v0), (k1, v1) in zip(points, points[1:]):
        if k0 <= t < k1:
            if interp == 'Constant':
                return v0
            return v0 + (v1 - v0) * (t - k0) / (k1 - k0)
    return points[-1][1]


class BuildRole:
    """The champion's role as the build names it (e.g. 'MagicCaster', 'AttackSpecialist_Ammo'). `archetype` is the
    middle word (Caster, Fighter, ...), which items read as `champion.role.archetype`."""

    def __init__(self, key):
        self.key = key
        self.value = key
        core = key
        for prefix in ('Attack', 'Magic', 'Hybrid'):
            if core.startswith(prefix):
                core = core[len(prefix):]
                break
        self.archetype = core.split('_')[0]
        self.variant = core.split('_')[1] if '_' in core else None

    def __repr__(self):
        return f'BuildRole({self.key})'


class RoleEffects(Item):
    """The role's stat effects from the build, applied in the static-stats pass before any combat phase (E13, B5):
    ManaPerAttack, ManaPerSecond, the ManaMax floor, and attack speed through the role's lookup curve at
    champion.stage (the Fighter's FighterAttackSpeed curve). Other modifiers (movement speed, threat) don't affect
    damage against dummies and are listed in `ignored`."""

    def __init__(self, role_entry):
        super().__init__(name='Role', phases=None)
        self.role_key = role_entry.key
        self.mods = [m for e in role_entry.d.get('effects') or [] if e for m in e.get('modifiers') or []]
        self.ignored = []

    @staticmethod
    def _single(m):
        vals = m.get('values') or []
        if len(set(vals)) != 1:
            raise BuildDataError(f'role modifier {m["attribute"]} is not a single value: {m["text"]}')
        return vals[0]

    def applyStats(self, champion):
        self.ignored = []
        for m in self.mods:
            a, op = m['attribute'], m['op']
            if a == 'ManaPerAttack' and op == '+':
                champion.manaPerAttack.addStat(self._single(m))
            elif a == 'ManaPerSecond' and op == '+':
                champion.manaRegen.addStat(self._single(m))
            elif a == 'ManaMax' and op == 'at least':
                floor = self._single(m)
                if champion.fullMana.base > -1 and champion.fullMana.base < floor:
                    champion.fullMana.base = floor
            elif a == 'AttackSpeed' and m.get('lookup'):
                lk = m['lookup']
                v = curve_at(lk['points'], champion.stage, lk.get('interp') or 'Constant')
                # MultiplyAdditive: the value's excess over 1 is a percent bonus (1.05 -> +5% attack speed)
                champion.aspd.addStat((v - 1) * 100)
            else:
                self.ignored.append(f'{a} {op} {m["text"]}')


class BuildChampion(Champion):
    KEY = None  # the champion's data asset, e.g. 'DA_Ahri19'
    SPELL = None  # the spell timeline that times its casts (default: the build's first)

    def __init__(self, level, build=None):
        if not self.KEY:
            raise TypeError(f'{type(self).__name__} has no KEY')
        b = build or load_build()
        c = b.champion(self.KEY)
        if level not in (1, 2, 3):
            raise BuildDataError(f'{self.KEY}: star level {level} is not in the extracted data (1-3 only)')
        if c.d.get('hp') is None or 'HealthMax' not in c.d['stats']:
            raise BuildDataError(f'{self.KEY} has no HealthMax in build {b.version}')
        if c.d.get('ad') is None:
            raise BuildDataError(f'{self.KEY} has no AutoAttackDamage row in build {b.version}')
        s = c.d['stats']
        mana_max = s.get('ManaMax', -1)
        # level=1 to the base class: HP and AD are already this star's values (E11, B1)
        super().__init__(c.name, c.hp[level - 1], c.ad[level - 1], c.mana_start, mana_max, c.attack_speed,
                         s.get('Armor', 0), s.get('MagicResist', 0), 1)
        self.level = level
        self.build = b
        self.data = c
        self.attack_range = s.get('AttackRange', 1)
        self.role = BuildRole(c.role)
        self.items = [RoleEffects(b.role(c.role))]
        g = b.data.get('globals') or {}
        cap = (g.get('attack_speed_cap') or {}).get('value')
        if cap:
            self.aspd.as_cap = cap
        ex = curve_at(((g.get('excess_crit_to_crit_damage') or {}).get('points')), 1)
        if ex is not None:
            self.excess_crit_ratio = ex
        self.crit.base = s.get('CritChance', BASE_CRIT_CHANCE)
        self.critDmg.base = s.get('CritDamage', BASE_CRIT_DAMAGE)
        self.timing = Timing.from_build(c, spell=self.SPELL)
        # traits (B11): tiers are set at combat start by the board's trait buffs (set19buffs.BuildTrait); the page
        # preselects the champion's own traits that the simulator implements
        self.trait_tiers = {}
        self.spell_crit_sources = 0  # Precision sources (Damage.Status.CanSpellCrit), see addPrecision
        self.default_traits = [name for name in set19buffs.class_buffs
                               if getattr(set19buffs, name).KEY in (c.d.get('trait_keys') or [])]
        self.sources = {
            'build': b.version,
            'hp': f'HealthMax {s["HealthMax"]} x star multiplier', 'ad': 'AutoAttackDamage row',
            'mana': 'ManaStarting/Mana, ManaMax', 'attack_speed': 'AttackSpeed',
            'armor/mr': 'Armor, MagicResist',
            'attack_range': 'AttackRange' if 'AttackRange' in s else 'default 1 (no AttackRange: melee)',
            'role': f'role {c.role} effects', 'attack_speed_cap': 'GE_AttackSpeedMax' if cap else 'default 5',
            'excess_crit_ratio': 'CT_ExtraCritChanceToCritDamage' if ex is not None else 'default 0.5',
            'crit_chance': 'CritChance' if 'CritChance' in s else f'{BASE_CRIT_CHANCE} (owner, 2026-11-17: unchanged in Set 19)',
            'crit_damage': 'CritDamage' if 'CritDamage' in s else f'{BASE_CRIT_DAMAGE} (owner, 2026-11-17: unchanged in Set 19)',
            'timing': self.timing.source,
        }

    def addPrecision(self):
        """One Precision source (an effect granting Damage.Status.CanSpellCrit): spell damage can crit, and with n
        sources the unit has CT_SpellCritToCritDamageConversion(n) bonus crit damage (B7: 0 at 1, +0.1 per extra)."""
        curve = (self.build.data.get('globals') or {}).get('spell_crit_bonus_crit_damage')
        if not curve:
            raise BuildDataError(f'no spell_crit_bonus_crit_damage curve in build {self.build.version}')

        def bonus(n):
            return curve_at(curve['points'], n, curve.get('interp') or 'Constant')

        self.spell_crit_sources += 1
        self.canSpellCrit = True
        self.critDmg.addStat(bonus(self.spell_crit_sources) - bonus(self.spell_crit_sources - 1))

    def row(self, name, star=None):
        """This champion's curve row at its star level (or `star`), from the selected build."""
        return self.data.row(name, star=star or self.level)

    # ------------------------------------------------------------ spell timelines from the build
    def chrono(self, name):
        """One timeline (chrono) in the champion's folder: {'length', 'events': [[name, t], ...], 'projectiles'}."""
        ch = (self.data.d.get('chronos') or {}).get(name)
        if ch is None:
            raise BuildDataError(f'{self.KEY} has no chrono {name!r} in build {self.build.version}')
        return ch

    def chrono_event(self, chrono, event):
        """Seconds from the chrono's start to `event` (the first one of that name)."""
        for n, t in self.chrono(chrono)['events']:
            if n == event:
                return t
        raise BuildDataError(f'{self.KEY}: chrono {chrono} has no event {event!r} in build {self.build.version}')

    def chrono_projectile_speed(self, chrono, projectile):
        """Move speed (units/s) of the projectile named `projectile` that `chrono` spawns."""
        speeds = {p['speed'] for p in self.chrono(chrono).get('projectiles') or [] if p['name'] == projectile}
        if len(speeds) != 1 or None in speeds:
            raise BuildDataError(f'{self.KEY}: chrono {chrono} has no single speed for projectile {projectile!r} '
                                 f'in build {self.build.version} ({sorted(speeds, key=str)})')
        return speeds.pop()

    def chrono_projectile_ticks(self, chrono, projectile, hexes):
        """Flight ticks over `hexes` for the projectile named `projectile` that `chrono` spawns (G4): a fixed speed,
        or an accelerating one (initial speed, acceleration, max speed; P12)."""
        ps = [p for p in self.chrono(chrono).get('projectiles') or [] if p['name'] == projectile]
        accel = {(p['initial_speed'], p['acceleration'], p['max_speed']) for p in ps if 'acceleration' in p}
        if accel:
            if len(accel) != 1 or len(ps) != len([p for p in ps if 'acceleration' in p]):
                raise BuildDataError(f'{self.KEY}: chrono {chrono} has mixed movements for {projectile!r} '
                                     f'in build {self.build.version}')
            return accelerating_projectile_ticks(*accel.pop(), hexes)
        return projectile_ticks(self.chrono_projectile_speed(chrono, projectile), hexes)

    def chrono_projectile_spawn(self, chrono, projectile):
        """Seconds from the chrono's start to the spawn of the projectile named `projectile` (its module's PlayPoint;
        one spawn time only)."""
        spawns = {t for p in self.chrono(chrono).get('projectiles') or [] if p['name'] == projectile
                  for t in p.get('spawn_at') or []}
        if len(spawns) != 1:
            raise BuildDataError(f'{self.KEY}: chrono {chrono} has no single spawn time for {projectile!r} '
                                 f'in build {self.build.version} ({sorted(spawns)})')
        return spawns.pop()

    def trait_tier(self, trait_key):
        """The tier this champion's board reaches in a trait (0 = inactive), set at combat start (B11)."""
        return self.trait_tiers.get(trait_key, 0)

    def trait_value(self, trait_key, row, tier=None):
        """A trait's curve row at a tier (default: the board's tier), from the selected build (exact curve point)."""
        return self.build.trait(trait_key).row(row, col=self.trait_tier(trait_key) if tier is None else tier)

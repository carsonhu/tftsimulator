"""Client-build data for the simulator: every Set 19 number comes from a chosen game build.

    from buildstore import load_build
    b = load_build()                          # newest build in builds/index.json
    b = load_build('rls-19.1.0.5973071.Set19.Shipping.pbe')
    ahri = b.champion('DA_Ahri19')
    ahri.row('APDamage')            -> (28, 42, 400)      # per star, from the champion's curve table
    ahri.row('APDamage', star=2)    -> 42
    ahri.stat('AttackSpeed'), ahri.hp, ahri.ad, ahri.mana_start, ahri.mana_max
    b.role('MagicCaster').modifier('ManaPerAttack') -> 7

A missing name raises BuildDataError naming the build, so a row Riot renames or removes in a new build fails
loudly instead of silently becoming 0. No number in here is edited; see docs/ASSUMPTIONS.md for how each is used.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BUILDS = os.path.join(HERE, 'builds')


class BuildDataError(KeyError):
    pass


class _Entry:
    def __init__(self, build, kind, d):
        self.build, self.kind, self.d = build, kind, d
        self.key, self.name = d.get('key'), d.get('name')

    def _missing(self, what):
        return BuildDataError(f'{self.kind} {self.key} has no {what} in build {self.build.version}')

    def rows(self):
        return dict(self.d.get('ability', self.d).get('rows') or {})


class Champion(_Entry):
    def row(self, name, star=None):
        """Per-star value of a curve-table row: a (1, 2, 3)-star tuple, or one star's value."""
        rows = self.d['ability']['rows']
        if name not in rows:
            raise self._missing(f'curve row {name!r}')
        vals = tuple(rows[name])
        return vals if star is None else vals[star - 1]

    def stat(self, name):
        if name not in self.d['stats']:
            raise self._missing(f'stat {name!r}')
        return self.d['stats'][name]

    def stat_or(self, name, default):
        return self.d['stats'].get(name, default)

    @property
    def hp(self):
        return tuple(self.d['hp'])

    @property
    def ad(self):
        return tuple(self.d['ad'])

    @property
    def attack_speed(self):
        return self.stat('AttackSpeed')

    @property
    def mana_max(self):
        return self.stat_or('ManaMax', 0)

    @property
    def mana_start(self):
        """ManaStarting if the build has it, else Mana (both are starting mana in the attribute map)."""
        return self.d['stats'].get('ManaStarting', self.d['stats'].get('Mana', 0))

    @property
    def role(self):
        return self.d['role']

    @property
    def timing(self):
        return self.d['timing']

    @property
    def calcs(self):
        return self.d['ability']['calcs']


class Role(_Entry):
    def modifier(self, attribute):
        for e in self.d.get('effects') or []:
            for m in (e or {}).get('modifiers') or []:
                if m['attribute'] == attribute:
                    vals = m.get('values') or [None]
                    if len(set(vals)) != 1:
                        raise BuildDataError(f'role {self.key}: {attribute} is not a single value ({m["text"]})')
                    return vals[0]
        raise self._missing(f'modifier {attribute!r}')


class Table(_Entry):
    @property
    def thresholds(self):
        """A trait's tier thresholds in units, ascending (Encore: [2, 4]); [] for items and augments."""
        return sorted(t['threshold'] for t in self.d.get('tiers') or [])

    def tier_of(self, units):
        """The trait tier `units` trait units reach: 0 inactive, 1 the first threshold, ..."""
        return sum(1 for t in self.thresholds if units >= t)

    def row(self, name, col=None):
        """[[time, value], ...] curve points, or the value at one time (exact point only)."""
        rows = self.d.get('rows') or {}
        if name not in rows:
            raise self._missing(f'curve row {name!r}')
        pts = rows[name]
        if col is None:
            return pts
        for t, v in pts:
            if t == col:
                return v
        raise self._missing(f'point {col} of row {name!r}')


class Build:
    def __init__(self, data):
        self.data = data
        self.meta = data['meta']
        self.version = self.meta['version']

    def _get(self, kind, cls, key):
        d = self.data[kind].get(key)
        if d is None:
            raise BuildDataError(f'{kind[:-1]} {key} is not in build {self.version}')
        return cls(self, kind[:-1], d)

    def champion(self, key):
        return self._get('champions', Champion, key)

    def role(self, key):
        return self._get('roles', Role, key)

    def trait(self, key):
        return self._get('traits', Table, key)

    def item(self, key):
        return self._get('items', Table, key)

    def augment(self, key):
        return self._get('augments', Table, key)

    def has_champion(self, key):
        return key in self.data['champions']


def list_builds():
    return json.load(open(os.path.join(BUILDS, 'index.json'), encoding='utf-8'))['builds']


_cache = {}


def load_build(version=None):
    """A build by version string (default: newest). Cached per process."""
    builds = list_builds()
    if version is None:
        version = builds[0]['version']
    if version not in _cache:
        # the index names each build's file (the browser worker fetches the same name, B9)
        file = next((b.get('file') for b in builds if b['version'] == version), None) or f'{version}.json'
        path = os.path.join(BUILDS, file)
        if not os.path.exists(path):
            raise BuildDataError(f'build {version} is not imported (python tools/import_build.py)')
        _cache[version] = Build(json.load(open(path, encoding='utf-8')))
    return _cache[version]

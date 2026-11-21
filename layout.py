"""Where the training dummies stand (restructure step 5): one place answers how far the target is, who stands within
N hexes of a dummy, and where a ricochet goes.

Hexes are axial coordinates (q, r). The champion stands at (0, 0) and its target at (R, 0), R = the champion's
attack range (G4: the target is at attack range). The page sets one number, the targets (owner, 2026-11-18): the
target and `targets` - 1 enemies on the hexes next to it, filled starting behind the target (away from the champion)
and going round, so each is next to the one before (ricochets fly 1 hex, B12). Every splash, line or nearby-enemies
rule of 1 hex or more meets all of them. The targets are every enemy in play (owner, 2026-11-19: "Jhin with 1 target
should only hit 1 target"): there used to be one more, always 2 hexes behind the target, which a 1-target fight's
piercing shots still hit. The default is 2 targets: the target and one enemy behind it. A champion whose damage
does not depend on the targets gets no slider and the default.

A fight with one target also holds a spare dummy far away, out of play: no area, line or ricochet sees it; only
Titanic Hydra's assumed neighbour (owner: always one enemy next to the target) uses it (`neighbour`).

`opponents[0]` stays the target: the dummies are placed, and kept, in that order (nearest the target first).
"""

import math

DIRECTIONS = ((1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1))
HEX_UNITS = 215.0  # world units between hex centres (timing.HEX_UNITS, G4)
TARGETS = 2  # the page's default: the target and 1 enemy next to it
MAX_TARGETS = 7  # the target and its 6 neighbours: the page's cap unless a champion sets its own (TARGETS_MAX)
LIMIT_TARGETS = 10  # a full enemy board (level 10): Vladimir's chandelier hits all of them (owner, 2026-11-20)


def hex_distance(a, b):
    dq, dr = a[0] - b[0], a[1] - b[1]
    return (abs(dq) + abs(dr) + abs(dq + dr)) // 2


def ring(center, radius):
    """The hexes exactly `radius` from `center`, starting behind it (+q) and walking round."""
    q, r = center[0] + radius, center[1]
    out = []
    for i in range(6):
        dq, dr = DIRECTIONS[(i + 2) % 6]
        for _ in range(radius):
            out.append((q, r))
            q, r = q + dq, r + dr
    return out


SHAPES = ("cluster", "line", "rings")


class Layout:
    """The page's layout setting: the number of targets, and how they stand (the champion's `TARGETS_SHAPE`):
    "cluster" (default), the target and the enemies on the hexes next to it; "line", the target and the enemies
    behind it, each 1 hex further, in line with the champion (owner, 2026-11-19: Jhin's piercing shots, at most 3);
    "rings", the i-th enemy `rings[i]` hexes from the target (the last value for the rest), each ring filled in pairs
    mirrored about the champion-target line, furthest from the champion first (owner, 2026-11-20: Vladimir's
    chandelier, the target at its centre, 2 adjacent, 2 at 2 hexes, 2 at 3, the rest at 4; not clumped)."""

    def __init__(self, targets=TARGETS, shape="cluster", rings=None):
        if not 1 <= targets <= LIMIT_TARGETS:
            raise ValueError(f'layout: {targets} targets (1-{LIMIT_TARGETS})')
        if shape not in SHAPES:
            raise ValueError(f'layout: shape {shape!r} (one of {SHAPES})')
        if shape == "rings" and not rings:
            raise ValueError('layout: shape "rings" needs its rings')
        self.targets = targets
        self.shape = shape
        self.rings = tuple(rings) if rings else None

    @property
    def count(self):
        """Dummies a fight needs: the targets, and a spare out of play when there is only one (`neighbour`)."""
        return self.targets + (self.targets == 1)

    def place(self, champion, dummies):
        """Put the champion and `dummies` (the target first) on their hexes; any beyond the targets are out of play."""
        target = (max(1, champion.attack_range or 1), 0)
        if self.shape == "line":  # behind the target, away from the champion
            free = [(target[0] + k, 0) for k in range(1, self.targets)]
        elif self.shape == "rings":
            free = self._ring_spots(target)
        else:  # a melee unit stands on one of the target's neighbouring hexes: skip it (a 7th then stands 2 away)
            free = [h for h in ring(target, 1) + ring(target, 2) if h != (0, 0)]
        spots = [target] + free[:self.targets - 1]
        champion.hex = (0, 0)
        for i, dummy in enumerate(dummies):
            dummy.in_play = i < len(spots)
            dummy.hex = spots[i] if dummy.in_play else (target[0] + 10 + i, 0)

    def _ring_spots(self, target):
        """The hexes of targets 2.. for the "rings" shape: target i at `rings[i]` hexes from the target (the last value
        for any beyond), each ring's hexes in mirrored pairs (the reflection about the champion-target line), the pairs
        furthest from the champion first."""
        def mirror(h):  # reflection about the line r = 0 through the champion and the target (axial q, r)
            return (h[0] + h[1], -h[1])

        queues, spots = {}, []
        for i in range(1, self.targets):
            r = self.rings[i] if i < len(self.rings) else self.rings[-1]
            if r not in queues:
                cands = [h for h in ring(target, r) if h != (0, 0)]
                cands.sort(key=lambda h: (-hex_distance(h, (0, 0)), mirror(h) == h, h[1] < 0))
                order = []
                for h in cands:
                    if h in order:
                        continue
                    order.append(h)
                    m = mirror(h)
                    if m != h and m in cands and m not in order:
                        order.append(m)
                queues[r] = order
            spots.append(queues[r].pop(0))
        return spots

    def __repr__(self):
        rings = f', rings={self.rings}' if self.rings else ''
        return f'Layout(targets={self.targets}, shape={self.shape!r}{rings})'


def in_play(dummies):
    return [d for d in dummies if getattr(d, 'in_play', True)]


def distance(a, b):
    """Hexes between two placed units."""
    return hex_distance(a.hex, b.hex)


def around(target, hexes, dummies):
    """The dummies in play within `hexes` of `target`, not counting it, nearest first (ties in placement order)."""
    near = [d for d in in_play(dummies) if d is not target and distance(d, target) <= hexes]
    return sorted(near, key=lambda d: distance(d, target))


def nearest(unit, n, dummies, exclude=()):
    """The `n` dummies in play nearest `unit` (e.g. the champion), leaving out `exclude`; ties in placement order."""
    near = [d for d in in_play(dummies) if d is not unit and all(d is not x for x in exclude)]
    return sorted(near, key=lambda d: distance(d, unit))[:n]


def neighbour(target, dummies):
    """One enemy next to `target` whatever the page's targets (owner, 2026-11-18: Titanic Hydra): the nearest in play,
    else the spare."""
    near = around(target, 1, dummies)
    if near:
        return near[0]
    spare = [d for d in dummies if d is not target and not getattr(d, 'in_play', True)]
    return spare[0] if spare else next(d for d in dummies if d is not target)


def world(h):
    """A hex's centre in world units (axial coordinates, neighbours HEX_UNITS apart)."""
    q, r = h
    return HEX_UNITS * (q + r / 2), HEX_UNITS * math.sqrt(3) / 2 * r


def line_hits(source, target, dummies, length, width, pool=None):
    """A rectangle `length` x `width` (world units) from `source`, turned to hit the most dummies with `target` among
    them (TFTMathSubsystem.FindRectangleRotationFromLocationToHitActorsWithRequired; directions tried: every degree and
    straight at each dummy, ties to the one nearest the target's direction). Returns (direction, [(dummy, distance
    along the line from source)]) for the dummies of `pool` (default: all) within width / 2 of that line, in front
    of the source, nearest first."""
    dummies = in_play(dummies)
    sx, sy = world(source.hex)
    pts = {id(d): world(d.hex) for d in dummies}

    def along(d, ux, uy):
        x, y = pts[id(d)][0] - sx, pts[id(d)][1] - sy
        return x * ux + y * uy, abs(x * uy - y * ux)

    def inside(d, ux, uy, limit):
        a, off = along(d, ux, uy)
        return -1e-9 <= a <= limit and off <= width / 2 + 1e-9

    tx, ty = pts[id(target)][0] - sx, pts[id(target)][1] - sy
    aim = math.atan2(ty, tx)
    angles = [math.radians(a) for a in range(360)] + [math.atan2(pts[id(d)][1] - sy, pts[id(d)][0] - sx)
                                                      for d in dummies if d.hex != source.hex]
    best = None
    for ang in angles:
        ux, uy = math.cos(ang), math.sin(ang)
        if not inside(target, ux, uy, length):
            continue
        n = sum(inside(d, ux, uy, length) for d in dummies)
        dev = abs(math.remainder(ang - aim, 2 * math.pi))
        if best is None or (n, -dev) > (best[0], -best[1]):
            best = (n, dev, ux, uy)
    if best is None:  # the target is out of reach: straight at it
        ux, uy = math.cos(aim), math.sin(aim)
    else:
        ux, uy = best[2], best[3]
    hits = [(d, along(d, ux, uy)[0]) for d in (dummies if pool is None else in_play(pool))
            if along(d, ux, uy)[0] >= -1e-9 and along(d, ux, uy)[1] <= width / 2 + 1e-9]
    return (ux, uy), sorted(hits, key=lambda h: h[1])


def ricochet(previous, hit, dummies):
    """(next target, hexes flown) for a ricochet from `previous` (B12): the nearest dummy not yet in `hit`; when every
    dummy has been hit, the nearest other one; with a single dummy, back to it (0 hexes). Ties go to the next dummy
    in placement order after `previous`. Only dummies in play."""
    dummies = in_play(dummies)
    n = len(dummies)
    start = dummies.index(previous)

    def order(d):
        return distance(d, previous), (dummies.index(d) - start) % n

    fresh = [d for d in dummies if d is not previous and d not in hit]
    others = fresh or [d for d in dummies if d is not previous]
    if not others:
        return previous, 0
    nxt = min(others, key=order)
    return nxt, distance(nxt, previous)

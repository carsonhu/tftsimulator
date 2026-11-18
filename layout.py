"""Where the training dummies stand (restructure step 5): one place answers how far the target is, who stands within
N hexes of a dummy, and where a ricochet goes.

Hexes are axial coordinates (q, r). The champion stands at (0, 0) and its target at (R, 0), R = the champion's
attack range (G4: the target is at attack range). The other dummies stand around the target: `adjacent` of them on
the hexes next to it, `two_hex` on hexes 2 away, the rest in a line beyond (3, 4, ... hexes from the target). The
default (one of each) is the line of dummies 1 hex apart the engine assumed before (B12): the target, a neighbour,
one 2 hexes away. Each ring is filled starting behind the target (away from the champion), going round.

`opponents[0]` stays the target: the dummies are placed, and kept, in that order (nearest the target first).
"""

import math

DIRECTIONS = ((1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1))
HEX_UNITS = 215.0  # world units between hex centres (timing.HEX_UNITS, G4)
COUNT = 8  # dummies in a fight unless the layout needs more


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


class Layout:
    """The page's layout settings: enemies next to the target and enemies 2 hexes from it."""

    def __init__(self, adjacent=1, two_hex=1):
        if not 0 <= adjacent <= 6 or not 0 <= two_hex <= 12:
            raise ValueError(f'layout: {adjacent} adjacent (0-6), {two_hex} at 2 hexes (0-12)')
        self.adjacent = adjacent
        self.two_hex = two_hex

    @property
    def count(self):
        """Dummies a fight needs: 8, or more when the rings ask for more."""
        return max(COUNT, 1 + self.adjacent + self.two_hex)

    def place(self, champion, dummies):
        """Put the champion and `dummies` (the target first) on their hexes."""
        target = (max(1, champion.attack_range or 1), 0)
        spots = [target] + ring(target, 1)[:self.adjacent] + ring(target, 2)[:self.two_hex]
        spots += [(target[0] + 3 + i, 0) for i in range(max(0, len(dummies) - len(spots)))]
        champion.hex = (0, 0)
        for dummy, spot in zip(dummies, spots):
            dummy.hex = spot

    def __repr__(self):
        return f'Layout(adjacent={self.adjacent}, two_hex={self.two_hex})'


def distance(a, b):
    """Hexes between two placed units."""
    return hex_distance(a.hex, b.hex)


def around(target, hexes, dummies):
    """The dummies within `hexes` of `target`, not counting it, nearest first (ties in placement order)."""
    near = [d for d in dummies if d is not target and distance(d, target) <= hexes]
    return sorted(near, key=lambda d: distance(d, target))


def nearest(unit, n, dummies, exclude=()):
    """The `n` dummies nearest `unit` (e.g. the champion), leaving out `exclude`; ties in placement order."""
    near = [d for d in dummies if d is not unit and all(d is not x for x in exclude)]
    return sorted(near, key=lambda d: distance(d, unit))[:n]


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
    hits = [(d, along(d, ux, uy)[0]) for d in (dummies if pool is None else pool)
            if along(d, ux, uy)[0] >= -1e-9 and along(d, ux, uy)[1] <= width / 2 + 1e-9]
    return (ux, uy), sorted(hits, key=lambda h: h[1])


def ricochet(previous, hit, dummies):
    """(next target, hexes flown) for a ricochet from `previous` (B12): the nearest dummy not yet in `hit`; when every
    dummy has been hit, the nearest other one; with a single dummy, back to it (0 hexes). Ties go to the next dummy
    in placement order after `previous` (the line of dummies the engine assumed before)."""
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

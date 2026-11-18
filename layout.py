"""Where the training dummies stand (restructure step 5): one place answers how far the target is, who stands within
N hexes of a dummy, and where a ricochet goes.

Hexes are axial coordinates (q, r). The champion stands at (0, 0) and its target at (R, 0), R = the champion's
attack range (G4: the target is at attack range). The other dummies stand around the target: `adjacent` of them on
the hexes next to it, `two_hex` on hexes 2 away, the rest in a line beyond (3, 4, ... hexes from the target). The
default (one of each) is the line of dummies 1 hex apart the engine assumed before (B12): the target, a neighbour,
one 2 hexes away. Each ring is filled starting behind the target (away from the champion), going round.

`opponents[0]` stays the target: the dummies are placed, and kept, in that order (nearest the target first).
"""

DIRECTIONS = ((1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1))
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

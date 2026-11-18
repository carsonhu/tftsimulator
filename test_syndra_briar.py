"""Syndra and Briar (champions/Syndra.md, Briar.md): numbers from build rls-19.1.0.5973071 (multi-phase chronos placed
by phase); the spells from GA_Syndra19_Spell, GA_Briar19_Spell and their effects (client assets)."""
import pytest

from buildstore import load_build
from layout import Layout
from set19champs import Briar, Syndra
from simulator import Simulator
from test_timing import dummy
from timing import TPS

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'


def fight(cls, targets=3, seconds=8, ad=None):
    c = cls(1, build=load_build(V))
    lay = Layout(targets)
    ds = [dummy() for _ in range(lay.count)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    casts = []
    orig = c._cast

    def cast(o, i, t):
        casts.append(c.tick)
        orig(o, i, t)
    c._cast = cast
    mana = []
    orig_add = c.addMana

    def add(amount, time=None):
        before = c.curMana
        orig_add(amount, time)
        if c.curMana > before:
            mana.append(c.tick)
    c.addMana = add
    Simulator().simulate([], [], c, ds, seconds, layout=lay)
    rows = [(round(t * TPS), round(v[0], 4), v[1]) for t, v, *_ in c.dmgVector]
    return c, casts, rows, mana


def test_syndra_cast_timeline():
    # CD_Syndra19_CastAnim by phase: Volleyball spawn 1.3085 s (40 ticks), Unlock 1.99 s (60: mana lock 60, cast lock
    # 61). The ball flies 4 hexes at 2400 (11 ticks): 300 x AP on the target; the bounce to the dummy behind it, 1 hex
    # at 2000 (4 ticks): 110 x AP
    c, casts, rows, mana = fight(Syndra)
    assert round(c.timing.mana_lock * TPS) == 60 and round(c.timing.cast_lock * TPS) == 61
    cast = casts[0]
    magic = [(t - cast, d) for t, d, typ in rows if typ == 'magical']
    assert magic == [(51, 300), (55, 110)]


def test_syndra_bounces_in_place_alone():
    # nobody behind the target: CD_Syndra19_BounceInPlace, the chrono's 0.4999 s (G21) -> 15 ticks, on the target
    c, casts, rows, mana = fight(Syndra, targets=1)
    magic = [(t - casts[0], d) for t, d, typ in rows if typ == 'magical']
    assert magic == [(51, 300), (66, 110)]


def test_syndra_bounce_goes_behind():
    # the cone points away from Syndra: of the target's neighbours, the one straight behind it
    c, casts, rows, mana = fight(Syndra, targets=7, seconds=1)
    target = c.opponents[0]
    other = c.bounce_target(target)
    assert other.hex == (target.hex[0] + 1, target.hex[1])


def test_briar_cast_timeline_and_frenzy():
    # 10 mana per hit: hits 10, 47, 85 -> cast at 86. Windup Kick 0.191 s (6), the Short dash (the snack target 2
    # hexes away): Boom +10 (+200% AS), Land +16 (100 x AD on the 3 targets), Unlock +24 -> cast lock 31. Then 3
    # slashes of 100 x AD; the AS buff ends at the 3rd and the mana lock the tick after
    c, casts, rows, mana = fight(Briar)
    cast = casts[0]
    assert casts[0] == 86 and round(c.timing.cast_lock * TPS) == 31
    land = [t for t, d, typ in rows if t == cast + 6 + 16]
    assert len(land) == 3
    slashes = [t for t, d, typ in rows if t > cast + 22 and d == 100]
    assert len(slashes) == 3
    assert not [t for t in mana if cast <= t <= slashes[-1]]  # mana locked until the tick after the 3rd slash
    assert c.aspd.stat == pytest.approx(0.8)  # the buff is gone


def test_briar_aoe_reads_the_targets():
    for targets in (1, 3, 5):
        c, casts, rows, mana = fight(Briar, targets=targets, seconds=4)
        assert len([t for t, d, typ in rows if t == casts[0] + 22]) == targets

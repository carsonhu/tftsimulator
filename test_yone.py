"""Yone (champions/Yone.md): numbers from build rls-19.1.0.5986094; the cast against the owner's 60 fps VOD6
(18-40-41-766, round 2-1: Yone 1 star in AP form)."""
import pytest

import set19buffs
from buildstore import load_build
from set19champs import Yone
from simulator import Simulator
from test_timing import dummy
from test_viego import LaunchCounter

V = 'rls-19.1.0.5986094.Set19.Shipping.pbe'
BIAS = 1 << set19buffs.Heartsteel.BIAS


def fight(ap=0.0, buffs=(), resist=50, seconds=8):
    y = Yone(1, build=load_build(V))
    if ap:
        y.ap.modify('+', ap)
    casts, perform = [], y.performAbility

    def logged(o, i, t):
        casts.append(y.tick)
        perform(o, i, t)
    y.performAbility = logged
    counter = LaunchCounter()
    ds = [dummy() for _ in range(3)]
    for d in ds:
        d.armor.base = d.mr.base = resist
    Simulator().simulate([counter], list(buffs), y, ds, seconds)
    cast = casts[0]
    return y, cast, counter, [(round(t * 30) - cast, round(d[0], 4), d[1]) for t, d, *_ in y.dmgVector
                              if round(t * 30) >= cast]


def test_build_numbers():
    y = Yone(1, build=load_build(V))
    assert (y.fullMana.stat, y.aspd.stat, y.attack_range, y.hp.stat, y.armor.stat) == (50, 0.85, 1, 1150, 70)
    # CD_Yone19_CastAnim (non-Alt, E3): 'StartStrikes' 0.4992 s; _Part2: 'DealDamage' 0.3453, 'Unlock' 0.6589
    assert (y.start_strikes, y.deal, y.unlock) == (0.4992, 0.3453, 0.6589)
    assert not y.ap_form() and y.strikes() == (10, 10)


def test_ad_cast():
    y, cast, counter, rows = fight()
    spell = [r for r in rows if r[0] <= 48]
    strikes = [d for t, d, _ in spell[:-1]]
    assert len(strikes) == 10 and all(d == pytest.approx(35 / 1.5, abs=1e-3) for d in strikes)  # 35 x AD against 50 armor
    assert spell[-1][0] == 48 and spell[-1][1] == pytest.approx(175 / 1.5, abs=1e-3) and spell[-1][2] == 'physical'
    # one simulated launch per 3 strikes
    assert len([t for t in counter.launches if cast < t < cast + 48]) == 3
    # the slash interval at 0.8925 AS: 0.085 / (1 + (1.05 - 1) x 0.5); the cast ends after the slash's 'Unlock'
    end = round((0.4992 + 9 * 0.085 / 1.025 + 0.6589) * 30 + 0.4999)
    assert round(y.timing.mana_lock * 30) == end and round(y.timing.cast_lock * 30) == end + 1


def test_ap_form_and_bias():
    y, _, _, rows = fight(ap=0.3)
    assert y.ap_form()
    assert {kind for _, _, kind in rows} == {'magical'}  # strikes, slash and attacks
    assert rows[0][1] == pytest.approx(35 * 1.3 / 1.5, abs=1e-3)
    # the Heartsteel Bias: 12 strikes in the same time, 25% armor ignored
    y, _, _, rows = fight(buffs=[set19buffs.Heartsteel(3, BIAS)])
    assert y.strikes() == (12, 10)
    strikes = [d for t, d, _ in rows if t < 45]
    assert len(strikes) == 12 and strikes[0] == pytest.approx(35 / (1 + 50 * 0.75 / 100), abs=1e-3)

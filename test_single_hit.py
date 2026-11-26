"""The Hit table (single_hit.py, sim_entry.run_hits; owner, 2026-11-19): one attack or one cast at fixed stats."""
import math

import pytest

import set19champs
import set19items
import sim_entry
import single_hit

ENEMY = {"hp": 1800, "armor": 100, "mr": 100}


def cfg(champ, **kw):
    return dict({"champ": champ, "level": 1, "items": ["NoItem"] * 3, "buffs": [], "enemy": ENEMY}, **kw)


def hit(champ, item="NoItem", mode="cast", seconds=0.0, **kw):
    c = cfg(champ, **kw)
    return single_hit.damage(sim_entry._build_champion(c), sim_entry._build_enemy(c), getattr(set19items, item)(),
                             False, mode, sim_entry._layout(c), seconds)


def rows(champ, **kw):
    return {r["cls"]: r for r in sim_entry.run_hits(cfg(champ, **kw))["rows"]}


def test_every_champion_hits_with_every_listed_item():
    for name in set19champs.champ_list:
        c = cfg(name)
        champ = sim_entry._build_champion(c)
        items = sim_entry._hit_items(single_hit.item_lists(champ))
        for mode in single_hit.modes(champ):
            for cls in ["NoItem"] + [classes[0] for _, classes in items]:
                d = hit(name, cls, mode, 15)
                assert math.isfinite(d) and d > 0, (name, mode, cls)


def test_viego_per_sword_by_hand():
    # one sword: DamagePerSwordAD 26 (build 6037882; 28 before) x AD 1 + DamagePerSwordAP 3 x AP 1 = 29 physical,
    # 100 armor halves it
    assert hit("Viego") == pytest.approx(14.5)
    assert sim_entry.run_hits(cfg("Viego", hitMode="cast"))["per"] == "sword"


def test_the_tables_assumptions():
    r = rows("Ahri", hitSeconds=15)
    # Archangel's: 30% AP + 20 AP per 5 s: 3 stacks at 15 s
    assert r["ArchangelsStaff"]["ratio"] == pytest.approx(1.9, abs=0.01)
    assert rows("Ahri", hitSeconds=0)["ArchangelsStaff"]["ratio"] == pytest.approx(1.3, abs=0.01)
    # Void Staff: 35% AP, and the dummies' MR already shredded 30%: 1.35 x 200 / 170
    assert r["VoidStaff"]["ratio"] == pytest.approx(1.35 * 200 / 170, abs=0.01)
    # Striker's Flail: 10% amp + 4 stacks x 5% (her spell can't crit)
    assert r["StrikersFlail"]["ratio"] == pytest.approx(1.3, abs=0.01)
    # Spear of Shojin and Blue Buff share a row
    assert r["SpearOfShojin"]["icons"] == ["SpearOfShojin", "BlueBuff"]
    # Last Whisper on an attack: 15% AD, 20% crit (x0.4 more each) and the dummies' armor already sundered 30%
    a = rows("Jinx", hitMode="attack")
    assert a["LastWhisper"]["ratio"] == pytest.approx(1.15 * (1 + 0.45 * 0.4) / 1.1 * 200 / 170, abs=0.01)


def test_modes_and_lists():
    out = sim_entry.run_hits(cfg("Ahri"))
    assert (out["modes"], out["ap"]) == (["cast"], True)
    assert sim_entry.run_hits(cfg("Kaisa"))["modes"] == ["attack"]  # her spell is attack speed only
    # an Attack Caster attacks too (owner), opening on the cast
    out = sim_entry.run_hits(cfg("Ezreal"))
    assert (out["modes"], out["mode"]) == (["attack", "cast"], "cast")
    assert sim_entry.run_hits(cfg("Katarina"))["modes"] == ["cast"]  # a Magic Fighter casts only (owner)
    assert sim_entry.run_hits(cfg("Kayle"))["modes"] == ["attack", "cast"]  # a Magic Marksman attacks
    assert sim_entry.run_hits(cfg("Jinx"))["modes"] == ["attack", "cast"]
    out = sim_entry.run_hits(cfg("Jinx"))
    assert (out["mode"], out["ap"], out["seconds"]) == ("attack", False, None)
    assert "KrakensFury" not in rows("Jinx")
    # Yone is truly hybrid (owner): every item of both lists once, and the Archangel's slider
    out = sim_entry.run_hits(cfg("Yone"))
    classes = [r["cls"] for r in out["rows"]]
    assert out["ap"] and len(classes) == len(set(classes))
    assert {"Deathblade", "SteraksGage", "ArchangelsStaff", "RabadonsDeathcap", "VoidStaff"} <= set(classes)


def test_units_and_empowered_attacks():
    # Briar per slash, without the dash; Ashe's cast is her 6 flurries
    briar = sim_entry._build_champion(cfg("Briar"))
    slash = briar.row("DamageFrenzyAD") * 1.0 / 2  # AD 1, 100 armor
    assert hit("Briar") == pytest.approx(slash)
    assert hit("Ashe") > 6 * hit("Ashe", mode="attack")
    # Jinx per rocket: DamagePerMissileAD x AD + DamagePerMissileAP x AP, halved by armor
    jinx = sim_entry._build_champion(cfg("Jinx"))
    assert hit("Jinx") == pytest.approx(jinx.missile_damage(1, 1.0, 1.0) / 2)
    # Gnar: a plain attack, and his rock as its own tab (owner): ADDamage x AD, physical, halved by armor
    gnar = sim_entry._build_champion(cfg("Gnar"))
    assert sim_entry.run_hits(cfg("Gnar"))["modes"] == ["attack", "rock"]
    assert hit("Gnar", mode="attack") == pytest.approx(gnar.atk.stat * (1 + 0.25 * 0.4) / 2)  # 25% crit averaged
    assert hit("Gnar", mode="rock") == pytest.approx(gnar.rock_damage(1, 1.0, 1.0) / 2)


def test_radiants():
    # owner, 2026-11-19: each item's Radiant instead; Shojin's and Blue Buff's Radiants differ, so their row splits
    r = rows("Ahri", hitRadiant=True)
    assert "ArchangelsStaffRadiant" in r and "ArchangelsStaff" not in r
    assert r["SpearOfShojinRadiant"]["icons"] == ["SpearOfShojinRadiant"]
    assert r["BlueBuffRadiant"]["damage"] > r["SpearOfShojinRadiant"]["damage"]
    assert r["ArchangelsStaffRadiant"]["damage"] > rows("Ahri")["ArchangelsStaff"]["damage"]


def test_archangels_defaults_to_10_seconds():
    # owner, 2026-11-19: 10 s, 2 stacks: 30% AP + 40 AP
    out = sim_entry.run_hits(cfg("Ahri"))
    assert out["seconds"] == 10
    assert {r["cls"]: r for r in out["rows"]}["ArchangelsStaff"]["ratio"] == pytest.approx(1.7, abs=0.01)


def test_the_math_multiplies_to_the_damage():
    # owner, 2026-11-20: the panel beside the table explains a hit as before amp x amp x crit x resists, each measured
    # on the hit itself, so the chain gives the table's number for every champion, hit and item
    for name in set19champs.champ_list:
        for mode in single_hit.modes(sim_entry._build_champion(cfg(name))):
            for r in sim_entry.run_hits(cfg(name, hitMode=mode))["rows"]:
                m = r["math"]
                assert m["raw"] * m["amp"] * m["crit"] * m["resist"] == pytest.approx(r["damage"], rel=2e-3, abs=0.1), \
                    (name, mode, r["cls"])
    # Void Staff's shred shows in the resist the hit met
    r = rows("Ahri")
    assert (r["NoItem"]["math"]["resists"], r["VoidStaff"]["math"]["resists"]) == ({"mr": 100.0}, {"mr": 70.0})

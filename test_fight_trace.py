"""The fight viewer's recorder (fight_trace.py, sim_entry.run_trace): it records a fight without changing it."""
import pytest

import set19champs
import set19items
import sim_core
import sim_entry
from fight_trace import Tracer


def _cfg(champ, **kw):
    cfg = {"champ": champ, "level": 1, "slice": "Craftable", "items": ["NoItem"] * 3, "buffs": [],
           "layout": {"targets": 3}}
    cfg.update(kw)
    return cfg


@pytest.mark.parametrize("champ", set19champs.champ_list)
def test_recording_changes_nothing_and_misses_nothing(champ):
    # the same fight with and without the recorder: identical results; the recorded hits are exactly the fight's
    cfg = _cfg(champ, buffs=[["Trickshot", 2, 0]])
    c = sim_entry._build_champion(cfg)
    enemy = sim_entry._build_enemy(cfg)
    extra = set19items.NoItem()
    _, plain = sim_core.run_one(c, enemy, extra, False, 30, layout=sim_entry._layout(cfg))
    holder = {}

    def attach(champ_, dummies):
        champ_.tracer = holder["t"] = Tracer(champ_, dummies)

    _, traced = sim_core.run_one(c, enemy, extra, False, 30, layout=sim_entry._layout(cfg), setup=attach)
    assert traced == plain
    tr = holder["t"]
    assert len(tr.damage_events) == len(plain)
    assert sum(d["v"] for d in tr.damage_events) == pytest.approx(sum(r[1][0] for r in plain), abs=0.01 * len(plain))
    for p in tr.projectiles:
        assert p["t1"] >= p["t0"] and p["from"] is not None and p["to"] is not None


def test_run_trace_is_the_rows_fight():
    # the viewer's fight for a row has the row's damage: Draven with Guinsoo's Rageblade, 30 s
    cfg = _cfg("Draven")
    rows = sim_entry.run_slice(dict(cfg, t=30))
    row = next(r for r in rows["rows"] if r["extraCls"] == "GuinsoosRageblade")
    trace = sim_entry.run_trace(dict(cfg, row=row["idx"], seconds=30))
    assert trace["extra"] == row["extra"]
    total = rows["timelines"][str(row["idx"])]["cum"][-1]
    assert sum(d["v"] for d in trace["damage"]) == pytest.approx(total, rel=1e-3)
    assert trace["ticks"] == 900 and trace["snapshots"][0][0] == 0
    assert {"ad", "as", "mana", "mods", "d1"} <= set(trace["snapshots"][0][1])
    # the champion's attacks and its spell's projectiles (Draven's record) are drawn
    assert {"attack", "record"} <= {p["name"] for p in trace["projectiles"]}


def test_damage_is_labelled_by_its_source():
    trace = sim_entry.run_trace(_cfg("Ziggs", items=["NoItem"] * 3))
    kinds = {(d["kind"], d["by"]) for d in trace["damage"]}
    # his attack, the passive riding on it, and the bomb
    assert ("attack", None) in kinds and ("spell", "passive") in kinds and ("spell", "land") in kinds


def test_catalog_offers_fight_lengths():
    assert sim_entry.get_catalog()["defaults"]["traceSeconds"] == list(sim_entry.TRACE_SECONDS)
    trace = sim_entry.run_trace(_cfg("Neeko", seconds=60))
    assert trace["ticks"] == 1800


def test_idle_heartsteel_is_off_the_viewer_card():
    # owner, 2026-11-19: Heartsteel in Team Traits with no member ticked does nothing, so the card doesn't name it;
    # on a member it always counts (the unit fields itself)
    import sim_entry
    cfg = {"champ": "Gnar", "level": 1, "items": ["Deathblade", "NoItem", "NoItem"], "buffs": [["Heartsteel", 1, 0]],
           "team": ["Heartsteel"], "slice": "Craftable", "enemy": {"hp": 1800, "armor": 100, "mr": 100}, "row": 0}
    assert "Heartsteel" not in sim_entry.run_trace(cfg)["items"]
    cfg["buffs"] = [["Heartsteel", 1, 1]]  # Kayn ticked
    assert "Heartsteel" in sim_entry.run_trace(cfg)["items"]
    cfg.update(champ="Ezreal", buffs=[["Heartsteel", 3, 0]], team=[])
    assert "Heartsteel" in sim_entry.run_trace(cfg)["items"]

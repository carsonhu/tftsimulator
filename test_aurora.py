"""Aurora (champions/Aurora.md): GA_Aurora19_Spell (D1) on build rls-19.1.0.6011486, checked against the owner's 60 fps
VOD8 (13-2-9-650: Aurora 1 star, no items, at 5-6 with Heartsteel (3) and Aphelios fielded: AS 0.75 x 1.06)."""
import set19buffs
from buildstore import load_build
from layout import Layout
from set19champs import Aurora
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.6011486.Set19.Shipping.pbe'
APHELIOS = 1 << 2  # Heartsteel's 'Fielded' box for Aphelios (traits/heartsteel.py MEMBERS)


class LoggedAurora(Aurora):
    def __init__(self, level=1):
        super().__init__(level, build=load_build(V))
        self.casts, self.launch_log, self.blasts = [], [], []

    def performAbility(self, opponents, items, time):
        self.casts.append(self.tick)
        super().performAbility(opponents, items, time)

    def onLaunch(self, opponents, items):
        super().onLaunch(opponents, items)
        self.launch_log.append(self.tick)

    def blast_targets(self, target):
        marks = super().blast_targets(target)
        self.blasts.append(marks)
        return marks


def fight(a, buffs=(), seconds=16, targets=2):
    lay = Layout(targets)
    ds = [dummy() for _ in range(lay.count)]
    for d in ds:
        d.armor.base = d.mr.base = 0
    Simulator().simulate([], list(buffs), a, ds, seconds, layout=lay)
    rows = {}
    for t, d, *_ in a.dmgVector:
        rows.setdefault(round(t * 30), []).append(round(d[0], 4))
    return ds, rows


def test_build_numbers():
    a = LoggedAurora(1)
    assert (a.curMana, a.fullMana.stat, a.aspd.stat, a.attack_range, a.atk.stat, a.hp.stat) == (0, 60, 0.75, 4, 35, 850)
    # 'Unlock' 2.0323 s -> the mana lock on tick 61, the cast lock one tick later
    assert round(a.timing.mana_lock * 30) == 61 and round(a.timing.cast_lock * 30) == 62
    assert round(a.timing.launch, 4) == 0.3348


def test_vod8_5_6_panel():
    # VOD8 5-6 planning panel (30:46): 850 / 850, 0 / 60, AD 35, AP 0%, AS 0.79 (0.75 x 1.06: Aphelios' Heartsteel
    # bonus; float32 0.79499996 shows 0.79)
    a = LoggedAurora(1)
    fight(a, [set19buffs.Heartsteel(3, APHELIOS)], seconds=0.1)
    assert round(a.aspd.stat, 3) == 0.795 and round(a.ap.stat, 3) == 1.0


def test_vod8_5_6_casts():
    # VOD8 5-6 (combat start f112267, the timer's flip to 30): her attacks' mana (+7) shows 11, 48, 86 ticks in, then
    # 37-38 ticks apart (one 44.5-tick gap: a target change); the 7th fills the bar (58 + 7) and the cast follows;
    # the banked 5 shows 62.5 ticks after the filling attack (f112754 -> f112879; engine: unlocked 62 after), the next
    # attack 74.5 ticks after it (f112903; engine 73, T10's +1 on a fresh attack); 2nd cast: fill f113280, next attack
    # f113427 = 73.5 ticks
    a = LoggedAurora(1)
    fight(a, [set19buffs.Heartsteel(3, APHELIOS)])
    assert a.launch_log[:3] == [10, 48, 85]
    assert [b - x for x, b in zip(a.launch_log[:6], a.launch_log[1:7])] == [38, 37, 38, 38, 38, 37]
    fill = a.launch_log[6]
    assert a.casts[0] == fill + 1
    assert a.mana_locked_until - fill == 62
    assert [t for t in a.launch_log if t > a.casts[0]][0] - fill == 73


def test_blast_lands_at_damage():
    # 'Damage' 1.0738 s -> 33 ticks after the cast; VOD8 5-6: her omnivamp heal (+94, +63 HP) shows at f112823 and
    # f113347, 68 frames after the filling attacks (the cast one tick after: 2 + 66 frames)
    a = LoggedAurora(1)
    _, rows = fight(a, [set19buffs.Heartsteel(3, APHELIOS)], seconds=10)
    assert rows[a.casts[0] + 33] == [300.0, 300.0]


def test_one_target_takes_the_primary_twice():
    # one enemy in the line: HighestHP falls back to PrimaryTarget (ComputeTargetsInLineAndUpdate 0x5ce-0x5f9)
    a = LoggedAurora(1)
    _, rows = fight(a, seconds=10, targets=1)
    assert rows[a.casts[0] + 33] == [300.0, 300.0]


def test_two_highest_health_take_the_primary():
    # 4 targets, all in the line: her attacks have hit the target, so the 2 others with the most Health take
    # PrimaryDamageAP x AP and the target and the last take AOEDamageAP x AP; at the next cast the one that took only
    # the AOE leads (90 lost), then a first-cast primary (300), the target last (its attacks and the AOE)
    a = LoggedAurora(1)
    ds, rows = fight(a, seconds=20, targets=4)
    assert sorted(rows[a.casts[0] + 33]) == [90.0, 90.0, 300.0, 300.0]
    (p1, s1, rest1), (p2, s2, rest2) = a.blasts[:2]
    assert ds[0] not in (p1, s1) and ds[0] in rest1
    aoe_only = next(d for d in rest1 if d is not ds[0])
    assert p2 is aoe_only and s2 in (p1, s1) and ds[0] in rest2


def test_line_holds_every_page_target():
    # LineWidth 440: the target and its 6 neighbours stand within 186 units of a line along a hex axis
    for n in range(1, 8):
        a = LoggedAurora(2)
        _, rows = fight(a, seconds=10, targets=n)
        assert len(rows[a.casts[0] + 33]) == max(n, 2)

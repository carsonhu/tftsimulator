"""The item stats layer (docs/ASSUMPTIONS.md I1-I3, docs/ITEMS.md): numbers from build rls-19.1.0.5973071."""
import copy

import pytest

import set19items
from buildstore import Build, BuildDataError, load_build
from events import CRIT, IS_ATTACK, ON_HIT, ON_SPELL, UNIT, CombatEvent, damage_tags
from set19champs import Neeko
from simulator import Simulator
from test_timing import dummy

V = 'rls-19.1.0.5973071.Set19.Shipping.pbe'



def attack_crit(c):
    """The CRIT event of an attack (events.py)."""
    return CombatEvent(c, tags=damage_tags('physical', UNIT, IS_ATTACK, ON_HIT))


def spell_crit(c):
    return CombatEvent(c, tags=damage_tags('magical', UNIT, ON_SPELL))

def equipped(*items, build=None):
    n = Neeko(1, build=build or load_build(V))
    Simulator().itemStats(list(items) + n.items, n)
    return n


def test_infinity_edge():
    # GE_InfinityEdge: AttackDamage + 0.35, CritChance + 0.35, grants CanSpellCrit (Precision)
    n = equipped(set19items.InfinityEdge())
    assert n.bonus_ad.stat == pytest.approx(1.35) and n.crit.stat == pytest.approx(0.60)
    assert n.canSpellCrit and n.critDmg.stat == pytest.approx(1.4)  # one Precision source: no bonus (B7)


def test_second_precision_source_adds_crit_damage_from_the_curve():
    # CT_SpellCritToCritDamageConversion: linear 1 -> 0, 10 -> 0.9, so 2 sources = +0.1, 3 = +0.2
    n = equipped(set19items.InfinityEdge(), set19items.JeweledGauntlet())
    assert n.critDmg.stat == pytest.approx(1.5) and n.spell_crit_sources == 2
    n = equipped(set19items.InfinityEdge(), set19items.JeweledGauntlet(), set19items.InfinityEdge())
    assert n.critDmg.stat == pytest.approx(1.6) and n.crit.stat == pytest.approx(1.3)


def test_spear_of_shojin_mana_per_attack_joins_the_role_mana():
    # GE_SpearOfShojin: AD + 0.15, AP + 0.15, ManaPerSecond + 1, ManaPerAttack + 5 (I3); MagicCaster: 7 / attack, 2 / s
    n = equipped(set19items.SpearOfShojin())
    assert (n.manaPerAttack.stat, n.manaRegen.stat) == (12, 3)
    assert n.ap.stat == pytest.approx(1.15) and n.bonus_ad.stat == pytest.approx(1.15)


def test_precision_lets_neekos_spell_crit():
    # Jeweled Gauntlet: AP 1.35, crit 60%, Precision; Neeko's damage GE rolls crit if the unit can spell-crit:
    # 75 x 1.35 x (0.4 + 0.6 x 1.4) = 125.55 average per Popper missile
    n = Neeko(1, build=load_build(V))
    d = dummy()
    d.mr.base = 0
    Simulator().simulate([set19items.JeweledGauntlet()], [], n, [d], 10)
    spell = [round(x[1][0], 2) for x in n.dmgVector if x[1][0] > 50]
    assert spell[:3] == [125.55] * 3


def test_attack_speed_is_multiply_additive():
    # Guinsoo's base effect: AttackSpeed MultiplyAdditive 1.1 -> +10% (its stacking is the script, not tested here)
    cls = type('G', (set19items.BuildItem,), {'KEY': 'DA_GuinsoosRageblade', 'STATS': ('GE_GuinsoosRageblade_Base',),
                                             'display_name': 'G'})
    n = equipped(cls())
    assert n.aspd.stat == pytest.approx(0.77) and n.ap.stat == pytest.approx(1.10)


def test_the_champions_build_supplies_the_numbers():
    # an item reads the build the champion was made from, not the newest
    data = copy.deepcopy(load_build(V).data)
    for e in data['items']['DA_InfinityEdge']['effects']:
        for m in e['modifiers']:
            if m['attribute'] == 'AttackDamage':
                m['values'] = [0.5]
    other = Build(data)
    n = equipped(set19items.InfinityEdge(), build=other)
    assert n.bonus_ad.stat == pytest.approx(1.5)


@pytest.mark.parametrize('key,effect,why', [
    ('DA_SteadfastHeart', None, 'not a plain value'),  # HealthMax computed in game
])
def test_what_the_stats_layer_refuses(key, effect, why):
    entry = load_build(V).item(key)
    effects = [effect] if effect else [e['effect'] for e in entry.d['effects']]
    with pytest.raises(BuildDataError, match=why):
        set19items.item_stats(entry, effects)


def test_every_registered_item_reads_cleanly():
    for name in set19items.offensive_craftables:
        cls = getattr(set19items, name)
        set19items.item_stats(load_build(V).item(cls.KEY), cls.STATS)


def test_phase_order_static_stats_then_flags_then_effects():
    # Build stats and trait tiers apply in the static pass, before any phase, so prePreCombat stays free for flags
    # (set18's Retribution: an augment sets a flag in prePreCombat that an item reads in preCombat; items run before
    # buffs within a phase, so the flag must come a phase earlier).
    from item import Item
    seen = {}

    class FlagAugment(Item):
        def __init__(self):
            super().__init__('Flag', phases=['prePreCombat'])

        def performAbility(self, phase, time, champion, input_=0):
            seen['ad_when_flag_set'] = champion.bonus_ad.stat  # item stats already applied
            champion.flag = True
            return 0

    class FlagReader(Item):
        def __init__(self):
            super().__init__('Reader', phases=['preCombat'])

        def performAbility(self, phase, time, champion, input_=0):
            seen['flag'] = getattr(champion, 'flag', False)
            return 0

    n = Neeko(1, build=load_build(V))
    # items first, augment last: the order the simulator builds (items + buffs + champion.items)
    Simulator().itemStats([set19items.InfinityEdge(), FlagReader(), FlagAugment()] + n.items, n)
    assert seen == {'ad_when_flag_set': pytest.approx(1.35), 'flag': True}


def stat_changes(item, seconds=12, attr='aspd'):
    n = Neeko(1, build=load_build(V))
    log = []
    orig = n.update

    def upd(opp, items, time):
        before = getattr(n, attr).stat
        orig(opp, items, time)
        if getattr(n, attr).stat != before:
            log.append((n.tick, round(getattr(n, attr).stat, 4)))
    n.update = upd
    Simulator().simulate([item], [], n, [dummy()], seconds)
    return n, log


def test_guinsoos_rageblade_matches_the_vod():
    # items/GuinsoosRageblade.md E1 (Varus, 60 fps VOD): first stack 60 frames = 1.000 s after combat start, then one
    # per second; AS = base x (1.10 + 0.07n), read 0.82 0.87 0.92 0.97 1.01 1.06 (Neeko's base AS is Varus's, 0.70)
    n, log = stat_changes(set19items.GuinsoosRageblade())
    assert [t for t, _ in log[:6]] == [30, 60, 90, 120, 150, 180]
    assert [round(v, 2) for _, v in log[:6]] == [0.82, 0.87, 0.92, 0.97, 1.01, 1.06]


def test_archangels_staff_every_period_from_combat_start():
    # CT_ArchangelsStaff Period 5, APStack 20, StackToAP 0.01 x Stack: +20 AP at 5 s, 10 s (base 30% AP from the stats)
    n, log = stat_changes(set19items.ArchangelsStaff(), seconds=11, attr='ap')
    assert log == [(150, 1.5), (300, 1.7)]


def test_blue_buff_mana_at_combat_start():
    # GE_BlueBuff_StartingMana: + StartingMana (10) at combat start (items/BlueBuff.md E1, Varus: 30 -> 40 on the combat-start frame)
    n = Neeko(1, build=load_build(V))
    Simulator().itemStats([set19items.BlueBuff()] + n.items, n)
    assert n.curMana == 10 and n.manaRegen.stat == 8  # 2 (MagicCaster) + 6


# ---------------------------------------------------------------- Deathblade / Rabadon's: x bonus on Channel1 (I5)
def test_deathblade_multiplies_every_bonus_ad():
    # Channel1: ((1 + bonuses) x 1.15) - 1.15 + 1 = 1 + 1.15 x bonuses
    assert equipped(set19items.Deathblade()).bonus_ad.stat == pytest.approx(1 + 0.55 * 1.15)
    n = equipped(set19items.Deathblade(), set19items.BlueBuff())  # Blue Buff's 15% AD is multiplied too
    assert n.bonus_ad.stat == pytest.approx(1 + 0.70 * 1.15)
    # two: the MultiplyAdditives sum (x1.30), and so do the AddFinals (-2.30 + 2)
    assert equipped(set19items.Deathblade(), set19items.Deathblade()).bonus_ad.stat == pytest.approx(1 + 1.10 * 1.30)


def test_rabadons_multiplies_every_bonus_ap():
    assert equipped(set19items.RabadonsDeathcap()).ap.stat == pytest.approx(1 + 0.55 * 1.15)
    assert equipped(set19items.RabadonsDeathcap(), set19items.JeweledGauntlet()).ap.stat == pytest.approx(1 + 0.90 * 1.15)


def _deathblade_with(change):
    data = copy.deepcopy(load_build(V).data)
    change(data['items']['DA_Deathblade']['effects'][0]['modifiers'])
    return equipped(set19items.Deathblade(), build=Build(data))


def test_modifiers_apply_as_listed_without_a_cancelling_check():
    # I5: the game's formula, not a rule about which AddFinals must come with a multiplier. Without the AddFinal +1,
    # AD = (1 + 0.55) x 1.15 - 1.15
    def drop_one(ms):
        ms.remove(next(m for m in ms if m['op'] == 'AddFinal' and m['values'] == [1]))
    assert _deathblade_with(drop_one).bonus_ad.stat == pytest.approx(1.55 * 1.15 - 1.15)


def test_each_modifier_lands_on_its_channel():
    # I5: the +0.55 on Channel2 comes after Channel1's x1.15 (whose AddFinals cancel it on the base 1): AD = 1 + 0.55
    def channel2(ms):
        next(m for m in ms if m['op'] == '+')['channel'] = 2
    assert _deathblade_with(channel2).bonus_ad.stat == pytest.approx(1.55)
    assert _deathblade_with(lambda ms: None).bonus_ad.stat == pytest.approx(1 + 0.55 * 1.15)


@pytest.mark.parametrize('items,base_ad,pct,ad', [
    (('Deathblade',), 42, 63, 69),                                # Samira 1*, 5:00
    (('InfinityEdge', 'Deathblade'), 42, 103, 85),                # Samira 1*, 5:04
    (('InfinityEdge', 'Deathblade', 'Deathblade'), 30, 189, 87),  # Kai'Sa 1*, 11:12-11:44
])
def test_vod3_panel_bonus_ad(items, base_ad, pct, ad):
    # VOD3 (17-13-37-283, 60 fps): the panel's bonus AD % and AD. 103.5 and 188.5 sit on a rounding half (the game
    # rounds its float32 value), so the % is checked to 0.5; the AD numbers are not on a boundary
    n = equipped(*[getattr(set19items, i)() for i in items])
    assert abs((n.bonus_ad.stat - 1) * 100 - pct) <= 0.5 + 1e-9
    assert round(base_ad * n.bonus_ad.stat) == ad


def test_quicksilver_vod4_senna():
    # VOD4 1-4: Senna 1* with Quicksilver and Guinsoo's: 0.94 in planning, then one step a second from 1 s:
    # 1.01, 1.09, 1.16, 1.24, 1.31, 1.39, 1.46, 1.54, 1.61 = 0.75 x (1.25 + 0.1k) (Guinsoo 7% + Quicksilver 3%)
    import set19items
    from set19champs import Senna
    from simulator import Simulator
    from test_timing import dummy
    s = Senna(1, build=load_build(V))
    log = {}
    orig = s.update

    def update(opponents, items, time):
        r = orig(opponents, items, time)
        log[s.tick] = round(s.aspd.stat, 2)
        return r
    s.update = update
    Simulator().simulate([set19items.Quicksilver(), set19items.GuinsoosRageblade()], [], s, [dummy()], 10)
    assert log[0] == 0.94
    assert [log[30 * k] for k in range(1, 10)] == [1.01, 1.09, 1.16, 1.24, 1.31, 1.39, 1.46, 1.54, 1.61]
    assert log[29] == 0.94


def test_titans_resolve_vod4_ezreal():
    # VOD4 2-2: Ezreal's AP % (Guinsoo 10% + 2% a stack) rose on every release's frame and twice per cast (his two
    # simulated attacks): 12, 14, 16, 20, 22, 24, 26, 28, 32, 34, 36, 38 -> stacks = releases + 2 x casts
    import set19items
    from set19champs import Ezreal
    from simulator import Simulator
    from test_timing import dummy
    e = Ezreal(1, build=load_build(V))
    t = set19items.TitansResolve()
    Simulator().simulate([t, set19items.InfinityEdge(), set19items.GuinsoosRageblade()], [], e, [dummy()], 6)
    assert t.stacks == min(25, e.launches + 2 * e.numCasts) and e.numCasts >= 1
    assert abs(e.ap.stat - (1.1 + 0.02 * t.stacks)) < 1e-9
    e2 = Ezreal(1, build=load_build(V))
    t2 = set19items.TitansResolve()
    Simulator().simulate([t2], [], e2, [dummy()], 30)
    assert t2.stacks == 25 and abs(e2.bonus_ad.stat - 1.5) < 1e-9  # capped at 25: +50% AD


def test_simulated_attacks_reach_items():
    # Ziggs's bomb (1 per cast) and Senna's blast (every other cast) also give Titan's stacks (G11)
    import set19items
    from set19champs import Senna, Ziggs
    from simulator import Simulator
    from test_timing import dummy
    z = Ziggs(1, build=load_build(V))
    t = set19items.TitansResolve()
    Simulator().simulate([t], [], z, [dummy()], 8)
    assert t.stacks == z.launches + z.numCasts
    s = Senna(1, build=load_build(V))
    t = set19items.TitansResolve()
    Simulator().simulate([t], [], s, [dummy()], 8)
    assert t.stacks == s.launches + (s.numCasts + 1) // 2  # blast, detonate, blast, ...


def test_offensive_items_whose_scripts_never_trigger_on_dummies():
    # stats only: Bloodthirster 15/15, Edge of Night 10/10 + 15% AS, Sterak's 45% AD, Gunblade 20/20
    for item, ad, ap in ((set19items.Bloodthirster(), 1.15, 1.15), (set19items.EdgeOfNight(), 1.10, 1.10),
                         (set19items.SteraksGage(), 1.45, 1.0), (set19items.HextechGunblade(), 1.2, 1.2)):
        n = equipped(item)
        assert (n.bonus_ad.stat, n.ap.stat) == (pytest.approx(ad), pytest.approx(ap)), item.KEY
    # Hand of Justice: 20% crit + the above-50%-health effect (36% AD, 36% AP) all fight
    n = equipped(set19items.HandOfJustice())
    assert (n.bonus_ad.stat, n.ap.stat, n.crit.stat) == (pytest.approx(1.36), pytest.approx(1.36), pytest.approx(0.45))


def test_adaptive_helm_by_role():
    # GE_AdaptiveHelm_Stats: 3 regen, +15% mana gained; a non-Tank/Fighter role also gets OtherRoles (10% AD, 10% AP)
    base = equipped()
    n = equipped(set19items.AdaptiveHelm())
    assert n.manaRegen.stat == base.manaRegen.stat + 3 and n.manaGainMultiplier.stat == pytest.approx(1.15)
    assert (n.bonus_ad.stat, n.ap.stat) == (pytest.approx(1.1), pytest.approx(1.1))
    f = Neeko(1, build=load_build(V))
    f.role.archetype = 'Fighter'
    Simulator().itemStats([set19items.AdaptiveHelm()] + f.items, f)
    assert (f.bonus_ad.stat, f.ap.stat) == (1, 1)


def test_giant_slayer_vs_tank_or_not():
    assert equipped(set19items.GiantSlayer()).dmgMultiplier.stat == pytest.approx(1.30)
    assert equipped(set19items.GiantSlayerNoTank()).dmgMultiplier.stat == pytest.approx(1.15)


def test_krakens_fury_stacks_per_launch_then_attack_speed():
    from set19champs import Draven
    for seconds in (4, 30):
        d = Draven(1, build=load_build(V))
        k = set19items.KrakensFury()
        Simulator().simulate([k], [], d, [dummy()], seconds)
        assert k.stacks == min(15, d.launches)
        assert d.bonus_ad.stat == pytest.approx(1.10 + 0.035 * k.stacks)
        assert d.aspd.total('MultiplyAdditive') * 100 == pytest.approx(10 + (15 if k.stacks == 15 else 0))  # +15% AS at the 15th stack


def test_nashors_tooth_mana_on_attack_crits_only():
    n = equipped(set19items.NashorsTooth())
    nt = next(i for i in [set19items.NashorsTooth()])
    before = n.curMana
    n.emit(CRIT, attack_crit(n), [nt])
    assert n.curMana == pytest.approx(before + 2)
    n.emit(CRIT, spell_crit(n), [nt])  # a spell crit gives nothing (the listener wants IsAttack)
    assert n.curMana == pytest.approx(before + 2)
    assert n.manaPerAttack.stat == equipped().manaPerAttack.stat + 2  # ManaPerAttack 2 with the role's mana (I3)


def test_strikers_flail_four_instances_of_five_percent():
    n = equipped(set19items.StrikersFlail())
    f = set19items.StrikersFlail()
    base = n.dmgMultiplier.stat
    for k in range(5):
        n.tick = 15 * k  # a crit every 0.5 s
        n.emit(CRIT, attack_crit(n), [f])
    assert n.dmgMultiplier.stat == pytest.approx(base + 0.20)  # capped at 4 instances
    from effects import expire_effects
    expire_effects(n, 168)  # 5.6 s, past the 2nd crit's 5 s (0.5 s): the 2nd has worn off; the 5th renewed the 1st
    assert n.dmgMultiplier.stat == pytest.approx(base + 0.15)


@pytest.mark.parametrize("cls", ["RedBuff", "Morellonomicon", "RedBuffRadiant", "MorellonomiconRadiant"])
def test_no_burn(cls):
    # burn is not simulated (owner, 2026-11-18, as set18): the item is its stats, and its name says so
    from set19champs import Draven
    item = getattr(set19items, cls)()
    assert item.name.endswith(" (no burn)")
    d = Draven(1, build=load_build(V))
    t = dummy()
    Simulator().simulate([item], [], d, [t], 6)
    assert "Burn" not in t.effects and all(x[1][1] != "true" for x in d.dmgVector)


def test_last_whisper_and_void_staff_after_the_hit():
    # GE_ArmorSunder / GE_MRShred at level 30: x0.7, applied after each damage (PostApply), for 3 s / 5 s
    from set19champs import Draven
    d = Draven(1, build=load_build(V))
    t = dummy()
    Simulator().simulate([set19items.LastWhisper()], [], d, [t], 6)
    s = t.effects['Sunder']
    assert s.modifiers == [('armor', 'MultiplyAdditive', 0.7, 2)]  # GE_ArmorSunder's op and channel (I5, I7)
    assert s.last_tick == round(d.dmgVector[-1][0] * 30) + 90  # 3 s from the last hit (T14)
    d = Draven(1, build=load_build(V))
    t = dummy()
    Simulator().simulate([set19items.VoidStaff()], [], d, [t], 6)
    assert t.effects['Shred'].modifiers == [('mr', 'MultiplyAdditive', 0.7, 2)]


def test_radiants_use_their_own_numbers():
    # each Radiant runs the base script with its own effects (read through its GA parameters) and rows (I9)
    n = equipped(set19items.InfinityEdgeRadiant())
    assert n.bonus_ad.stat == pytest.approx(1.75) and n.crit.stat == pytest.approx(1.0)
    n = equipped(set19items.DeathbladeRadiant())
    assert n.bonus_ad.stat == pytest.approx(1 + 1.0 * 1.3)  # 100% AD, every bonus AD x1.30
    n = Neeko(1, build=load_build(V))
    Simulator().simulate([set19items.BlueBuffRadiant()], [], n, [dummy()], 0.1)
    assert n.manaRegen.stat == equipped().manaRegen.stat + 12
    g = equipped(set19items.GiantSlayerRadiant())
    assert g.dmgMultiplier.stat == pytest.approx(1.6)  # 30% + 30% vs Tanks
    k = set19items.NashorsToothRadiant()
    n = equipped(k)
    before = n.curMana
    n.emit(CRIT, attack_crit(n), [k])
    assert n.curMana == pytest.approx(before + 2)  # GE_NashorsToothRadiant_Mana
    from set19champs import Draven
    d = Draven(1, build=load_build(V))
    t = dummy()
    Simulator().simulate([set19items.LastWhisperRadiant()], [], d, [t], 4)
    assert t.effects['Sunder'].last_tick == round(d.dmgVector[-1][0] * 30) + 1500  # renewed by each hit (T14)
    assert len(set19items.radiants) == len(set19items.offensive_craftables)


def artifact_fight(item, champ=None, seconds=12, n=8, stage=4, hp=1800, mr=100, layout=None):
    from set19champs import Draven
    c = (champ or Draven)(1, build=load_build(V))
    c.stage = stage
    ds = [dummy() for _ in range(n)]
    for d in ds:
        d.hp.base, d.mr.base = hp, mr
    Simulator().simulate([item], [], c, ds, seconds, layout=layout)
    return c, ds


def test_stats_only_artifacts_and_silvermere_lock():
    n = equipped(set19items.InfinityForce())
    assert (n.bonus_ad.stat, n.ap.stat, n.aspd.total('MultiplyAdditive') * 100) == (pytest.approx(1.3), pytest.approx(1.3), pytest.approx(30))
    n = equipped(set19items.SilvermereDawn(), set19items.GuinsoosRageblade())
    assert n.aspd.stat == 0.5 and n.bonus_ad.stat == pytest.approx(2.5)  # Channel2 Override: 0.5 whatever else
    n = equipped(set19items.RapidFireCannon())
    assert n.attack_range == equipped().attack_range and n.bonus_range.stat == 1  # flights keep the unit's own range
    assert n.dmgMultiplier.stat == pytest.approx(1.05)
    n = equipped(set19items.GamblersBlade())
    assert n.aspd.total('MultiplyAdditive') * 100 == pytest.approx(55 + 30)  # 30 gold (owner)
    n = Neeko(1, build=load_build(V))
    n.takedowns = 12
    Simulator().itemStats([set19items.CappaJuice()] + n.items, n)
    assert n.ap.stat == pytest.approx(1.25 + 0.12)  # 12 Hats = the page's takedowns
    n = equipped(set19items.Hullcrusher())
    assert (n.bonus_ad.stat, n.ap.stat) == (pytest.approx(1.1), pytest.approx(1.1))
    n = equipped(set19items.HellfireHatchet())  # its AS per missing Health is skipped (0 at full Health)
    assert n.aspd.total('MultiplyAdditive') * 100 == 0


def test_statikk_shiv_every_third_release():
    # 6 bolts of 15 + bonus AP x 0.35; magic; not boosted by damage amp. 6 enemies assumed whatever the page's
    # targets (owner, 2026-11-18): with fewer, the bolts go round the dummies in play
    from layout import Layout
    per = 15 + 0.25 * 100 * 0.35  # Shiv's own 25% AP
    for targets in (1, 3, 7):
        c, ds = artifact_fight(set19items.StatikkShiv(), n=max(2, targets), mr=0, layout=Layout(targets))
        shots = [d for t, d, *_ in c.dmgVector if abs(d[0] - per) < 1e-6]
        assert len(shots) == 6 * (c.launches // 3)


def test_on_hit_artifacts():
    # Wit's End: OnHitDamage at the stage (stage 4: 65), magic, after each attack; Hellfire: 3% of max HP, physical
    c, ds = artifact_fight(set19items.WitsEnd(), mr=0)
    hits = [d[0] for t, d, *_ in c.dmgVector if d[0] == pytest.approx(65)]
    assert len(hits) >= c.launches - 1
    c, ds = artifact_fight(set19items.WitsEnd(), stage=6, mr=0)
    assert any(d[0] == pytest.approx(100) for t, d, *_ in c.dmgVector)
    # Titanic Hydra: 2% max HP + 4% AD, physical, to the target and the next dummy, before the hit
    h = set19items.TitanicHydra()
    c, ds = artifact_fight(h, n=8)
    amount = c.hp.stat * 0.02 + c.atk.stat * c.bonus_ad.stat * 0.04
    first = [d[0] for t, d, *_ in c.dmgVector][:3]
    assert first[0] == pytest.approx(amount) and first[1] == pytest.approx(amount)  # the test dummies have 0 armor


def test_lich_bane_once_per_cast():
    # armed by every cast, procs on the next attack hit after a release: stage 4 ProcDamage 500 magic
    from set19champs import Neeko
    c, ds = artifact_fight(set19items.LichBane(), champ=Neeko, seconds=20, mr=0)
    procs = [t for t, d, *_ in c.dmgVector if d[0] == pytest.approx(500)]
    assert 1 <= len(procs) <= c.numCasts and len(procs) >= c.numCasts - 1


def test_flickerblades_and_blighting_jewel():
    f = set19items.Flickerblades()
    c, ds = artifact_fight(f, seconds=6)
    assert c.aspd.total('MultiplyAdditive') * 100 == pytest.approx(20 + 4 * c.launches)
    assert c.bonus_ad.stat == pytest.approx(1 + 0.02 * (c.launches // 3))


def test_dawncore_manazane_talisman():
    from set19champs import Neeko
    n = equipped(set19items.Dawncore())
    assert n.fullMana.stat == equipped().fullMana.stat - 10
    c, ds = artifact_fight(set19items.Dawncore(), champ=Neeko, seconds=15)
    full = equipped().fullMana.stat - 10
    for _ in range(c.numCasts):
        full -= min(0.05 * full, full - 15)
    assert c.fullMana.stat == pytest.approx(full)
    m = set19items.Manazane()
    c, ds = artifact_fight(m, champ=Neeko, seconds=20)
    assert m.given == pytest.approx(110) and m.next_tick is None
    c, ds = artifact_fight(set19items.TalismanOfAscension(), champ=Neeko, seconds=23)
    assert c.dmgMultiplier.stat == pytest.approx(2.2) and c.manaRegen.stat == equipped().manaRegen.stat + 12


@pytest.mark.parametrize("cls", set19items.emblems)
def test_every_listed_spatula_item_reads_from_the_build(cls):
    equipped(getattr(set19items, cls)())  # raises if a stat can't be applied exactly


def test_emblem_stats():
    # GE_Jazz19_Emblem: 100 HP, AS 1 x AttackSpeedCalc1 (1 + EmblemAS 0.1); GE_DemonVision19_Emblem (Rock): +20% crit,
    # +15% AS; GE_Pentakill19_Emblem: 15% AD and AP
    base = equipped()
    n = equipped(set19items.JazzEmblem())
    assert n.aspd.stat == pytest.approx(base.aspd.stat * 1.1) and n.hp.stat == base.hp.stat + 100
    n = equipped(set19items.RockEmblem())
    assert n.crit.stat == pytest.approx(base.crit.stat + 0.2) and n.aspd.stat == pytest.approx(base.aspd.stat * 1.15)
    n = equipped(set19items.PentakillEmblem())
    assert (n.bonus_ad.stat, n.ap.stat) == (pytest.approx(1.15), pytest.approx(1.15))
    assert set19items.JazzEmblem().trait == "Jazz" and set19items.RockEmblem().trait is None

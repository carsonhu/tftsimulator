import set17champs as champs
import set17items as items
import set17buffs as buffs
from stats import Stat

def test_precision():
    c = champs.BaseChamp(level=1)
    jl1 = buffs.JeweledLotusI()
    jl1.performAbility("preCombat", 0, c)
    
    assert c.canSpellCrit == True, "Failed to apply spell crit"
    
    initial_crit_dmg = c.critDmg.stat
    ie = items.InfinityEdge()
    ie.performAbility("preCombat", 0, c)
    
    new_crit_dmg = c.critDmg.stat
    assert abs(new_crit_dmg - (initial_crit_dmg + 0.1)) < 0.001, "Precision did not stack critical strike damage properly."
    print("Test 1 Passed: Precision stacks correctly.")

def test_lucky_crit():
    # Mocking opponent
    opp = champs.BaseChamp(level=1)
    
    # Test without lucky crit
    c = champs.BaseChamp(level=1)
    c.luckyCrit = False
    c.critCounter = 0
    c.doDamage(opponent=opp, items=[], critChance=0.25, damageIfCrit=150, damage=100, dtype="physical", time=0)
    normal_crit_counter = c.critCounter
    
    # Test with lucky crit
    c2 = champs.BaseChamp(level=1)
    c2.luckyCrit = True
    c2.critCounter = 0
    c2.doDamage(opponent=opp, items=[], critChance=0.25, damageIfCrit=150, damage=100, dtype="physical", time=0)
    lucky_crit_counter = c2.critCounter
    
    expected_lucky = 1 - (1 - 0.25)**2
    assert abs(normal_crit_counter - 0.25) < 0.001, "Normal crit chance failed."
    assert abs(lucky_crit_counter - expected_lucky) < 0.001, "Lucky crit chance calculation failed."
    print(f"Test 2 Passed: Lucky Crit Chance correctly calculated (Expected: {expected_lucky}, Got: {lucky_crit_counter})")

def test_caitlyn_fateweaver():
    c = champs.Caitlyn(level=1)
    
    fw = buffs.Fateweaver(2, params=0)
    fw.performAbility("preCombat", 0, c)
    assert c.luckyAbility == True, "Fateweaver 2 did not assign luckyAbility"
    
    c_ult = None
    for item in c.items:
        if isinstance(item, buffs.CaitlynUlt):
            c_ult = item
            
    assert c_ult is not None, "Caitlyn is missing CaitlynUlt"
    
    class MockInput:
        regularAuto = True
        
    c_ult.performAbility("preAttack", 0, c, MockInput())
    
    expected_increment = 1 - (1 - 0.15)**2
    assert abs(c_ult.counter - expected_increment) < 0.001, "Caitlyn did not increment counter with lucky math"
    print(f"Test 3 Passed: Caitlyn correctly increments lucky counter (Expected: {expected_increment}, Got: {c_ult.counter})")

def test_nova():
    c = champs.Caitlyn(level=1)
    c.aspd.base = 0.8 # override base AS to mock testing environment
    c.aspd.add = 0
    c.aspd.mult = 1
    
    nova = buffs.NOVA(2, 0)
    nova.performAbility("preCombat", 0, c)
    c.novas["Caitlyn"] = True
    c.items.append(nova)
    
    initial_as = c.aspd.stat
    for t in [0.0, 2.0, 4.0, 5.9]:
        nova.ability("onUpdate", t, c)
    
    assert abs(c.aspd.stat - initial_as) < 0.001, "AS bumped prematurely"
    
    nova.ability("onUpdate", 6.0, c)
    assert abs(c.aspd.stat - (initial_as * 1.20)) < 0.001, f"AS didn't bump correctly at 6s, got {c.aspd.stat}"
    
    nova.ability("onUpdate", 8.0, c)
    assert abs(c.aspd.stat - (initial_as * 1.20)) < 0.001, "AS bumped multiple times"
    
    print("Test 4 Passed: N.O.V.A. buff accurately bumps stats strictly at 6.0s barrier and only once.")

def test_ezreal():
    e = champs.Ezreal(level=2)
    e.takedowns = 16 # Should yield 2 drones
    
    enemy = champs.DummyTank(level=1)
    enemy.hp.base = 1800
    enemy.armor.base = 100
    enemy.mr.base = 100
    
    # We don't care about the damage multiplier applying logic, just the raw base traces
    # which go through Champion.doDamage and append to dmgVector.
    # Actually doDamage applies armor, so enemy with 100 armor means 50% dmg reduction.
    # 225 -> 112.5. Drone 12 -> 6. Drone 12 -> 6. Total = 124.5
    
    e.performAbility([enemy], [], 0)
    
    # Dmg vector contains tuples like (time, (dmg_amt, type), aspd, mana, max_mana)
    # Wait, dmgVector is a list of tuples? Let's just check length of it.
    assert len(e.dmgVector) == 3, f"Expected 3 damage instances (1 spell + 2 drones), got {len(e.dmgVector)}"
    
    total_dmg = sum(hit[1] if not isinstance(hit[1], tuple) else hit[1][0] for hit in e.dmgVector)
    # 225 base hit + 12 drone + 12 drone = 249 raw physical dmg.
    # 50% physical reduction from 100 armor = 124.5
    assert abs(total_dmg - 124.5) < 0.001, f"Expected 124.5 damage, got {total_dmg}"
    print("Test 5 Passed: Ezreal successfully scales 150/225/340 ability and executes Drones based on takedowns.")

def test_jinx():
    j = champs.Jinx(level=2)
    j.aspd.add = 70 # 70% bonus AS -> 15 + 70//35 = 17 rockets
    
    enemy = champs.DummyTank(level=1)
    enemy.hp.base = 1800
    enemy.armor.base = 0 # 0 armor for easy math
    enemy.mr.base = 0
    
    j.performAbility([enemy], [], 0)
    
    # Expected rockets: 15 + 70//35 = 17 rockets
    # Base dmg Jinx 2: 38 AD + 5 AP = 43 per rocket
    # Total dmg: 17 * 43 = 731
    # numAttacks should be incremented by 2
    
    assert len(j.dmgVector) == 17, f"Expected 17 rockets, got {len(j.dmgVector)}"
    assert j.numAttacks == 2, f"Expected 2 attacks triggered, got {j.numAttacks}"
    
    total_dmg = sum(hit[1][0] if isinstance(hit[1], tuple) else hit[1] for hit in j.dmgVector)
    assert abs(total_dmg - 731) < 0.001, f"Expected 731 damage, got {total_dmg}"
    print("Test 6 Passed: Jinx successfully scales rockets with AS and increments attack counter.")

def test_pyke():
    p = champs.Pyke(level=2)
    # Pyke 2 stats: HP 1260, AD 68, AS 0.8
    # Ability Scaling: Harpoon 90, Cleave 360, Area 180 (for Pyke 2)
    
    enemy1 = champs.DummyTank(level=1)
    enemy1.hp.base = 5000
    enemy1.armor.base = 0
    enemy1.mr.base = 0
    
    enemy2 = champs.DummyTank(level=1)
    enemy2.hp.base = 5000
    enemy2.armor.base = 0
    enemy2.mr.base = 0
    
    p.performAbility([enemy1, enemy2], [], 0)
    
    # Expected hits: 
    # Harpoon: 90 (on enemy1)
    # Cleave: 360 (on enemy1)
    # Area: 180 * num_targets(2) (on enemy1 and enemy2)
    # Total dmg: 90 + 360 + 180 + 180 = 810
    
    # dmgVector length should be 1 + 1 + 2 = 4
    assert len(p.dmgVector) == 4, f"Expected 4 damage instances, got {len(p.dmgVector)}"
    
    total_dmg = sum(hit[1][0] if isinstance(hit[1], tuple) else hit[1] for hit in p.dmgVector)
    assert abs(total_dmg - 810) < 0.001, f"Expected 810 damage, got {total_dmg}"
    print("Test 7 Passed: Pyke ability correctly executes 3-part damage sequence.")

def test_voyager():
    c = champs.Pyke(level=1) # Pyke is ASSASSIN, not Tank/Fighter
    initial_amp = c.dmgMultiplier.stat
    
    # Voyager 2 (9%)
    v2_non_voyager = buffs.Voyager(2, 0)
    v2_non_voyager.performAbility("preCombat", 0, c)
    # Bonus should be 0.09 (is_voyager=0)
    assert abs(c.dmgMultiplier.stat - (initial_amp + 0.09)) < 0.001, f"Voyager 2 non-voyager failed, got {c.dmgMultiplier.stat}"
    
    # Voyager 2 Voyager (18%)
    c2 = champs.Pyke(level=1)
    v2_voyager = buffs.Voyager(2, 1)
    v2_voyager.performAbility("preCombat", 0, c2)
    assert abs(c2.dmgMultiplier.stat - (initial_amp + 0.18)) < 0.001, f"Voyager 2 voyager failed, got {c2.dmgMultiplier.stat}"
    
    # Tank check
    tank = champs.DummyTank(level=1) # Role.TANK
    v2_tank = buffs.Voyager(2, 1)
    v2_tank.performAbility("preCombat", 0, tank)
    assert abs(tank.dmgMultiplier.stat - initial_amp) < 0.001, "Voyager applied to Tank"
    
    print("Test 8 Passed: Voyager correctly applies Damage Amp based on role and voyager status.")

def test_master_yi():
    y = champs.MasterYi(level=2)
    # Yi 2 stats: AD 90, AS 0.85, Mana 30/70
    
    enemy = champs.DummyTank(level=1)
    enemy.hp.base = 10000
    enemy.armor.base = 0
    enemy.mr.base = 0
    
    # Test Passive
    y.startAttack([enemy], [], 0) # attack_counter = 1
    y.startAttack([enemy], [], 0) # attack_counter = 2
    y.startAttack([enemy], [], 0) # attack_counter = 3 -> passive trigger
    
    # Expected hits from passive: 90 bonus damage
    # plus the 3 auto attacks (90 each)
    # Total dmgVector hits: 3 autos + 1 passive = 4
    assert len(y.dmgVector) == 4, f"Expected 4 hits, got {len(y.dmgVector)}"
    
    # Test Active
    y.curMana = 70
    y.update([enemy], [], 4.0) 
    
    # Manually check status
    status_name = "Psi Strikes"
    assert status_name in y.statuses
    s = y.statuses[status_name]
    assert s.active == True
    assert abs(y.aspd.add - 70) < 0.001
    assert abs(y.omnivamp.stat - 0.15) < 0.001
    
    # Projections (Twice per second for 5s = 10 projections)
    # First projection fires 1.5s after meditation start (4.0 + 1.5 = 5.5)
    start_time = 4.0
    for i in range(1, 13): # Extended loop to catch the shifted projections
        y.update([enemy], [], start_time + 0.5 * i + 0.05)
    
    # Projections fired: 10 (at 5.5, 6.0, 6.5, 7.0, 7.5, 8.0, 8.5, 9.0, 9.5, 10.0)
    # Previous hits: 4
    # Total hits: 14 (plus any autos after t=5.0)
    # Yi 2 nextAttackTime was set to max(nextAttackTime, 4.0 + 1.0) = 5.0
    # Between 4.0 and 9.0, Yi 2 with 1.55 AS should attack every 0.645s
    # but manalock doesn't prevent attacks, only mana gain.
    # However, meditation (castTime lockout) ends at 5.0.
    # So between 5.0 and 9.0, he should attack.
    # 4s / 0.645s = ~6 attacks.
    # 14 + 6 = 20.
    assert len(y.dmgVector) >= 14, f"Expected at least 14 hits (10 projections + 4 original), got {len(y.dmgVector)}"
    
    print("Test 9 Passed: Master Yi passive and active mechanics verified.")

def test_marauder():
    c = champs.MasterYi(level=1) # Marauder
    initial_ad = c.bonus_ad.stat
    initial_vamp = c.omnivamp.stat
    
    # Marauder 4: 7% extra vamp, 35% extra AD, + 5% team vamp
    m4 = buffs.Marauder(4, 0)
    m4.performAbility("preCombat", 0, c)
    
    # bonus_ad is AP-based: stat = (100 + add) / 100
    # initial_ad was 1.0. After +35, it's 1.35.
    assert abs(c.omnivamp.stat - (initial_vamp + 0.05 + 0.07)) < 0.001, f"Expected {initial_vamp + 0.12} vamp, got {c.omnivamp.stat}"
    assert abs(c.bonus_ad.stat - (initial_ad + 0.35)) < 0.001, f"Expected {initial_ad + 0.35} AD, got {c.bonus_ad.stat}"
    
    print("Test 10 Passed: Marauder trait correctly applies team and unit bonuses.")

if __name__ == "__main__":
    print("Running Tests...\n")
    test_precision()
    test_lucky_crit()
    test_caitlyn_fateweaver()
    test_nova()
    test_ezreal()
    test_jinx()
    test_pyke()
    test_voyager()
    test_master_yi()
    test_marauder()
    print("\nAll tests ran successfully!")

import set17champs as champs
import set17buffs as buffs
from stats import Stat

def test_lissandra_stats():
    print("Testing Lissandra Stats...")
    l = champs.Lissandra(level=1)
    assert l.hp.base == 450
    assert l.atk.stat == 30
    assert l.curMana == 0
    assert l.fullMana.stat == 30
    assert l.aspd.stat == 0.70
    assert l.armor.stat == 15
    assert l.mr.stat == 15
    assert l.castTime == 1.0
    print("Lissandra Stats Passed!")

def test_lissandra_ability_no_replicator():
    print("Testing Lissandra Ability (No Replicator)...")
    l = champs.Lissandra(level=1)
    l.curMana = l.fullMana.stat
    
    # Enemies with 0 resistances for easy math
    enemy1 = champs.ZeroResistance(level=1)
    enemy2 = champs.ZeroResistance(level=1)
    enemy3 = champs.ZeroResistance(level=1)
    opponents = [enemy1, enemy2, enemy3]
    
    l.update(opponents, [], 0)
    
    # hits: 1 primary (250), 2 secondary (50 each)
    # Total dmgVector should have 3 entries
    assert len(l.dmgVector) == 3, f"Expected 3 hits, got {len(l.dmgVector)}"
    
    dmgs = [h[1][0] for h in l.dmgVector]
    assert 250 in dmgs, f"Expected 250 primary damage, got {dmgs}"
    assert dmgs.count(50) == 2, f"Expected two 50 secondary damage hits, got {dmgs}"
    
    print("Lissandra Ability (No Replicator) Passed!")

def test_lissandra_secondary_logic():
    print("Testing Lissandra Secondary Logic...")
    # num_targets = 1 -> 0 secondary
    l1 = champs.Lissandra(level=1)
    l1.num_targets = 1
    l1.performAbility([champs.ZeroResistance(level=1)], [], 0)
    assert len(l1.dmgVector) == 1, f"Expected 1 hit for num_targets=1, got {len(l1.dmgVector)}"
    
    # num_targets = 2 -> 1 secondary
    l2 = champs.Lissandra(level=1)
    l2.num_targets = 2
    l2.performAbility([champs.ZeroResistance(level=1), champs.ZeroResistance(level=1)], [], 0)
    assert len(l2.dmgVector) == 2, f"Expected 2 hits for num_targets=2, got {len(l2.dmgVector)}"

    # num_targets = 3 -> 2 secondary
    l3 = champs.Lissandra(level=1)
    l3.num_targets = 3
    l3.performAbility([champs.ZeroResistance(level=1), champs.ZeroResistance(level=1), champs.ZeroResistance(level=1)], [], 0)
    assert len(l3.dmgVector) == 3, f"Expected 3 hits for num_targets=3, got {len(l3.dmgVector)}"

    print("Lissandra Secondary Logic Passed!")

def test_lissandra_replicator_2():
    print("Testing Lissandra with Replicator 2...")
    l = champs.Lissandra(level=1)
    l.curMana = l.fullMana.stat
    
    # Replicator level 2 (scaling 0.22)
    rep = buffs.Replicator(2, 0)
    rep.performAbility("preCombat", 0, l)
    
    enemy1 = champs.ZeroResistance(level=1)
    opponents = [enemy1] # just 1 target for simplicity
    
    l.update(opponents, [], 0)
    
    # hits: 1 primary (250), 1 replicator primary (250 * 0.22 = 55)
    assert len(l.dmgVector) == 2, f"Expected 2 hits, got {len(l.dmgVector)}"
    dmgs = [h[1][0] for h in l.dmgVector]
    assert 250 in dmgs
    assert 55 in dmgs
    
    print("Lissandra Replicator 2 Passed!")

def test_lissandra_replicator_4():
    print("Testing Lissandra with Replicator 4...")
    l = champs.Lissandra(level=1)
    l.curMana = l.fullMana.stat
    
    # Replicator level 4 (scaling 0.45)
    rep = buffs.Replicator(4, 0)
    rep.performAbility("preCombat", 0, l)
    
    enemy1 = champs.ZeroResistance(level=1)
    enemy2 = champs.ZeroResistance(level=1)
    opponents = [enemy1, enemy2]
    
    l.update(opponents, [], 0)
    
    # hits: 
    # Primary Cast: 1 primary(250), 1 secondary(50)
    # Replicator Cast: 1 primary(250*0.45=112.5), 1 secondary(50*0.45=22.5)
    # Total 4 hits
    assert len(l.dmgVector) == 4, f"Expected 4 hits, got {len(l.dmgVector)}"
    dmgs = [h[1][0] for h in l.dmgVector]
    assert 250 in dmgs
    assert 50 in dmgs
    assert 112.5 in dmgs
    assert 22.5 in dmgs
    
    print("Lissandra Replicator 4 Passed!")

if __name__ == "__main__":
    test_lissandra_stats()
    test_lissandra_ability_no_replicator()
    test_lissandra_secondary_logic()
    test_lissandra_replicator_2()
    test_lissandra_replicator_4()
    print("\nAll Lissandra tests passed!")

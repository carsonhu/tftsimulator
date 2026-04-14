import set17champs as champs
import set17buffs as buffs
from stats import Stat

def test_corki_stats():
    print("Testing Corki Stats...")
    c = champs.Corki(level=2)
    # HP: 1530
    assert abs(c.hp.base - 1530) < 0.1, f"Expected HP 1530, got {c.hp.base}"
    # AD: 45 * 1.5 = 67.5
    assert abs(c.atk.stat - 67.5) < 0.1, f"Expected AD 67.5, got {c.atk.stat}"
    # Mana: 0/60
    assert c.curMana == 0
    assert c.fullMana.stat == 60
    # AS: 0.8
    assert abs(c.aspd.stat - 0.8) < 0.001
    # Armor/MR: 30
    assert c.armor.stat == 30
    assert c.mr.stat == 30
    print("Corki Stats Passed!")

def test_meeple_trait():
    print("Testing Meeple Trait...")
    c = champs.Corki(level=2)
    # Initial HP 1530
    initial_hp = c.hp.stat
    
    # 3 Meeple: 100 HP, 2 meeps
    meeple = buffs.Meeple(3, 0)
    meeple.performAbility("preCombat", 0, c)
    
    assert c.hp.stat == initial_hp + 100, f"Expected HP {initial_hp + 100}, got {c.hp.stat}"
    assert c.meep == 2, f"Expected 2 meeps, got {getattr(c, 'meep', 'None')}"
    print("Meeple Trait Passed!")

def test_corki_ability_timing():
    print("Testing Corki Ability Timing...")
    c = champs.Corki(level=2)
    enemy = champs.DummyTank(level=1)
    opponents = [enemy]
    
    # Give full mana
    c.curMana = c.fullMana.stat
    
    # Start cast at t=0
    c.update(opponents, [], 0)
    
    # Manalock for 3.5s
    assert abs(c.manalockTime - 3.5) < 0.001, f"Expected manalockTime 3.5, got {c.manalockTime}"
    # Attack lockout for 4.0s
    assert abs(c.nextAttackTime - 4.0) < 0.001, f"Expected nextAttackTime 4.0, got {c.nextAttackTime}"
    
    # Hits at t=0
    # Asteroid Blaster fires 21 missiles immediately in performAbility
    hits = [h for h in c.dmgVector if h[0] == 0]
    assert len(hits) == 21, f"Expected 21 missiles at t=0, got {len(hits)}"
    print("Corki Ability Timing Passed!")

def test_meep_bonus_timing():
    print("Testing Meep Bonus Timing...")
    c = champs.Corki(level=2)
    # Apply 2 meeps
    c.meep = 2
    # Reset status to pick up new meep count (usually happens at preCombat)
    c.applyStatus(champs.MeepBonusStatus(scaling=c.meepScaling), c, 0, 999, 0)
    
    enemy1 = champs.DummyTank(level=1)
    enemy2 = champs.DummyTank(level=1)
    opponents = [enemy1, enemy2]
    
    # t=0: Status initialized, next_proc = 0 + 8 * (1 - 0.2) = 6.4
    # update at t=6.3
    c.update(opponents, [], 6.3)
    meep_hits_early = [h for h in c.dmgVector if h[1][0] > 50]
    assert len(meep_hits_early) == 0, "Meep bonus fired too early"
    
    # update at t=6.5
    c.update(opponents, [], 6.5)
    # Should fire 2 hits (num_targets=2)
    meep_hits = [h for h in c.dmgVector if abs(h[0] - 6.5) < 0.1 and h[1][0] > 50]
    assert len(meep_hits) == 2, f"Expected 2 meep hits at t=6.5, got {len(meep_hits)}"
    
    # Next proc at 6.4 + 6.4 = 12.8
    c.update(opponents, [], 12.0)
    meep_hits_12 = [h for h in c.dmgVector if h[1][0] > 50]
    assert len(meep_hits_12) == 2
    c.update(opponents, [], 13.0)
    meep_hits_13 = [h for h in c.dmgVector if h[1][0] > 50]
    assert len(meep_hits_13) == 4
    
    print("Meep Bonus Timing Passed!")

def test_corki_mega_missile_deterministic():
    print("Testing Mega Missile Deterministic Logic...")
    c = champs.Corki(level=2)
    # Base chance 20% (0.2)
    # Over 21 missiles:
    # 1: 0.2 (normal)
    # 2: 0.4 (normal)
    # 3: 0.6 (normal)
    # 4: 0.8 (normal)
    # 5: 1.0 (MEGA, counter -> 0)
    # So every 5th missile is Mega.
    # 21 // 5 = 4 Mega missiles.
    
    enemy = champs.DummyTank(level=1)
    opponents = [enemy]
    c.performAbility(opponents, [], 0)
    
    # Damage values:
    # Standard: [28, 42, 280] AD + [5, 7, 24] AP
    # Base level 2 AD is 68. Base AP 100.
    # Standard damage = 42 * (68/68) + 7 * (100/100) = 49.
    # enemy has 100 Armor. 100/(100+100) = 0.5 multiplier.
    # Expected standard damage: 49 * 0.5 = 24.5
    # Expected mega damage: 24.5 * 3.5 = 85.75
    
    mega_hits = [h for h in c.dmgVector if h[1][0] > 50]
    standard_hits = [h for h in c.dmgVector if h[1][0] < 50]
    
    assert len(mega_hits) == 4, f"Expected 4 mega hits, got {len(mega_hits)}"
    assert len(standard_hits) == 17, f"Expected 17 standard hits, got {len(standard_hits)}"
    
    # Test Lucky (Fateweaver 2)
    c_lucky = champs.Corki(level=2)
    c_lucky.luckyAbility = True # Activated by Fateweaver 2
    # p = 0.36
    # 1: 0.36
    # 2: 0.72
    # 3: 1.08 (MEGA, counter -> 0.08)
    # 4: 0.44
    # 5: 0.80
    # 6: 1.16 (MEGA, counter -> 0.16)
    # 21 * 0.36 = 7.56. So 7 mega hits.
    
    c_lucky.performAbility(opponents, [], 0)
    mega_hits_lucky = [h for h in c_lucky.dmgVector if h[1][0] > 50]
    assert len(mega_hits_lucky) == 7, f"Expected 7 lucky mega hits, got {len(mega_hits_lucky)}"
    
    print("Mega Missile Deterministic Logic Passed!")

if __name__ == "__main__":
    test_corki_stats()
    test_meeple_trait()
    test_corki_ability_timing()
    test_meep_bonus_timing()
    test_corki_mega_missile_deterministic()
    print("\nAll Corki tests passed!")

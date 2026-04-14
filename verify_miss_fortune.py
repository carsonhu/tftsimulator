import set17champs as champs
import set17buffs as buffs
from stats import Stat

def test_miss_fortune_timing():
    print("Testing Miss Fortune Timing...")
    mf = champs.MissFortuneConduit(level=1)
    # Give full mana
    mf.curMana = mf.fullMana.stat
    
    enemy1 = champs.DummyTank(level=1)
    enemy2 = champs.DummyTank(level=1)
    opponents = [enemy1, enemy2]
    
    # Start cast at t=1.0
    start_time = 1.0
    mf.update(opponents, [], start_time)
    
    # 1. Check damage dealt immediately (burst at start)
    # Scale: AD [162.5], AP [25] -> Total 187.5 per target
    # DummyTank has 100 armor -> 50% reduction -> 93.75 per target
    # Total dmgVector length should be 2
    assert len(mf.dmgVector) == 2, f"Expected 2 damage hits, got {len(mf.dmgVector)}"
    total_dmg = sum(hit[1][0] for hit in mf.dmgVector)
    assert abs(total_dmg - 187.5) < 0.001, f"Expected 187.5 total damage, got {total_dmg}"
    
    # 2. Check manalock and cast lockout
    # Based on our base class change: 
    # manalockTime = time + manalockDuration (if > 0) = 1.0 + 2.5 = 3.5
    # nextAttackTime = time + castTime = 1.0 + 3.0 = 4.0
    assert abs(mf.manalockTime - 3.5) < 0.001, f"Expected manalockTime 3.5, got {mf.manalockTime}"
    assert abs(mf.nextAttackTime - 4.0) < 0.001, f"Expected nextAttackTime 4.0, got {mf.nextAttackTime}"
    
    # 3. Test mana gain after 2.5s but before 3.0s
    # Mana regen is processed in update. 
    # At t=3.6, manalock (3.5) is over.
    mf.manaRegen.base = 10 # 10 mana per second -> 5 mana per 0.5s tick
    mf.nextMana = 3.5 # Sync mana tick
    mf.update(opponents, [], 3.6)
    
    # Should have gained 5 mana * 1.2 (innate multiplier) = 6 mana
    # Wait, innate multiplier (1.2) is applied in preCombat. Let's apply it.
    cond = buffs.Conduit(0, 1) # Level 0, is_conduit=1
    cond.performAbility("preCombat", 0, mf)
    
    mf.curMana = 0
    mf.nextMana = 3.5
    mf.update(opponents, [], 3.6)
    assert mf.curMana > 0, f"Miss Fortune should have gained mana after 2.5s, curMana={mf.curMana}"
    assert abs(mf.curMana - 6.0) < 0.001, f"Expected 6.0 mana (5 * 1.2), got {mf.curMana}"
    
    # 4. Test no attack before 3.0s
    # At t=3.9, nextAttackTime is 4.0. Should not have attacked yet.
    # Current attacks: mf.numAttacks (multiTargetSpell doesn't increment numAttacks unless specified, but for MF we used default which is 0)
    # Wait, Champion.startAttack increments numAttacks.
    initial_attacks = mf.numAttacks
    mf.update(opponents, [], 3.9)
    assert mf.numAttacks == initial_attacks, "MF attacked before castTime ended"
    
    # 5. Test attack after 3.0s
    mf.update(opponents, [], 4.1)
    assert mf.numAttacks > initial_attacks, "MF did not attack after castTime ended"
    
    print("Test Miss Fortune Timing Passed!")

def test_conduit_innate():
    print("Testing Conduit Innate...")
    mf = champs.MissFortuneConduit(level=1)
    initial_multiplier = mf.manaGainMultiplier.stat
    
    # Apply Conduit Level 0
    cond = buffs.Conduit(0, 1)
    cond.ability("preCombat", 0, mf)
    
    # Should have 20% extra
    assert abs(mf.manaGainMultiplier.stat - (initial_multiplier + 0.20)) < 0.001, f"Expected {initial_multiplier + 0.20}, got {mf.manaGainMultiplier.stat}"
    print("Test Conduit Innate Passed!")

def test_conduit_regen():
    print("Testing Conduit Regen...")
    mf = champs.MissFortuneConduit(level=1)
    other = champs.BaseChamp(level=1)
    
    # Apply Conduit Level 2
    # (2) 1 Team | 3 Conduits
    cond_mf = buffs.Conduit(2, 1)
    cond_other = buffs.Conduit(2, 0)
    
    cond_mf.performAbility("preCombat", 0, mf)
    cond_other.performAbility("preCombat", 0, other)
    
    assert abs(mf.manaRegen.stat - 3) < 0.001, f"Expected 3 mana regen for Conduit, got {mf.manaRegen.stat}"
    assert abs(other.manaRegen.stat - 1) < 0.001, f"Expected 1 mana regen for non-Conduit, got {other.manaRegen.stat}"
    
    # Apply Conduit Level 5
    # (5) 3 Team | 9 Conduits
    mf2 = champs.MissFortuneConduit(level=1)
    other2 = champs.BaseChamp(level=1)
    cond_mf5 = buffs.Conduit(5, 1)
    cond_other5 = buffs.Conduit(5, 0)
    
    cond_mf5.performAbility("preCombat", 0, mf2)
    cond_other5.performAbility("preCombat", 0, other2)
    
    assert abs(mf2.manaRegen.stat - 9) < 0.001, f"Expected 9 mana regen for Conduit, got {mf2.manaRegen.stat}"
    assert abs(other2.manaRegen.stat - 3) < 0.001, f"Expected 3 mana regen for non-Conduit, got {other2.manaRegen.stat}"
    
    print("Test Conduit Regen Passed!")

if __name__ == "__main__":
    test_miss_fortune_timing()
    test_conduit_innate()
    test_conduit_regen()
    print("\nAll Miss Fortune & Conduit tests passed!")

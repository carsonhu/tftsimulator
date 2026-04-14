import sys
import os

# Add parent directory to path to import local modules
sys.path.append(os.getcwd())

import sim_core
from set17champs import Leblanc
from champion import Champion
from role import Role
import set17buffs
import set17items
import simulator

def log_comparison():
    print("Arbiter Deep Dive: Attack 3 vs Deal Damage 10 (Leblanc 2)")
    
    # Reset patches to be safe
    if hasattr(set17buffs.ArbiterAttack, "original_perform"):
        set17buffs.ArbiterAttack.performAbility = set17buffs.ArbiterAttack.original_perform
    if hasattr(set17buffs.ArbiterDealDamage, "original_perform"):
        set17buffs.ArbiterDealDamage.performAbility = set17buffs.ArbiterDealDamage.original_perform

    def run_case(cause_name, is_attack_case):
        champ = Leblanc(2)
        champ.cause = cause_name
        champ.effect = "Gain AP"
        dummy = Champion("Dummy", 50000, 0, 0, 100, 0.5, 0, 0, 1, Role.TANK)
        arbiter = set17buffs.Arbiter(2, 6)
        champ.items.append(arbiter)
        
        if is_attack_case:
            orig = set17buffs.ArbiterAttack.performAbility
            def patched(self, phase, time, champion, input_=0):
                old = self.attack_counter
                res = orig(self, phase, time, champion, input_)
                if self.attack_counter > old and self.attack_counter % 3 == 0:
                    print(f" > [Attack 3] Trigger at {time:.2f}s (Attack {self.attack_counter})")
                return res
            set17buffs.ArbiterAttack.performAbility = patched
        else:
            orig = set17buffs.ArbiterDealDamage.performAbility
            def patched(self, phase, time, champion, input_=0):
                old = self.counter
                res = orig(self, phase, time, champion, input_)
                if self.counter < old:
                    print(f" > [Damage 10] Trigger at {time:.2f}s (Instances reach 10)")
                return res
            set17buffs.ArbiterDealDamage.performAbility = patched

        sim = simulator.Simulator()
        sim.simulate([], [], champ, [dummy for _ in range(8)], 15.0)
        
        # Restore
        if is_attack_case:
            set17buffs.ArbiterAttack.performAbility = orig
        else:
            set17buffs.ArbiterDealDamage.performAbility = orig

    print("\n--- Testing Attack 3 times ---")
    run_case("When an Arbiter attacks 3 times", True)
    
    print("\n--- Testing Deal Damage 10 times ---")
    run_case("When an Arbiter deals damage 10 times", False)

if __name__ == "__main__":
    log_comparison()

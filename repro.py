import set17champs as champs
import status

def reproduce():
    # 1. 0 Meeps - should NOT fire
    c0 = champs.Corki(level=1)
    c0.meep = 0
    # Status applied in __init__ has interval 8, next_proc 8.
    opponents = [champs.DummyTank(level=1)]
    c0.update(opponents, [], 9.0)
    meep_hits0 = [h for h in c0.dmgVector if h[1][0] > 50]
    print(f"Meep hits with 0 meeps: {len(meep_hits0)}")
    assert len(meep_hits0) == 0

    # 2. 1 Meep - should fire
    c1 = champs.Corki(level=1)
    c1.meep = 1
    # In Corki __init__, meep was 0 (default). interval was 8. 
    # Next proc is 8.0.
    c1.update(opponents, [], 9.0)
    meep_hits1 = [h for h in c1.dmgVector if h[1][0] > 50]
    print(f"Meep hits with 1 meep: {len(meep_hits1)}")
    assert len(meep_hits1) > 0
    print("Verification finished successfully.")

if __name__ == "__main__":
    reproduce()

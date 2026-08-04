import json
import os
import sys

# Add the parent directory to sys.path to allow importing modules from there
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import set18.set18champs as set18champs
from set18.champion import Champion

def load_json_data(champ_name):
    # Normalize name for file search (lowercase, remove spaces/punctuation if needed)
    # The files seem to be tft16_lowercase.cdtb.bin.json
    normalized_name = champ_name.lower().replace(" ", "").replace("'", "").replace(".", "")
    
    # Special cases mapping if needed (e.g. kaisa -> kaisa, but file might be kai'sa? no, file is kaisa)
    # Based on file list:
    # Cho'Gath -> chogath
    # Kai'Sa -> kaisa
    # Kha'Zix -> khazix
    # Vel'Koz -> velkoz
    # Bel'Veth -> belveth
    # Rek'Sai -> reksai
    # Jarvan IV -> jarvaniv
    # Miss Fortune -> missfortune
    # Twisted Fate -> twistedfate
    # Xin Zhao -> xinzhao
    # Lee Sin -> leesin
    # Master Yi -> masteryi
    # Dr. Mundo -> drmundo
    # Tahm Kench -> tahmkench
    # Aurelion Sol -> aurelionsol
    
    filename = f"tft16_{normalized_name}.cdtb.bin.json"
    filepath = os.path.join(os.path.dirname(__file__), "data_reference", filename)
    
    if not os.path.exists(filepath):
        print(f"Warning: File not found for {champ_name}: {filepath}")
        return None
        
    with open(filepath, 'r') as f:
        return json.load(f)

def get_json_value(data, path):
    # Helper to traverse nested dictionary with a path string "Key/SubKey"
    keys = path.split('/')
    curr = data
    for k in keys:
        if isinstance(curr, dict) and k in curr:
            curr = curr[k]
        else:
            return None
    return curr

def compare_champion(champ_name):
    print(f"--- Comparing {champ_name} ---")
    
    # 1. Load JSON Data
    json_data = load_json_data(champ_name)
    if not json_data:
        return

    # 2. Instantiate Python Class
    try:
        champ_class = getattr(set18champs, champ_name.replace(" ", "").replace("'", "").replace(".", ""))
        champ = champ_class(level=1)
    except AttributeError:
        print(f"Error: Class not found for {champ_name} in set18champs.py")
        return
    except Exception as e:
        print(f"Error instantiating {champ_name}: {e}")
        return

    # 3. Extract and Compare Stats
    
    # Root path for stats
    # 3. Extract and Compare Stats
    
    # Root path for stats
    root_key = f"Characters/TFT16_{champ_name.replace(' ', '').replace('.', '')}/CharacterRecords/Root"
    
    root_data = json_data.get(root_key)
    if not root_data:
        # Try to find the key that looks like CharacterRecords/Root
        for key, val in json_data.items():
            if key.endswith("/CharacterRecords/Root"):
                root_data = val
                break
    
    # Fallback: Search for object with baseHP and mCharacterName
    if not root_data:
        for val in json_data.values():
            if isinstance(val, dict) and "baseHP" in val and "mCharacterName" in val:
                root_data = val
                break
    
    if not root_data:
        print(f"Error: Could not find CharacterRecords/Root for {champ_name}")
        return

    # Stats Mapping: (JSON Key, Python Value, Tolerance/Multiplier)
    comparisons = [
        ("baseHP", champ.hp.stat, "HP"),
        ("baseDamage", champ.atk.stat, "AD"),
        ("baseArmor", champ.armor.stat, "Armor"),
        ("baseSpellBlock", champ.mr.stat, "MR"),
        ("attackSpeed", champ.aspd.stat, "AS"),
        ("primaryAbilityResource", champ.fullMana.stat, "Mana"), 
        # Mana needs special handling because it's a dict in JSON
    ]

    for json_key, py_val, label in comparisons:
        json_val = root_data.get(json_key)
        
        if label == "Mana":
            if isinstance(json_val, dict):
                json_val = json_val.get("arBase", 0)
            else:
                json_val = 0 # Manaless?
        
        if json_val is None:
            print(f"  [MISSING] {label}: JSON has no value")
            continue
            
        # Check for mismatch
        # Floating point comparison
        if abs(json_val - py_val) > 0.1:
             print(f"  [MISMATCH] {label}: JSON={json_val}, Python={py_val}")
        else:
             # print(f"  [OK] {label}")
             pass

    # 4. Compare Spells
    # The user mentioned: TFT16_AniviaSpell has DataValues, indices 1-4 correspond to damage
    # And "spells" field in Root lists spell names.
    
    # 4. Compare Spells
    
    spell_found = False
    target_spell_name = f"TFT16_{champ_name.replace(' ', '').replace('.', '')}Spell".lower()
    
    # Special mappings: ChampName -> { JSON_Field: Python_Method_Name }
    special_mappings = {
        "Orianna": {
            "TargetDamage": "abilityScaling",
            "ExplosionDamage": "extraAbilityScaling"
        },
        "Seraphine": {
            "DamagePerCrystal": "abilityScaling",
            "BigCastDamage": "extraAbilityScaling",
            "_setup": {"musicNotes": 1}
        },
        "Lissandra": {
            "TargetDamage": "abilityScaling",
            "SecondaryDamage": "extraAbilityScaling"
        },
        "Teemo": {
            "PrimaryDamage": "abilityScaling",
            "DamagePerSecond": "dotScaling"
        }
    }
    
    champ_mappings = special_mappings.get(champ_name, {})
    
    # Run setup if exists
    if "_setup" in champ_mappings:
        for attr, val in champ_mappings["_setup"].items():
            setattr(champ, attr, val)
    
    issues_found = []

    def log_issue(msg):
        issues_found.append(msg)

    for key, val in json_data.items():
        is_spell_obj = False
        if "Spells/" in key and "mSpell" in val:
            is_spell_obj = True
        elif "mSpell" in val:
            # Check ObjectName or mScriptName
            obj_name = val.get("ObjectName", "").lower()
            script_name = val.get("mScriptName", "").lower()
            if target_spell_name in obj_name or target_spell_name in script_name:
                is_spell_obj = True
        
        if is_spell_obj:
            mSpell = val["mSpell"]
            data_values = mSpell.get("DataValues", [])
            
            # Collect all data values into a dict for easy lookup
            dv_map = {dv.get("mName"): dv.get("mValues") for dv in data_values if dv.get("mName")}
            
            # Standard checks
            damage_values = dv_map.get("Damage")
            ad_damage_values = dv_map.get("ADDamage")
            ap_damage_values = dv_map.get("APDamage")
            
            # Check if any standard or special keys exist
            found_any = (damage_values or ad_damage_values or ap_damage_values)
            for json_field in champ_mappings:
                if json_field in dv_map:
                    found_any = True
                    break
            
            if found_any:
                spell_found = True
                # Success message silenced
                # print(f"  [SPELL] Found damage values in {key} (Obj: {val.get('ObjectName')})")
                
                # Helper to compare
                def check_values(json_vals, py_method_name, label):
                    if not json_vals: return
                    
                    # Get python method
                    py_func = getattr(champ, py_method_name, None)
                    if not py_func:
                        log_issue(f"    [ERROR] Python method {py_method_name} not found on {champ_name}")
                        return

                    for level in range(1, 4):
                        # Probe with AD=0, AP=1 (Standard AP scaling assumption)
                        try:
                            py_val = py_func(level, 0, 1)
                        except TypeError:
                            log_issue(f"    [ERROR] Signature mismatch for {py_method_name}")
                            return

                        if level < len(json_vals):
                            json_val = json_vals[level]
                            if abs(json_val - py_val) > 1:
                                log_issue(f"    [MISMATCH] Lvl {level} ({label}): JSON={json_val}, Python={py_val}")
                        else:
                             log_issue(f"    [MISSING] Lvl {level} ({label}): JSON has fewer levels")

                # Run standard checks
                if damage_values:
                    check_values(damage_values, "abilityScaling", "Damage")
                if ad_damage_values:
                    # For AD damage, we probe differently: AD=1, AP=0
                    for level in range(1, 4):
                        py_val = champ.abilityScaling(level, 1, 0)
                        if level < len(ad_damage_values):
                            json_val = ad_damage_values[level]
                            if abs(json_val - py_val) > 1:
                                log_issue(f"    [MISMATCH] Lvl {level} (AD): JSON={json_val}, Python={py_val}")
                        else:
                             log_issue(f"    [MISSING] Lvl {level} (AD): JSON has fewer levels")
                if ap_damage_values:
                    check_values(ap_damage_values, "abilityScaling", "AP")

                # Run special checks
                for json_field, py_method in champ_mappings.items():
                    if json_field == "_setup": continue
                    vals = dv_map.get(json_field)
                    if vals:
                        check_values(vals, py_method, json_field)
                
                break
    
    if not spell_found:
        log_issue("  [MISSING] Could not find spell damage values in JSON")

    if issues_found:
        print(f"--- Comparing {champ_name} ---")
        for issue in issues_found:
            print(issue)

def main():
    # List of champions to check
    # We can get this from set18champs.champ_list
    
    print("Starting comparison...")
    for champ_name in set18champs.champ_list:
        # Skip commented out ones or special headers if any (champ_list is just strings)
        compare_champion(champ_name)

if __name__ == "__main__":
    main()

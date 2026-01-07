def optimize_bilgewater_stats(silver_serpents):
    """
    Calculates the optimal stats gained from spending silver serpents in the Bilgewater Black Market.
    Uses a greedy approach based on cost efficiency.
    """
    # Definitions of the tiers
    # (cost_base, hp_percent, as_percent, adap_percent)
    tiers = [
        {"id": 1, "cost_base": 15, "hp": 4, "as": 4, "adap": 3},
        {"id": 2, "cost_base": 30, "hp": 6, "as": 6, "adap": 5},
        {"id": 3, "cost_base": 50, "hp": 8, "as": 8, "adap": 7},
    ]

    # Initialize current counts for each purchase type
    # Keys will be like "T1_HP", "T2_AS", etc.
    counts = {}
    for tier in tiers:
        counts[f"T{tier['id']}_HP"] = 0
        counts[f"T{tier['id']}_AS"] = 0
        counts[f"T{tier['id']}_ADAP"] = 0

    accumulated_stats = {"HP": 0, "AS": 0, "AD": 0, "AP": 0}

    while silver_serpents > 0:
        best_option = None
        best_ratio = -1  # We want to maximize Stat / Cost
        
        # Check all 9 options
        for tier in tiers:
            t_id = tier['id']
            cost_base = tier['cost_base']
            
            # --- HP ---
            key_hp = f"T{t_id}_HP"
            count_hp = counts[key_hp]
            current_cost_hp = cost_base * (count_hp + 1)
            stat_val_hp = tier['hp']
            
            # Check ratio
            if current_cost_hp <= silver_serpents:
                ratio = stat_val_hp / current_cost_hp
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_option = ("HP", key_hp, current_cost_hp, stat_val_hp)
                elif ratio == best_ratio and best_option:
                     # Tie-breaking: usually prefer higher raw stat, or cheaper cost?
                     # Let's prefer cheaper cost to save money?
                     # Or higher stat to dump money faster?
                     # If Cost/Stat is same, e.g. 4/15 vs 8/30.
                     # 4/15 = 0.266. 8/30 = 0.266.
                     # If we have 30 gold. Buy 4/15, left 15. Buy 4/15 again? Cost becomes 30.
                     # So buying smaller chunks is safer for granularity.
                     if current_cost_hp < best_option[2]:
                         best_option = ("HP", key_hp, current_cost_hp, stat_val_hp)

            # --- AS ---
            key_as = f"T{t_id}_AS"
            count_as = counts[key_as]
            current_cost_as = cost_base * (count_as + 1)
            stat_val_as = tier['as']
            
            if current_cost_as <= silver_serpents:
                ratio = stat_val_as / current_cost_as
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_option = ("AS", key_as, current_cost_as, stat_val_as)
                elif ratio == best_ratio and best_option:
                     if current_cost_as < best_option[2]:
                         best_option = ("AS", key_as, current_cost_as, stat_val_as)

            # --- AD/AP ---
            key_adap = f"T{t_id}_ADAP"
            count_adap = counts[key_adap]
            current_cost_adap = cost_base * (count_adap + 1)
            stat_val_adap = tier['adap']
            # Assuming AD/AP value is equal to the % number for ratio calculation
            # Note: 3% AD/AP usually means 3 AD and 3 AP. 
            # If the user considers that "6 value", the ratios change heavily.
            # Based on T1 offering 4% HP vs 3% AD/AP, it implies 3% AD/AP is roughly worth 4% HP.
            # Start with direct comparison (3 value). 
            
            if current_cost_adap <= silver_serpents:
                ratio = stat_val_adap / current_cost_adap
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_option = ("ADAP", key_adap, current_cost_adap, stat_val_adap)
                elif ratio == best_ratio and best_option:
                     if current_cost_adap < best_option[2]:
                         best_option = ("ADAP", key_adap, current_cost_adap, stat_val_adap)

        if best_option:
            # Buy the best option
            stat_type, key, cost, val = best_option
            silver_serpents -= cost
            counts[key] += 1
            
            if stat_type == "HP":
                accumulated_stats["HP"] += val
            elif stat_type == "AS":
                accumulated_stats["AS"] += val
            elif stat_type == "ADAP":
                accumulated_stats["AD"] += val
                accumulated_stats["AP"] += val
        else:
            # No affordable options
            break

    return accumulated_stats

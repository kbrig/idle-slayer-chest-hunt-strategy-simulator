import random

# Define enemy types and their respective soul rewards
enemies = {
    "slime": {"type": "small", "reward": 8, "element": "neutral"},
    "mage": {"type": "small", "reward": 16, "element": "electric"},
    "dragon": {"type": "small", "reward": 30, "element": "dark"},
    "yeti": {"type": "giant", "reward": 2000, "element": "electric"}
}

# Define attack patterns as lists of enemies
patterns = [
    ["mage"],
    ["mage", "mage", "slime"],
    ["mage"] * 4,
    ["dragon"] * 5
]

# Define mode-specific bonuses and settings
idle_giant_chance = 0.16  # 16% chance of encountering a giant in idle mode

# Simulation parameters
base_crit_rate = 0.27  # 27% base crit chance
crit_multiplier = 2.1  # Crits multiply the reward by 2.1
simulation_duration = 120  # Simulate for 120 seconds

# Initialize bonuses dictionary
bonuses = {
    "soul_bonus": 1.3765,  # Global soul bonus
    "electric_bonus": 1.0,  # Bonus for electric enemies
    "dark_bonus": 2.51,  # Bonus for dark enemies
    "giant_bonus": 1.2625,  # Bonus for giants
    "crit_soul_bonus": 2.1125,  # Bonus from critical hits
    "level_soul_bonus": 1.554,  # Level-based bonus
    "crit_rate_bonus": 0.03,  # (additive) bonus to critical hit rate
    "souls_with_bow": 1.73, # Bonus to kills with bow
    "souls_with_boost": 4, # Bonus to kills while boosting
    "rage_mode_bonus": 221
}

# Function to initialize statistics
def initialize_stats():
    return {
        "total_souls": 0,
        "souls_per_monster": {enemy: 0 for enemy in enemies},
        "total_criticals": 0,
        "highest_critical": 0,
        "highest_crit_monster": None,
        "total_patterns": 0,
        "bonus_contributions": {key: 0 for key in bonuses},
        "base_crit_contribution": 0,
        "kills_per_monster": {enemy: 0 for enemy in enemies},
        "souls_with_bow": 0,
    }

# Function to format numbers for readability
def human_readable(num):
    units = ["", "K", "M", "B", "T", "Qa", "qi"]
    for i, unit in enumerate(units):
        if abs(num) < 1000:
            return f"{num:.1f}{unit}"
        num /= 1000
    return f"{num:.1f}{units[-1]}"

# Function to simulate Active Play with Bow
def simulate_active_bow():
    stats = initialize_stats()
    for _ in range(simulation_duration):  # 1 pattern per second
        selected_pattern = random.choice(patterns)
        selected_pattern = [enemy for enemy in selected_pattern if random.random() <= 0.95]  # 95% chance for other enemies
        selected_pattern.append("yeti") if random.random() <= 0.05 else None
        simulate_pattern(selected_pattern, stats, use_bow=True)
    return stats

# Function to simulate Active Play in Rage Mode
def simulate_active_rage(nb_seconds=simulation_duration):
    stats = initialize_stats()
    next_giant = random.randint(5, 13)
    nb_patterns = (2*nb_seconds)
    
    for _ in range(nb_patterns):  # Rage mode lasts for 34 patterns
        selected_pattern = random.choice(patterns)
        if next_giant == 0:
            selected_pattern.append("yeti")
            next_giant = random.randint(5, 13)
        next_giant -= 1
        simulate_pattern(selected_pattern, stats, rage_mode=True)
    return stats

# Function to simulate Idle Play
def simulate_idle_play():
    stats = initialize_stats()
    num_patterns = int(simulation_duration / 0.05)  # 1 enemy every 0.05 seconds
    for _ in range(num_patterns):
        if random.random() <= idle_giant_chance:  # 16% chance for a giant
            selected_pattern = ["yeti"]
        else:
            selected_pattern = [random.choice(list(enemies.keys()))]
        simulate_pattern(selected_pattern, stats)
    return stats

# Function to simulate a pattern and update stats
def simulate_pattern(pattern, stats, use_bow=False, rage_mode=False):
    for enemy_name in pattern:
        reward = calculate_reward(enemy_name, stats, use_bow=use_bow, rage_mode=rage_mode)
        stats["total_souls"] += reward
        stats["souls_per_monster"][enemy_name] += reward
        stats["kills_per_monster"][enemy_name] += 1
    stats["total_patterns"] += 1

# Function to calculate rewards, applying bonuses
def calculate_reward(enemy_name, stats, use_bow=False, rage_mode=False):
    enemy = enemies[enemy_name]
    base_reward = enemy["reward"]
    soul_reward = base_reward
    print(f" -> Encountered '{enemy_name}' ({soul_reward})")

    if rage_mode:
        total_bonus_multiplier = bonuses["rage_mode_bonus"]
    else: 
        total_bonus_multiplier = bonuses["souls_with_boost"]
    
    print(f"    -> Rage Mode? {rage_mode} - Start multiplier: {total_bonus_multiplier}")

    # Apply global and specific bonuses
    total_bonus_multiplier *= bonuses["soul_bonus"]

    # Apply mode-specific bonuses
    if use_bow and enemy["type"] != "giant":
        total_bonus_multiplier *= bonuses["souls_with_bow"]
        print(f"    -> kill with bow! New multiplier: {total_bonus_multiplier}")
    elif enemy["type"] == "giant":
        total_bonus_multiplier *= bonuses["giant_bonus"]
        print(f"    -> kill via sword! New multiplier: {total_bonus_multiplier}")

    if enemy["element"] == "electric":
        total_bonus_multiplier *= bonuses["electric_bonus"]
        print(f"    -> Electric Enemy! New multiplier: {total_bonus_multiplier}")
    if enemy["element"] == "dark":
        total_bonus_multiplier *= bonuses["dark_bonus"]
        print(f"    -> Dark Enemy! New multiplier: {total_bonus_multiplier}")

    # Apply level-based bonus
    total_bonus_multiplier *= bonuses["level_soul_bonus"]
    print(f" -> Zone bonus of {bonuses["level_soul_bonus"]}! New multiplier: {total_bonus_multiplier}")

    # Calculate and apply critical hit bonuses
    crit_rate = base_crit_rate + bonuses["crit_rate_bonus"]
    is_crit = random.random() < crit_rate
    if is_crit:
        total_bonus_multiplier *= bonuses["crit_soul_bonus"]
        print(f" -> Critical Hit! New multiplier: {total_bonus_multiplier}")
        stats["total_criticals"] += 1
        if soul_reward > stats["highest_critical"]:
            stats["highest_critical"] = soul_reward
            stats["highest_crit_monster"] = enemy_name


    # Calculate the final soul reward
    soul_reward = base_reward * total_bonus_multiplier
    print(f"{enemy_name} kill! Reward: {human_readable(soul_reward)} = {base_reward} * {total_bonus_multiplier}")

    # Calculate the contribution of each bonus
    if use_bow and enemy["type"] != "giant":
        stats["bonus_contributions"]["souls_with_bow"] += base_reward * (bonuses["souls_with_bow"] - 1) / (total_bonus_multiplier - 1)

    if rage_mode:
        stats["bonus_contributions"]["rage_mode_bonus"] += base_reward * bonuses["rage_mode_bonus"] / (total_bonus_multiplier - 1)

    stats["bonus_contributions"]["soul_bonus"] += base_reward * (bonuses["soul_bonus"] - 1) / (total_bonus_multiplier - 1)

    if enemy["type"] == "giant":
        stats["bonus_contributions"]["giant_bonus"] += base_reward * (bonuses["giant_bonus"] - 1) / (total_bonus_multiplier - 1)
    if enemy["element"] == "electric":
        stats["bonus_contributions"]["electric_bonus"] += base_reward * (bonuses["electric_bonus"] - 1) / (total_bonus_multiplier - 1)
    if enemy["element"] == "dark":
        stats["bonus_contributions"]["dark_bonus"] += base_reward * (bonuses["dark_bonus"] - 1) / (total_bonus_multiplier - 1)

    stats["bonus_contributions"]["level_soul_bonus"] += base_reward * (bonuses["level_soul_bonus"] - 1) / (total_bonus_multiplier - 1)

    if is_crit:
        crit_reward = base_reward * (bonuses["crit_soul_bonus"] - 1)
        crit_bonus = bonuses["crit_rate_bonus"]
        stats["bonus_contributions"]["crit_soul_bonus"] += crit_reward
        stats["bonus_contributions"]["crit_rate_bonus"] += crit_reward * (crit_bonus / (base_crit_rate + crit_bonus))

    return soul_reward

# Function to display simulation statistics
def display_stats(mode, stats):
    print(f"\n--- {mode} Stats ---")
    print(f"Total souls gained: {human_readable(stats['total_souls'])}")
    print("Souls gained per monster type:")
    for monster, souls in stats["souls_per_monster"].items():
        kills = stats["kills_per_monster"][monster]
        print(f"  {monster}: {human_readable(souls)} ({kills})")
    print(f"Total critical hits: {stats['total_criticals']}")
    print(f"Highest critical hit: {human_readable(stats['highest_critical'])}")
    if stats["highest_crit_monster"]:
        print(f"Monster with highest critical hit: {stats['highest_crit_monster']}")
    print(f"Total patterns simulated: {stats['total_patterns']}")

    sorted_contributions = sorted(stats["bonus_contributions"].items(), key=lambda item: item[1], reverse=True)
    total_bonus_contribution = sum(stats["bonus_contributions"].values()) + stats["base_crit_contribution"]

    print("\nBonus contributions to soul increase:")
    for bonus, contribution in sorted_contributions:
        percentage = (contribution / total_bonus_contribution) * 100 if total_bonus_contribution > 0 else 0
        print(f"  {bonus}: {human_readable(contribution)} ({percentage:.2f}%)")

# Run simulations for each mode and aggregate results
def run_multiple_simulations(simulation_func, num_simulations=50):
    all_stats = []

    for _ in range(num_simulations):
        stats = simulation_func()
        all_stats.append(stats)

    # Calculate average, worst, and best stats
    avg_stats = initialize_stats()
    best_stats = initialize_stats()
    worst_stats = all_stats[0]

    for stats in all_stats:
        # Aggregate for average
        for key in avg_stats:
            #print(avg_stats[key])
            if isinstance(avg_stats[key], dict):
                for sub_key in avg_stats[key]:
                
                    avg_stats[key][sub_key] += stats[key][sub_key]
            elif isinstance(avg_stats[key], int):
                avg_stats[key] += stats[key]

        # Determine best and worst stats
        if stats['total_souls'] > best_stats['total_souls']:
            best_stats = stats
        if stats['total_souls'] < worst_stats['total_souls']:
            worst_stats = stats

    # Average the stats
    for key in avg_stats:
        if isinstance(avg_stats[key], dict):
            for sub_key in avg_stats[key]:
                avg_stats[key][sub_key] /= num_simulations
        elif isinstance(avg_stats[key], float):
            avg_stats[key] /= num_simulations

    return avg_stats, worst_stats, best_stats

# Display results for multiple simulations
def display_aggregated_stats(mode, avg_stats, worst_stats, best_stats):
    print(f"\n--- {mode} Simulation Results ---")
    print("\nAverage Stats:")
    display_stats("Average", avg_stats)
    print("\nWorst Stats:")
    display_stats("Worst", worst_stats)
    print("\nBest Stats:")
    display_stats("Best", best_stats)

# Run and display the results for 50 simulations
num_simulations = 50

avg_bow_stats, worst_bow_stats, best_bow_stats = run_multiple_simulations(simulate_active_bow, num_simulations)
avg_rage_stats, worst_rage_stats, best_rage_stats = run_multiple_simulations(simulate_active_rage, num_simulations)
avg_idle_stats, worst_idle_stats, best_idle_stats = run_multiple_simulations(simulate_idle_play, num_simulations)

display_aggregated_stats("Active Play with Bow", avg_bow_stats, worst_bow_stats, best_bow_stats)
display_aggregated_stats("Active Play in Rage Mode", avg_rage_stats, worst_rage_stats, best_rage_stats)
display_aggregated_stats("Idle Play", avg_idle_stats, worst_idle_stats, best_idle_stats)
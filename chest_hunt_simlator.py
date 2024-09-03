import random

# Define constants
NUM_BOXES = 30
NUM_SIMULATIONS = 1000000  # Adjust as needed for accuracy

def print_game(index, picks, mimic_positions, saver_position, multiplier_position):
    for i in range(len(picks)):
        print_game_row(i, picks[:i + 1], mimic_positions, saver_position, multiplier_position)


def print_game_row(index, picks, mimic_positions, saver_position, multiplier_position):
    line = f"{index:02d}: "
    for i in range(NUM_BOXES):
        if len(picks) > 0 and i == picks[len(picks) - 1]:
            line += "➡️"
        if i in picks:
            if i in mimic_positions:
                line += " ☠️ "
            elif i == saver_position:
                line += " ⛨ "
            elif i == multiplier_position:
                line += " ⚡ "
            else:
                line += " 📤 "
        elif i == saver_position:
            line += " 🛡️ "
        else:
            line += " 📦 "
    print(line)

# Function to simulate one game with any given strategy
def simulate_game(strategy, num_boxes):
    # Initialize the game setup
    boxes = ["empty"] * num_boxes
    saver_position = random.randint(0, num_boxes - 1)
    multiplier_position = random.choice([i for i in range(num_boxes) if i != saver_position])
    mimic_positions = random.sample([i for i in range(num_boxes) if i != saver_position and i != multiplier_position], 4)

    boxes[saver_position] = "saver"
    boxes[multiplier_position] = "multiplier"
    for mimic_position in mimic_positions:
        boxes[mimic_position] = "mimic"

    # Initialize the game state
    savers = 0
    mimics_remaining = 4
    mimics_encountered = 0
    sucker_punch_kills = 0
    picks = strategy(num_boxes, saver_position, multiplier_position, mimic_positions)
    boxes_opened = 0
    multiplier = 1


    # print_game(0, [], mimic_positions, saver_position, multiplier_position)
    for i, pick in enumerate(picks):
        boxes_opened += 1
        content = boxes[pick]

        # print_game(i, picks[:i + 1], mimic_positions, saver_position, multiplier_position)
        if i < 2:
            # First two picks are safe: kill mimics or reveal the saver/multiplier
            if content == "mimic":
                boxes[pick] = "empty"  # Safe pick eliminates mimic
                mimics_encountered += 1
                mimics_remaining -= 1
            elif content == "saver":
                savers += 1 * multiplier
                multiplier = 1
            elif content == "multiplier":
                multiplier = 2  # If multiplier is found, saver is automatically granted
                #return True, boxes_opened, mimics_encountered, sucker_punch_kills
        else:
            if content == "mimic":
                mimics_encountered += 1
                if savers > 0:
                    savers -= 1  # Mimic consumes the saver
                    boxes[pick] = "empty"  # 2% chance to kill the mimic
                    mimics_remaining -= 1
                elif random.random() < 0.02:
                    boxes[pick] = "empty"  # 2% chance to kill the mimic
                    sucker_punch_kills += 1
                    mimics_remaining -= 1
                else:
                    return False, boxes_opened, mimics_encountered, sucker_punch_kills  # Game over, mimic found without a saver
            elif content == "saver":
                savers += 1 * multiplier
                multiplier = 1
            elif content == "multiplier":
                multiplier = 2

        # Check if the game should end
        if mimics_remaining == 0 or boxes_opened == num_boxes - mimics_remaining:
            boxes_opened = num_boxes
            mimics_encountered += mimics_remaining
            return True, boxes_opened, mimics_encountered, sucker_punch_kills
        

    # print_game(i, picks[:i + 1], mimic_positions, saver_position, multiplier_position)
    return False, boxes_opened, mimics_encountered, sucker_punch_kills

# Dynamic random strategy implementation
def dynamic_random_strategy(num_boxes, saver_position, multiplier_position, mimic_positions):
    picks = random.sample(range(num_boxes), num_boxes)
    picks.remove(saver_position)

    first_two_picks = picks[:2]
    mimics_found = any(pick in mimic_positions for pick in first_two_picks)

    if not mimics_found:
        picks.insert(2, saver_position)
    else:
        picks.insert(picks.index(multiplier_position) + 1, saver_position)
    
    # print_game(0, picks, mimic_positions, saver_position, multiplier_position)
    return picks

# Dynamic sequential strategy implementation
def dynamic_sequential_strategy(num_boxes, saver_position, multiplier_position, mimic_positions):
    picks = list(range(num_boxes))
    picks.remove(saver_position)

    first_two_picks = picks[:2]
    mimics_found = any(pick in mimic_positions for pick in first_two_picks)

    if not mimics_found:
        picks.insert(2, saver_position)
    else:
        multiplier_index = picks.index(multiplier_position)
        picks.insert(multiplier_index + 1, saver_position)

    return picks

# Dynamic reverse sequential strategy implementation
def dynamic_sequential_reverse_strategy(num_boxes, saver_position, multiplier_position, mimic_positions):
    picks = list(range(num_boxes - 1, -1, -1))
    picks.remove(saver_position)

    first_two_picks = picks[:2]
    mimics_found = any(pick in mimic_positions for pick in first_two_picks)

    if not mimics_found:
        picks.insert(2, saver_position)
    else:
        multiplier_index = picks.index(multiplier_position)
        picks.insert(multiplier_index + 1, saver_position)

    return picks

# Static random strategy implementation
def static_random_strategy(num_boxes, saver_position, multiplier_position, mimic_positions):
    return random.sample(range(num_boxes), num_boxes)

# Static sequential strategy implementation
def static_sequential_strategy(num_boxes, saver_position, multiplier_position, mimic_positions):
    return list(range(num_boxes))

# Static reverse sequential strategy implementation
def static_sequential_reverse_strategy(num_boxes, saver_position, multiplier_position, mimic_positions):
    return list(range(num_boxes - 1, -1, -1))

# Your refined strategy implementation
def refined_strategy_picks(num_boxes, saver_position, multiplier_position, mimic_positions):
    picks = []
    picked_boxes = set()
    
    def make_pick(position):
        if position in picked_boxes:
            return True
        if position >= 0 and position < num_boxes:
            picks.append(position)
            picked_boxes.add(position)

            if (position == multiplier_position):
                picks.append(saver_position)
                picked_boxes.add(saver_position)
            return True
        return False
    
    # 1. First two picks based on the saver's position
    if not make_pick(saver_position + 2):
        make_pick(saver_position - 4)
    if not make_pick(saver_position - 2):
        make_pick(saver_position + 4)

    no_special_pick = True
    if multiplier_position in picked_boxes:
        no_special_pick = False
    for p in picks:
        if p in mimic_positions:
            no_special_pick = False
    
    if no_special_pick:
        make_pick(saver_position)

    # 2. Start picking boxes every two indices based on saver position
    direction = -1 if saver_position < num_boxes / 2 else 1
    current_position = saver_position
    
    def pick_in_direction():
        nonlocal current_position, direction
        current_position += 2 * direction
        while make_pick(current_position):
            current_position += 2 * direction
            

    # 3. Pick all the boxes in the direction that has the least
    pick_in_direction()

    # 4. Change direction and pick boxes that way as well
    direction = -direction
    current_position = saver_position
    pick_in_direction()

    # 5. Once no more can be picked in that direction, pick every other remaining boxes from smallest to largest index
    pick_next = True
    while len(picked_boxes) < num_boxes:
        for i in range(num_boxes):
            if i not in picked_boxes:
                make_pick(i) if pick_next else None
                pick_next = not pick_next

    return picks

# Define strategies to test
strategies = {
    # "static_random": static_random_strategy,
    # "static_sequential": static_sequential_strategy,
    # "static_sequential_reverse": static_sequential_reverse_strategy,
    "dynamic_random": dynamic_random_strategy,
    "dynamic_sequential": dynamic_sequential_strategy,
    "dynamic_sequential_reverse": dynamic_sequential_reverse_strategy,
    "refined_dynamic_strategy": refined_strategy_picks,
}

# Function to run simulations for each strategy
def run_simulations():
    results = {
        strategy_name: {
            "wins": 0,
            "total_boxes_opened": 0,
            "min_boxes": float('inf'),
            "max_boxes": 0,
            "total_mimics_encountered": 0,
            "min_mimics": float('inf'),
            "max_mimics": 0,
            "sucker_punch_kills": 0
        }
        for strategy_name in strategies
    }

    for strategy_name, strategy_func in strategies.items():
        for _ in range(NUM_SIMULATIONS):
            win, boxes_opened, mimics_encountered, sucker_punch_kills = simulate_game(strategy_func, NUM_BOXES)
            results[strategy_name]["total_boxes_opened"] += boxes_opened
            results[strategy_name]["min_boxes"] = min(results[strategy_name]["min_boxes"], boxes_opened)
            results[strategy_name]["max_boxes"] = max(results[strategy_name]["max_boxes"], boxes_opened)
            results[strategy_name]["total_mimics_encountered"] += mimics_encountered
            results[strategy_name]["min_mimics"] = min(results[strategy_name]["min_mimics"], mimics_encountered)
            results[strategy_name]["max_mimics"] = max(results[strategy_name]["max_mimics"], mimics_encountered)
            results[strategy_name]["sucker_punch_kills"] += sucker_punch_kills
            if win:
                results[strategy_name]["wins"] += 1

    return results

# Run simulations and display results
if __name__ == "__main__":
    results = run_simulations()
    print("Simulation results:")
    for strategy, data in results.items():
        avg_boxes_opened = data["total_boxes_opened"] / NUM_SIMULATIONS
        avg_mimics_encountered = data["total_mimics_encountered"] / NUM_SIMULATIONS
        avg_sucker_punch_kills = data['sucker_punch_kills'] / NUM_SIMULATIONS
        win_rate = data["wins"] / NUM_SIMULATIONS
        print(f"{strategy}: {win_rate:.2%} win rate")
        print(f"  Worst: {data['min_boxes']} boxes opened")  # Worst scenario should be min_boxes
        print(f"  Best: {data['max_boxes']} boxes opened")   # Best scenario should be max_boxes
        print(f"  Average: {avg_boxes_opened:.2f} boxes opened")
        print(f"  Mimics Encountered - Worst: {data['min_mimics']}, Best: {data['max_mimics']}, Average: {avg_mimics_encountered:.2f}")
        print(f"  Average Sucker Punch Kills: {avg_sucker_punch_kills:.2f}")

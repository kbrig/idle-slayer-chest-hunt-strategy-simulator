import json
import os

class LoadoutManager:
    def __init__(self, items_data, bonuses_data):
        self.items_data = items_data
        self.bonuses_data = bonuses_data
        self.loadouts = {}

    def print_colored(self, text, color_code):
        print(f"\033[{color_code}m{text}\033[0m")

    def calculate_total_bonuses(self, loadout):
        total_bonuses = {}
        for slot, item_info in loadout.items():
            item = self.items_data[item_info['type']][item_info['name']]
            level = item_info['level']
            rarity = item_info['rarity']

            # Add main bonuses
            for bonus in item.get("Main Bonuses", []):
                bonus_key = bonus["Bonus Key"]
                bonus_value = bonus["Bonus per Level"] * (level + 1) * 1.25 if rarity == "excellent" else 1
                
                if bonus_key in total_bonuses:
                    total_bonuses[bonus_key] += bonus_value
                else:
                    total_bonuses[bonus_key] = bonus_value

            # Add selected optional bonuses
            for selected_bonus in item_info.get('enabled_optional_bonuses', []):
                print(f"Adding optional bonus {selected_bonus}")
                print(item["Optional Bonuses"])
                bonus = next(b for b in item["Optional Bonuses"] if b["Bonus Key"] == selected_bonus)
                bonus_key = bonus["Bonus Key"]
                bonus_value = bonus["Bonus per Level"] * (level + 1) * 1.25 if rarity == "excellent" else 1
                self.print_colored(f"Adding optional bonus {bonus_key} with value {bonus_value} level {level}", '94')  # Light blue for optional bonuses
                if bonus_key in total_bonuses:
                    total_bonuses[bonus_key] += bonus_value
                else:
                    total_bonuses[bonus_key] = bonus_value

        return total_bonuses

    def create_loadout(self):
        loadout = {}
        while True:
            slot_types = list(self.items_data.keys())
            print("\nAvailable Slots:")
            for i, slot_type in enumerate(slot_types, 1):
                print(f"{i}. {slot_type}")
            print(f"{len(slot_types) + 1}. Finish loadout creation")
            slot_choice = int(input(f"\nSelect a slot by number (or select to finish): ")) - 1

            if slot_choice == len(slot_types):
                break

            selected_slot_type = slot_types[slot_choice]

            items = list(self.items_data[selected_slot_type].keys())
            print(f"\nAvailable Items for {selected_slot_type}:")
            for i, item_name in enumerate(items, 1):
                item = self.items_data[selected_slot_type][item_name]
                if item.get('excellent', False):
                    color_code = '32'  # Green
                elif 'options' in item:
                    if item['level'] >= 7:
                        color_code = '33'  # Yellow
                    else:
                        color_code = '34'  # Blue
                else:
                    color_code = '37'  # White
                self.print_colored(f"{i}. {item_name}", color_code)
            item_choice = int(input(f"\nSelect an item by number: ")) - 1
            item_name = items[item_choice]

            item = self.items_data[selected_slot_type][item_name]
            level = 1 if item.get("Key Item", False) else int(input("Enter item level (1-20): "))
            rarity_input = "n" if item.get("Key Item", False) else input("Enter rarity (n for normal, e for excellent): ").lower()
            rarity = "normal" if rarity_input == "n" else "excellent"

            # Handle optional bonuses selection
            enabled_optional_bonuses = []
            if item.get("Optional Bonuses"):
                print(f"\nOptional bonuses for {item_name}:")
                for i, bonus in enumerate(item["Optional Bonuses"], 1):
                    print(f"{i}. {bonus['Bonus Key']} (+{bonus['Bonus per Level']} per level)")
                selected_indexes = input("Enter the numbers of the optional bonuses you want to enable (comma-separated): ")
                if selected_indexes:
                    selected_indexes = [int(i) - 1 for i in selected_indexes.split(",")]
                    enabled_optional_bonuses = [item["Optional Bonuses"][i]["Bonus Key"] for i in selected_indexes]

            # Handle skills selection
            selected_skills = []
            if item.get("Skills"):
                print(f"\nSkills for {item_name}:")
                for i, skill in enumerate(item["Skills"], 1):
                    print(f"{i}. {skill['Skill Name']}")
                selected_indexes = input("Enter the numbers of the skills you want to enable (comma-separated): ")
                if selected_indexes:
                    selected_indexes = [int(i) - 1 for i in selected_indexes.split(",")]
                    selected_skills = [item["Skills"][i]["Skill Name"] for i in selected_indexes]

            loadout[selected_slot_type] = {
                'name': item_name,
                'level': level,
                'rarity': rarity,
                'type': selected_slot_type,
                'enabled_optional_bonuses': enabled_optional_bonuses,
                'enabled_skills': selected_skills
            }

        loadout_name = input("\nEnter a name for this loadout: ")
        self.loadouts[loadout_name] = loadout
        self.save_loadouts()
        print("Loadout created successfully.")

    def save_loadouts(self):
        with open("loadouts.json", "w") as f:
            json.dump(self.loadouts, f)

    def load_loadouts(self):
        if os.path.exists("loadouts.json"):
            with open("loadouts.json", "r") as f:
                self.loadouts = json.load(f)

    def display_loadouts(self):
        if not self.loadouts:
            print("No loadouts available.")
            return
        print("Available loadouts:")
        for i, loadout_name in enumerate(self.loadouts.keys()):
            print(f"{i}. {loadout_name}")

    def load_loadout(self, loadout_index):
        try:
            loadout_index = int(loadout_index)
        except ValueError:
            print("Invalid loadout index. It must be an integer.")
            return None

        if loadout_index < 0 or loadout_index >= len(self.loadouts):
            print("Invalid loadout index.")
            return None

        loadout_name = list(self.loadouts.keys())[loadout_index]
        if loadout_name in self.loadouts:
            return self.loadouts[loadout_name]
        else:
            print("Loadout not found.")
            return None
    
    def resolve_bonus_value(self, base_value, item_level, rarity):
        return base_value * (item_level + 1) * (1.25 if rarity == "excellent" else 1)
    
    def resolve_bonus_name(self, bonus_key):
        return self.bonuses_data.get(bonus_key, bonus_key)
    
    def resolve_bonus_base_value(self, item, bonus_key):
        return next(bonus["Bonus per Level"] for bonus in item.get("Optional Bonuses", []) if bonus["Bonus Key"] == bonus_key)

    def calculate_bonuses_for_loadout(self, loadout_name):
        loadout = self.load_loadout(loadout_name)
        if loadout:
            total_bonuses = self.calculate_total_bonuses(loadout)
            print("\nTotal Bonuses for Loadout:")
            for bonus, value in total_bonuses.items():
                self.print_colored(f"{bonus}: {value}", '37')  # White for main bonuses

            print("\nItems in Loadout:")
            for slot, item_info in loadout.items():
                item = self.items_data[item_info['type']][item_info['name']]
                item_name = item_info['name']
                item_level = item_info['level']

                main_bonuses = ', '.join([f"{self.resolve_bonus_name(bonus['Bonus Key'])} \033[92m+{self.resolve_bonus_value(self. bonus['Bonus per Level'], item_level, item_info['rarity'])}\033[0m" for bonus in item.get('Main Bonuses', [])])
                optional_bonuses = ', '.join([f"{self.resolve_bonus_name(bonus_key)} \033[92m+{self.resolve_bonus_value(item, bonus_key)}\033[0m" for bonus_key in item_info.get('enabled_optional_bonuses', [])])

                # Determine color for item name
                if item_info.get('rarity') == 'excellent':
                    item_color_code = '32'  # Green
                elif 'options' in item:
                    if item_level >= 7:
                        item_color_code = '33'  # Yellow
                    else:
                        item_color_code = '34'  # Blue
                else:
                    item_color_code = '37'  # White

                # Construct the colored string
                slot_str = f"\033[37m{slot}: \033[0m"
                item_str = f"\033[{item_color_code}m{item_name} +{item_level}\033[0m"
                main_bonuses_str = f"\033[37m[{main_bonuses}]\033[0m"
                optional_bonuses_str = f"\033[94m({optional_bonuses})\033[0m"

                # Print the entire line
                print(f"{slot_str}{item_str} - {main_bonuses_str} {optional_bonuses_str}")

    def compare_loadouts(self, loadout_name_1, loadout_name_2):
        loadout_1 = self.load_loadout(loadout_name_1)
        loadout_2 = self.load_loadout(loadout_name_2)

        if loadout_1 and loadout_2:
            bonuses_1 = self.calculate_total_bonuses(loadout_1)
            bonuses_2 = self.calculate_total_bonuses(loadout_2)

            print(f"\nComparison between {loadout_name_1} and {loadout_name_2}:")
            all_bonuses = set(bonuses_1.keys()).union(set(bonuses_2.keys()))

            for bonus in all_bonuses:
                value_1 = bonuses_1.get(bonus, 0)
                value_2 = bonuses_2.get(bonus, 0)
                difference = value_2 - value_1
                percentage_difference = ((difference) / value_1 * 100) if value_1 != 0 else 100

                if percentage_difference > 0:
                    color_code = "92"  # Green for positive
                elif percentage_difference < 0:
                    color_code = "91"  # Red for negative
                else:
                    color_code = "93"  # Yellow for no difference

                self.print_colored(f"{bonus}: {percentage_difference:.2f}%", color_code)

def load_items_data():
    with open("armory.json", "r") as f:
        return json.load(f)

def load_bonuses_data():
    with open("bonuses.json", "r") as f:
        return json.load(f)

def main():
    items_data = load_items_data()
    bonuses_data = load_bonuses_data()

    manager = LoadoutManager(items_data, bonuses_data)
    manager.load_loadouts()

    while True:
        print("\nMenu:")
        print("1. Create new loadout")
        print("2. Display available loadouts")
        print("3. Calculate bonuses for a loadout")
        print("4. Compare two loadouts")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            manager.create_loadout()
        elif choice == "2":
            manager.display_loadouts()
        elif choice == "3":
            manager.display_loadouts()
            loadout_name = input("Enter the name of the loadout to calculate bonuses: ")
            manager.calculate_bonuses_for_loadout(loadout_name)
        elif choice == "4":
            manager.display_loadouts()
            loadout_name_1 = int(input("Enter the index of the first loadout: ")) - 1
            loadout_name_2 = int(input("Enter the index of the second loadout: ")) - 1
            manager.compare_loadouts(loadout_name_1, loadout_name_2)
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

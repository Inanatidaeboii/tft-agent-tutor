import pandas as pd
import json
from collections import Counter

class MetaEngine:
    def __init__(self, data_path="tft_challenger_data.json"):
        self.data_path = data_path
        self._load_data()

    def _load_data(self):
        try:
            with open(self.data_path, 'r') as f:
                self.raw_data = json.load(f)
            print(f"Data loaded successfully from {self.data_path}")
        except FileNotFoundError:
            self.raw_data = []
            print(f"Data file {self.data_path} not found. Starting with empty data.")

    def analyze_unit(self, unit_name: str):
        """
        Analyze a specific unit from the local match data.
        Returns: Pick Count, Top Items, Average Placement
        """

        unit_name_lower = unit_name.lower()

        relevent_units = []
        placements = []

        for match in self.raw_data:
            for unit in match.get('units', []):
                raw_name = unit.get('name', '').lower()

                if unit_name_lower in raw_name:
                    relevent_units.append(unit)
                    placements.append(match.get('placement', 8))
        
        count = len(relevent_units)

        if count == 0:
            return None
        
        avg_placement = sum(placements) / count

        all_items = []
        for u in relevent_units:
            all_items.extend(u.get('items', []))

        item_counts = Counter(all_items).most_common(5)

        return {
            "unit": unit_name,
            "sample_size": count,
            "average_placement": round(avg_placement, 2),
            "top_items": item_counts
        }
    
if __name__ == "__main__":
    engine = MetaEngine()
import pandas as pd
import json

class MetaEngine:
    def __init__(self, data_patch="tft_challenger_data.json"):
        with open(data_patch, 'r') as f:
            raw_data = json.load(f)
        
        self.df_units = self._flatten_units(raw_data)
        print(f"Loaded {len(self.df_units)} unit records from {data_patch}")

    def _flatten_units(self, raw_data):
        """Converts complex JSON structure into a flat DataFrame for easier analysis."""
        flat_list = []
        for match in raw_data:
            placement = match['placement']
            
            if placement <= 4:
                for unit in match['units']:
                    flat_list.append({
                        "units": unit['name'],
                        "items": unit['items'],
                        "tier": unit['tier'],
                        "placement": placement
                    })
        return pd.DataFrame(flat_list)
    
    def get_best_items(self, unit_name):
        """Returns the most common items for specific unit in top 4 matches"""
        
        unit_df = self.df_units[self.df_units['units'] == unit_name]

        if unit_df.empty:
            return f"No data found for {unit_name}"
        
        all_items = [item for sublist in unit_df['items'] for item in sublist]

        item_counts = pd.Series(all_items).value_counts().head(5)
        return item_counts.to_dict()

if __name__ == "__main__":
    engine = MetaEngine()
    print(engine.get_best_items("TFT16_Zoe"))
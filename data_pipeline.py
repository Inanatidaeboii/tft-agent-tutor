import json
from riot_api import get_challenger_players, get_match_ids_direct, crawl_matches

FILENAME = 'tft_challenger_data.json'
REGION = 'na1'
ROUTING = 'AMERICAS'

def run_pipeline():
    """
    Runs the full ETL process: Fetch Challengers -> Get Match IDs -> Crawl Matches -> Save JSON
    """
    print("Starting Riot Data Pipeline...")

    try:
        df = get_challenger_players(REGION)
        print(f"    - Found {len(df)} challengers.")

        match_ids = get_match_ids_direct(df.head(5), region_routing=ROUTING, matches_per_player=10)
        print(f"    - Retrieved {len(match_ids)} unique match IDs.")

        raw_data = crawl_matches(match_ids, region_routing=ROUTING)

        with open(FILENAME, 'w') as f:
            json.dump(raw_data, f)
        
        print(f"    Data refresh complete. Saved to {FILENAME}.")
    except Exception as e:
        print(f"    Error during pipeline execution: {e}")
        
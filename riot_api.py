from riotwatcher import TftWatcher
import pandas as pd
from dotenv import load_dotenv
import os
import time
import json
load_dotenv()

api_key = os.getenv("RIOT_API_KEY")
watcher = TftWatcher(api_key)
region = 'NA1'

def get_challenger_players(region):
    challenger_players = watcher.league.challenger(region)
    players = challenger_players['entries']

    sorted_players = sorted(players, key=lambda x: x['leaguePoints'], reverse=True)

    return pd.DataFrame(sorted_players)


def get_match_ids_direct(df, region_routing='AMERICAS', matchs_per_player=5):
    all_match_ids = set()

    target_puuids = df['puuid'].head(10).tolist()

    print("Fetching match IDs for top players...")
    for i, puuid in enumerate(target_puuids):
        try:
            matches = watcher.match.by_puuid(region_routing, puuid, count=matchs_per_player)
            all_match_ids.update(matches)
            print(f"Fetched matches for player {i+1}/{len(target_puuids)}")
            time.sleep(1)

        except Exception as e:
            print(f"Error fetching matches for puuid {puuid}: {e}")

    return list(all_match_ids)


def extract_match(match_id, match_detail):
    """
    Filters the raw Riot JSON to keep only what the AI needs.
    """

    processed_data = []

    participants = match_detail['info']['participants']
    for player in participants:
        player_stats = {
            "puuid": player['puuid'],
            "match_id": match_id,
            "placement": player['placement'],
            "level": player['level'],
            "traits": [],
            "units": []
        }
        for trait in player.get('traits', []):
            if trait.get('tier_current', 0) > 0:
                player_stats['traits'].append({
                    "name": trait.get('name', 'Unknown'),
                    "num_units": trait.get('num_units', 0),
                    "tier": trait.get('tier_current', 0)
                })
        for unit in player.get('units', []):
            unit_items = unit.get('itemNames', []) 
            
            player_stats['units'].append({
                "name": unit.get('character_id', 'Unknown_Unit'),
                "tier": unit.get('tier', 1),
                "items": unit_items 
        })
        processed_data.append(player_stats)
    return processed_data

def crawl_matches(match_ids, region_routing='AMERICAS'):
    dataset = []
    total = len(match_ids)
    print("Crawling match details...")

    for i, match_id in enumerate(match_ids):
        try:
            match_detail = watcher.match.by_id(region_routing, match_id)
            
            cleaned_data = extract_match(match_id, match_detail)
            dataset.extend(cleaned_data)
            print(f"Crawled match {i+1}/{total}")
            time.sleep(1)
        except Exception as e:
            print(f"Error fetching match {match_id}: {e}")
    
    return dataset

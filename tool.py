import pandas as pd
from langchain_core.tools import tool

try:
    df = pd.read_csv('unit_info.csv')
    df = df.astype(str) 
except FileNotFoundError:
    print("Error: unit_info.csv not found. Please generate it first.")
    df = pd.DataFrame()

try:
    item_df = pd.read_csv('metatft_items_final.csv')
    item_df = item_df.astype(str) 
except FileNotFoundError:
    print("Error: Item CSV not found. Please ensure the scraper ran successfully.")
    item_df = pd.DataFrame()

@tool
def search_unit_info(query: str) -> str:
    """
    Search for TFT unit information by name, trait, or role. 
    Useful when you need to find stats, abilities, or costs for specific units.
    
    Args:
        query: The name of the unit (e.g., 'Ahri') or a trait (e.g., 'Void').
    """
    if df.empty:
        return "Error: Database is empty."

    query = query.lower()
    
    mask = (
        df['Name'].str.lower().str.contains(query) | 
        df['Traits'].str.lower().str.contains(query) |
        df['Role'].str.lower().str.contains(query)
    )
    
    results = df[mask]
    
    if results.empty:
        return f"No units found matching '{query}'."
    
    return results.to_json(orient="records")

@tool
def search_item_info(query: str) -> str:
    """
    Search for TFT item statistics and recommendations.
    Useful for finding item Win Rates, Tiers, or finding the best items for a specific champion.
    
    Args:
        query: The name of the item (e.g., 'Guinsoo') or a champion name (e.g., 'Seraphine').
    """
    if item_df.empty:
        return "Error: Item database is empty."

    query = query.lower()

    mask = (
        item_df['Item'].str.lower().str.contains(query) | 
        item_df['Best Users'].str.lower().str.contains(query)
    )
    
    results = item_df[mask]
    
    if results.empty:
        return f"No items found matching '{query}'."
    
    return results.to_json(orient="records")
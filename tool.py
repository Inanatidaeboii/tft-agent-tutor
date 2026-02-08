import pandas as pd
from langchain_core.tools import tool

try:
    df = pd.read_csv('unit_info.csv')
    df = df.astype(str) 
except FileNotFoundError:
    print("Error: unit_info.csv not found. Please generate it first.")
    df = pd.DataFrame()

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
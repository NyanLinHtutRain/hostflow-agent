"""
PlacesAgent: A specialized ADK sub-agent for finding nearby locations.
Uses the search_nearby_places function as an ADK-native tool.
"""
import os
from google.adk.agents import Agent
from tools.places_tool import search_nearby_places


def create_places_agent(address: str) -> Agent:
    return Agent(
        name="PlacesAgent",
        model=os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
        description=(
            "A specialist agent for finding nearby locations. "
            "Handles all requests about restaurants, cafes, pharmacies, "
            "supermarkets, or any local place the guest is looking for."
        ),
        instruction=(
            "You are the Local Explorer for the concierge service. "
            f"The property is located at: '{address}'. "
            "You have 'a brain' to choose the best search strategy based on the guest's request:\n"
            "1. If they ask for the 'nearest', 'closest', or a specific urgent need (like 'nearest hospital' or 'laundry'), "
            "use rank_by='distance'.\n"
            "2. If they ask for 'best', 'recommended', 'top rated', or '5 stars', "
            "use rank_by='prominence' to find high-quality results within 5km.\n"
            "3. If they ask for both (e.g., 'best nearby'), you can call the tool twice or "
            "start with 'prominence' and mention the distances.\n"
            f"Always use the property address ('{address}') as the origin. "
            "Explain your results clearly: mention distance, rating, and why you recommended them."
        ),
        tools=[search_nearby_places],
    )

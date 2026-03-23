"""
MCP Tool: search_nearby_places
Calls the Google Places API to find real nearby locations.
Defined as a plain Python function — ADK handles the MCP wrapping automatically.
"""
import os
import httpx


async def search_nearby_places(query: str, address: str, rank_by: str = "distance") -> dict:
    """
    Search for nearby places (restaurants, coffee shops, pharmacies, etc.)
    given a query type and the property's address.

    Args:
        query: The type of place to search for (e.g., 'coffee', 'pizza', 'pharmacy')
        address: The property address to use as the search origin
        rank_by: How to rank results. Options: 'distance' (default) or 'prominence'.
                 Note: 'prominence' uses a fixed 5km radius to find high-quality results.

    Returns:
        A dict with a list of nearby places and their details.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    print(f"[SERVERLESS AGENT ACTION] -> Places tool called for: '{query}' near '{address}' (Ranking: {rank_by})")

    if not api_key:
        # Graceful mock for demo/development without a key
        return {
            "status": "mock",
            "results": [
                {"name": f"Joe's Local {query.title()} Shop", "distance": "0.2 km", "rating": 4.8, "address": "123 Demo Street"},
                {"name": f"Downtown {query.title()} Bar", "distance": "0.5 km", "rating": 4.5, "address": "456 Example Ave"},
            ]
        }

    # Geocode the address first to get lat/lng
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json"
    async with httpx.AsyncClient() as client:
        # Strategy: Try full address first, then fallback to parts (like postal code)
        geo_resp = await client.get(geocode_url, params={"address": address, "key": api_key})
        geo_data = geo_resp.json()
        
        if geo_data.get("status") != "OK":
            print(f"[RETRY] Geocoding failed for: '{address}'. Trying fallback...")
            # Simple fallback: take the last part (often postal code) or middle parts
            parts = address.split(",")
            # Add 'Singapore' to fallback if it's not already there
            fallback_address = f"{parts[-1].strip()}, Singapore" if len(parts) > 1 else f"{address}, Singapore"
            geo_resp = await client.get(geocode_url, params={"address": fallback_address, "key": api_key})
            geo_data = geo_resp.json()

        if geo_data.get("status") != "OK":
            status = geo_data.get("status")
            print(f"[ERROR] Geocoding failed again for fallback: '{address}'")
            return {"status": "error", "message": f"Could not geocode address. API Status: {status}"}

        location = geo_data["results"][0]["geometry"]["location"]
        lat, lng = location["lat"], location["lng"]

        # Search for nearby places
        places_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        params = {
            "location": f"{lat},{lng}",
            "keyword": query,
            "key": api_key
        }

        if rank_by == "distance":
            params["rankby"] = "distance"
        else:
            params["rankby"] = "prominence"
            params["radius"] = 5000  # 5km radius for prominence searches

        places_resp = await client.get(places_url, params=params)
        places_data = places_resp.json()

    results = []
    for place in places_data.get("results", [])[:5]: # Return up to 5 results
        results.append({
            "name": place.get("name"),
            "address": place.get("vicinity"),
            "rating": place.get("rating"),
            "user_ratings_total": place.get("user_ratings_total"),
            "open_now": place.get("opening_hours", {}).get("open_now"),
        })

    return {"status": "success", "results": results}

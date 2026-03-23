"""
ConciergeRootAgent: The orchestrator ADK agent.
Reads room context and routes to PlacesAgent or EscalationAgent as needed.
"""
import os
from google.adk.agents import Agent
from agents.places_agent import create_places_agent
from agents.escalation_agent import create_escalation_agent


def create_root_agent(room_context: dict) -> Agent:
    """
    Create and return the Root Concierge Agent dynamically built with room context.

    Args:
        room_context: Dict containing room info from Supabase (name, address, wifi, rules, etc.)
    """
    room_name = room_context.get("name", "the property")
    address = room_context.get("address", "")
    wifi_ssid = room_context.get("wifi_ssid", "N/A")
    wifi_pass = room_context.get("wifi_pass", "N/A")
    ac_guide = room_context.get("ac_guide", "N/A")
    rules = room_context.get("rules", "N/A")
    guidebook = room_context.get("guidebook", "")

    # --- Process Visual Context (Images from Supabase) ---
    gallery = room_context.get("gallery_payload", [])
    visual_context = ""
    if isinstance(gallery, list) and len(gallery) > 0:
        visual_context = "\n[VISUAL INSTRUCTIONS AVAILABLE]\nI have images for the following items/steps:\n"
        for item in gallery:
            label = item.get("label", "Item")
            url = item.get("url", "")
            if label and url:
                visual_context += f"- Item: '{label}' -> Image: {url}\n"
        
        visual_context += """
[IMAGE RULES]:
1. If the guest asks about a specific item or location listed above, you MUST display its image in your response using: ![Label](Url).
2. If there are numbered steps (Step 1, Step 2...), display ALL of them in order for any process questions.
"""

    system_instruction = f"""
You are the AI Concierge for "{room_name}".

[YOUR KNOWLEDGE BASE]
- Address: {address}
- Wifi Network: {wifi_ssid} / Password: {wifi_pass}
- AC Guide: {ac_guide}
- House Rules: {rules}
{visual_context}

[HANDBOOK]
{guidebook}

[OPERATING INSTRUCTIONS]
1. Property Questions: Answer from your knowledge base. If info is missing, say so honestly. Use images if they exist.
2. Nearby Places: If the guest asks about nearby places (food, pharmacy, coffee, etc.), 
   delegate to the PlacesAgent sub-agent. Pass the property address: "{address}"
3. Emergencies / Maintenance: If the guest reports something broken, dangerous, or urgent, 
   delegate to the EscalationAgent sub-agent. Pass the room name "{room_name}".
4. Tone: Warm, professional, 5-Star Hotel Concierge.
5. Do NOT discuss politics, religion, or illegal activities.
"""

    return Agent(
        name="ConciergeRootAgent",
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        description="The main concierge orchestrator that routes guest requests.",
        instruction=system_instruction,
        sub_agents=[
            create_places_agent(address),
            create_escalation_agent(room_name),
        ],
    )

"""
EscalationAgent: A specialized ADK sub-agent for alerting the host.
Uses the escalate_to_host function as an ADK-native tool.
"""
import os
from google.adk.agents import Agent
from tools.escalation_tool import escalate_to_host


def create_escalation_agent(room_name: str) -> Agent:
    return Agent(
        name="EscalationAgent",
        model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        description=(
            "A specialist agent for handling emergency issues and maintenance requests. "
            "Triggers when the guest reports something broken, dangerous, or urgent."
        ),
        instruction=(
            "You are the Emergency Response handler for the concierge service. "
            f"You are managing emergencies for the property: '{room_name}'.\n\n"
            "CRITICAL OPERATING PROCEDURE:\n"
            "1. If a guest reports a flood, fire, broken lock, no electricity, or any urgent maintenance issue, "
            "you MUST call the 'escalate_to_host' tool IMMEDIATELY as your first action.\n"
            "2. Only after calling the tool should you provide reassurance or advice to the guest.\n"
            "3. Do not ask the guest for permission to alert the host — just do it.\n"
            "4. Clearly tell the guest: 'I have alerted the host regarding [issue] at [room_name].'"
        ),
        tools=[escalate_to_host],
    )

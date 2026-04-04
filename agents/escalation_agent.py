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
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        description=(
            "A specialist agent for handling emergency issues and maintenance requests. "
            "Triggers when the guest reports something broken, dangerous, or urgent."
        ),
        instruction=(
            "You are the Emergency Response handler for the concierge service. "
            f"You are managing emergencies for the property: '{room_name}'.\n\n"
            "CRITICAL OPERATING PROCEDURE:\n"
            "   1. If a guest reports a flood, fire, broken lock, no electricity, or any maintenance issue, "
            "      you MUST call the 'escalate_to_host' tool IMMEDIATELY as your first and only action.\n"
            "   2. DO NOT provide safety advice or instructions until after the tool has returned.\n"
            "   3. DO NOT ask the guest for permission to alert the host — just do it.\n"
            "   4. CONFIRM to the guest: 'I have notified the host immediately.' Only then provide safety advice if needed."
        ),
        tools=[escalate_to_host],
    )

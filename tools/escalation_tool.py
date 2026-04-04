"""
MCP Tool: escalate_to_host
Fires a Telegram message to the host's account with a severity badge.
Defined as a plain Python function — ADK handles the MCP wrapping automatically.
"""
import os
import httpx

SEVERITY_EMOJI = {
    "LOW": "ℹ️",
    "MODERATE": "⚠️",
    "CRITICAL": "🚨",
}


async def escalate_to_host(issue: str, severity: str, room_name: str) -> dict:
    """
    Sends an emergency alert to the host via Telegram with a severity level.

    Args:
        issue: A short description of the problem the guest reported.
        severity: The urgency level — must be 'LOW', 'MODERATE', or 'CRITICAL'.
        room_name: The name of the room/property where the issue occurred.

    Returns:
        A dict with success or failure status.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    severity = severity.upper()
    emoji = SEVERITY_EMOJI.get(severity, "⚠️")

    message = (
        f"{emoji} *HostFlow Alert* [{severity}]\n\n"
        f"*Property:* {room_name}\n"
        f"*Issue:* {issue}\n\n"
        f"_Please check in with your guest immediately._"
    )

    print(f"[SERVERLESS AGENT ACTION] 🚨 TELEGRAM ALERT FIRED! [{severity}] {issue}")

    if not bot_token or not chat_id:
        print(f"[MOCK TELEGRAM] Would have sent: {message}")
        return {
            "status": "mock",
            "message": f"Mock alert sent. Severity: {severity}. In production, this fires to your Telegram."
        }

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        })

    if resp.status_code == 200:
        return {"status": "success", "message": "The host has been alerted via Telegram."}
    else:
        return {"status": "error", "message": f"Telegram API returned {resp.status_code}"}

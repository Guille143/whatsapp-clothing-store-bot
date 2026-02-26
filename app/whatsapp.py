import httpx

GRAPH_API_BASE = "https://graph.facebook.com/v20.0"

async def send_text_message(*, token: str, phone_number_id: str, to: str, text: str) -> None:
    url = f"{GRAPH_API_BASE}/{phone_number_id}/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text},
    }

    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(url, headers=headers, json=payload)
        r.raise_for_status()

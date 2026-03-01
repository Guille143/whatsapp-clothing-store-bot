import os
from fastapi import FastAPI, Request, Response, HTTPException
from dotenv import load_dotenv

from app.whatsapp import send_text_message
from app.flows import route_message, MENU
from app.storage import init_db, get_handoff, set_handoff, log_message

load_dotenv()

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")

app = FastAPI(title="WhatsApp Clothing Store Bot")

@app.on_event("startup")
def _startup():
    init_db()

@app.get("/webhook")
def verify_webhook(request: Request):
    # Meta webhook verification handshake: return hub.challenge if token matches :contentReference[oaicite:2]{index=2}
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN and challenge:
        return Response(content=challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Webhook verification failed")

from fastapi import FastAPI, Request, Response, HTTPException
import json
import os

@app.post("/webhook")
async def receive_webhook(payload: dict):
    # 1) Log crudo (así vemos qué llega)
    print("=== INCOMING WEBHOOK ===")
    print(json.dumps(payload, ensure_ascii=False)[:4000])  # recorta para no explotar logs

    # 2) Ignorar statuses (no son mensajes)
    try:
        entry = payload.get("entry", [])
        if not entry:
            return {"ok": True}

        changes = entry[0].get("changes", [])
        if not changes:
            return {"ok": True}

        value = changes[0].get("value", {})

        # Si es status update, salimos
        if "statuses" in value and "messages" not in value:
            print("Webhook status update (ignored)")
            return {"ok": True}

        messages = value.get("messages", [])
        if not messages:
            print("No messages key found (ignored)")
            return {"ok": True}

        msg = messages[0]
        from_number = msg.get("from")
        msg_type = msg.get("type")

        text_body = None
        if msg_type == "text":
            text_body = msg.get("text", {}).get("body")

        print(f"Parsed message -> from={from_number} type={msg_type} text={text_body}")

        if not from_number:
            return {"ok": True}

        # 3) Si no es texto, respondemos algo corto
        if not text_body:
            await send_text_message(from_number, "👋 Por ahora solo entiendo mensajes de texto. Mandame 'menu'.")
            return {"ok": True}

        # 4) Ruteo principal
        reply = route_message(from_number, text_body)  # si es async, poné await
        await send_text_message(from_number, reply)
        return {"ok": True}

    except Exception as e:
        print("ERROR processing webhook:", repr(e))
        return {"ok": True}


@app.get("/")
def health():
    return {"status": "up", "hint": "Use /webhook for Meta verification and messages", "menu_preview": MENU}

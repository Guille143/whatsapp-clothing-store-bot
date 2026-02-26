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

@app.post("/webhook")
async def receive_webhook(payload: dict):
    """
    WhatsApp Cloud API manda eventos por POST (messages, statuses, etc.)
    Nosotros respondemos solo cuando llega un mensaje de usuario.
    """
    try:
        entry = payload.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        if not messages:
            return {"ok": True}  # statuses u otros eventos

        msg = messages[0]
        from_phone = msg.get("from")  # teléfono del cliente
        text = (msg.get("text") or {}).get("body", "")

        log_message(from_phone, "in", text)

        # si está derivado a humano, no respondemos automático
        if get_handoff(from_phone):
            return {"ok": True, "handoff": True}

        reply = route_message(text)
        if reply.handoff:
            set_handoff(from_phone, True)

        await send_text_message(
            token=WHATSAPP_TOKEN,
            phone_number_id=PHONE_NUMBER_ID,
            to=from_phone,
            text=reply.text
        )
        log_message(from_phone, "out", reply.text)
        return {"ok": True}
    except Exception as e:
        # para debug en Render/Railway se ve en logs
        return {"ok": False, "error": str(e)}

@app.get("/")
def health():
    return {"status": "up", "hint": "Use /webhook for Meta verification and messages", "menu_preview": MENU}

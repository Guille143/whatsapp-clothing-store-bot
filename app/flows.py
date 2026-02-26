from dataclasses import dataclass

@dataclass
class BotReply:
    text: str
    handoff: bool = False

MENU = (
    "👕 *Tienda de Ropa*\n"
    "Elegí una opción:\n"
    "1) Ver catálogo\n"
    "2) Consultar talle/stock\n"
    "3) Envíos\n"
    "4) Cambios y devoluciones\n"
    "5) Hablar con asesor\n\n"
    "Escribí el número (1-5)."
)

def normalize(msg: str) -> str:
    return (msg or "").strip().lower()

def route_message(user_text: str) -> BotReply:
    t = normalize(user_text)

    # keywords para derivar
    if any(k in t for k in ["asesor", "humano", "persona", "hablar con alguien"]):
        return BotReply("Dale 🙌 En breve te atiende un asesor. Mientras tanto, ¿qué necesitás?", handoff=True)

    if t in ["menu", "menú", "0", "volver"]:
        return BotReply(MENU)

    if t == "1":
        return BotReply(
            "📦 *Catálogo*\n"
            "A) Remeras\nB) Buzos\nC) Pantalones\nD) Camperas\n\n"
            "Respondé con A/B/C/D."
        )

    if t in ["a", "remeras"]:
        return BotReply("Remeras: RM101 (S-M-L), RM205 (M-L-XL). Escribí el código + talle. Ej: RM101 M")

    if t == "2":
        return BotReply("Decime *código + talle*. Ej: RM101 M")

    if t == "3":
        return BotReply("🚚 Envíos: a coordinar. También podés retirar en el local. ¿De qué zona sos?")

    if t == "4":
        return BotReply("🔁 Cambios: dentro de 10 días con etiqueta y ticket. ¿Querés cambiar por talle o por otro modelo?")

    if t == "5":
        return BotReply("Perfecto 🙌 Te paso con un asesor.", handoff=True)

    return BotReply("No te entendí del todo 😅 Escribí *menu* para ver opciones.")

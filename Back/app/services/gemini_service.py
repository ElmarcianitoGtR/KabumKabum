"""
Servicio Gemini — traducción ES/EN/Náhuatl, resumen de documentos y chatbot.
"""

from typing import Optional
from app.core.config import get_settings

settings = get_settings()

try:
    import google.generativeai as genai
    genai.configure(api_key=settings.gemini_api_key)
    model = genai.GenerativeModel(settings.gemini_model)
    GEMINI_AVAILABLE = bool(settings.gemini_api_key)
except ImportError:
    GEMINI_AVAILABLE = False
    model = None


# ─────────────────────────────────────────────────
#  HELPER INTERNO
# ─────────────────────────────────────────────────

async def _ask_gemini(prompt: str, max_tokens: int = 1024) -> str:
    if not GEMINI_AVAILABLE or model is None:
        return "[Gemini no configurado — agrega GEMINI_API_KEY en .env]"
    try:
        response = await model.generate_content_async(
            prompt,
            generation_config={"max_output_tokens": max_tokens},
        )
        return response.text.strip()
    except Exception as e:
        return f"[Error Gemini: {e}]"


# ─────────────────────────────────────────────────
#  TRADUCCIÓN
# ─────────────────────────────────────────────────

LANG_NAMES = {
    "es":  "español",
    "en":  "English",
    "nah": "Náhuatl clásico (con transliteración moderna)",
}

async def translate(text: str, target_lang: str) -> str:
    """Traduce un texto al idioma indicado (es / en / nah)."""
    lang_name = LANG_NAMES.get(target_lang, target_lang)
    prompt = (
        f"Traduce el siguiente texto al {lang_name}. "
        f"Solo devuelve la traducción, sin explicaciones.\n\n"
        f"Texto: {text}"
    )
    return await _ask_gemini(prompt)


async def translate_all(text: str) -> dict:
    """Traduce a los 3 idiomas del sistema."""
    return {
        "es":  await translate(text, "es"),
        "en":  await translate(text, "en"),
        "nah": await translate(text, "nah"),
    }


# ─────────────────────────────────────────────────
#  RESUMEN DE DOCUMENTOS
# ─────────────────────────────────────────────────

async def summarize_document(content: str, lang: str = "es") -> str:
    """Genera un resumen técnico de un documento del reactor."""
    lang_name = LANG_NAMES.get(lang, lang)
    prompt = (
        f"Eres un experto en ingeniería nuclear. "
        f"Resume el siguiente documento técnico en {lang_name}, "
        f"en máximo 5 puntos clave. Sé conciso y preciso.\n\n"
        f"Documento:\n{content[:4000]}"  # límite de contexto
    )
    return await _ask_gemini(prompt, max_tokens=512)


async def summarize_all_langs(content: str) -> dict:
    """Genera resumen en los 3 idiomas."""
    return {
        "es":  await summarize_document(content, "es"),
        "en":  await summarize_document(content, "en"),
        "nah": await summarize_document(content, "nah"),
    }


# ─────────────────────────────────────────────────
#  RECOMENDACIÓN BASADA EN ANÁLISIS
# ─────────────────────────────────────────────────

async def generate_recommendation(
    alert_level: str,
    life_score: float,
    fault_prob: float,
    operating_state: str,
    lang: str = "es",
) -> str:
    """
    Genera una recomendación técnica basada en los resultados
    de la red bayesiana + Mamdani.
    """
    lang_name = LANG_NAMES.get(lang, lang)
    prompt = (
        f"Eres un experto en seguridad de reactores nucleares. "
        f"En base a los siguientes datos, genera una recomendación técnica "
        f"clara y concisa en {lang_name} (máximo 3 oraciones):\n\n"
        f"- Nivel de alerta: {alert_level}\n"
        f"- Puntuación de vida útil: {life_score:.1f}/100\n"
        f"- Probabilidad de fallo: {fault_prob*100:.1f}%\n"
        f"- Estado operativo: {operating_state}\n"
    )
    return await _ask_gemini(prompt, max_tokens=256)


# ─────────────────────────────────────────────────
#  CHATBOT TÉCNICO
# ─────────────────────────────────────────────────

async def chat(
    user_message: str,
    history: list,
    lang: str = "es",
) -> str:
    """
    Chatbot especializado en reactores nucleares.
    history: lista de dicts {"role": "user"/"model", "parts": [texto]}
    """
    if not GEMINI_AVAILABLE or model is None:
        return "[Chatbot no disponible — configura GEMINI_API_KEY]"

    lang_name = LANG_NAMES.get(lang, lang)
    system_prompt = (
        f"Eres ReactorGuard AI, asistente especializado en monitoreo y "
        f"mantenimiento de reactores nucleares. Responde siempre en {lang_name}. "
        f"Sé técnico, preciso y conciso. No inventes datos."
    )

    try:
        chat_session = model.start_chat(history=history)
        full_message = f"{system_prompt}\n\nUsuario: {user_message}"
        response = await chat_session.send_message_async(full_message)
        return response.text.strip()
    except Exception as e:
        return f"[Error chatbot: {e}]"

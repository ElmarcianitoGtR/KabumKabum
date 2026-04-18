"""
Servicio Gemini — traducción ES/EN/Náhuatl, resumen de documentos y chatbot.
Integra el procesador de manuales de tu compañera.
"""

import os
import json
from typing import Optional
from app.core.config import get_settings

settings = get_settings()

# ── Imports de Gemini ──────────────────────────────────────────────────────
try:
    from google import genai
    from google.genai import types
    client = genai.Client(api_key=settings.gemini_api_key)
    GEMINI_AVAILABLE = bool(settings.gemini_api_key)
except ImportError:
    GEMINI_AVAILABLE = False
    client = None

MODEL_NAME = "gemini-2.5-flash"
MAX_CHARS  = 12000

IDIOMAS = {
    "es":  "español",
    "en":  "inglés",
    "nah": "náhuatl"
}

# ═══════════════════════════════════════════════════════
#  GLOSARIO NÁHUATL (de tu compañera)
# ═══════════════════════════════════════════════════════

def crear_glosario_nahuatl_base() -> dict:
    return {
        "seguridad": "netlapializtli",
        "protección": "netlapializtli",
        "riesgo": "ouihcayotl",
        "peligro": "ouihcayotl",
        "vigilancia": "tlapializtli",
        "monitoreo": "tlapializtli",
        "norma": "tlanahuatilli",
        "procedimiento": "tlanahuatilli",
        "inspección": "tlachializtli",
        "medición": "tlatamachihualiztli",
        "error": "ahcuallotl",
        "fallo": "ahcuallotl",
        "anomalía": "ahcuallotl",
        "sensor": "tepoztli",
        "máquina": "tepoztli",
        "planta": "tepozcalli",
        "trabajador": "tequitqui",
        "operador": "tlachihuani",
        "supervisor": "tlapiani",
        "fuego": "tletl",
        "calor": "totoncayotl",
        "temperatura": "totoncayotl",
        "agua": "atl",
        "aire": "ehecatl",
        "energía": "chicahualiztli",
        "datos": "tlapohualiztli",
        "análisis": "tlayolteohuiliztli",
        "reactor": "yollotl",
        "núcleo": "yollotl",
        "enfriamiento": "cehualiztli",
        "inteligencia artificial": "tepozixtlamatiliztli",
    }


def cargar_glosario_nahuatl(ruta: str = "glosario_nahuatl.json") -> dict:
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    return crear_glosario_nahuatl_base()


def construir_bloque_glosario(glosario: dict) -> str:
    return "\n".join([f"- {es} -> {nah}" for es, nah in glosario.items()])


# ═══════════════════════════════════════════════════════
#  UTILIDADES DE TEXTO
# ═══════════════════════════════════════════════════════

def dividir_texto(texto: str, max_chars: int = MAX_CHARS) -> list:
    texto = texto.strip()
    if not texto:
        return []
    chunks = []
    inicio = 0
    while inicio < len(texto):
        fin = inicio + max_chars
        if fin < len(texto):
            corte = texto.rfind("\n", inicio, fin)
            if corte == -1:
                corte = texto.rfind(" ", inicio, fin)
            if corte == -1:
                corte = fin
        else:
            corte = len(texto)
        chunk = texto[inicio:corte].strip()
        if chunk:
            chunks.append(chunk)
        inicio = corte
    return chunks


# ═══════════════════════════════════════════════════════
#  HELPER GEMINI
# ═══════════════════════════════════════════════════════

def _generar_texto(prompt: str, response_mime_type: str = None, temperature: float = 0.2) -> str:
    if not GEMINI_AVAILABLE or client is None:
        return "[Gemini no configurado — agrega GEMINI_API_KEY en .env]"
    try:
        config_kwargs = {"temperature": temperature}
        if response_mime_type:
            config_kwargs["response_mime_type"] = response_mime_type

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(**config_kwargs)
        )
        if not response.text:
            raise ValueError("Respuesta vacía del modelo")
        return response.text.strip()
    except Exception as e:
        return f"[Error Gemini: {e}]"


async def _ask_gemini(prompt: str) -> str:
    """Versión async para el chatbot."""
    return _generar_texto(prompt)


# ═══════════════════════════════════════════════════════
#  RESUMEN DE DOCUMENTOS (código de tu compañera)
# ═══════════════════════════════════════════════════════

def _prompt_resumen(chunk: str) -> str:
    return f"""
Eres un analista experto en seguridad industrial y nuclear.

Extrae únicamente información EXPLÍCITA del documento.
No agregues conocimientos externos ni inferencias.

Devuelve SOLO JSON válido con esta estructura exacta:
{{
  "riesgos": [],
  "protocolos": [],
  "emergencias": [],
  "nivel_riesgo": ""
}}

Reglas:
- Usa solo información presente en el documento.
- "nivel_riesgo" debe ser uno de: ["bajo", "medio", "alto", "crítico"].
- No escribas nada fuera del JSON.

Documento:
{chunk}
"""

def _prompt_integracion_resumen(resumenes_json: list) -> str:
    return f"""
Integra los siguientes JSON parciales en un único JSON consolidado.
No inventes información nueva. Elimina duplicados.

Devuelve SOLO JSON válido con esta estructura exacta:
{{
  "riesgos": [],
  "protocolos": [],
  "emergencias": [],
  "nivel_riesgo": ""
}}

JSON parciales:
{chr(10).join(resumenes_json)}
"""

def resumir_documento(texto: str) -> dict:
    """Genera resumen estructurado del documento en JSON."""
    chunks = dividir_texto(texto, MAX_CHARS)
    if not chunks:
        raise ValueError("Texto vacío")

    resumenes = []
    for i, chunk in enumerate(chunks, 1):
        print(f"Resumiendo bloque {i}/{len(chunks)}...")
        salida = _generar_texto(_prompt_resumen(chunk), "application/json", 0.1)
        try:
            resumenes.append(json.loads(salida))
        except json.JSONDecodeError:
            resumenes.append({"riesgos": [], "protocolos": [], "emergencias": [], "nivel_riesgo": "medio"})

    if len(resumenes) == 1:
        return resumenes[0]

    # Integrar múltiples bloques
    resumenes_json = [json.dumps(r, ensure_ascii=False) for r in resumenes]
    salida_final = _generar_texto(_prompt_integracion_resumen(resumenes_json), "application/json", 0.1)
    try:
        return json.loads(salida_final)
    except json.JSONDecodeError:
        return resumenes[0]


# ═══════════════════════════════════════════════════════
#  TRADUCCIÓN DE DOCUMENTOS (código de tu compañera)
# ═══════════════════════════════════════════════════════

def _prompt_traduccion(chunk: str, idioma_destino: str, glosario: dict = None) -> str:
    nombre_idioma = IDIOMAS[idioma_destino]
    reglas_extra = ""
    bloque_glosario = ""

    if idioma_destino == "nah":
        reglas_extra = """
- Usa un estilo claro y comprensible.
- Si un término técnico no tiene equivalente en náhuatl, conserva el término en español.
- Si un término aparece en el glosario, úsalo como referencia prioritaria.
"""
        if glosario:
            bloque_glosario = f"\nGLOSARIO PREFERIDO:\n{construir_bloque_glosario(glosario)}"

    return f"""
Eres un traductor técnico especializado en manuales de seguridad industrial y nuclear.

Traduce el siguiente texto al idioma: {nombre_idioma}.

Reglas:
- Mantén el significado técnico exacto.
- No resumas ni expliques.
- Conserva listas, numeración y estructura.
{reglas_extra}
{bloque_glosario}
- Devuelve SOLO la traducción final.

Texto:
{chunk}
"""

def _prompt_unificacion(texto: str, idioma_destino: str, glosario: dict = None) -> str:
    nombre_idioma = IDIOMAS[idioma_destino]
    bloque_glosario = ""
    if idioma_destino == "nah" and glosario:
        bloque_glosario = f"\nRespeta estas equivalencias:\n{construir_bloque_glosario(glosario)}"

    return f"""
Revisa la siguiente traducción al {nombre_idioma}.
- Unifica terminología técnica
- Corrige inconsistencias menores
- Mantén el sentido exacto
- No resumas ni agregues contenido
{bloque_glosario}

Devuelve SOLO la versión final corregida.

Texto:
{texto}
"""

def traducir_documento(texto: str, idioma_destino: str) -> str:
    """Traduce un documento completo al idioma indicado (es/en/nah)."""
    if idioma_destino not in IDIOMAS:
        raise ValueError(f"Idioma no válido: {idioma_destino}")

    glosario = cargar_glosario_nahuatl() if idioma_destino == "nah" else None
    chunks   = dividir_texto(texto, MAX_CHARS)

    traducciones = []
    for i, chunk in enumerate(chunks, 1):
        print(f"Traduciendo bloque {i}/{len(chunks)}...")
        traduccion = _generar_texto(_prompt_traduccion(chunk, idioma_destino, glosario))
        traducciones.append(traduccion)

    traduccion_unida = "\n\n".join(traducciones)

    print("Unificando estilo final...")
    return _generar_texto(_prompt_unificacion(traduccion_unida, idioma_destino, glosario), temperature=0.1)


async def summarize_all_langs(texto: str) -> dict:
    """Genera resumen en los 3 idiomas."""
    resumen = resumir_documento(texto)
    resumen_str = json.dumps(resumen, ensure_ascii=False)
    return {
        "es":      resumen_str,
        "en":      traducir_documento(resumen_str, "en"),
        "nah":     traducir_documento(resumen_str, "nah"),
        "json":    resumen,
    }


# ═══════════════════════════════════════════════════════
#  RECOMENDACIÓN BASADA EN ANÁLISIS
# ═══════════════════════════════════════════════════════

async def generate_recommendation(
    alert_level: str,
    life_score: float,
    fault_prob: float,
    operating_state: str,
    lang: str = "es",
) -> str:
    lang_name = IDIOMAS.get(lang, "español")
    prompt = (
        f"Eres un experto en seguridad de reactores nucleares. "
        f"Genera una recomendación técnica clara en {lang_name} (máximo 3 oraciones):\n\n"
        f"- Nivel de alerta: {alert_level}\n"
        f"- Puntuación de vida útil: {life_score:.1f}/100\n"
        f"- Probabilidad de fallo: {fault_prob*100:.1f}%\n"
        f"- Estado operativo: {operating_state}\n"
    )
    return await _ask_gemini(prompt)


# ═══════════════════════════════════════════════════════
#  TRADUCCIÓN SIMPLE (para el chatbot)
# ═══════════════════════════════════════════════════════

async def translate(text: str, target_lang: str) -> str:
    lang_name = IDIOMAS.get(target_lang, target_lang)
    prompt = (
        f"Traduce el siguiente texto al {lang_name}. "
        f"Solo devuelve la traducción, sin explicaciones.\n\nTexto: {text}"
    )
    return await _ask_gemini(prompt)


async def translate_all(text: str) -> dict:
    return {
        "es":  await translate(text, "es"),
        "en":  await translate(text, "en"),
        "nah": await translate(text, "nah"),
    }


# ═══════════════════════════════════════════════════════
#  CHATBOT TÉCNICO
# ═══════════════════════════════════════════════════════

async def chat(user_message: str, history: list, lang: str = "es") -> str:
    """Chatbot especializado en reactores nucleares."""
    if not GEMINI_AVAILABLE or client is None:
        return "[Chatbot no disponible — configura GEMINI_API_KEY en .env]"

    lang_name = IDIOMAS.get(lang, "español")

    try:
        chat_session = client.chats.create(model=MODEL_NAME)
        system = (
            f"Eres ReactorGuard AI, asistente especializado en monitoreo "
            f"y mantenimiento de reactores nucleares. "
            f"Responde siempre en {lang_name}. Sé técnico, preciso y conciso."
        )
        full_message = f"{system}\n\nUsuario: {user_message}"
        response = chat_session.send_message(full_message)
        return response.text.strip()
    except Exception as e:
        return f"[Error chatbot: {e}]"

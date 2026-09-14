"""In-memory conversation history — the model 'remembers' because we resend it."""

import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types

load_dotenv()

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

MODEL = "gemini-3.5-flash-lite"  # ajuste: el que tienes disponible en tu proyecto
SYSTEM_INSTRUCTION = "Eres un asistente breve. Respondes en español."

MAX_TURNS = 10  # keeps the last 10 user/model exchanges (20 entries)

# List of plain dicts, same shape as `contents` — nothing hidden here.
history: list[dict] = []


def trim_history() -> None:
    max_entries = MAX_TURNS * 2
    if len(history) > max_entries:
        del history[:-max_entries]


def send(message: str, _retries: int = 0) -> str:
    trim_history()
    history.append({"role": "user", "parts": [{"text": message}]})

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=history,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_INSTRUCTION),
        )
    except errors.ClientError as exc:
        if exc.code == 429 and _retries < 3:
            wait = 2 ** _retries
            print(f"[429] Límite de RPM alcanzado. Reintentando en {wait}s...")
            time.sleep(wait)
            history.pop()  # avoid duplicating the same user turn
            return send(message, _retries=_retries + 1)
        history.pop()
        return f"Error del cliente ({exc.code}): {exc.message}. No se reintenta."
    except errors.ServerError as exc:
        if _retries < 3:
            wait = 2 ** _retries
            print(f"[{exc.code}] Error del servidor. Reintentando en {wait}s...")
            time.sleep(wait)
            history.pop()
            return send(message, _retries=_retries + 1)
        history.pop()
        return f"El servicio no respondió tras varios intentos ({exc.code})."

    finish_reason = str(response.candidates[0].finish_reason)
    if "MAX_TOKENS" in finish_reason:
        print("[warning] Respuesta truncada por max_output_tokens.")

    history.append({"role": "model", "parts": [{"text": response.text}]})
    return response.text


def main() -> None:
    # 8 turns: the fact goes in turn 1, and gets asked back at turn 8.
    print(send("Me llamo Alex y mi color favorito es el verde."))
    print(send("¿Qué framework de Python vimos en la Clase 1?"))
    print(send("Dame un ejemplo de dato que no cabe en un int."))
    print(send("¿Qué hace el comando uv init?"))
    print(send("Explica en una frase qué es un token."))
    print(send("¿Qué significa que una API sea stateless?"))
    print(send("¿Para qué sirve un archivo .env?"))
    print(send("¿Cómo me llamo y cuál es mi color favorito?"))


def trigger_rate_limit() -> None:
    """Sends several requests back to back to hit the free tier's requests-per-minute cap."""
    global history
    history = []
    for i in range(1, 10000):
        print(f"Request {i}: {send(f'Cuenta hasta {i}.')}")


if __name__ == "__main__":
    main()
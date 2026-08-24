# IMPORTS
import os
import sqlite3
import json
import asyncio
import edge_tts
import pygame
from openai import OpenAI
from dotenv import load_dotenv

# CARGA DEL CLIENTE DE OPENROUTER
load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

# MODELO USADO
MODELO = "nvidia/nemotron-3.5-lightning:free"

# -------------------------------------------------
# VOZ GENERADA (edge-tts)
# -------------------------------------------------
async def _generar_audio_edge(texto: str, output_file: str):
    """
    Se conecta a la API de Microsoft Azure TTS y guarda el archivo de audio.
    """
    # Voz neuronal de Colombia
    VOICE = "es-CO-GonzaloNeural"
    communicate = edge_tts.Communicate(texto, VOICE)
    await communicate.save(output_file)


def hablar(texto: str):
    """
    Genera y reproduce el audio usando edge-tts y pygame.
    Esta función bloquea la ejecución hasta que el audio termine de sonar.
    """
    print(f"[voz]: {texto}")

    archivo_temp = "respuesta_vetvoz.mp3"

    # 1. Generar el audio
    asyncio.run(_generar_audio_edge(texto, archivo_temp))

    # 2. Inicializar el mixer de pygame para reproducir
    pygame.mixer.init()
    pygame.mixer.music.load(archivo_temp)
    pygame.mixer.music.play()

    # 3. Esperar a que el audio termine
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # 4. Limpiar y liberar el archivo para que se pueda borrar y sobreescribir luego
    pygame.mixer.music.unload()
    pygame.mixer.quit()

    # 5. Borrar el archivo temporal
    if os.path.exists(archivo_temp):
        os.remove(archivo_temp)


# -------------------------------------------------
# RECONOCIMIENTO DE VOZ (STT)
# -------------------------------------------------
def transcribir_audio() -> str:
    """
    Aquí conectarías el STT real (Vosk o Whisper.cpp) para capturar
    la pregunta del estudiante desde el micrófono.
    Por ahora devolvemos una pregunta ya transcrita, a modo de prueba.
    """
    return "cual es la dosis de tramadol para un perro de 5 kilos"


# -------------------------------------------------
# LÓGICA DE DATOS
# -------------------------------------------------
def extraer_entidades(pregunta: str) -> dict:
    """
    Le pide al modelo (vía OpenRouter) que lea la pregunta en lenguaje
    natural y devuelva SOLO un JSON con los datos que necesitamos.
    """
    prompt = (
        "Extrae del siguiente texto el nombre del farmaco, la especie "
        '("perro" o "gato") y el peso en kilogramos si se menciona. '
        "Responde UNICAMENTE con JSON, sin texto adicional, con este "
        'formato exacto: {"farmaco": "", "especie": "", "peso_kg": null}\n\n'
        f'Texto: "{pregunta}"'
    )
    respuesta = client.chat.completions.create(
        model=MODELO,
        messages=[{"role": "user", "content": prompt}],
    )
    contenido = respuesta.choices[0].message.content.strip()
    contenido = contenido.replace("```json", "").replace("```", "").strip()
    return json.loads(contenido)


def consultar_farmaco(nombre: str, especie: str):
    """Busca el fármaco en la base de datos local."""
    conn = sqlite3.connect("farmacos.db")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM farmacos WHERE nombre LIKE ? AND especie = ?",
        (f"%{nombre}%", especie),
    )
    fila = cur.fetchone()
    conn.close()
    return dict(fila) if fila else None


def generar_respuesta(datos: dict, peso_kg) -> str:
    """Arma la frase final, calculando la dosis exacta si hay peso disponible."""
    if peso_kg:
        dosis_min = round(datos["dosis_min"] * peso_kg, 1)
        dosis_max = round(datos["dosis_max"] * peso_kg, 1)
        return (
            f"{datos['nombre']}: entre {dosis_min} y {dosis_max} miligramos para un "
            f"{datos['especie']} de {peso_kg} kilos, vía {datos['via']}, "
            f"{datos['frecuencia']}. {datos['contraindicaciones']}."
        )
    return (
        f"{datos['nombre']}: {datos['dosis_min']} a {datos['dosis_max']} "
        f"{datos['unidad']}, vía {datos['via']}, {datos['frecuencia']}. "
        f"{datos['contraindicaciones']}."
    )


def main():
    pregunta = transcribir_audio()
    print("Pregunta transcrita:", pregunta)

    entidades = extraer_entidades(pregunta)
    print("Entidades detectadas (OpenRouter):", entidades)

    datos = consultar_farmaco(entidades["farmaco"], entidades["especie"])
    if not datos:
        hablar("No encontré ese fármaco en la base de datos.")
        return

    respuesta = generar_respuesta(datos, entidades.get("peso_kg"))
    hablar(respuesta)


if __name__ == "__main__":
    main()
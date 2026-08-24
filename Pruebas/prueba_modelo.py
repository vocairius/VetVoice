"""
Prueba de conexion con OpenRouter: SOLO confirma que la API key es valida
y que el modelo responde. No es parte del pipeline final, es un chequeo
rapido antes de seguir construyendo.

Requisitos:
    pip install openai python-dotenv
    Archivo .env en la misma carpeta con:
        OPENROUTER_API_KEY=sk-or-v1-tu-key-real
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")
if not api_key:
    raise SystemExit(
        "No encontre OPENROUTER_API_KEY. Revisa que exista un archivo .env "
        "con esa variable en la misma carpeta donde corres este script."
    )

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

MODELO = "nvidia/nemotron-3.5-lightning:free"

print(f"Probando conexion con {MODELO}...")

respuesta = client.chat.completions.create(
    model=MODELO,
    messages=[
        {"role": "user", "content": "Responde solo con la palabra: funciona"}
    ],
)

print("Respuesta cruda del modelo:")
print(respuesta.choices[0].message.content)
print("\nSi ves algo parecido a 'funciona' arriba, la conexion esta OK.")
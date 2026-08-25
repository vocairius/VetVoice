"""
Prueba de STT con deteccion automatica de silencio (VAD simple por volumen):
graba desde que empiezas a hablar hasta que detecta silencio, sin duracion
fija. Se calibra sola al ruido de fondo de tu entorno antes de escuchar.

Requisitos:
    pip install faster-whisper sounddevice numpy
"""
import sounddevice as sd
import numpy as np
import queue
from faster_whisper import WhisperModel

FRECUENCIA_MUESTREO = 16000
TAMANO_BLOQUE = 1024  # frames por "pedacito" (~64 ms a 16kHz), fijo para que el timing sea predecible
SEGUNDOS_SILENCIO_PARA_CORTAR = 1.2  # cuanto silencio despues de hablar corta la grabacion
SEGUNDOS_MAX_GRABACION = 15  # limite de seguridad: nunca te quedes grabando para siempre
SEGUNDOS_CALIBRACION = 0.6

CHUNKS_SILENCIO_MAX = int(SEGUNDOS_SILENCIO_PARA_CORTAR * FRECUENCIA_MUESTREO / TAMANO_BLOQUE)
CHUNKS_MAX_TOTAL = int(SEGUNDOS_MAX_GRABACION * FRECUENCIA_MUESTREO / TAMANO_BLOQUE)

print("Cargando motor auditivo (Whisper base)...")
modelo_stt = WhisperModel("base", device="cpu", compute_type="int8")
cola_audio = queue.Queue()
print("Motor auditivo listo.")


def _callback_audio(indata, frames, time, status):
    """Guarda cada pedacito de audio entrante en una cola en tiempo real."""
    if status:
        print(status)
    cola_audio.put(indata.copy())


def _vaciar_cola():
    """Descarta cualquier audio viejo que haya quedado pendiente en la cola."""
    while not cola_audio.empty():
        cola_audio.get_nowait()


def _calibrar_umbral() -> float:
    """
    Graba un poco de silencio ambiente al arrancar y calcula un umbral de
    voz relativo a ESE ruido de fondo, en vez de un numero fijo que hay
    que ajustar a mano cada vez que cambias de entorno.
    """
    print("Calibrando ruido de fondo, no hables todavia...")
    chunks_calibracion = int(SEGUNDOS_CALIBRACION * FRECUENCIA_MUESTREO / TAMANO_BLOQUE)
    niveles = []
    with sd.InputStream(samplerate=FRECUENCIA_MUESTREO, channels=1, dtype='float32',
                         blocksize=TAMANO_BLOQUE, callback=_callback_audio):
        _vaciar_cola()
        for _ in range(chunks_calibracion):
            chunk = cola_audio.get()
            niveles.append(np.sqrt(np.mean(chunk ** 2)))

    ruido_base = float(np.mean(niveles)) if niveles else 0.005
    umbral = max(ruido_base * 4, 0.01)
    print(f"Ruido de fondo: {ruido_base:.4f} -> umbral de voz: {umbral:.4f}")
    return umbral


def transcribir_audio() -> str:
    """
    Graba el microfono dinamicamente: espera a que empieces a hablar y
    corta sola cuando detecta silencio despues de tu voz.
    """
    umbral_silencio = _calibrar_umbral()
    print("\n[STT]: Esperando a que hables...")

    audio_grabado = []
    hablando = False
    silencio_consecutivo = 0
    total_chunks = 0

    with sd.InputStream(samplerate=FRECUENCIA_MUESTREO, channels=1, dtype='float32',
                         blocksize=TAMANO_BLOQUE, callback=_callback_audio):
        _vaciar_cola()
        while True:
            chunk = cola_audio.get()
            total_chunks += 1
            volumen = np.sqrt(np.mean(chunk ** 2))

            if volumen > umbral_silencio:
                hablando = True
                silencio_consecutivo = 0
                audio_grabado.append(chunk)
            elif hablando:
                silencio_consecutivo += 1
                audio_grabado.append(chunk)
                if silencio_consecutivo > CHUNKS_SILENCIO_MAX:
                    break

            if total_chunks > CHUNKS_MAX_TOTAL:
                print("[STT]: Se alcanzo el limite maximo de grabacion (15s).")
                break

    if not audio_grabado:
        print("[STT]: No se detecto voz.")
        return ""

    print("[STT]: Silencio detectado. Procesando voz...")
    audio_final = np.concatenate(audio_grabado).flatten()

    segmentos, info = modelo_stt.transcribe(audio_final, language="es")
    texto = " ".join(seg.text for seg in segmentos).strip()
    return texto


if __name__ == "__main__":
    resultado = transcribir_audio()
    print(f"\nResultado final de la transcripcion:\n{resultado}")
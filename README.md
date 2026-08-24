# 🐾 VetVoz: Asistente Farmacológico Manos Libres

VetVoz es una interfaz de voz no convencional diseñada para estudiantes y profesionales de la medicina veterinaria. Permite realizar consultas farmacológicas rápidas (dosis, vías de administración, alertas) en tiempo real mediante lenguaje natural. 

El objetivo principal es **eliminar la fricción en entornos clínicos o de laboratorio**: permite al usuario obtener información precisa y cálculos de dosis mientras mantiene las manos libres para sujetar al paciente o manipular instrumental.

---

## ✨ Características Principales

* **Interacción 100% por Voz:** Consultas en lenguaje natural (ej. *"¿Cuál es la dosis de amoxicilina para un perro de 10 kilos?"*).
* **Cálculo Automático:** Extrae inteligentemente el fármaco, la especie y el peso para devolver la dosis exacta precalculada.
* **Síntesis Neuronal:** Respuestas de audio fluidas y naturales utilizando la API de Microsoft Azure TTS (vía `edge-tts`).
* **Arquitectura Ligera:** Procesamiento lógico apoyado en LLMs y una base de datos local SQLite ultrarrápida.

---

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3
* **Procesamiento de Lenguaje Natural (NLP):** OpenRouter API (Modelo `nvidia/nemotron-3.5-lightning:free`) para extracción de entidades (JSON).
* **Text-to-Speech (TTS):** `edge-tts` y `pygame` para síntesis y reproducción de voz.
* **Base de Datos:** `sqlite3`.

---

## 🗄️ Estructura de la Base de Datos

El sistema se apoya en una base de datos local SQLite (`farmacos.db`)[cite: 2]. El script de inicialización incluye un catálogo base de 18 registros enfocados en especies menores (perros y gatos), abarcando antibióticos, antiparasitarios, analgésicos y anestésicos[cite: 2].

> [!WARNING] Advertencia de Uso Clínico
> Los valores de dosis incluidos por defecto en la base de datos son estrictamente **ILUSTRATIVOS** y están diseñados para fines de prototipado[cite: 2]. Antes de utilizarse en un entorno clínico real, toda la información debe ser verificada contra literatura oficial como el *Plumb's Veterinary Drug Handbook* o el *Manual Merck*[cite: 2].

El esquema principal de la tabla `farmacos` contiene:
* `nombre` y `categoria` (Principio activo y clasificación)[cite: 1, 2].
* `especie` (perro/gato)[cite: 1, 2].
* `dosis_min`, `dosis_max` y `unidad` (Rangos de dosificación predeterminados en mg/kg)[cite: 1, 2].
* `via` y `frecuencia` (Ej. Oral, SC, IM, IV / Cada 12 h, Cada 24 h)[cite: 1, 2].
* `contraindicaciones` (Alertas médicas críticas)[cite: 1, 2].

---

## 🚀 Instalación y Ejecución

Sigue estos pasos para desplegar el proyecto en tu entorno local.

### 1. Clonar el repositorio
```bash
git clone [https://github.com/USUARIO/VetVoz.git](https://github.com/USUARIO/VetVoz.git)
cd VetVoz
```

### 2. Configurar el entorno virtual
Se recomienda el uso de un entorno virtual para aislar las dependencias.
```bash
# Mac/Linux:
python3 -m venv venv
source venv/bin/activate

# Windows:
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install edge-tts pygame openai python-dotenv
```

### 4. Configurar Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto y añade tu API Key de OpenRouter (es gratuita):
```env
OPENROUTER_API_KEY=tu_api_key_aqui
```

### 5. Inicializar la Base de Datos
El proyecto incluye un script de configuración que construye y puebla la base de datos local[cite: 2]. Este script es idempotente (se puede ejecutar múltiples veces sin generar registros duplicados)[cite: 2].
```bash
python setup_db.py
```

### 6. Ejecutar VetVoz
Inicia el asistente principal interactivo:
```bash
python pipeline_voz.py
```

---

## 🤝 Contribuciones
¡Las contribuciones son bienvenidas! Si deseas agregar soporte para modelos de reconocimiento de voz (STT) locales como Whisper.cpp, mejorar la base de datos o integrar interfaces visuales (como alertas 3D o web), siéntete libre de hacer un *fork* del repositorio y enviar tu *Pull Request*.

# Echo BUD -LLM Chat UI with MQTT Control

A local AI assistant (Jarvis) powered by Groq that can control smart home devices via MQTT and speak responses using Piper TTS.

## Features
- Chat UI built with Tkinter
- LLM function calling via Groq API
- MQTT device control (lights, switches, scenes)
- Text-to-speech via Piper TTS (local, offline)

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/vvs-tsr/Echo_BUD.git
cd Echo_BUD
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure secrets
```bash
cp .env.example .env
# Edit .env and fill in your real API keys and MQTT credentials
```

### 5. Download voice models
Place your Piper `.onnx` voice files into the `voices/` folder.
Get them from: https://github.com/rhasspy/piper/releases

### 6. Run
```bash
python llm_ui.py
```

## Environment Variables
See `.env.example` for all required variables:
- `GROQ_API_KEY` -from console.groq.com
- `MQTT_BROKER`, `MQTT_PORT`, `MQTT_USERNAME`, `MQTT_PASSWORD` -HiveMQ Cloud credentials

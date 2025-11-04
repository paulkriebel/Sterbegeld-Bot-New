# Sterbegeld Bot - CHECK24 Prototype

LLM-basierter Chatbot für Sterbegeldversicherungen

## Features

- **GPT-5 Integration**: OpenAI GPT-5 für natürliche Konversationen
- **Function Calling**: Automatische Tarifsuche basierend auf Kundenbedarf
- **Mobile-First UI**: CHECK24-Design, optimiert für Mobile und Desktop
- **Debug-Panel**: Entwickler-Tools zur Prompt-Inspektion
- **TDD-Entwicklung**: 8 Tests, alle grün ✅

## Quick Start

### 1. Dependencies installieren

```bash
# Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# oder: venv\Scripts\activate  # Windows

# Packages installieren
pip install -r requirements.txt
```

### 2. Environment konfigurieren

Die `.env` Datei ist bereits konfiguriert mit:
- OpenAI API Key: ✅ Vorhanden
- Model: GPT-5
- Debug-Modus: Aktiviert

### 3. Server starten

```bash
python run.py
```

Die App läuft auf: **http://localhost:5000**

## Projektstruktur

```
├── app/
│   ├── api/              # REST API Endpoints
│   ├── core/             # LLM Client
│   ├── products/         # Sterbegeld Chatbot
│   ├── static/           # CSS & JavaScript
│   ├── templates/        # HTML Templates
│   └── utils/            # Logging
├── data/
│   └── sterbegeld/
│       ├── prompts/      # LLM Prompts
│       └── tariffs.json  # Tarifdaten (5 Beispiele)
├── tests/                # pytest Tests (8 Tests)
├── run.py               # Entry Point
└── requirements.txt     # Dependencies
```

## API Endpoints

### `GET /health`
Health Check

### `POST /api/chat`
Chat mit dem Chatbot

**Request:**
```json
{
  "message": "User message",
  "conversation_history": []
}
```

**Response:**
```json
{
  "reply": "Bot response",
  "debug": {
    "system_prompt": "...",
    "tokens_used": 123
  }
}
```

## Tests ausführen

```bash
pytest tests/ -v
```

**Erwartetes Ergebnis:** 8 passed ✅

## Tech Stack

- **Backend**: Python 3.9, Flask 3.0
- **LLM**: OpenAI GPT-5
- **Frontend**: Vanilla HTML/CSS/JS (kein Framework)
- **Testing**: pytest
- **Styling**: Mobile-First, CHECK24 Farben

## Gesprächsablauf

1. **Weichenstellung**: Direkt Tarife oder erst Fragen?
2. **Pflicht-Parameter**: Geburtsdatum + Versicherungssumme
3. **Optional-Parameter**: Filter anbieten (Gesundheitserklärung, Wartezeit, etc.)
4. **Tarifsuche**: Function Call zur Tarif-Engine
5. **Empfehlung**: Top 3 Tarife, günstigster hervorgehoben
6. **Nachfragen**: Weitere Details oder Abschluss

## Entwickelt mit TDD

Test-Driven Development wurde konsequent angewendet:
- RED: Test schreiben (fails)
- GREEN: Code implementieren (passes)
- REFACTOR: Code verbessern

**Testabdeckung:**
- Tariff Schema Validation (2 Tests)
- Tariff Search Engine (6 Tests)

## Status

```
Phase 1: Projekt-Setup          ████████████████████ 100% ✅
Phase 2: Backend-Core            ████████████████████ 100% ✅
Phase 3: Frontend                ████████████████████ 100% ✅
Phase 4: Testing & Integration   ░░░░░░░░░░░░░░░░░░░░  TBD
Phase 5: Deployment              ░░░░░░░░░░░░░░░░░░░░  TBD
```

**Fortschritt:** 60% (3/5 Phasen komplett)

## Nächste Schritte

- [ ] End-to-End Testing mit echten Dialogen
- [ ] Prompt-Optimierung basierend auf Logs
- [ ] Performance-Messung
- [ ] Produktion-Deployment


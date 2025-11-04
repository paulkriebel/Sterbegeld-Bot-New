# Architektur-Spezifikation

## Zweck
Definition der Gesamtarchitektur des Chatbot-Prototyps mit Fokus auf Einfachheit und Erweiterbarkeit.

## Architekturstil

**Monolithische Web-Anwendung** mit klarer Schichttrennung:

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (Client)                      │
│  ┌──────────────────┐  ┌──────────────────────────────┐ │
│  │  Chat Interface  │  │      Debug Panel             │ │
│  │  (iPhone-Style)  │  │  (Prompt Inspection)         │ │
│  └──────────────────┘  └──────────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────┐│
│  │  Prompt Input Form (3 Kern-Inputs als Freitext)     ││
│  └──────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
                          │ HTTP (REST API)
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Python Backend (Flask/FastAPI)              │
│  ┌─────────────────────────────────────────────────────┐│
│  │            API Layer (REST Endpoints)               ││
│  └─────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────┐│
│  │         Chatbot Service (Core Logic)                ││
│  │  • Prompt Assembly                                  ││
│  │  • Conversation Management                          ││
│  │  • Response Parsing                                 ││
│  └─────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────┐│
│  │         LLM Integration Layer                       ││
│  │  • OpenAI API Client                                ││
│  │  • Function Calling Handler                         ││
│  └─────────────────────────────────────────────────────┘│
│  ┌─────────────────────────────────────────────────────┐│
│  │         Tariff Comparison Engine                    ││
│  │  • JSON/CSV Loader                                  ││
│  │  • Filtering & Ranking Logic                        ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                 OpenAI API (GPT-4o)                      │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│            Static Data Files (Local FS)                  │
│  • tariffs.json (Sterbegeld-Tarife)                     │
│  • product_logic_prompt.txt                             │
│  • interaction_style_prompt.txt                         │
│  • tariff_table_prompt.txt                              │
└─────────────────────────────────────────────────────────┘
```

## Technologie-Stack

### Backend
- **Framework**: **Flask** (Empfehlung für Rapid Prototyping)
  - Einfacher als FastAPI für statische Templates
  - Jinja2 Templates für Server-Side Rendering
  - Flask-CORS für lokale Cross-Origin-Requests
- **Python-Version**: Python 3.10+
- **LLM-Client**: `openai` Python SDK (v1.x)
- **Weitere Libraries**:
  - `python-dotenv` (Environment Variables)
  - `pandas` (CSV-Handling falls nötig)

### Frontend
- **Rendering**: Server-Side Templates (Jinja2) + Progressive Enhancement
- **Styling**: 
  - **Vanilla CSS** mit Mobile-First Approach
  - CSS Grid für Layout (Chat links, Debug rechts)
  - Flexbox für Chat-Nachrichten
- **Interaktivität**: Vanilla JavaScript (kein Build-Step)
  - Fetch API für Backend-Kommunikation
  - LocalStorage für temporäre Konversations-Speicherung (optional)

### Datenbank
**Keine Datenbank** – Statische JSON/CSV-Dateien im Filesystem.

## Datenfluss

### 1. Initiale Seite laden
```
Browser → GET / → Flask → Render index.html (Chat + Debug Panel)
```

### 2. Chat-Nachricht senden
```
User Input → POST /api/chat
  ├─ Request Body: { "message": "Ich bin 45 Jahre alt", "conversation_id": null }
  │
  ├─ Backend: Prompt Assembly
  │   ├─ Load: product_logic_prompt.txt
  │   ├─ Load: interaction_style_prompt.txt
  │   ├─ Load: tariff_table_prompt.txt
  │   └─ Combine with User Message
  │
  ├─ Backend: OpenAI API Call
  │   ├─ Model: gpt-4o
  │   ├─ System Prompt: [Combined Prompts]
  │   ├─ User Message: [User Input]
  │   └─ Function Calling (optional): tariff_search()
  │
  ├─ Backend: Response Processing
  │   ├─ Extract Assistant Message
  │   ├─ If Function Call: Execute tariff_search() → Return results
  │   └─ Log to Console (Debug)
  │
  └─ Response: { "reply": "...", "debug": { "prompt": "...", "raw_response": "..." }}
```

### 3. Tarif-Suche (via Function Calling)
```
LLM triggers function: tariff_search(age=45, health="good", coverage=5000)
  ├─ Backend: Load tariffs.json
  ├─ Filter by criteria
  ├─ Sort by price (ascending)
  ├─ Return top 3 matches
  └─ LLM formats results into natural language
```

## Modulare Schichten

### 1. Generische Chatbot-Schicht (Wiederverwendbar)
**Dateien**:
- `app/chatbot/base.py` – Abstrakte `InsuranceChatbot`-Klasse
- `app/chatbot/llm_client.py` – OpenAI API Wrapper
- `app/chatbot/prompt_builder.py` – Dynamische Prompt-Generierung

**Verantwortlichkeiten**:
- Konversations-Management (Stateless: Alle Messages im Request)
- LLM-Integration
- Function Calling Handler

### 2. Produktspezifische Schicht (Sterbegeld)
**Dateien**:
- `app/products/sterbegeld/chatbot.py` – `SterbeGeldChatbot(InsuranceChatbot)`
- `app/products/sterbegeld/tariffs.py` – Tariff Loading & Filtering
- `data/sterbegeld/tariffs.json` – Tarif-Daten
- `data/sterbegeld/prompts/` – Produktspezifische Prompts

**Verantwortlichkeiten**:
- Produktlogik definieren
- Tarif-Vergleichslogik
- Spezifische Function Definitions

### 3. API Layer
**Dateien**:
- `app/api/routes.py` – REST Endpoints

**Endpoints**:
- `GET /` – HTML-Interface
- `POST /api/chat` – Chat-Nachricht senden
- `POST /api/update-prompts` – Kern-Inputs aktualisieren (für Debug-Panel)
- `GET /api/tariffs` – Alle Tarife abrufen (für Debugging)

## Deployment-Architektur

### Lokal (Initial)
```
├─ Run: python run.py
├─ Server: http://localhost:5000
└─ OpenAI API Key: .env (OPENAI_API_KEY=...)
```

### Spätere Cloud-Migration (Out of Scope für v1)
- Docker-Container
- AWS/GCP/Azure Deployment
- Environment-based Config (dev/staging/prod)

## Nicht-funktionale Anforderungen

### Performance
- **Antwortzeit**: < 5 Sekunden (LLM-Latenz dominiert)
- **Concurrency**: Single-User (kein Load Balancing)

### Skalierbarkeit
- **Horizontal**: Nicht erforderlich (Prototyp)
- **Vertikal**: Ausreichend für 1-5 parallele Nutzer

### Sicherheit
- **API-Key-Schutz**: `.env`-Datei (nicht in Git committen)
- **Input-Validation**: Basis-Validierung (max. Message-Length)
- **Keine Authentifizierung** (lokaler Zugriff)

### Monitoring & Logging
- **Python Logging**: Console + File (`logs/app.log`)
- **Log-Level**: DEBUG (für Entwicklung)
- **Inhalte**:
  - Alle LLM-Requests (Prompt + Response)
  - API-Calls
  - Errors & Exceptions

## Erweiterungspunkte (Future)

1. **Multi-Produkt-Support**:
   - Abstract Factory Pattern für Chatbot-Instanzen
   - Produkt-Switcher im Frontend

2. **Session-Management**:
   - Redis für Konversations-Historie
   - User-ID basierte Sessions

3. **Advanced UI**:
   - React/Vue für SPA
   - Tailwind CSS für Styling

4. **RAG-Integration**:
   - Vektordatenbank (Pinecone, Weaviate)
   - Embeddings für Produktdokumente

## Implementierungshinweise

- **Code-Struktur**: Folgt Flask Best Practices (Blueprints)
- **Testbarkeit**: Klare Trennung zwischen LLM-Logik und Business-Logik
- **Dokumentation**: Docstrings in allen Modulen (Google-Style)

# Deployment & Betrieb-Spezifikation

## Zweck
Definition der Deployment-Strategie, Betriebsanforderungen und Wartung des Prototyps.

## Deployment-Strategie

### Phase 1: Lokales Development (Initial)

**Ziel**: Schnelle Iteration für Produktmanager-Evaluierung

**Setup-Schritte**:

```bash
# 1. Repository klonen (falls Git verwendet)
git clone <repo-url>
cd sterbegeld-bot

# 2. Python Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# oder: venv\Scripts\activate  # Windows

# 3. Dependencies installieren
pip install -r requirements.txt

# 4. Environment Variables setzen
cp .env.example .env
# .env editieren und OPENAI_API_KEY eintragen

# 5. Datenverzeichnisse erstellen
mkdir -p data/sterbegeld/prompts
mkdir -p logs

# 6. Server starten
python run.py
```

**Zugriff**: `http://localhost:5000`

---

## Environment Configuration

### `.env` Datei

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-proj-...  # ← MUST SET
OPENAI_MODEL=gpt-5

# Flask Configuration
FLASK_ENV=development
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=logs/app.log

# App Settings
MAX_MESSAGE_LENGTH=500
```

**Sicherheit**: `.env` NIEMALS in Git committen!

`.gitignore` sollte enthalten:
```
.env
*.log
logs/
__pycache__/
venv/
```

---

## Requirements

### `requirements.txt`

```txt
# Core Framework
flask==3.0.0
flask-cors==4.0.0

# LLM Integration
openai==1.3.0

# Configuration
python-dotenv==1.0.0

# Optional: Data Handling
pandas==2.1.0

# Optional: Validation
jsonschema==4.19.0

# Development/Testing
pytest==7.4.0
pytest-flask==1.2.0
```

### Python-Version
**Minimum**: Python 3.10  
**Empfohlen**: Python 3.11+

**Grund**: Für `match`-Statement und Type Hints

---

## Projektstruktur (Deployment-Ready)

```
sterbegeld-bot/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── api/
│   ├── chatbot/
│   ├── products/
│   ├── utils/
│   └── templates/
├── data/
│   └── sterbegeld/
│       ├── tariffs.json
│       └── prompts/
│           ├── product_logic.txt
│           ├── tariff_table.txt
│           └── interaction_style.txt
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── logs/                    # Generated at runtime
│   └── app.log
├── tests/                   # Optional
│   ├── test_api.py
│   └── test_tariffs.py
├── .env.example             # Template (committed)
├── .env                     # Actual secrets (gitignored)
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

---

## Startup & Shutdown

### Startup

#### Entwicklung (mit Auto-Reload)
```bash
# Aktiviere Virtual Environment
source venv/bin/activate

# Starte Server
python run.py

# Output:
# * Running on http://0.0.0.0:5000
# * Restarting with stat
```

#### Produktion (später)
```bash
# Mit Gunicorn (robuster)
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Shutdown

**Development**: `Ctrl+C` im Terminal

**Produktion**: `systemctl stop chatbot` (wenn als Service eingerichtet)

---

## Monitoring & Logging

### Logging-Strategie

#### Log-Levels

| Level | Use Case | Beispiel |
|-------|----------|----------|
| `DEBUG` | Entwicklung, alle Details | LLM-Prompts, Responses |
| `INFO` | Wichtige Events | API-Calls, Tarifsuchen |
| `WARNING` | Potenzielle Probleme | Lange Antwortzeiten |
| `ERROR` | Fehler ohne Crash | LLM-API-Fehler |
| `CRITICAL` | System-Crash | Server nicht erreichbar |

#### Log-Ausgabe

**Console** (für Entwicklung):
```
2025-11-04 15:30:00 - chatbot - INFO - POST /api/chat - Age: 45, Health: good
2025-11-04 15:30:02 - chatbot - DEBUG - LLM Response: {"choices": [...]}
```

**Datei** (`logs/app.log`):
```
2025-11-04 15:30:00,123 - chatbot - INFO - User requested tariffs
2025-11-04 15:30:02,456 - chatbot - DEBUG - Found 3 matching tariffs
```

#### Wichtige Log-Inhalte

**Bei jedem API-Call**:
- Timestamp
- Endpoint
- Request-Parameter (ohne sensible Daten!)
- Response-Status
- Execution Time

**Bei LLM-Calls**:
- System-Prompt (vollständig)
- User-Message
- LLM-Response
- Token-Usage
- Latenz

---

### Health-Check

#### Endpoint: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-04T15:30:00Z",
  "openai_api": "reachable",
  "tariffs_loaded": true,
  "prompts_loaded": true
}
```

**Use Case**: Automatisches Monitoring (später)

---

## Fehlerbehandlung im Betrieb

### Typische Fehler & Lösungen

#### 1. OpenAI API nicht erreichbar

**Fehler**:
```
openai.error.APIError: The server had an error while processing your request
```

**Lösung**:
- Prüfe Internetverbindung
- Prüfe API-Key-Gültigkeit
- Fallback-Message an User

**Code**:
```python
try:
    response = openai.ChatCompletion.create(...)
except openai.error.APIError as e:
    logger.error(f"OpenAI API Error: {e}")
    return jsonify({
        "reply": "Entschuldigung, ich habe gerade technische Probleme. Bitte versuche es später erneut.",
        "error": "api_error"
    }), 503
```

---

#### 2. Tarif-Datei nicht gefunden

**Fehler**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/sterbegeld/tariffs.json'
```

**Lösung**:
- Prüfe, ob `data/sterbegeld/tariffs.json` existiert
- Falls nicht: Erstelle Beispiel-Datei

**Code**:
```python
def load_tariffs():
    try:
        with open('data/sterbegeld/tariffs.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Tariffs file not found! Creating default...")
        create_default_tariffs()
        return load_tariffs()
```

---

#### 3. Port bereits belegt

**Fehler**:
```
OSError: [Errno 48] Address already in use
```

**Lösung**:
```bash
# Finde Prozess auf Port 5000
lsof -i :5000

# Beende Prozess
kill -9 <PID>

# Oder: Nutze anderen Port
python run.py --port 5001
```

---

## Performance-Optimierung

### Baseline-Metriken (Ziel für Prototyp)

| Metrik | Ziel | Aktuell |
|--------|------|---------|
| **Chat-Response-Zeit** | < 5s | TBD |
| **LLM-Latenz** | < 3s | ~1-2s (OpenAI) |
| **Tarif-Search-Zeit** | < 100ms | ~10ms (lokal) |
| **Page-Load-Zeit** | < 2s | TBD |

### Optimierungen (falls nötig)

#### 1. Prompt-Caching
```python
# Cache System-Prompt (ändert sich selten)
from functools import lru_cache

@lru_cache(maxsize=1)
def get_system_prompt():
    return load_all_prompts()
```

#### 2. Tarif-Caching
```python
# Lade Tarife nur einmal beim Start
class TariffSearchEngine:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.tariffs = load_tariffs()
        return cls._instance
```

#### 3. OpenAI Request-Optimization
```python
# Reduziere max_tokens falls möglich
response = openai.ChatCompletion.create(
    model="gpt-5",
    max_tokens=300,  # Statt 500
    ...
)
```

---

## Datensicherung

### Was muss gesichert werden?

**Für Prototyp (minimal)**:
- `data/sterbegeld/tariffs.json`
- `data/sterbegeld/prompts/*.txt`
- `.env` (separat, verschlüsselt!)

**Später (Produktion)**:
- Datenbank-Dumps
- Konversations-Logs (falls gespeichert)
- Config-Files

### Backup-Strategie (Future)

```bash
# Automatisches Backup-Script
#!/bin/bash
BACKUP_DIR="backups/$(date +%Y-%m-%d)"
mkdir -p $BACKUP_DIR

# Backup Data
cp -r data/ $BACKUP_DIR/
cp .env $BACKUP_DIR/.env.backup

# Komprimieren
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

echo "Backup erstellt: $BACKUP_DIR.tar.gz"
```

---

## Update-Prozess

### Code-Updates

```bash
# 1. Neuesten Code holen
git pull origin main

# 2. Dependencies aktualisieren
pip install -r requirements.txt --upgrade

# 3. Server neustarten
# (Ctrl+C und python run.py)
```

### Prompt-Updates

**Ohne Neustart möglich** (via API):
```bash
curl -X POST http://localhost:5000/api/update-prompts \
  -H "Content-Type: application/json" \
  -d '{
    "product_logic": "Neue Produktlogik...",
    "tariff_table": "Neue Tarife...",
    "interaction_style": "Neuer Stil..."
  }'
```

### Tarif-Daten-Updates

**Einfach**: Editiere `data/sterbegeld/tariffs.json` direkt.  
**Neustart erforderlich**: Ja (oder implementiere Hot-Reload)

---

## Umgebungen (Future)

Aktuell: **Nur Development**

Später:
```
Development (localhost:5000)
    ↓
Staging (staging.example.com)
    ↓
Production (chatbot.example.com)
```

**Environment-based Config**:
```python
# config.py
class DevelopmentConfig(Config):
    DEBUG = True
    OPENAI_MODEL = "gpt-5"

class ProductionConfig(Config):
    DEBUG = False
    OPENAI_MODEL = "gpt-5"
```

---

## Docker-Deployment (Optional, Future)

### `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p logs

# Expose port
EXPOSE 5000

# Run application
CMD ["python", "run.py"]
```

### `docker-compose.yml`

```yaml
version: '3.8'

services:
  chatbot:
    build: .
    ports:
      - "5000:5000"
    env_file:
      - .env
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
```

**Start**:
```bash
docker-compose up -d
```

---

## Cloud-Deployment (Future)

### Option 1: AWS Elastic Beanstalk
- Einfach: Upload ZIP mit Code
- Autoscaling
- Managed Environment

### Option 2: Google Cloud Run
- Serverless
- Container-based
- Pay-per-Request

### Option 3: Heroku
- Einfachste Option
- Ein Command: `git push heroku main`

---

## Sicherheit (Basis)

### API-Key-Schutz

✅ **Gut**:
- In `.env`-Datei
- Nie in Git committen
- Nie in Logs anzeigen

❌ **Schlecht**:
- Hardcoded im Code
- In Config-Dateien in Git

### Input-Validation

```python
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    
    # Validiere Message-Length
    if len(data.get('message', '')) > 500:
        return jsonify({'error': 'Message too long'}), 400
    
    # Sanitize Input (basic)
    message = data['message'].strip()
    
    ...
```

### CORS (für lokalen Zugriff)

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=['http://localhost:5000'])
```

---

## Troubleshooting

### Debug-Checklist

1. ✅ Python Virtual Environment aktiviert?
   ```bash
   which python  # Sollte auf venv zeigen
   ```

2. ✅ Dependencies installiert?
   ```bash
   pip list | grep flask
   ```

3. ✅ `.env` vorhanden und korrekt?
   ```bash
   cat .env | grep OPENAI_API_KEY
   ```

4. ✅ Tariff-Daten vorhanden?
   ```bash
   ls data/sterbegeld/tariffs.json
   ```

5. ✅ Port frei?
   ```bash
   lsof -i :5000
   ```

### Häufige Probleme

**Problem**: "ModuleNotFoundError: No module named 'flask'"  
**Lösung**: `pip install -r requirements.txt`

**Problem**: "OpenAI API Key not set"  
**Lösung**: Prüfe `.env` und `load_dotenv()`

**Problem**: "Tariffs not found"  
**Lösung**: Erstelle `data/sterbegeld/tariffs.json`

---

## Maintenance

### Regelmäßige Aufgaben

| Aufgabe | Frequenz | Beschreibung |
|---------|----------|--------------|
| **Log-Rotation** | Wöchentlich | Lösche alte Logs (> 7 Tage) |
| **Dependency-Updates** | Monatlich | `pip list --outdated` |
| **Backup** | Täglich | Sichere Daten (später) |
| **Health-Check** | Kontinuierlich | Monitoring-Tool (später) |

---

## Zusammenfassung

| Aspekt | Aktuell (Prototyp) | Später (Produktion) |
|--------|-------------------|---------------------|
| **Deployment** | Lokal (localhost) | Cloud (AWS/GCP/Heroku) |
| **Environment** | Development only | Dev/Staging/Prod |
| **Logging** | Console + File | Centralized (ELK/CloudWatch) |
| **Monitoring** | Manuell | Automatisiert (Grafana) |
| **Backup** | Manuell | Automatisiert (täglich) |
| **Security** | Basis (.env) | Production-Grade (Vault) |

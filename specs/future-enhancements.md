# Zukünftige Erweiterungen-Spezifikation

## Zweck
Dokumentation geplanter Features und Erweiterungen, die explizit **nicht** im initialen Prototyp enthalten sind.

---

## Kategorisierung

### 🟢 Quick Wins (Aufwand: niedrig, Nutzen: hoch)
Einfach zu implementieren, großer Mehrwert.

### 🟡 Medium Complexity (Aufwand: mittel, Nutzen: mittel-hoch)
Erfordert Architektur-Anpassungen.

### 🔴 Major Features (Aufwand: hoch, Nutzen: hoch)
Signifikante Entwicklung, strategische Entscheidungen.

---

## Produktfeatures

### 🟢 1. Multi-Produkt-Unterstützung

**Beschreibung**: Erweiterung auf andere Versicherungsprodukte (Haftpflicht, Krankenversicherung, etc.)

**Technische Umsetzung**:
- Abstract Factory Pattern für Chatbot-Instanzen
- Produkt-Switcher im Frontend
- Gemeinsame `InsuranceChatbot`-Basisklasse (bereits vorhanden!)

**Projektstruktur**:
```
app/products/
├── sterbegeld/
│   ├── chatbot.py
│   ├── tariffs.py
│   └── functions.py
├── haftpflicht/
│   ├── chatbot.py
│   ├── tariffs.py
│   └── functions.py
└── krankenversicherung/
    ├── chatbot.py
    ├── tariffs.py
    └── functions.py
```

**API-Anpassung**:
```json
POST /api/chat
{
  "product": "sterbegeld",  // NEU
  "message": "...",
  "conversation_history": [...]
}
```

**Aufwand**: 2-3 Tage  
**Priorität**: Hoch (strategisch wichtig)

---

### 🟡 2. Session-Management & Konversations-Historie

**Beschreibung**: Server-seitige Speicherung von Konversationen für Analyse und Wiederaufnahme.

**Technische Umsetzung**:
- **Session-ID** bei jedem Chat generieren
- **Redis** oder **PostgreSQL** für Speicherung
- API-Endpoint: `GET /api/conversations/:id`

**Datenmodell**:
```json
{
  "session_id": "sess_abc123",
  "product": "sterbegeld",
  "created_at": "2025-11-04T15:00:00Z",
  "messages": [
    {"role": "assistant", "content": "...", "timestamp": "..."},
    {"role": "user", "content": "...", "timestamp": "..."}
  ],
  "extracted_params": {
    "age": 45,
    "health": "good",
    "coverage_amount": 5000
  },
  "recommended_tariffs": [...]
}
```

**Use Cases**:
- Konversation später fortsetzen
- Analyse: Wo brechen User ab?
- A/B-Testing: Welche Prompts funktionieren besser?

**Aufwand**: 3-5 Tage  
**Priorität**: Mittel

---

### 🟢 3. Markdown-Rendering für Bot-Antworten

**Beschreibung**: Bot kann formatierte Antworten senden (fett, kursiv, Listen).

**Technische Umsetzung**:
- Frontend: Markdown-Parser (z.B. `marked.js`)
- Backend: Keine Änderung nötig

**Beispiel**:
```markdown
**Sterbegeld Best**
- 💶 21,28 €/Monat
- ✅ Keine Wartezeit
```

**Aufwand**: < 1 Tag  
**Priorität**: Niedrig (Nice-to-Have)

---

### 🟡 4. Vergleichslogik anpassbar machen

**Beschreibung**: User kann Priorisierung ändern (günstigster vs. beste Leistung vs. keine Wartezeit).

**UI**:
```
☐ Günstigster Preis
☐ Beste Leistung
☐ Keine Wartezeit
☐ Keine Gesundheitsprüfung
```

**API**:
```json
POST /api/chat
{
  "message": "...",
  "preferences": {
    "sort_by": "price",  // "coverage", "waiting_period"
    "exclude_health_check": false
  }
}
```

**Aufwand**: 2-3 Tage  
**Priorität**: Hoch (Differenzierung!)

---

### 🔴 5. Vertragsbabschluss-Integration

**Beschreibung**: Übergang von Tarifauswahl zu tatsächlichem Abschluss.

**Flow**:
```
Tarifauswahl → Antragsstrecke → CHECK24-Integration → Vertragsabschluss
```

**Herausforderungen**:
- Rechtliche Compliance (DSGVO, Versicherungsrecht)
- Anbindung an CHECK24-Backend
- E-Signatur
- Payment

**Aufwand**: Mehrere Wochen (nicht für Prototyp)  
**Priorität**: Niedrig (erst nach erfolgreicher Evaluierung)

---

## UI/UX-Verbesserungen

### 🟢 6. UI-Bibliothek (Tailwind CSS, Material UI)

**Beschreibung**: Professionelleres Design mit etablierten Frameworks.

**Optionen**:
- **Tailwind CSS**: Utility-First, moderne Ästhetik
- **Material UI**: Google-Design, komponentenbasiert
- **Chakra UI**: React-basiert, Accessibility-first

**Aufwand**: 2-3 Tage (Redesign)  
**Priorität**: Mittel

---

### 🟢 7. Typing-Indikator mit Animation

**Beschreibung**: Zeige "..." mit Animation während LLM-Request.

**Implementierung**:
```javascript
function showTypingIndicator() {
  const indicator = document.createElement('div');
  indicator.className = 'typing-indicator';
  indicator.innerHTML = '<span></span><span></span><span></span>';
  chatContainer.appendChild(indicator);
}
```

**CSS**:
```css
.typing-indicator span {
  animation: blink 1.4s infinite;
}
```

**Aufwand**: < 1 Tag  
**Priorität**: Hoch (verbessert UX erheblich)

---

### 🟡 8. Voice-Input (Speech-to-Text)

**Beschreibung**: User kann sprechen statt tippen.

**Technische Umsetzung**:
- Browser Web Speech API
- Oder: OpenAI Whisper API

**Code**:
```javascript
const recognition = new webkitSpeechRecognition();
recognition.onresult = (event) => {
  const transcript = event.results[0][0].transcript;
  sendMessage(transcript);
};
```

**Aufwand**: 1-2 Tage  
**Priorität**: Niedrig (experimentell)

---

### 🟢 9. Copy-to-Clipboard für Debug-Panel

**Beschreibung**: Ein-Klick-Kopie von Prompts/Responses.

**UI**:
```html
<button onclick="copyToClipboard('debug-system-prompt')">
  📋 Kopieren
</button>
```

**Code**:
```javascript
function copyToClipboard(elementId) {
  const text = document.getElementById(elementId).textContent;
  navigator.clipboard.writeText(text);
}
```

**Aufwand**: < 1 Tag  
**Priorität**: Mittel (Developer-QoL)

---

## LLM & Prompt-Engineering

### 🟡 10. A/B-Testing für Prompts

**Beschreibung**: Paralleles Testen verschiedener Prompt-Strategien.

**Mechanismus**:
- 50% der Requests nutzen Prompt A
- 50% der Requests nutzen Prompt B
- Tracking: Welche Version führt zu besseren Dialogen?

**Metriken**:
- Erfolgsrate (Tarifempfehlung erreicht)
- Durchschnittliche Anzahl Nachrichten
- User-Satisfaction (Umfrage)

**Aufwand**: 3-5 Tage  
**Priorität**: Hoch (für Optimierung essentiell)

---

### 🔴 11. RAG (Retrieval-Augmented Generation)

**Beschreibung**: Statt alle Tarife im Prompt, nur relevante via Semantic Search abrufen.

**Vorteile**:
- Reduzierter Token-Verbrauch (günstigere API-Kosten)
- Skaliert auf 1000+ Tarife
- Immer aktuellste Daten (keine Prompt-Updates nötig)

**Technologie-Stack**:
- **Vektordatenbank**: Pinecone, Weaviate, ChromaDB
- **Embeddings**: OpenAI `text-embedding-3-small`
- **Retrieval**: Semantic Search bei Tarifsuche

**Flow**:
```
User-Query → Embedding → Semantic Search → Top 5 Tarife → LLM-Kontext
```

**Aufwand**: 1-2 Wochen  
**Priorität**: Mittel (erst bei >100 Tarifen sinnvoll)

---

### 🟢 12. Streaming-Antworten

**Beschreibung**: Bot-Antworten erscheinen Wort für Wort (wie ChatGPT).

**Technische Umsetzung**:
- OpenAI `stream=True`
- Server-Sent Events (SSE) im Backend
- JavaScript EventSource im Frontend

**Code**:
```python
response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[...],
    stream=True
)

for chunk in response:
    yield f"data: {chunk['choices'][0]['delta']['content']}\n\n"
```

**Aufwand**: 2-3 Tage  
**Priorität**: Mittel (bessere UX, aber nicht kritisch)

---

### 🟡 13. Multi-Language-Support

**Beschreibung**: Chatbot in mehreren Sprachen (Englisch, Türkisch, etc.).

**Technische Umsetzung**:
- Prompt-Templates pro Sprache
- Frontend: Language-Switcher
- Backend: `language` Parameter

**Projektstruktur**:
```
data/sterbegeld/prompts/
├── de/
│   ├── product_logic.txt
│   ├── tariff_table.txt
│   └── interaction_style.txt
├── en/
│   ├── product_logic.txt
│   └── ...
└── tr/
    └── ...
```

**Aufwand**: 1-2 Tage pro Sprache (+ Übersetzungen)  
**Priorität**: Niedrig (erst nach erfolgreicher deutscher Version)

---

## Daten & Analytics

### 🟡 14. Analytics-Dashboard

**Beschreibung**: Visualisierung von Konversations-Metriken.

**Metriken**:
- Anzahl Konversationen pro Tag
- Durchschnittliche Dialog-Länge
- Erfolgsrate (Tarifempfehlung erreicht)
- Häufigste Abbruchpunkte
- Beliebteste Tarife

**Technologie**:
- **Grafana** + Prometheus
- Oder: Custom-Dashboard mit Chart.js

**Aufwand**: 3-5 Tage  
**Priorität**: Mittel (für Produkt-Iterationen wichtig)

---

### 🟢 15. Export-Funktion für Konversationen

**Beschreibung**: Produktmanager können Dialoge als JSON/CSV exportieren.

**API**:
```
GET /api/export/conversations?from=2025-11-01&to=2025-11-30
```

**Response**: CSV-Datei
```csv
session_id,timestamp,product,age,health,coverage,recommended_tariff,success
sess_001,2025-11-04 15:30:00,sterbegeld,45,good,5000,Sterbegeld Best,true
```

**Aufwand**: 1-2 Tage  
**Priorität**: Hoch (für Evaluierung)

---

### 🔴 16. Machine Learning für Tarifempfehlungen

**Beschreibung**: ML-Modell lernt aus vergangenen Konversationen, welche Tarife am besten passen.

**Ansatz**:
- Training-Daten: Historische Konversationen + User-Feedback
- Features: Alter, Gesundheit, Präferenzen, Interaktionsmuster
- Modell: Collaborative Filtering oder Gradient Boosting

**Aufwand**: Mehrere Wochen  
**Priorität**: Niedrig (erst nach viel Daten)

---

## Sicherheit & Compliance

### 🟡 17. DSGVO-konforme Datenhaltung

**Beschreibung**: Rechtskonforme Speicherung personenbezogener Daten.

**Anforderungen**:
- **Einwilligung**: User muss zustimmen
- **Recht auf Löschung**: User kann Daten löschen lassen
- **Verschlüsselung**: At-rest und in-transit
- **Audit-Logs**: Wer hat wann auf welche Daten zugegriffen?

**Aufwand**: 5-10 Tage (+ rechtliche Beratung)  
**Priorität**: Hoch (für produktiven Einsatz mit echten Kunden)

---

### 🟢 18. Rate Limiting

**Beschreibung**: Schutz vor Missbrauch (z.B. zu viele Requests).

**Technische Umsetzung**:
- Flask-Limiter: `@limiter.limit("10 per minute")`
- Oder: Nginx Rate Limiting

**Code**:
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/api/chat')
@limiter.limit("10 per minute")
def chat():
    ...
```

**Aufwand**: < 1 Tag  
**Priorität**: Mittel

---

### 🟡 19. Authentifizierung & User-Management

**Beschreibung**: User müssen sich einloggen, um Chatbot zu nutzen.

**Technologie**:
- **Auth0** (einfach zu integrieren)
- Oder: Flask-Login mit PostgreSQL

**Features**:
- Login/Logout
- User-Profil (gespeicherte Konversationen)
- Admin-Panel (für Produktmanager)

**Aufwand**: 3-5 Tage  
**Priorität**: Niedrig (erst bei öffentlichem Zugang)

---

## Infrastruktur

### 🟡 20. CI/CD Pipeline

**Beschreibung**: Automatisierte Tests und Deployment bei jedem Git-Push.

**Tools**:
- **GitHub Actions**: Einfach, kostenlos
- **Jenkins**: Selbst-gehostet, flexibel

**Pipeline**:
```yaml
name: CI/CD

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: pip install -r requirements.txt
      - run: pytest

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - run: ssh user@server "cd /app && git pull && systemctl restart chatbot"
```

**Aufwand**: 2-3 Tage  
**Priorität**: Mittel

---

### 🟢 21. Docker-Containerisierung

**Beschreibung**: Einfaches Deployment via Docker.

**Vorteile**:
- Plattform-unabhängig
- Reproduzierbare Environments
- Einfaches Scaling

**Aufwand**: 1-2 Tage  
**Priorität**: Mittel

---

### 🔴 22. Kubernetes-Orchestration

**Beschreibung**: Hochverfügbares, skalierbares Deployment.

**Use Case**: Erst bei 1000+ parallelen Nutzern sinnvoll.

**Aufwand**: 1-2 Wochen  
**Priorität**: Sehr niedrig (Overkill für Prototyp)

---

## Testing

### 🟡 23. Automatisierte End-to-End-Tests

**Beschreibung**: Simulierte Dialoge testen gesamte Kette (Frontend → Backend → LLM).

**Tools**:
- **Selenium** / **Playwright**: Browser-Automation
- **Pytest**: Test-Framework

**Beispiel-Test**:
```python
def test_full_conversation():
    # 1. Öffne Chatbot
    browser.get('http://localhost:5000')
    
    # 2. Sende "Ich bin 45 Jahre alt, gesund und möchte 5000 Euro versichern"
    input_field = browser.find_element_by_id('user-input')
    input_field.send_keys('Ich bin 45, gesund, 5000 Euro')
    input_field.submit()
    
    # 3. Warte auf Tarifempfehlung
    wait.until(EC.text_to_be_present_in_element((By.CLASS_NAME, 'message-bot'), 'Sterbegeld Best'))
    
    # 4. Assert: Günstigster Tarif angezeigt
    assert 'Sterbegeld Best' in browser.page_source
```

**Aufwand**: 3-5 Tage  
**Priorität**: Mittel (für Regression-Testing wichtig)

---

### 🟢 24. Unit-Tests für Tarif-Logik

**Beschreibung**: Teste Filter- und Ranking-Logik isoliert.

**Beispiel**:
```python
def test_tariff_search():
    engine = TariffSearchEngine()
    results = engine.search(age=45, health='good', coverage=5000)
    
    assert len(results) > 0
    assert results[0]['monthly_premium'] < results[1]['monthly_premium']
    assert all(t['coverage_amount'] >= 5000 for t in results)
```

**Aufwand**: 1-2 Tage  
**Priorität**: Hoch (verhindert Bugs)

---

## Zusammenfassung: Prioritäts-Matrix

| Feature | Aufwand | Priorität | Wann? |
|---------|---------|-----------|-------|
| **Typing-Indikator** | 🟢 Niedrig | Hoch | Sofort |
| **Multi-Produkt-Support** | 🟢 Niedrig | Hoch | Phase 2 |
| **Export-Funktion** | 🟢 Niedrig | Hoch | Phase 2 |
| **Unit-Tests** | 🟢 Niedrig | Hoch | Phase 1 |
| **Vergleichslogik anpassbar** | 🟡 Mittel | Hoch | Phase 2 |
| **A/B-Testing** | 🟡 Mittel | Hoch | Phase 3 |
| **Session-Management** | 🟡 Mittel | Mittel | Phase 3 |
| **Analytics-Dashboard** | 🟡 Mittel | Mittel | Phase 3 |
| **RAG** | 🔴 Hoch | Mittel | Phase 4 |
| **Vertragsbabschluss** | 🔴 Hoch | Niedrig | Phase 5+ |

---

## Implementierungs-Roadmap (Vorschlag)

### **Phase 1 (Prototyp)** – Jetzt
✅ Alle Basisfunktionen

### **Phase 2 (MVP)** – Nach erfolgreicher Evaluierung
- Multi-Produkt-Support
- Export-Funktion
- Vergleichslogik anpassbar
- Typing-Indikator

### **Phase 3 (Skalierung)** – Bei 100+ täglichen Nutzern
- Session-Management
- Analytics-Dashboard
- A/B-Testing
- E2E-Tests

### **Phase 4 (Optimierung)** – Bei 1000+ Tarifen
- RAG-Integration
- ML-Empfehlungen
- Performance-Tuning

### **Phase 5 (Produktion)** – Bei echten Kunden
- DSGVO-Compliance
- Vertragsbabschluss
- Auth & User-Management

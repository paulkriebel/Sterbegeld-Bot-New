# LLM-Integration & Prompt-Engineering Spezifikation

## Zweck
Definition der LLM-Nutzung, Prompt-Strategien und Function-Calling-Mechanismen für den Chatbot.

## LLM-Provider & Modell

### Modell-Auswahl
**Primär**: **GPT-5** (OpenAI)
- **Aktuell verfügbar**: Ja ✅
- **Capabilities**: Function Calling, JSON Mode, Verbesserte Reasoning
- **Context Window**: 200k+ Tokens (geschätzt)
- **Output**: 8k+ Tokens (geschätzt)

**Vorteile gegenüber GPT-4o**:
- Besseres Reasoning (weniger Halluzinationen)
- Längeres Context-Window
- Schnellere Antwortzeiten

### API-Konfiguration
```python
openai.ChatCompletion.create(
    model="gpt-5",          # ✅ GPT-5 verfügbar
    messages=[...],
    temperature=0.7,        # Balance zwischen Kreativität und Konsistenz
    max_tokens=500,         # Ausreichend für Chatbot-Antworten
    top_p=1.0,
    frequency_penalty=0.0,
    presence_penalty=0.0,
    functions=[...],        # Function Calling Definitions
    function_call="auto"    # LLM entscheidet, wann Funktion aufgerufen wird
)
```

---

## Prompt-Architektur

### Drei-Kern-Input-System

Das System basiert auf **drei konfigurierbaren Prompt-Komponenten**, die zur Laufzeit kombiniert werden:

#### 1. **Produktlogik-Prompt**
**Datei**: `data/sterbegeld/prompts/product_logic.txt`

**Zweck**: Beschreibt die Funktionsweise von Sterbegeldversicherungen.

**Inhalt** (Beispiel):
```
# Produktlogik: Sterbegeldversicherungen

## Was ist eine Sterbegeldversicherung?
Eine Sterbegeldversicherung ist eine Kapitallebensversicherung, die im Todesfall eine vereinbarte Summe zur Deckung der Bestattungskosten auszahlt.

## Wichtige Parameter:
- **Versicherungssumme**: Zwischen 2.000 € und 15.000 €
- **Beitrag**: Monatlich oder jährlich zahlbar
- **Alter**: Eintrittsalter meist 40-85 Jahre
- **Gesundheitsprüfung**: Vereinfachte oder keine Gesundheitsprüfung bei vielen Tarifen

## Berechnungsgrundlagen:
- Höherer Beitrag bei höherem Eintrittsalter
- Gesundheitszustand beeinflusst Beitragshöhe (bei Gesundheitsprüfung)
- Keine Gewinnbeteiligung

## Wartezeiten:
- Oft 12-36 Monate Wartezeit bei Tod durch Krankheit
- Keine Wartezeit bei Unfalltod

## Steuerliche Aspekte:
- Auszahlung ist steuerfrei (bei Tod des Versicherten)
```

---

#### 2. **Tarif-Tabelle-Prompt**
**Datei**: `data/sterbegeld/prompts/tariff_table.txt`

**Zweck**: Stellt verfügbare Tarife in textueller Form dar (alternativ zur JSON-Datei).

**Inhalt** (Beispiel):
```
# Verfügbare Sterbegeld-Tarife

## Tarif A: "Sterbegeld Basis"
- Anbieter: VersicherungPlus
- Monatlicher Beitrag: 10,50 € (Beispiel für 45-jährige Person)
- Versicherungssumme: 3.000 €
- Altersbereich: 40-75 Jahre
- Gesundheitsprüfung: Keine
- Wartezeit: 24 Monate (Krankheit), 0 Monate (Unfall)

## Tarif B: "Sterbegeld Komfort"
- Anbieter: VersicherungPlus
- Monatlicher Beitrag: 17,80 € (Beispiel für 45-jährige Person)
- Versicherungssumme: 5.000 €
- Altersbereich: 40-75 Jahre
- Gesundheitsprüfung: Keine
- Wartezeit: 24 Monate (Krankheit), 0 Monate (Unfall)

## Tarif C: "Sterbegeld Premium"
- Anbieter: VersicherungPlus
- Monatlicher Beitrag: 26,50 € (Beispiel für 45-jährige Person)
- Versicherungssumme: 8.000 €
- Altersbereich: 40-80 Jahre
- Gesundheitsprüfung: Vereinfacht
- Wartezeit: 12 Monate (Krankheit), 0 Monate (Unfall)

## Tarif D: "Sterbegeld Best"
- Anbieter: SecureLife
- Monatlicher Beitrag: 15,20 € (Beispiel für 45-jährige Person)
- Versicherungssumme: 5.000 €
- Altersbereich: 18-65 Jahre
- Gesundheitsprüfung: Ja (vollständig)
- Wartezeit: 0 Monate
- Besonderheit: Keine Wartezeit bei guter Gesundheit

**Hinweis**: Die Beiträge variieren je nach Alter und Gesundheitszustand.
```

---

#### 3. **Interaktionsstil-Prompt**
**Datei**: `data/sterbegeld/prompts/interaction_style.txt`

**Zweck**: Definiert die bevorzugte Gesprächsführung des Chatbots.

**Inhalt** (Beispiel):
```
# Interaktionsstil: Sterbegeld-Beratung

## Grundsätze:
- **Freundlich und einfühlsam**: Sterbegeldversicherungen sind ein sensibles Thema
- **Klar und verständlich**: Vermeide Versicherungsjargon
- **Fokussiert**: Stelle maximal EINE Frage pro Antwort
- **Aktiv**: Führe das Gespräch proaktiv, um alle nötigen Informationen zu erfassen

## Gesprächsablauf:
1. **Begrüßung**: Kurz und freundlich
2. **Bedarfsermittlung**: Erfrage nacheinander:
   - Alter
   - Gesundheitszustand (grobe Einschätzung: ausgezeichnet, gut, mittel, schlecht)
   - Gewünschte Versicherungssumme
3. **Tarifvorschlag**: Nenne die 3 günstigsten passenden Tarife
4. **Abschluss**: Frage, ob weitere Informationen gewünscht sind

## Tonalität:
- Duzen (informell, aber respektvoll)
- Kurze Sätze (max. 2-3 Sätze pro Antwort)
- Verwende Emojis sparsam (nur bei Begrüßung/Verabschiedung)

## Beispiel-Dialog:
**Bot**: Hallo! Ich helfe dir, die passende Sterbegeldversicherung zu finden. Wie alt bist du?
**User**: 45
**Bot**: Danke! Wie würdest du deinen aktuellen Gesundheitszustand beschreiben? (ausgezeichnet, gut, mittel oder schlecht)
**User**: gut
**Bot**: Perfekt! Welche Versicherungssumme möchtest du absichern? Übliche Summen liegen zwischen 3.000 und 10.000 Euro.
**User**: 5000 Euro
**Bot**: Ich habe drei passende Tarife für dich gefunden:
1. **Sterbegeld Komfort** – 17,80 €/Monat (5.000 € Deckung)
2. **Sterbegeld Best** – 15,20 €/Monat (5.000 € Deckung, mit Gesundheitsprüfung)
3. **Sterbegeld Premium** – 26,50 €/Monat (8.000 € Deckung)

Der günstigste Tarif ist "Sterbegeld Best" für 15,20 €/Monat. Benötigst du weitere Details?
```

---

### Prompt-Assembly-Strategie

**Für Rapid Prototype: System-Prompt-Ansatz**

Alle drei Kern-Inputs werden zu einem einzigen **System-Prompt** kombiniert:

```python
def build_system_prompt(product_logic: str, tariff_table: str, 
                        interaction_style: str) -> str:
    return f"""
Du bist ein KI-Versicherungsberater, spezialisiert auf Sterbegeldversicherungen.

# 1. PRODUKTLOGIK
{product_logic}

# 2. VERFÜGBARE TARIFE
{tariff_table}

# 3. INTERAKTIONSSTIL
{interaction_style}

# 4. DEINE AUFGABE
Führe ein natürliches Gespräch, um folgende Parameter zu erfassen:
- Alter des Kunden
- Gesundheitszustand (ausgezeichnet, gut, mittel, schlecht)
- Gewünschte Versicherungssumme

Wenn alle Informationen vorliegen, rufe die Funktion `tariff_search` auf, 
um die passenden Tarife zu finden und empfehle dem Kunden die günstigste Option.

WICHTIG: Halte dich strikt an den definierten Interaktionsstil!
"""
```

**Vorteile**:
- ✅ Einfach zu implementieren
- ✅ Keine zusätzliche Infrastruktur (keine Vektordatenbank)
- ✅ Schnelle Iteration (Prompts einfach editierbar)
- ✅ Transparent (gesamter Prompt im Debug-Panel sichtbar)

**Nachteile** (akzeptabel für Prototyp):
- ⚠️ Token-Verbrauch höher als bei RAG
- ⚠️ Context-Window-Limit bei sehr großen Tarif-Tabellen

**Alternative für spätere Skalierung: RAG (Retrieval-Augmented Generation)**
- Tarif-Tabelle in Vektordatenbank (Pinecone, ChromaDB)
- Nur relevante Tarife via Semantic Search abrufen
- Reduziert Token-Verbrauch bei 100+ Tarifen

---

## Function Calling (Strukturierte Outputs)

### Zweck
**Problem**: LLM könnte Tarife "halluzinieren" oder ungenaue Empfehlungen geben.

**Lösung**: **Function Calling** erzwingt strukturierte Datenabfragen.

### Mechanismus

#### 1. Function Definition (Backend)
```python
{
    "name": "tariff_search",
    "description": "Sucht passende Sterbegeld-Tarife basierend auf Kundendaten. Rufe diese Funktion auf, sobald du Alter, Gesundheitszustand und gewünschte Versicherungssumme des Kunden kennst.",
    "parameters": {
        "type": "object",
        "properties": {
            "age": {
                "type": "integer",
                "description": "Alter des Kunden in Jahren (18-99)"
            },
            "health": {
                "type": "string",
                "enum": ["excellent", "good", "fair", "poor"],
                "description": "Gesundheitszustand: excellent (ausgezeichnet), good (gut), fair (mittel), poor (schlecht)"
            },
            "coverage_amount": {
                "type": "integer",
                "description": "Gewünschte Versicherungssumme in Euro (z.B. 5000)"
            }
        },
        "required": ["age", "health", "coverage_amount"]
    }
}
```

#### 2. LLM-Entscheidung
Wenn der User sagt: _"Ich bin 45 Jahre alt, in guter Gesundheit und möchte 5000 Euro absichern"_

LLM-Response:
```json
{
  "role": "assistant",
  "content": null,
  "function_call": {
    "name": "tariff_search",
    "arguments": "{\"age\": 45, \"health\": \"good\", \"coverage_amount\": 5000}"
  }
}
```

#### 3. Backend-Execution
```python
# Backend führt Tarif-Suche aus
results = tariff_engine.search(age=45, health='good', coverage=5000)

# Ergebnis:
[
  {"name": "Sterbegeld Best", "premium": 15.20, "coverage": 5000},
  {"name": "Sterbegeld Komfort", "premium": 17.80, "coverage": 5000}
]
```

#### 4. Second LLM Call (mit Function Result)
```python
messages = [
  {"role": "user", "content": "Ich bin 45, gut gesund, 5000 Euro"},
  {"role": "assistant", "content": null, "function_call": {...}},
  {"role": "function", "name": "tariff_search", "content": json.dumps(results)}
]

# LLM formatiert Ergebnis in natürlicher Sprache:
"Ich habe zwei passende Tarife gefunden:
1. **Sterbegeld Best** – 15,20 €/Monat
2. **Sterbegeld Komfort** – 17,80 €/Monat

Der günstigste ist Sterbegeld Best für 15,20 € pro Monat."
```

---

## Prompt-Best-Practices (OpenAI Empfehlungen)

### 1. Klare Anweisungen
✅ **Gut**:
```
Stelle maximal EINE Frage pro Antwort. Erfrage die Parameter nacheinander.
```

❌ **Schlecht**:
```
Sei freundlich und hilfreich.
```

### 2. Beispiele geben (Few-Shot Learning)
```
# Beispiel-Dialog:
**Bot**: Wie alt bist du?
**User**: 45
**Bot**: Danke! Wie würdest du deinen Gesundheitszustand beschreiben?
```

### 3. Output-Format definieren
```
Wenn du Tarife empfiehlst, nutze dieses Format:
1. **Tarifname** – Preis/Monat (Deckung)
2. ...
```

### 4. Constraints setzen
```
NIEMALS:
- Tarife erfinden, die nicht in der Tarif-Tabelle stehen
- Rechtliche Beratung geben
- Persönliche Empfehlungen außerhalb der Preislogik
```

### 5. Tone/Voice definieren
```
Tonalität: Freundlich, einfühlsam, klar. Duzen.
Satzlänge: Kurz (max. 2-3 Sätze).
```

---

## Konversations-Management (Stateless)

### Ansatz für Prototyp
**Stateless Architecture**: Keine serverseitige Session-Speicherung.

**Mechanismus**:
- Client sendet **gesamte Konversations-Historie** bei jedem Request
- Backend hat keinen State zwischen Requests

**Beispiel**:
```json
POST /api/chat
{
  "message": "5000 Euro",
  "conversation_history": [
    {"role": "assistant", "content": "Hallo! Wie alt bist du?"},
    {"role": "user", "content": "45"},
    {"role": "assistant", "content": "Danke! Wie ist dein Gesundheitszustand?"},
    {"role": "user", "content": "gut"}
  ]
}
```

**Vorteile**:
- ✅ Einfach zu implementieren
- ✅ Keine Datenbank nötig
- ✅ Horizontal skalierbar (jeder Request unabhängig)

**Nachteile**:
- ⚠️ Token-Verbrauch steigt mit langer Konversation
- ⚠️ Client muss Historie verwalten (in LocalStorage/State)

**Mitigation für Token-Verbrauch**:
```python
def truncate_history(history: List[Dict], max_messages: int = 10) -> List[Dict]:
    """Keep only last N messages to avoid context overflow"""
    return history[-max_messages:]
```

---

## Error Handling & Fallbacks

### LLM-Fehler
**Problem**: OpenAI API nicht erreichbar oder Rate Limit

**Lösung**:
```python
try:
    response = openai.ChatCompletion.create(...)
except openai.error.RateLimitError:
    return {
        "reply": "Entschuldigung, ich bin gerade überlastet. Bitte versuche es in einer Minute erneut.",
        "error": "rate_limit"
    }
except openai.error.APIError:
    return {
        "reply": "Es gab ein technisches Problem. Bitte versuche es später erneut.",
        "error": "api_error"
    }
```

### Halluzination-Prevention
**Problem**: LLM erfindet Tarife oder Preise

**Lösungen**:
1. **Function Calling**: Erzwingt strukturierte Datenabfragen
2. **Prompt-Constraint**:
   ```
   NIEMALS Tarife oder Preise nennen, die nicht explizit in der Tarif-Tabelle stehen.
   Wenn unsicher, sage: "Ich habe keine passenden Tarife gefunden."
   ```
3. **Post-Processing**: Backend validiert LLM-Output gegen echte Tarif-Daten

---

## Monitoring & Debugging

### Log-Inhalte
```python
logger.debug(f"System Prompt: {system_prompt}")
logger.debug(f"User Message: {user_message}")
logger.debug(f"LLM Response: {response}")
logger.info(f"Tokens used: {response['usage']['total_tokens']}")
```

### Debug-Panel-Anzeige
Im Frontend sichtbar:
- Vollständiger System-Prompt
- User-Message
- Raw LLM-Response (JSON)
- Function Calls (falls vorhanden)
- Token-Verbrauch

---

## Kosten-Optimierung

### GPT-4o Pricing (Stand Nov 2025)
- Input: ~$5 / 1M Tokens
- Output: ~$15 / 1M Tokens

### Durchschnittlicher Request (geschätzt)
- System Prompt: ~1.000 Tokens
- Conversation History: ~200 Tokens
- User Message: ~50 Tokens
- Output: ~100 Tokens
- **Total**: ~1.350 Tokens ≈ $0,02 pro Request

### Optimierungen:
1. **Prompt-Komprimierung**: Entferne unnötige Beispiele
2. **History-Truncation**: Nur letzte 10 Messages
3. **Caching**: (Später) Identische Anfragen cachen

---

## ~~Migration zu GPT-5~~ ✅ BEREITS VERFÜGBAR

GPT-5 ist bereits verfügbar und wird direkt genutzt.

### Konfiguration
```python
# config.py
OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-5')
```

### Fallback auf GPT-4o (falls nötig)
```python
# Falls GPT-5 temporär nicht verfügbar:
OPENAI_MODEL=gpt-4o  # In .env
```

---

## Zusammenfassung

| Aspekt | Entscheidung | Begründung |
|--------|--------------|------------|
| **Modell** | GPT-5 | Beste verfügbare Option, Function Calling |
| **Prompt-Strategie** | System-Prompt-Kombination | Einfach, transparent, schnell iterierbar |
| **Function Calling** | Ja (`tariff_search`) | Verhindert Halluzinationen |
| **Konversations-State** | Stateless (Client-Side) | Keine Datenbank nötig, einfacher |
| **Monitoring** | Python Logging + Debug-Panel | Ausreichend für Prototyp |
| **Kosten** | ~$0,02 pro Request | Akzeptabel für interne Evaluierung |

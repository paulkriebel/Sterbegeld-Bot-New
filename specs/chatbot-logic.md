# Chatbot-Logik & Gesprächsfluss-Spezifikation

## Zweck
Definition des Konversationsflusses, der Dialogstrategien und der Geschäftslogik des Chatbots.

## Gesprächsfluss-Übersicht

### Phasen des Dialogs

```
┌─────────────────────────────────────────────────────────┐
│ Phase 1: BEGRÜSSUNG                                     │
│ • Willkommensnachricht                                  │
│ • Erklärung des Zwecks                                  │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 2: BEDARFSERMITTLUNG (aktives Erfragen)          │
│ • Parameter 1: Alter                                    │
│ • Parameter 2: Gesundheitszustand                       │
│ • Parameter 3: Gewünschte Versicherungssumme           │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 3: TARIFSUCHE (Function Calling)                 │
│ • LLM ruft tariff_search() auf                         │
│ • Backend filtert und rankt Tarife                      │
│ • Ergebnis zurück an LLM                                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 4: EMPFEHLUNG                                     │
│ • Anzeige der Top 3 Tarife                              │
│ • Hervorhebung des günstigsten                          │
│ • Erklärung der Unterschiede                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ Phase 5: NACHFRAGE & ABSCHLUSS                          │
│ • "Benötigst du weitere Informationen?"                 │
│ • Optional: Details zu einzelnen Tarifen                │
│ • Verabschiedung                                        │
└─────────────────────────────────────────────────────────┘
```

---

## Detaillierter Gesprächsfluss

### Phase 1: Begrüßung

**Ziel**: User willkommen heißen und Kontext setzen.

**Beispiel-Dialog**:
```
Bot: Hallo! 👋 Ich helfe dir, die passende Sterbegeldversicherung zu finden. 
     Um dir die besten Angebote zu zeigen, stelle ich dir ein paar kurze Fragen. 
     Bereit? 😊
```

**Prompt-Anweisung**:
```
Beginne das Gespräch mit einer freundlichen Begrüßung und erkläre kurz,
dass du einige Fragen stellen wirst, um passende Tarife zu finden.
```

---

### Phase 2: Bedarfsermittlung

**Ziel**: Die drei Kern-Parameter erfragen (Alter, Gesundheit, Versicherungssumme).

#### 2.1 Parameter: Alter

**Bot-Frage**:
```
Bot: Wie alt bist du?
```

**User-Antwort (Varianten)**:
- ✅ `"45"` → Klar, direkt weiter
- ✅ `"Ich bin 45 Jahre alt"` → Extrahiere Zahl
- ✅ `"45 Jahre"` → Extrahiere Zahl
- ❌ `"Ich bin Mitte 40"` → Bot: "Kannst du mir dein genaues Alter in Jahren nennen?"

**LLM-Anweisung**:
```
Extrahiere das Alter aus der Antwort. Wenn unklar, frage nach einer genauen Zahl.
Akzeptiere Werte zwischen 18 und 99 Jahren.
```

---

#### 2.2 Parameter: Gesundheitszustand

**Bot-Frage**:
```
Bot: Danke! Wie würdest du deinen aktuellen Gesundheitszustand beschreiben?
     (ausgezeichnet / gut / mittel / schlecht)
```

**User-Antwort (Varianten)**:
- ✅ `"gut"` → Direkt gemappt zu "good"
- ✅ `"Ich bin gesund"` → LLM interpretiert als "good"
- ✅ `"habe leichte Beschwerden"` → LLM interpretiert als "fair"
- ❌ `"weiß nicht"` → Bot: "Keine Sorge! Schätze einfach grob ein: ausgezeichnet, gut, mittel oder schlecht?"

**Mapping (Backend)**:
```python
HEALTH_MAPPING = {
    'ausgezeichnet': 'excellent',
    'excellent': 'excellent',
    'sehr gut': 'excellent',
    'gut': 'good',
    'good': 'good',
    'gesund': 'good',
    'mittel': 'fair',
    'fair': 'fair',
    'geht so': 'fair',
    'schlecht': 'poor',
    'poor': 'poor',
    'krank': 'poor'
}
```

**LLM-Anweisung**:
```
Frage nach dem Gesundheitszustand. Akzeptiere natürlichsprachige Antworten
und mappe sie auf: excellent, good, fair, poor.
Wenn extrem vage, frage nochmal mit konkreten Optionen nach.
```

---

#### 2.3 Parameter: Versicherungssumme

**Bot-Frage**:
```
Bot: Perfekt! Welche Versicherungssumme möchtest du absichern?
     (Typische Summen liegen zwischen 3.000 und 10.000 Euro)
```

**User-Antwort (Varianten)**:
- ✅ `"5000"` → Direkt als 5000 interpretiert
- ✅ `"5000 Euro"` → Extrahiere 5000
- ✅ `"ca. 5k"` → Interpretiere als 5000
- ✅ `"zwischen 4000 und 6000"` → Bot: "Verstehe. Welcher Wert ist dir am wichtigsten? Ich empfehle 5000 Euro."
- ❌ `"keine Ahnung"` → Bot: "Für eine durchschnittliche Bestattung werden oft 5.000 Euro empfohlen. Passt das?"

**LLM-Anweisung**:
```
Frage nach der gewünschten Versicherungssumme. Extrahiere eine Zahl in Euro.
Wenn User unsicher ist, schlage 5.000 Euro als Standardwert vor.
Akzeptiere Werte zwischen 2.000 und 15.000 Euro.
```

---

### Phase 3: Tarifsuche (Function Calling)

**Trigger**: LLM hat alle drei Parameter erfasst.

**Function Call** (von LLM generiert):
```json
{
  "name": "tariff_search",
  "arguments": {
    "age": 45,
    "health": "good",
    "coverage_amount": 5000
  }
}
```

**Backend-Verarbeitung**:
1. Lade `tariffs.json`
2. Filtere Tarife:
   - Altersbereich passt
   - Gesundheitsanforderung erfüllt
   - Versicherungssumme ≥ gewünschter Betrag
3. Berechne individuellen Preis (dynamisch)
4. Sortiere nach Preis (aufsteigend)
5. Returniere Top 3

**Function Result** (an LLM zurück):
```json
[
  {
    "name": "Sterbegeld Best",
    "provider": "SecureLife",
    "monthly_premium": 21.28,
    "coverage_amount": 5000,
    "features": ["Keine Wartezeit", "Vollständige Gesundheitsprüfung"]
  },
  {
    "name": "Sterbegeld Komfort",
    "provider": "VersicherungPlus",
    "monthly_premium": 24.92,
    "coverage_amount": 5000,
    "features": ["Keine Gesundheitsprüfung", "24 Monate Wartezeit"]
  },
  {
    "name": "Sterbegeld Premium",
    "provider": "VersicherungPlus",
    "monthly_premium": 37.10,
    "coverage_amount": 8000,
    "features": ["Vereinfachte Gesundheitsprüfung", "12 Monate Wartezeit"]
  }
]
```

---

### Phase 4: Empfehlung

**Ziel**: Tarife klar und verständlich präsentieren.

**Bot-Antwort**:
```
Bot: Ich habe drei passende Tarife für dich gefunden:

1. 🏆 **Sterbegeld Best** (SecureLife)
   💶 21,28 €/Monat | 5.000 € Deckung
   ✅ Keine Wartezeit | ⚕️ Gesundheitsprüfung erforderlich

2. **Sterbegeld Komfort** (VersicherungPlus)
   💶 24,92 €/Monat | 5.000 € Deckung
   ✅ Keine Gesundheitsprüfung | ⏳ 24 Monate Wartezeit

3. **Sterbegeld Premium** (VersicherungPlus)
   💶 37,10 €/Monat | 8.000 € Deckung
   ✅ Vereinfachte Gesundheitsprüfung | ⏳ 12 Monate Wartezeit

➡️ Der günstigste Tarif für dich ist **Sterbegeld Best** für 21,28 € pro Monat.
```

**Formatting-Regeln** (für LLM):
```
Wenn du Tarife präsentierst:
1. Nummeriere sie (1, 2, 3)
2. Markiere den günstigsten mit 🏆
3. Zeige: Tarifname, Anbieter, Preis/Monat, Deckung
4. Liste 1-2 wichtige Features
5. Betone am Ende den günstigsten Tarif
```

---

### Phase 5: Nachfrage & Abschluss

**Bot-Frage**:
```
Bot: Möchtest du mehr Details zu einem der Tarife erfahren, oder hast du weitere Fragen?
```

**User-Antwort (Varianten)**:

#### Szenario A: Nachfrage zu spezifischem Tarif
**User**: `"Was bedeutet Wartezeit?"`

**Bot**:
```
Bot: Gerne! Die Wartezeit ist der Zeitraum nach Vertragsabschluss, in dem bei Tod durch
     Krankheit noch nicht die volle Versicherungssumme ausgezahlt wird. Bei Unfalltod
     gilt meist keine Wartezeit. Für "Sterbegeld Komfort" beträgt sie 24 Monate.
     
     Hast du noch weitere Fragen?
```

#### Szenario B: Vergleich zweier Tarife
**User**: `"Warum ist Sterbegeld Best günstiger als Komfort?"`

**Bot**:
```
Bot: Gute Frage! Sterbegeld Best ist günstiger, weil eine vollständige Gesundheitsprüfung
     erforderlich ist. Bei guter Gesundheit (wie bei dir) sinkt das Risiko für den
     Versicherer, daher der niedrigere Beitrag. Sterbegeld Komfort verzichtet auf die
     Prüfung, ist aber deshalb etwas teurer.
```

#### Szenario C: Abschluss
**User**: `"Das reicht, danke!"`

**Bot**:
```
Bot: Sehr gerne! Viel Erfolg bei deiner Entscheidung. Falls du später noch Fragen hast,
     kannst du jederzeit zurückkommen. Tschüss! 👋
```

---

## Dialog-Strategien

### 1. **Eine Frage pro Antwort** (Fokussierung)

❌ **Schlecht**:
```
Bot: Wie alt bist du und wie ist dein Gesundheitszustand?
```

✅ **Gut**:
```
Bot: Wie alt bist du?
User: 45
Bot: Danke! Wie würdest du deinen Gesundheitszustand beschreiben?
```

**Begründung**: Weniger überfordernd, besonders auf mobilen Geräten.

---

### 2. **Aktive Führung** (Proaktivität)

❌ **Passiv**:
```
Bot: Was möchtest du wissen?
```

✅ **Aktiv**:
```
Bot: Um dir die besten Tarife zu zeigen, brauche ich noch dein Alter. Wie alt bist du?
```

---

### 3. **Fehlertoleranz** (Flexibilität)

**User**: `"Ich weiß nicht genau, vielleicht Mitte 40"`

❌ **Starr**:
```
Bot: ERROR: Bitte gib eine gültige Zahl ein.
```

✅ **Tolerant**:
```
Bot: Kein Problem! Kannst du mir dein ungefähres Alter als Zahl nennen? 
     Zum Beispiel 43, 45 oder 47?
```

---

### 4. **Kontextuelles Verständnis**

**User**: `"Ich bin 45 Jahre alt, gesund und möchte 5000 Euro versichern"`

✅ **LLM erkennt alle drei Parameter auf einmal**:
```
Bot: Super, das sind alle Infos die ich brauche! Einen Moment, ich suche die
     passenden Tarife für dich... ⏳
```

→ Function Call sofort ausführen, nicht noch nachfragen.

---

### 5. **Disambiguation** (Mehrdeutigkeiten klären)

**User**: `"Ich möchte etwas zwischen 4000 und 6000 Euro"`

**Bot**:
```
Bot: Verstanden! Soll ich nach Tarifen mit mindestens 6.000 € Deckung suchen,
     oder reichen dir auch 4.000 €? Ich empfehle 5.000 € als guten Mittelweg.
```

---

## Edge Cases & Fehlerbehandlung

### 1. Keine passenden Tarife

**Szenario**: User ist 90 Jahre alt (außerhalb aller Altersbereiche).

**Bot**:
```
Bot: Leider habe ich keine passenden Tarife für dein Alter gefunden. 
     Die meisten Sterbegeldversicherungen haben ein Höchstalter von 85 Jahren.
     Möchtest du weitere Informationen zu alternativen Bestattungsvorsorgen?
```

---

### 2. Ungültige Eingaben

**User**: `"Ich bin adsfjkl Jahre alt"`

**Bot**:
```
Bot: Das habe ich nicht verstanden. Kannst du mir dein Alter als Zahl nennen?
     Zum Beispiel "45".
```

---

### 3. LLM-Fehler (API nicht erreichbar)

**Fallback-Nachricht**:
```
Bot: Entschuldigung, ich habe gerade technische Probleme. 
     Bitte versuche es in einer Minute erneut. 🙏
```

---

### 4. User weicht vom Thema ab

**User**: `"Wie ist das Wetter?"`

**Bot**:
```
Bot: Gute Frage, aber ich bin nur auf Sterbegeldversicherungen spezialisiert. 😊
     Kann ich dir dabei helfen? Wenn ja, sag mir einfach dein Alter.
```

---

## State-Management (Stateless)

### Konversations-Historie (Client-Side)

**Struktur**:
```json
{
  "messages": [
    {"role": "assistant", "content": "Hallo! Wie alt bist du?"},
    {"role": "user", "content": "45"},
    {"role": "assistant", "content": "Danke! Wie ist dein Gesundheitszustand?"},
    {"role": "user", "content": "gut"}
  ],
  "extracted_params": {
    "age": 45,
    "health": "good",
    "coverage_amount": null
  }
}
```

**Client sendet gesamte Historie bei jedem Request**:
```json
POST /api/chat
{
  "message": "5000 Euro",
  "conversation_history": [...]
}
```

---

## Prompt-Templates

### System-Prompt (Konversations-Regeln)

```
Du bist ein KI-Versicherungsberater für Sterbegeldversicherungen.

# DEINE AUFGABE:
Führe ein freundliches, fokussiertes Gespräch, um folgende Parameter zu erfassen:
1. Alter (18-99 Jahre)
2. Gesundheitszustand (excellent, good, fair, poor)
3. Gewünschte Versicherungssumme (2.000-15.000 €)

# REGELN:
- Stelle MAXIMAL EINE Frage pro Antwort
- Sei freundlich und einfühlsam (sensibles Thema!)
- Duze den Kunden
- Verwende kurze, klare Sätze
- Wenn alle Parameter vorliegen, rufe SOFORT die Funktion tariff_search() auf

# WENN ALLE PARAMETER VORLIEGEN:
Rufe tariff_search(age=X, health=Y, coverage_amount=Z) auf.

# NACH DER TARIFSUCHE:
Präsentiere die Top 3 Tarife übersichtlich:
1. 🏆 [Günstigster] - Preis, Deckung, Features
2. [Zweitgünstigster] - ...
3. [Drittgünstigster] - ...

Betone, welcher Tarif der günstigste ist.

# WAS DU NIEMALS TUN DARFST:
- Mehrere Fragen auf einmal stellen
- Tarife erfinden, die nicht aus tariff_search() kamen
- Rechtliche Beratung geben
- Versicherungsjargon verwenden ohne Erklärung
```

---

## Testing & Qualitätssicherung

### Test-Dialoge

#### Test 1: Happy Path
```
Bot: Hallo! Wie alt bist du?
User: 45
Bot: Danke! Wie ist dein Gesundheitszustand?
User: gut
Bot: Perfekt! Welche Versicherungssumme möchtest du?
User: 5000 Euro
Bot: [Tarifsuche...] Ich habe drei Tarife gefunden: ...
```

#### Test 2: Alle Parameter auf einmal
```
User: Ich bin 45 Jahre alt, gesund und möchte 5000 Euro versichern
Bot: [Tarifsuche...] Ich habe drei Tarife gefunden: ...
```

#### Test 3: Ungültige Eingabe
```
Bot: Wie alt bist du?
User: adsfjkl
Bot: Das habe ich nicht verstanden. Kannst du mir dein Alter als Zahl nennen?
```

#### Test 4: Keine passenden Tarife
```
User: Ich bin 95 Jahre alt
Bot: Leider habe ich keine passenden Tarife für dein Alter gefunden...
```

---

## Metriken zur Evaluation

### Dialog-Qualität

| Metrik | Ziel | Messung |
|--------|------|---------|
| **Fragen pro Conversation** | ≤ 5 | Anzahl Bot-Nachrichten bis Empfehlung |
| **Erfolgsrate** | > 80% | % der Dialoge, die zu Tarifempfehlung führen |
| **Fehlerrate** | < 10% | % der Dialoge mit LLM-Fehler oder "nicht verstanden" |
| **User-Satisfaction** | > 4/5 | Umfrage nach Gespräch (später) |

### Prompt-Optimierung

**Feedback-Loop**:
1. Logs analysieren (welche Dialoge scheitern?)
2. Prompt anpassen (z.B. klarere Anweisungen)
3. A/B-Test mit neuer Version
4. Beste Version produktiv setzen

---

## Zusammenfassung

| Aspekt | Umsetzung |
|--------|-----------|
| **Gesprächsfluss** | 5 Phasen: Begrüßung → Bedarfsermittlung → Suche → Empfehlung → Abschluss |
| **Dialog-Strategie** | Eine Frage pro Antwort, aktive Führung, fehlertoler Fehlertoleranz |
| **Parameter-Extraktion** | LLM interpretiert natürlichsprachige Antworten |
| **Tarifempfehlung** | Top 3, günstigster hervorgehoben |
| **Fehlerbehandlung** | Graceful Fallbacks, klare Fehlermeldungen |
| **State-Management** | Stateless (Client-Side History) |

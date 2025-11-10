# GPT-5 Reasoning Tokens - Wichtige Information

## Was sind Reasoning Tokens?

GPT-5 nutzt ein neues Feature: **Interne Reasoning Tokens**

Bevor das Modell antwortet, "denkt" es intern nach und verbraucht dafür Tokens. Diese Reasoning Tokens zählen gegen das `max_completion_tokens` Limit.

## Beispiel aus den Logs

```json
{
  "finish_reason": "length",
  "message": {
    "content": "",  // ❌ LEER!
    ...
  },
  "completion_tokens": 500,
  "completion_tokens_details": {
    "reasoning_tokens": 500,  // Alle Tokens für Reasoning verbraucht
    "accepted_prediction_tokens": 0
  }
}
```

**Problem**: Bei `max_tokens=500` wurden alle 500 für Reasoning verbraucht → 0 Tokens für den Output → leere Antwort!

## Empfohlene max_tokens Werte

| Anwendungsfall | max_tokens | Formel |
|----------------|------------|---------|
| **Normale Antworten** | 2000 | 500 (reasoning) + 1500 (output) |
| **Tarif-Präsentationen** | 3000 | 500 (reasoning) + 2500 (output) |
| **Komplexe Analysen** | 4000+ | 500 (reasoning) + 3500+ (output) |

## Code-Beispiel

```python
# ❌ FALSCH - Zu wenig für GPT-5
response = client.chat.completions.create(
    model="gpt-5",
    messages=messages,
    max_completion_tokens=500  # ← Alle für Reasoning verbraucht!
)

# ✅ RICHTIG - Genug für Reasoning + Output
response = client.chat.completions.create(
    model="gpt-5",
    messages=messages,
    max_completion_tokens=2000  # ← 500 Reasoning + 1500 Output
)
```

## Wie erkennt man das Problem?

**Symptome:**
- Leere `content` in der Response
- `finish_reason: "length"`
- `reasoning_tokens` ≈ `completion_tokens`
- `completion_tokens` = Ihr `max_tokens` Limit

**Lösung:**
- Erhöhe `max_tokens` um mindestens 500-1000

## Performance-Überlegungen

**Trade-off:**
- ✅ **Höhere max_tokens** = Vollständige Antworten, bessere Qualität
- ❌ **Höhere max_tokens** = Etwas langsamer, höhere API-Kosten

**Unsere Wahl:**
- 2000 für normale Antworten (guter Kompromiss)
- 3000 für Tarif-Präsentationen (brauchen mehr Platz)

## Weitere Ressourcen

- OpenAI GPT-5 Docs: [Reasoning Tokens Explained](https://platform.openai.com/docs/models/gpt-5)
- Unser Prompt Caching reduziert Input-Tokens um 50-90%
- Streaming zeigt Antworten progressiv (gefühlte Wartezeit -90%)

## Update-Historie

- **10.11.2025**: Problem identifiziert, max_tokens von 500 auf 2000 erhöht
- **Resultat**: ✅ Keine leeren Antworten mehr, alle Tests bestehen

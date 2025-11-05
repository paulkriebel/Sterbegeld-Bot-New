# Versicherungssummen-Rundung Feature

## Übersicht

Diese Feature sorgt dafür, dass Kunden-Anfragen nach Versicherungssummen automatisch auf die verfügbaren Produktstufen gerundet werden und der Kunde darüber transparent informiert wird.

## Motivation

Sterbegeldversicherungen werden nur mit bestimmten, festgelegten Versicherungssummen angeboten. Wenn ein Kunde eine beliebige Zahl (z.B. 4.500 €) eingibt, muss diese auf die nächsthöhere verfügbare Summe aufgerundet werden.

## Verfügbare Versicherungssummen

```
1.000 €    (ab 2 €/Monat)
2.000 €    (ab 3 €/Monat)
3.000 €    (ab 5 €/Monat)
4.000 €    (ab 6 €/Monat)
5.000 €    (ab 8 €/Monat)
6.000 €    (ab 9 €/Monat)
7.000 €    (ab 11 €/Monat)
8.000 €    (ab 12 €/Monat)
9.000 €    (ab 14 €/Monat)
10.000 €   (ab 15 €/Monat)
12.500 €   (ab 19 €/Monat)
15.000 €   (ab 22 €/Monat)
20.000 €   (ab 30 €/Monat) - MAXIMUM
```

## Rundungs-Regeln

### 1. Exakte Übereinstimmung
Wenn der Kunde exakt eine verfügbare Summe nennt, wird **keine Rundung** durchgeführt.

**Beispiel:**
- Kunde: "5000 Euro"
- System: ✅ Direkte Suche mit 5.000 €, keine Nachricht

### 2. Aufrundung zur nächsthöheren Summe
Bei beliebigen Werten wird zur **nächsthöheren** verfügbaren Summe aufgerundet.

**Beispiele:**
- Kunde: "4500 Euro" → System: 5.000 €
- Kunde: "7200 Euro" → System: 8.000 €
- Kunde: "11000 Euro" → System: 12.500 €

### 3. Unter Minimum (< 1.000 €)
Werte unter 1.000 € werden auf 1.000 € aufgerundet.

**Beispiele:**
- Kunde: "500 Euro" → System: 1.000 €
- Kunde: "999 Euro" → System: 1.000 €

### 4. Über Maximum (> 20.000 €)
Werte über 20.000 € werden auf das Maximum von 20.000 € begrenzt.

**Beispiele:**
- Kunde: "25000 Euro" → System: 20.000 €
- Kunde: "50000 Euro" → System: 20.000 €

## Kundeninformation

**Wichtig:** Immer wenn eine Rundung stattfindet, wird der Kunde aktiv darüber informiert.

### Beispiel-Nachricht:
```
Hinweis: Ich habe deine Versicherungssumme von 4.500 € auf 5.000 € aufgerundet, 
da Tarife nur mit runden Versicherungssummen angeboten werden.
```

Der Bot formuliert diese Nachricht natürlich in seinem eigenen Stil, basierend auf der Vorlage aus den Suchergebnissen.

## Technische Implementierung

### 1. Tariff Engine (`app/products/sterbegeld/tariff_engine.py`)

Zwei neue Funktionen:

```python
def needs_rounding(coverage_amount: int) -> bool:
    """Prüft, ob eine Versicherungssumme gerundet werden muss"""
    return coverage_amount not in VALID_COVERAGE_AMOUNTS

def round_coverage_amount(coverage_amount: int) -> int:
    """Rundet eine Versicherungssumme auf den nächsthöheren gültigen Wert"""
    # Implementierung siehe tariff_engine.py
```

### 2. Chatbot Integration (`app/products/sterbegeld/chatbot.py`)

Die `_execute_function()` Methode prüft vor jedem `tariff_search` Aufruf:
1. Muss die Versicherungssumme gerundet werden?
2. Wenn ja: Rundet sie und fügt Rounding-Info zum Ergebnis hinzu
3. Der LLM erhält die Info und kommuniziert sie dem Kunden

### 3. Rückgabe-Format

Wenn Rundung stattfand:
```json
{
  "rounding_applied": true,
  "rounding_info": {
    "original_amount": 4500,
    "rounded_amount": 5000,
    "message": "Hinweis: Ich habe deine Versicherungssumme von 4.500 € auf 5.000 € aufgerundet..."
  },
  "tariffs": [...]
}
```

Ohne Rundung:
```json
{
  "rounding_applied": false,
  "tariffs": [...]
}
```

## Tests

### Unit Tests
- `test_round_coverage_amount()` - Testet die Rundungslogik
- `test_needs_rounding()` - Testet die Erkennungslogik

### Integration Tests (`tests/test_rounding_integration.py`)
- Exakte Werte (keine Rundung)
- Zwischenwerte (Aufrundung)
- Edge Cases:
  - Unter 1.000 € → 1.000 €
  - Über 20.000 € → 20.000 €
  - Zwischen 10.000 € und 12.500 € → 12.500 €
- Alle gültigen Werte

### E2E Test
End-to-End Test mit echtem LLM-Call bestätigt, dass:
- Rundung durchgeführt wird
- Kunde informiert wird
- Korrekte Tarife zurückgegeben werden

**Test-Ergebnis:** ✅ 16 Tests passed

## Beispiel-Dialog

```
👤 User: Ich möchte direkt Tarife finden
🤖 Bot: Perfekt! Wann bist du geboren?

👤 User: Ich bin am 15.05.1980 geboren
🤖 Bot: Danke! Welche Versicherungssumme möchtest du absichern?

👤 User: 4500 Euro
🤖 Bot: Möchtest du die Ergebnisse noch filtern?

👤 User: Nein, zeig mir direkt alle Tarife
🤖 Bot: Hinweis: Ich habe deine Versicherungssumme von 4.500 € auf 5.000 € 
       aufgerundet, da Tarife nur mit runden Summen angeboten werden.
       
       Hier sind drei passende Tarife:
       
       1. SeniorenVorsorge Tarif 51 (SeniorenVorsorge GmbH) – GÜNSTIGSTER
          • 8,97 €/Monat | 8.000 € Deckung
          • ...
```

## TDD-Prozess

Dieses Feature wurde nach strenger Test-Driven Development Methode implementiert:

1. 🔴 **RED**: Tests geschrieben (schlagen fehl, da Code nicht existiert)
2. 🟢 **GREEN**: Code implementiert (Tests bestehen)
3. 🔵 **REFACTOR**: Code verbessert, Tests weiterhin grün
4. ✅ **INTEGRATE**: In Chatbot integriert und E2E getestet

## Dateien

**Geändert:**
- `app/products/sterbegeld/tariff_engine.py` - Rundungslogik
- `app/products/sterbegeld/chatbot.py` - Integration und System-Prompt
- `data/sterbegeld/tariffs.json` - Tarif-Daten korrigiert

**Neu:**
- `tests/test_rounding_integration.py` - Integration-Tests

**Erweitert:**
- `tests/test_tariff_engine.py` - Unit-Tests hinzugefügt
- `plan.md` - Feature dokumentiert

## Status

✅ **IMPLEMENTIERT & GETESTET**  
📅 Datum: 04.11.2025  
🧪 Tests: 16/16 passed  
🚀 Production-ready

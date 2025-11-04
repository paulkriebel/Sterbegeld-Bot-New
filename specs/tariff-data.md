# Tarifdaten-Spezifikation

## Zweck
Definition der Datenstruktur für Sterbegeldversicherungs-Tarife und deren Verwaltung.

## Datenformat

### Primärformat: JSON
**Datei**: `data/sterbegeld/tariffs.json`

**Begründung**:
- Einfach zu lesen und zu bearbeiten
- Native Python-Support
- Geeignet für Prototyp (< 100 Tarife)
- Später migrierbar zu CSV oder Datenbank

---

## JSON-Schema

### Tarif-Struktur (Single Object)

**WICHTIG**: Preise sind **fest** (vom Versicherungsanbieter vorgegeben), **keine dynamische Kalkulation**.

```json
{
  "id": "tariff_basis_001",
  "name": "Sterbegeld Basis",
  "provider": "VersicherungPlus",
  "monthly_premium": 10.50,
  "coverage_amount": 3000,
  "age_min": 40,
  "age_max": 75,
  "health_requirement": "none",
  "waiting_period_illness_months": 24,
  "waiting_period_accident_months": 0,
  "features": [
    "Keine Gesundheitsprüfung",
    "Sofortiger Versicherungsschutz bei Unfall"
  ]
}
```

### Feld-Definitionen

| Feld | Typ | Pflicht | Beschreibung |
|------|-----|---------|--------------|
| `id` | string | Ja | Eindeutige Tarif-ID (interne Referenz) |
| `name` | string | Ja | Anzeigename des Tarifs |
| `provider` | string | Ja | Versicherungsanbieter |
| `monthly_premium` | float | Ja | **Fester** Monatsbeitrag (vom Anbieter vorgegeben) |
| `coverage_amount` | int | Ja | Versicherungssumme in Euro |
| `age_min` | int | Ja | Mindestalter für Abschluss |
| `age_max` | int | Ja | Höchstalter für Abschluss |
| `health_requirement` | string | Ja | `"none"`, `"simplified"`, `"full"` |
| `waiting_period_illness_months` | int | Ja | Wartezeit bei Tod durch Krankheit (Monate) |
| `waiting_period_accident_months` | int | Ja | Wartezeit bei Unfalltod (meist 0) |
| `features` | array | Nein | Besondere Leistungsmerkmale |

---

## Beispiel-Datensatz

### `data/sterbegeld/tariffs.json`

```json
[
  {
    "id": "tariff_basis_001",
    "name": "Sterbegeld Basis",
    "provider": "VersicherungPlus",
    "monthly_premium": 10.50,
    "coverage_amount": 3000,
    "age_min": 40,
    "age_max": 75,
    "health_requirement": "none",
    "waiting_period_illness_months": 24,
    "waiting_period_accident_months": 0,
    "features": [
      "Keine Gesundheitsprüfung",
      "Sofortiger Versicherungsschutz bei Unfall"
    ]
  },
  {
    "id": "tariff_komfort_002",
    "name": "Sterbegeld Komfort",
    "provider": "VersicherungPlus",
    "monthly_premium": 17.80,
    "coverage_amount": 5000,
    "age_min": 40,
    "age_max": 75,
    "health_requirement": "none",
    "waiting_period_illness_months": 24,
    "waiting_period_accident_months": 0,
    "features": [
      "Keine Gesundheitsprüfung",
      "Höhere Deckungssumme"
    ]
  },
  {
    "id": "tariff_premium_003",
    "name": "Sterbegeld Premium",
    "provider": "VersicherungPlus",
    "monthly_premium": 26.50,
    "coverage_amount": 8000,
    "age_min": 40,
    "age_max": 80,
    "health_requirement": "simplified",
    "waiting_period_illness_months": 12,
    "waiting_period_accident_months": 0,
    "features": [
      "Vereinfachte Gesundheitsprüfung",
      "Kürzere Wartezeit",
      "Bis 80 Jahre abschließbar"
    ]
  },
  {
    "id": "tariff_best_004",
    "name": "Sterbegeld Best",
    "provider": "SecureLife",
    "monthly_premium": 15.20,
    "coverage_amount": 5000,
    "age_min": 18,
    "age_max": 65,
    "health_requirement": "full",
    "waiting_period_illness_months": 0,
    "waiting_period_accident_months": 0,
    "features": [
      "Keine Wartezeit bei guter Gesundheit",
      "Günstigster Beitrag",
      "Vollständige Gesundheitsprüfung erforderlich"
    ]
  },
  {
    "id": "tariff_senior_005",
    "name": "Sterbegeld Senior",
    "provider": "SecureLife",
    "monthly_premium": 45.00,
    "coverage_amount": 5000,
    "age_min": 65,
    "age_max": 85,
    "health_requirement": "none",
    "waiting_period_illness_months": 36,
    "waiting_period_accident_months": 0,
    "features": [
      "Speziell für Senioren",
      "Keine Gesundheitsprüfung",
      "Bis 85 Jahre abschließbar"
    ]
  }
]
```

---

## ~~Dynamische Beitragskalkulation~~ ❌ NICHT BENÖTIGT

**Wichtig**: Tarife enthalten bereits **feste Preise** vom Versicherungsanbieter.  
Es gibt **keine dynamische Berechnung** basierend auf Alter/Gesundheit.

**Stattdessen**: Filterung nach passenden Tarifen (siehe unten).

---

## Filter- und Ranking-Logik

### 1. Filterkriterien (MUST MATCH)

```python
def filter_tariffs(tariffs: List[Dict], age: int, health: str, coverage: int) -> List[Dict]:
    """
    Filtert Tarife nach harten Kriterien.
    """
    matches = []
    
    for tariff in tariffs:
        # Altersbereich
        if not (tariff['age_min'] <= age <= tariff['age_max']):
            continue
        
        # Deckungssumme (muss mindestens gewünschte Summe sein)
        if tariff['coverage_amount'] < coverage:
            continue
        
        # Gesundheitsprüfung (vereinfacht)
        if not meets_health_requirement(health, tariff['health_requirement']):
            continue
        
        matches.append(tariff)
    
    return matches
```

### 2. Gesundheitsprüfungs-Logik

```python
def meets_health_requirement(customer_health: str, tariff_requirement: str) -> bool:
    """
    Prüft, ob der Kunde die Gesundheitsanforderungen erfüllt.
    
    Hierarchie:
    - 'none': Jeder wird akzeptiert
    - 'simplified': Nur excellent, good, fair
    - 'full': Nur excellent, good
    """
    requirements = {
        'none': ['excellent', 'good', 'fair', 'poor'],
        'simplified': ['excellent', 'good', 'fair'],
        'full': ['excellent', 'good']
    }
    
    return customer_health in requirements.get(tariff_requirement, [])
```

### 3. Ranking (SORT)

**Primäres Kriterium**: Niedrigster Preis

```python
def rank_tariffs(tariffs: List[Dict]) -> List[Dict]:
    """
    Sortiert Tarife nach Preis (aufsteigend).
    Kein Alter/Gesundheit nötig - Preise sind fest!
    """
    # Sortiere nach festem Preis
    tariffs.sort(key=lambda t: t['monthly_premium'])
    
    return tariffs[:3]  # Top 3
```

---

## Daten-Validierung

### Schema-Validierung (Optional)

```python
import jsonschema

TARIFF_SCHEMA = {
    "type": "object",
    "required": ["id", "name", "provider", "monthly_premium_base", 
                 "coverage_amount", "age_min", "age_max", "health_requirement"],
    "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "provider": {"type": "string"},
        "monthly_premium_base": {"type": "number", "minimum": 0},
        "coverage_amount": {"type": "integer", "minimum": 1000},
        "age_min": {"type": "integer", "minimum": 0, "maximum": 100},
        "age_max": {"type": "integer", "minimum": 0, "maximum": 100},
        "health_requirement": {"enum": ["none", "simplified", "full"]},
        "waiting_period_illness_months": {"type": "integer", "minimum": 0},
        "waiting_period_accident_months": {"type": "integer", "minimum": 0}
    }
}

def validate_tariff(tariff: Dict) -> bool:
    try:
        jsonschema.validate(tariff, TARIFF_SCHEMA)
        return True
    except jsonschema.ValidationError as e:
        logger.error(f"Invalid tariff: {e}")
        return False
```

---

## CSV-Alternative (Optional)

### Format: `data/sterbegeld/tariffs.csv`

```csv
id,name,provider,monthly_premium_base,coverage_amount,age_min,age_max,health_requirement,waiting_period_illness_months,waiting_period_accident_months
tariff_basis_001,Sterbegeld Basis,VersicherungPlus,10.50,3000,40,75,none,24,0
tariff_komfort_002,Sterbegeld Komfort,VersicherungPlus,17.80,5000,40,75,none,24,0
tariff_premium_003,Sterbegeld Premium,VersicherungPlus,26.50,8000,40,80,simplified,12,0
tariff_best_004,Sterbegeld Best,SecureLife,15.20,5000,18,65,full,0,0
tariff_senior_005,Sterbegeld Senior,SecureLife,45.00,5000,65,85,none,36,0
```

**Vorteile**:
- Einfacher zu editieren in Excel/Google Sheets
- Geringere Dateigröße

**Nachteile**:
- Keine nested Objekte (premium_calculation)
- Weniger flexibel

---

## Daten-Migration (Future)

### Zu PostgreSQL/SQLite

```sql
CREATE TABLE tariffs (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    provider VARCHAR(100) NOT NULL,
    monthly_premium_base DECIMAL(10, 2) NOT NULL,
    coverage_amount INTEGER NOT NULL,
    age_min INTEGER NOT NULL,
    age_max INTEGER NOT NULL,
    health_requirement VARCHAR(20) NOT NULL,
    waiting_period_illness_months INTEGER DEFAULT 0,
    waiting_period_accident_months INTEGER DEFAULT 0,
    features JSONB,
    premium_calculation JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_coverage ON tariffs(coverage_amount);
CREATE INDEX idx_age_range ON tariffs(age_min, age_max);
```

---

## Testdaten-Generierung

### Script: `scripts/generate_tariffs.py`

```python
import json
import random

def generate_test_tariffs(count: int = 20) -> List[Dict]:
    """
    Generiert Test-Tarife für Entwicklung/Testing.
    """
    providers = ["VersicherungPlus", "SecureLife", "BestProtect", "SafeGuard"]
    health_reqs = ["none", "simplified", "full"]
    
    tariffs = []
    for i in range(count):
        tariffs.append({
            "id": f"tariff_test_{i:03d}",
            "name": f"Test-Tarif {i+1}",
            "provider": random.choice(providers),
            "monthly_premium_base": round(random.uniform(10, 50), 2),
            "coverage_amount": random.choice([3000, 5000, 8000, 10000]),
            "age_min": random.choice([18, 40, 50]),
            "age_max": random.choice([65, 75, 85]),
            "health_requirement": random.choice(health_reqs),
            "waiting_period_illness_months": random.choice([0, 12, 24, 36]),
            "waiting_period_accident_months": 0
        })
    
    return tariffs

# Usage
tariffs = generate_test_tariffs(20)
with open('data/sterbegeld/tariffs.json', 'w', encoding='utf-8') as f:
    json.dump(tariffs, f, indent=2, ensure_ascii=False)
```

---

## Daten-Erweiterungen (Future)

### 1. Historische Tarife
Für Analyse und Vergleich:
```json
{
  "id": "tariff_basis_001",
  "versions": [
    {"valid_from": "2024-01-01", "monthly_premium_base": 10.00},
    {"valid_from": "2025-01-01", "monthly_premium_base": 10.50}
  ]
}
```

### 2. Multi-Produkt-Unterstützung
Gleiche Struktur für andere Versicherungen:
```
data/
├── sterbegeld/
│   └── tariffs.json
├── haftpflicht/
│   └── tariffs.json
└── krankenversicherung/
    └── tariffs.json
```

### 3. Regionale Unterschiede
```json
{
  "id": "tariff_basis_001",
  "regional_premiums": {
    "DE-BY": 10.50,  // Bayern
    "DE-BE": 11.00,  // Berlin
    "DE-NW": 10.80   // NRW
  }
}
```

---

## Zusammenfassung

| Aspekt | Entscheidung | Begründung |
|--------|--------------|------------|
| **Format** | JSON | Einfach, flexibel, Python-nativ |
| **Speicherort** | `data/sterbegeld/tariffs.json` | Klare Struktur, produkt-spezifisch |
| **Kalkulation** | ❌ Keine - Feste Preise | Tarife vom Anbieter vorgegeben |
| **Filterlogik** | Python-Funktion | Schnell genug für < 100 Tarife |
| **Ranking** | Preis (aufsteigend) | Erfüllt Anforderung "günstigster Tarif" |
| **Validierung** | Optional (JSON Schema) | Gut für Datenqualität, nicht kritisch für Prototyp |

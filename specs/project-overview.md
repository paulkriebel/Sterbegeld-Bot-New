# Projektübersicht: Sterbegeld-Tarifvergleichs-Chatbot

## Zweck

Entwicklung eines **Rapid Prototypes** für einen **LLM-basierten Chatbot**, der Kunden bei der Auswahl einer passenden **Sterbegeldversicherung** unterstützt. Der Chatbot führt einen natürlichsprachigen Dialog, erfasst relevante Kundendaten und empfiehlt den günstigsten Tarif basierend auf den Kundenpräferenzen.

## Projektziele

### Primäres Ziel
**Benutzerfreundlichkeit** – Der Prototyp soll Produktmanagern eine intuitive, dialogbasierte Tarifvergleichslösung demonstrieren.

### Sekundäre Ziele
- **Schnelle Umsetzung**: Fokus auf einfache, bewährte Technologien
- **Strukturelle Erweiterbarkeit**: Modulare Architektur für spätere Integration anderer Versicherungsprodukte
- **Evaluierbarkeit**: Transparente Chatbot-Logik zur Optimierung des Prompt-Engineerings

## Zielgruppe
- **Primär**: Produktmanager bei CHECK24 zur internen Evaluierung
- **Sekundär**: Potenzielle Erweiterung auf externe Testnutzer

## Projektumfang (Scope)

### ✅ Im Scope (Initial)
- Vollständiger vertikaler Prototyp für Sterbegeldversicherung
- Conversational UI für mobile Endgeräte
- Aktive Abfrage von Kundenpräferenzen (Alter, Gesundheitszustand, Versicherungssumme, Beitrag)
- Empfehlung des günstigsten Tarifs
- Stateless Architektur (keine Session-Persistierung)
- Lokales Hosting

### ⏳ Explizit für später vorgesehen
- Integration weiterer Versicherungsprodukte
- UI-Bibliotheken (Material UI, Tailwind)
- A/B-Testing verschiedener Prompt-Strategien
- Session-Management mit Konversations-Historie
- DSGVO-konforme Datenhaltung
- Cloud-Deployment

### ❌ Explizit nicht im Scope
- Vertragsbabschluss (endet bei Tarifauswahl)
- CHECK24-Integration (Standalone-Prototyp)
- Produktionsreife Security-Maßnahmen
- Legal Disclaimers

## Erfolgskriterien

### Funktional
1. ✅ Chatbot führt vollständigen Dialog zur Erfassung aller relevanten Parameter
2. ✅ Korrekte Tarifempfehlung basierend auf Eingaben
3. ✅ Flüssige, natürlichsprachige Konversation in deutscher Sprache

### Nicht-funktional
1. ✅ Mobile-optimierte Darstellung (responsive)
2. ✅ Antwortzeit < 5 Sekunden pro Chatbot-Antwort
3. ✅ Einfache lokale Installation (< 5 Minuten Setup)
4. ✅ Debug-Panel zur Nachvollziehbarkeit des LLM-Verhaltens

## Kernkomponenten

1. **Generische Versicherungs-Tarifvergleichs-Schicht**
   - Definiert die grundlegende Chatbot-Logik und Prompt-Struktur
   
2. **Produktspezifische Schicht: Sterbegeldversicherung**
   - Produktlogik-Prompt (Funktionsweise, Berechnungsgrundlagen)
   - Mehrdimensionale Tarif-Tabelle (JSON/CSV)
   - Interaktionsstil-Prompt (bevorzugte Gesprächsführung)

3. **Web-Interface**
   - Links: Chat-Oberfläche (iPhone-Screen-Stil)
   - Rechts: Debug-Panel (LLM-Prompts & Responses)
   - Unten: Weiteres Frontend zur Eingabe der drei Kern-Inputs

## Technologie-Entscheidungen (High-Level)

- **Backend**: Python (Flask)
- **LLM**: OpenAI GPT-5 ✅
- **Frontend**: Minimalistisch (HTML/CSS/JavaScript, Flask Templates)
- **Datenhaltung**: Statische JSON-Dateien (feste Preise)
- **Deployment**: Lokaler Server (localhost)

## Risiken & Annahmen

### Risiken
- **LLM-Halluzinationen**: Chatbot könnte falsche Tarifempfehlungen geben
  - *Mitigation*: Strukturierte Outputs via Function Calling, explizite Prompt-Constraints
- **Komplexität der Produktlogik**: Reale Versicherungslogik könnte zu komplex für Prompts sein
  - *Mitigation*: Vereinfachte Beispiel-Tarife für Prototyp

### Annahmen
- Produktmanager haben Zugriff auf moderne Browser (Chrome/Safari)
- OpenAI API ist erreichbar (Internet-Verbindung erforderlich)
- Keine rechtlichen Einschränkungen für Prototyp-Testing

## Nächste Schritte
Siehe detaillierte Spezifikationen in den domänenspezifischen Dokumenten (`specs/`) und den Implementierungsplan in `SPECS.md`.

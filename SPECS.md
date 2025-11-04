# Spezifikations-Übersicht: Sterbegeld-Tarifvergleichs-Chatbot

**Projekt**: Rapid Prototype – LLM-basierter Versicherungs-Tarifvergleichs-Chatbot (CHECK24)  
**Produkt**: Sterbegeldversicherung  
**Zielgruppe**: Produktmanager (interne Evaluierung)  
**Status**: ✅ Spezifikationsphase abgeschlossen

---

## 📋 Projektübersicht

Entwicklung eines **Rapid Prototypes** für einen **LLM-basierten Chatbot**, der Kunden bei der Auswahl einer passenden **Sterbegeldversicherung** unterstützt. Der Chatbot führt einen natürlichsprachigen Dialog, erfasst relevante Kundendaten (Alter, Gesundheitszustand, Versicherungssumme) und empfiehlt den günstigsten Tarif.

### Hauptziele
1. **Benutzerfreundlichkeit**: Intuitive, dialogbasierte Tarifauswahl
2. **Schnelle Umsetzung**: Fokus auf bewährte, einfache Technologien
3. **Erweiterbarkeit**: Modulare Architektur für spätere Multi-Produkt-Integration
4. **Evaluierbarkeit**: Transparente Chatbot-Logik mit Debug-Panel

### Technologie-Stack
- **Backend**: Python (Flask)
- **Frontend**: Vanilla HTML/CSS/JavaScript (Mobile-First)
- **LLM**: OpenAI GPT-5 ✅
- **Daten**: Statische JSON-Dateien (feste Preise)
- **Deployment**: Lokal (localhost)

---

## 📚 Spezifikationsdokumente

| Datei | Beschreibung |
|-------|--------------|
| [project-overview.md](specs/project-overview.md) | Projektziele, Scope, Erfolgskriterien, Risiken & Annahmen |
| [architecture.md](specs/architecture.md) | Gesamtarchitektur, Technologie-Stack, Datenfluss, Modulare Schichten |
| [frontend.md](specs/frontend.md) | UI-Design (Mobile-First), Layout, Komponenten, Interaktionsflows |
| [backend.md](specs/backend.md) | API-Endpunkte, Core-Module, Projektstruktur, Fehlerbehandlung |
| [llm-integration.md](specs/llm-integration.md) | LLM-Modell, Prompt-Engineering, Function Calling, Konversations-Management |
| [tariff-data.md](specs/tariff-data.md) | Tarifdaten-Struktur (JSON), Dynamische Kalkulation, Filter- & Ranking-Logik |
| [chatbot-logic.md](specs/chatbot-logic.md) | Gesprächsfluss (5 Phasen), Dialogstrategien, Edge Cases, Test-Dialoge |
| [deployment.md](specs/deployment.md) | Deployment-Strategie, Environment Setup, Monitoring, Troubleshooting |
| [future-enhancements.md](specs/future-enhancements.md) | Geplante Features (Multi-Produkt, RAG, A/B-Testing, etc.) |

---

## 🎯 Kernfunktionen (Initial)

### ✅ Conversational UI
- **Chat-Interface**: iPhone-Style, responsive (Mobile-First)
- **Debug-Panel**: Vereinfacht - nur LLM-Response anzeigen
- ~~**Prompt-Config-Panel**~~: ❌ Entfällt (Phase 2)

### ✅ Chatbot-Logik
- **5-Phasen-Dialog**: Begrüßung → Bedarfsermittlung → Tarifsuche → Empfehlung → Abschluss
- **Aktive Abfrage**: Chatbot fragt nacheinander Alter, Gesundheitszustand, Versicherungssumme ab
- **Function Calling**: LLM ruft `tariff_search()` auf, wenn alle Parameter vorliegen

### ✅ Tarifvergleich
- **Feste Preise**: Tarife mit vorgegebenen Preisen (vom Anbieter)
- **Filterlogik**: Altersbereich, Gesundheitsanforderungen, Versicherungssumme
- **Ranking**: Günstigster Tarif zuerst (Top 3 Anzeige)

### ✅ Technische Basis
- **Stateless Architecture**: Keine Session-Speicherung (Client-Side History)
- **Einfaches Logging**: Console + File (`logs/app.log`)
- **Modulare Struktur**: Generische Chatbot-Schicht + Produktspezifische Schicht

---

## 🚫 Explizit NICHT im Scope (Initial)

| Feature | Geplant für |
|---------|-------------|
| Vertragsbabschluss | Phase 5+ (nach erfolgreicher Evaluierung) |
| CHECK24-Integration | Produktions-Phase |
| Session-Management | Phase 3 (bei 100+ täglichen Nutzern) |
| UI-Frameworks (Tailwind, Material UI) | Phase 2 (nach Prototyp) |
| A/B-Testing | Phase 3 (Optimierung) |
| RAG (Retrieval-Augmented Generation) | Phase 4 (bei 1000+ Tarifen) |
| DSGVO-Compliance | Phase 5 (bei echten Kunden) |
| Multi-Produkt-Support | Phase 2 (nach erfolgreicher Evaluierung) |

---

## 📈 Implementierungsplan

### Phasen-Übersicht

| Phase | Fokus | Dauer (geschätzt) | Status |
|-------|-------|-------------------|--------|
| **Phase 1** | Projekt-Setup & Datenmodelle | 1-2 Tage | TBD |
| **Phase 2** | Backend-Core & LLM-Integration | 2-3 Tage | TBD |
| **Phase 3** | Frontend-Entwicklung | 2-3 Tage | TBD |
| **Phase 4** | Integration & Testing | 1-2 Tage | TBD |
| **Phase 5** | Feinschliff & Deployment | 1 Tag | TBD |
| **GESAMT** | | **7-11 Tage** ⚡ | TBD |

---

### Phase 1: Projekt-Setup & Datenmodelle (1-2 Tage) ⚡

| # | Aufgabe | Key Deliverables | Related Specs | Dauer | Status |
|---|---------|------------------|---------------|-------|--------|
| 1.1 | Repository-Setup & Projektstruktur | Git-Repo, `requirements.txt`, `.env.example` | [deployment.md](specs/deployment.md), [backend.md](specs/backend.md) | 1h | TBD |
| 1.2 | Python Virtual Environment & Dependencies | Funktionierende Flask-Installation | [deployment.md](specs/deployment.md) | 1h | TBD |
| 1.3 | Tarifdaten-Schema definieren | `data/sterbegeld/tariffs.json` mit 5 Beispiel-Tarifen (feste Preise!) | [tariff-data.md](specs/tariff-data.md) | 2h | TBD |
| 1.4 | Tarif-Search-Engine (Backend-Logik) | `app/products/sterbegeld/tariffs.py` (Filter, Ranking) - **KEINE Kalkulation!** | [tariff-data.md](specs/tariff-data.md) | 2h | TBD |
| 1.5 | ~~Unit-Tests für Tarif-Logik~~ | ~~`tests/test_tariffs.py` (mind. 5 Tests)~~ ❌ Später | [tariff-data.md](specs/tariff-data.md) | ~~2h~~ | SKIP |
| 1.6 | Prompt-Dateien erstellen | `data/sterbegeld/prompts/*.txt` (3 Kern-Inputs) | [llm-integration.md](specs/llm-integration.md) | 1h | TBD |

**Milestone**: ✅ Tarifdaten-Modell validiert, Beispiel-Tarife durchsuchbar (ohne Kalkulation!)

---

### Phase 2: Backend-Core & LLM-Integration (2-3 Tage) ⚡

| # | Aufgabe | Key Deliverables | Related Specs | Dauer | Status |
|---|---------|------------------|---------------|-------|--------|
| 2.1 | Flask App Factory & Config | `app/__init__.py`, `app/config.py` (GPT-5!) | [backend.md](specs/backend.md) | 1h | TBD |
| 2.2 | OpenAI LLM-Client | `app/chatbot/llm_client.py` (API-Wrapper, GPT-5) | [llm-integration.md](specs/llm-integration.md) | 2h | TBD |
| 2.3 | ~~Abstrakte Chatbot-Basisklasse~~ | ~~`app/chatbot/base.py` (InsuranceChatbot)~~ ❌ Vereinfachen | [backend.md](specs/backend.md) | ~~3h~~ | SKIP |
| 2.4 | Sterbegeld-Chatbot-Implementierung | `app/products/sterbegeld/chatbot.py` (Prompt-Assembly) - EINFACH! | [backend.md](specs/backend.md), [llm-integration.md](specs/llm-integration.md) | 3h | TBD |
| 2.5 | Function Calling Definitions | `app/products/sterbegeld/functions.py` (`tariff_search`) | [llm-integration.md](specs/llm-integration.md) | 1h | TBD |
| 2.6 | Function Execution Logik | Integration von Tarif-Search-Engine in Chatbot | [chatbot-logic.md](specs/chatbot-logic.md) | 2h | TBD |
| 2.7 | REST API Endpoints | `app/api/routes.py` (`POST /api/chat`, `GET /health`) | [backend.md](specs/backend.md) | 2h | TBD |
| 2.8 | Logging Setup (einfach) | `app/utils/logger.py` (Console only) | [backend.md](specs/backend.md), [deployment.md](specs/deployment.md) | 1h | TBD |
| 2.9 | API-Tests (manuell) | cURL-Tests für `/api/chat` | [backend.md](specs/backend.md) | 1h | TBD |

**Milestone**: ✅ Backend antwortet auf Chat-Requests, Function Calling funktioniert

---

### Phase 3: Frontend-Entwicklung (2-3 Tage) ⚡

| # | Aufgabe | Key Deliverables | Related Specs | Dauer | Status |
|---|---------|------------------|---------------|-------|--------|
| 3.1 | HTML-Basis-Template | `app/templates/index.html` (Chat + vereinfachtes Debug-Panel) | [frontend.md](specs/frontend.md) | 1h | TBD |
| 3.2 | CSS-Styling (Mobile-First, EINFACH) | `static/css/style.css` (Basis-Styling, funktional) | [frontend.md](specs/frontend.md) | 4h | TBD |
| 3.3 | Chat-Interface (DOM-Manipulation) | JavaScript: Message-Rendering, Scroll-to-Bottom | [frontend.md](specs/frontend.md) | 3h | TBD |
| 3.4 | Input-Handling & Send-Funktion | JavaScript: `sendMessage()`, Fetch API | [frontend.md](specs/frontend.md) | 2h | TBD |
| 3.5 | Debug-Panel (vereinfacht!) | JavaScript: Nur LLM-Response anzeigen (JSON) | [frontend.md](specs/frontend.md) | 2h | TBD |
| 3.6 | ~~Prompt-Config-Panel~~ | ~~HTML-Form + JavaScript für `/api/update-prompts`~~ ❌ Phase 2 | [frontend.md](specs/frontend.md) | ~~3h~~ | SKIP |
| 3.7 | Typing-Indikator (einfach) | Einfacher Spinner (kein CSS-Schnickschnack) | [frontend.md](specs/frontend.md) | 1h | TBD |
| 3.8 | Responsive Design Testing | Test auf iPhone + Desktop (Chrome, Safari) | [frontend.md](specs/frontend.md) | 1h | TBD |

**Milestone**: ✅ Vollständiges UI, Konversationen funktionieren End-to-End

---

### Phase 4: Integration & Testing (1-2 Tage) ⚡

| # | Aufgabe | Key Deliverables | Related Specs | Dauer | Status |
|---|---------|------------------|---------------|-------|--------|
| 4.1 | End-to-End Happy-Path-Test | User-Journey: Begrüßung → 3 Fragen → Tarifempfehlung | [chatbot-logic.md](specs/chatbot-logic.md) | 1h | TBD |
| 4.2 | Edge-Case-Testing (manuell) | Tests: Ungültige Eingaben, keine passenden Tarife | [chatbot-logic.md](specs/chatbot-logic.md) | 2h | TBD |
| 4.3 | Prompt-Optimierung (Iteration 1) | Logs analysieren, Prompt-Anweisungen schärfen | [llm-integration.md](specs/llm-integration.md) | 3h | TBD |
| 4.4 | Debug-Panel-Validierung | Prüfen: LLM-Response korrekt angezeigt | [frontend.md](specs/frontend.md) | 30min | TBD |
| 4.5 | ~~Performance-Messung~~ | ~~Antwortzeiten loggen (Ziel: < 5s)~~ ❌ Später | [deployment.md](specs/deployment.md) | ~~2h~~ | SKIP |
| 4.6 | Fehlerbehandlung (Basis) | Graceful Fallbacks für LLM-Fehler | [backend.md](specs/backend.md), [chatbot-logic.md](specs/chatbot-logic.md) | 1h | TBD |
| 4.7 | Test-Dialoge dokumentieren | Mind. 3 Test-Szenarien (Happy Path, Edge Cases) | [chatbot-logic.md](specs/chatbot-logic.md) | 1h | TBD |

**Milestone**: ✅ Alle Haupt-Flows funktionieren stabil

---

### Phase 5: Feinschliff & Deployment (1 Tag) ⚡

| # | Aufgabe | Key Deliverables | Related Specs | Dauer | Status |
|---|---------|------------------|---------------|-------|--------|
| 5.1 | README.md schreiben (knapp) | Setup-Anleitung, Screenshot | [deployment.md](specs/deployment.md) | 1h | TBD |
| 5.2 | .env.example erstellen | Template mit OPENAI_API_KEY | [deployment.md](specs/deployment.md) | 15min | TBD |
| 5.3 | ~~Code-Cleanup~~ | ~~Unused Imports entfernen, Docstrings ergänzen~~ ❌ Später | [backend.md](specs/backend.md) | ~~2h~~ | SKIP |
| 5.4 | ~~UI-Polish~~ | ~~Micro-Interactions (Hover-Effekte, Button-States)~~ ❌ Später | [frontend.md](specs/frontend.md) | ~~2h~~ | SKIP |
| 5.5 | Deployment-Test | Anleitung testen: Frische Installation | [deployment.md](specs/deployment.md) | 1h | TBD |
| 5.6 | Demo-Präsentation vorbereiten | Live-Demo für Produktmanager (kein Video) | [project-overview.md](specs/project-overview.md) | 1h | TBD |
| 5.7 | Finale Abnahme | User-Test mit Produktmanager | [project-overview.md](specs/project-overview.md) | 1h | TBD |

**Milestone**: ✅ Prototyp funktionsfähig für interne Evaluierung

---

## ✅ Erfolgskriterien

### Funktional
- ✅ Chatbot führt vollständigen Dialog zur Erfassung aller relevanten Parameter
- ✅ Korrekte Tarifempfehlung basierend auf Eingaben (günstigster Tarif zuerst)
- ✅ Flüssige, natürlichsprachige Konversation in deutscher Sprache

### Nicht-funktional
- ✅ Mobile-optimierte Darstellung (responsive, iPhone-optimiert)
- ✅ Antwortzeit < 5 Sekunden pro Chatbot-Antwort
- ✅ Einfache lokale Installation (< 5 Minuten Setup)
- ✅ Debug-Panel zur Nachvollziehbarkeit des LLM-Verhaltens

### Evaluierungs-Metriken
- **Dialog-Effizienz**: ≤ 5 Bot-Nachrichten bis zur Tarifempfehlung
- **Erfolgsrate**: > 80% der Dialoge führen zu Tarifempfehlung
- **User-Satisfaction**: Feedback von Produktmanagern (qualitativ)

---

## 🔄 Offene Fragen & Entscheidungen

| # | Frage | Entscheidung | Status |
|---|-------|--------------|--------|
| Q1 | ~~GPT-5 noch nicht verfügbar – wie lange GPT-4o nutzen?~~ | ✅ GPT-5 ist verfügbar und wird direkt genutzt | ✅ Geklärt |
| Q2 | Sollen echte Tarifdaten von CHECK24 genutzt werden? | Nein – Prototyp mit fiktiven Beispiel-Tarifen (5 Tarife ausreichend) | ✅ Geklärt |
| Q3 | Prompt-Updates: Zur Laufzeit editierbar via UI? | Ja – Prompt-Config-Panel unten im UI (Feature für Produktmanager) | ✅ Geklärt |
| Q4 | Welche Browser müssen unterstützt werden? | Chrome & Safari (macOS/iOS) – keine IE/Edge-Legacy-Unterstützung | ✅ Geklärt |
| Q5 | Soll der Prototyp öffentlich zugänglich sein? | Nein – nur lokal (localhost), später ggf. internes Staging | ✅ Geklärt |

---

## 🚀 Nächste Schritte

### Sofort (diese Woche)
1. ✅ Spezifikationen finalisiert → Freigabe durch Produktmanager
2. ⏳ **Phase 1 starten**: Projekt-Setup & Tarifdaten-Modell
3. ⏳ OpenAI API-Key beantragen/bereitstellen

### Diese Woche (bis Freitag)
4. ⏳ Phase 1 + Phase 2 abschließen (Backend funktionsfähig)
5. ⏳ Erste manuelle Tests mit Postman

### Nächste Woche
6. ⏳ Phase 3 (Frontend) + Phase 4 (Integration & Testing)
7. ⏳ Erste interne Demo

### Übernächste Woche
8. ⏳ Phase 5 (Feinschliff) + Finale Abnahme
9. ⏳ **Prototyp-Evaluierung** mit Produktmanagern

---

## 📞 Stakeholder & Ansprechpartner

| Rolle | Name | Verantwortung |
|-------|------|---------------|
| **Produktmanager** | [TBD] | Anforderungen, Abnahme |
| **Tech Lead** | [TBD] | Architektur-Review, Code-Review |
| **LLM-Engineer** | [TBD] | Prompt-Engineering, LLM-Integration |
| **Frontend-Developer** | [TBD] | UI/UX-Implementierung |
| **Backend-Developer** | [TBD] | API, Tarif-Logik |

---

## 📝 Change Log

| Datum | Version | Änderung | Autor |
|-------|---------|----------|-------|
| 2025-11-04 | v1.0 | Initiale Spezifikationen erstellt | SpecForge |
| TBD | v1.1 | Feedback aus Tech-Review eingearbeitet | [TBD] |

---

## 📚 Anhang: Wichtige Entscheidungen

### Warum Flask statt FastAPI?
- **Einfacheres Template-Rendering** (Jinja2 integriert)
- **Kürzere Lernkurve** für Rapid Prototyping
- **Kleinerer Boilerplate-Code**

### Warum statische JSON statt Datenbank?
- **Prototyp-Anforderung**: < 100 Tarife
- **Einfachste Datenänderung**: JSON-Datei editieren
- **Spätere Migration trivial**: JSON → PostgreSQL (siehe `tariff-data.md`)

### Warum Stateless Architecture?
- **Keine Datenbank nötig** (einfachstes Setup)
- **Horizontal skalierbar** (jeder Request unabhängig)
- **Client-Side History ausreichend** für Prototyp

### Warum System-Prompt statt RAG?
- **Einfacher zu implementieren** (keine Vektordatenbank)
- **Schnelle Iteration** (Prompt-Dateien direkt editieren)
- **Ausreichend für < 20 Tarife** (Token-Limit unkritisch)

---

**Ende der Spezifikationen. Bereit für Implementierung! 🚀**

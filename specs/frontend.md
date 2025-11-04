# Frontend-Spezifikation

## Zweck
Definition des User Interfaces für den Chatbot-Prototyp mit Fokus auf **Mobile-First**, **Einfachheit** und **Developer-Transparenz**.

## Design-Philosophie

### Prinzipien
1. **Mobile-First**: Primäre Optimierung für Smartphone-Displays (320-428px)
2. **Progressive Enhancement**: Funktioniert ohne JavaScript (Basis-Formular), wird mit JS besser
3. **Minimalistisch**: Keine CSS-Frameworks, keine Build-Tools
4. **Developer-Friendly**: Debug-Panel für Prompt-Inspektion

## Layout-Struktur

### Desktop-Ansicht (≥ 768px)
```
┌─────────────────────────────────────────────────────────┐
│                     Header (Logo / Titel)                │
├───────────────────────────┬─────────────────────────────┤
│                           │                             │
│    Chat Interface         │      Debug Panel            │
│    (50% width)            │      (50% width)            │
│                           │                             │
│  ┌──────────────────────┐ │  ┌────────────────────────┐ │
│  │  [Chatbot Avatar]    │ │  │  System Prompt:        │ │
│  │  "Hallo! Wie kann    │ │  │  [Collapsible]         │ │
│  │   ich helfen?"       │ │  │                        │ │
│  └──────────────────────┘ │  └────────────────────────┘ │
│                           │  ┌────────────────────────┐ │
│  ┌──────────────────────┐ │  │  Last User Message:    │ │
│  │      "Ich bin 45"    │ │  │  [Display]             │ │
│  │  [User Avatar]       │ │  └────────────────────────┘ │
│  └──────────────────────┘ │  ┌────────────────────────┐ │
│                           │  │  LLM Response:         │ │
│  ┌──────────────────────┐ │  │  [JSON Display]        │ │
│  │  [Input Field]       │ │  └────────────────────────┘ │
│  │  [Send Button]       │ │                             │
│  └──────────────────────┘ │                             │
├───────────────────────────┴─────────────────────────────┤
│           Prompt Configuration Panel (Bottom)           │
│  ┌─────────────────────────────────────────────────────┐│
│  │ Produktlogik-Prompt: [Textarea]                     ││
│  │ Tarif-Tabelle-Prompt: [Textarea]                    ││
│  │ Interaktionsstil-Prompt: [Textarea]                 ││
│  │ [Update Prompts Button]                             ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

### Mobile-Ansicht (< 768px)
```
┌────────────────────────┐
│  Header                │
├────────────────────────┤
│  Chat Interface        │
│  (Full Width)          │
│                        │
│  [Messages...]         │
│                        │
│  [Input + Send]        │
├────────────────────────┤
│  [Toggle Debug Button] │
├────────────────────────┤
│  Debug Panel           │
│  (Collapsible)         │
│  [Hidden by default]   │
└────────────────────────┘
```

## Komponenten-Spezifikation

### 1. Chat Interface (Primäre UI)

#### 1.1 Chat-Container
- **Element**: `<div id="chat-container">`
- **Styling**:
  - `height: calc(100vh - 200px)` (volle Höhe minus Header/Footer)
  - `overflow-y: auto`
  - `background-color: #f5f5f5`
  - `padding: 20px`

#### 1.2 Chat-Nachricht (Chatbot)
- **Element**: `<div class="message message-bot">`
- **Struktur**:
  ```html
  <div class="message message-bot">
    <div class="message-avatar">
      <img src="/static/bot-avatar.svg" alt="Bot">
    </div>
    <div class="message-content">
      <p>{{ message_text }}</p>
      <span class="message-time">{{ timestamp }}</span>
    </div>
  </div>
  ```
- **Styling**:
  - Ausrichtung: links
  - Hintergrund: weiß
  - Border-Radius: `16px`
  - Box-Shadow: leichter Schatten
  - Avatar: kreisrund, 40px Durchmesser

#### 1.3 Chat-Nachricht (User)
- **Element**: `<div class="message message-user">`
- **Struktur**: Analog zu Bot, aber:
  - Ausrichtung: rechts
  - Hintergrund: `#007aff` (iOS-Blau)
  - Text-Color: weiß
  - Kein Avatar (optional)

#### 1.4 Input-Bereich
- **Element**: `<form id="chat-form">`
- **Struktur**:
  ```html
  <form id="chat-form">
    <div class="input-wrapper">
      <textarea 
        id="user-input" 
        placeholder="Nachricht eingeben..." 
        rows="1"
        maxlength="500"
      ></textarea>
      <button type="submit" id="send-btn">
        <svg><!-- Send Icon --></svg>
      </button>
    </div>
  </form>
  ```
- **Features**:
  - Auto-Resize Textarea (bei mehrzeiligem Input)
  - Send-Button disabled wenn leer
  - Enter-Taste sendet (Shift+Enter = Zeilenumbruch)

#### 1.5 Typing-Indikator (Optional)
- **Element**: `<div class="typing-indicator">`
- **Anzeige**: Während LLM-Request läuft
- **Animation**: 3 pulsierende Dots

---

### 2. Debug Panel

#### 2.1 Panel-Container
- **Element**: `<div id="debug-panel">`
- **Styling**:
  - Desktop: feste rechte Spalte (50% width)
  - Mobile: Collapsible, Toggle-Button
  - `background-color: #1e1e1e` (dunkel)
  - `color: #d4d4d4` (helle Schrift)
  - `font-family: 'Courier New', monospace`

#### 2.2 Sections
1. **System Prompt**:
   ```html
   <details open>
     <summary>System Prompt</summary>
     <pre id="debug-system-prompt">{{ system_prompt }}</pre>
   </details>
   ```

2. **Last User Message**:
   ```html
   <div class="debug-section">
     <h4>Last User Message</h4>
     <pre id="debug-user-message">{{ user_message }}</pre>
   </div>
   ```

3. **LLM Response (Raw JSON)**:
   ```html
   <div class="debug-section">
     <h4>LLM Response</h4>
     <pre id="debug-llm-response">{{ llm_response_json }}</pre>
   </div>
   ```

#### 2.3 Toggle-Button (Mobile)
- **Element**: `<button id="toggle-debug">🔍 Debug</button>`
- **Position**: Fixed bottom-right
- **Funktion**: Zeigt/verbirgt Debug-Panel

---

### 3. Prompt Configuration Panel (Unten)

#### 3.1 Container
- **Element**: `<div id="prompt-config">`
- **Position**: Unterhalb des Chat/Debug-Bereichs
- **Collapsible**: Via `<details>` Element (Standard: geschlossen)

#### 3.2 Form-Felder
```html
<form id="prompt-config-form">
  <div class="prompt-field">
    <label for="product-logic-prompt">Produktlogik-Prompt</label>
    <textarea 
      id="product-logic-prompt" 
      rows="6"
      placeholder="Beschreibt die Logik von Sterbegeldversicherungen..."
    ></textarea>
  </div>

  <div class="prompt-field">
    <label for="tariff-table-prompt">Tarif-Tabelle-Prompt</label>
    <textarea 
      id="tariff-table-prompt" 
      rows="6"
      placeholder="Stellt mehrere Tarife mit Parametern dar..."
    ></textarea>
  </div>

  <div class="prompt-field">
    <label for="interaction-style-prompt">Interaktionsstil-Prompt</label>
    <textarea 
      id="interaction-style-prompt" 
      rows="6"
      placeholder="Legt die bevorzugte Gesprächsführung fest..."
    ></textarea>
  </div>

  <button type="submit">Prompts aktualisieren</button>
</form>
```

#### 3.3 Update-Mechanismus
- **API-Call**: `POST /api/update-prompts`
- **Feedback**: Toast-Notification "Prompts erfolgreich aktualisiert"
- **Persistierung**: In-Memory (Session), später: Filesystem/DB

---

## Interaktions-Flows

### Flow 1: Nachricht senden
1. User gibt Text in `#user-input` ein
2. User drückt Enter oder klickt Send
3. JavaScript:
   - Validiert Input (nicht leer)
   - Fügt User-Message sofort zum Chat hinzu (optimistic UI)
   - Zeigt Typing-Indikator
   - Sendet `POST /api/chat` mit `{ message: "...", conversation_history: [...] }`
4. Backend antwortet mit JSON: `{ reply: "...", debug: {...} }`
5. JavaScript:
   - Entfernt Typing-Indikator
   - Fügt Bot-Message zum Chat hinzu
   - Updated Debug-Panel
   - Scrollt zum neuesten Message

### Flow 2: Prompts aktualisieren
1. User öffnet Prompt-Config-Panel
2. User bearbeitet Textareas
3. User klickt "Aktualisieren"
4. JavaScript:
   - Sendet `POST /api/update-prompts` mit `{ product_logic: "...", tariff_table: "...", interaction_style: "..." }`
5. Backend speichert in Session/Memory
6. Toast-Notification: "✓ Prompts aktualisiert"

---

## Styling-Guidelines

### Farb-Palette
```css
:root {
  /* Primary Colors */
  --primary-blue: #007aff;      /* iOS-Stil */
  --primary-dark: #1e1e1e;      /* Debug-Panel */
  
  /* Backgrounds */
  --bg-light: #f5f5f5;          /* Chat-Hintergrund */
  --bg-white: #ffffff;          /* Bot-Nachricht */
  --bg-user: var(--primary-blue); /* User-Nachricht */
  
  /* Text */
  --text-dark: #333333;
  --text-light: #666666;
  --text-white: #ffffff;
  
  /* Accents */
  --border-color: #e0e0e0;
  --shadow: rgba(0, 0, 0, 0.1);
}
```

### Typography
```css
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  font-size: 16px;
  line-height: 1.5;
}

.message-content {
  font-size: 15px;
  line-height: 1.4;
}

#debug-panel {
  font-family: 'Courier New', monospace;
  font-size: 12px;
}
```

### Responsive Breakpoints
```css
/* Mobile */
@media (max-width: 767px) {
  #debug-panel {
    display: none; /* Hidden by default */
  }
  #debug-panel.open {
    display: block;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 50vh;
    z-index: 1000;
  }
}

/* Desktop */
@media (min-width: 768px) {
  .main-container {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }
}
```

---

## JavaScript-Funktionalität

### Core Functions (vanilla JS)

#### `sendMessage(text)`
```javascript
async function sendMessage(text) {
  // Add user message to UI
  addMessageToChat('user', text);
  
  // Show typing indicator
  showTypingIndicator();
  
  // API call
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
      message: text,
      conversation_history: getConversationHistory()
    })
  });
  
  const data = await response.json();
  
  // Hide typing indicator
  hideTypingIndicator();
  
  // Add bot response
  addMessageToChat('bot', data.reply);
  
  // Update debug panel
  updateDebugPanel(data.debug);
}
```

#### `addMessageToChat(role, text)`
```javascript
function addMessageToChat(role, text) {
  const messageDiv = document.createElement('div');
  messageDiv.className = `message message-${role}`;
  messageDiv.innerHTML = `
    <div class="message-content">
      <p>${text}</p>
      <span class="message-time">${getCurrentTime()}</span>
    </div>
  `;
  document.getElementById('chat-container').appendChild(messageDiv);
  scrollToBottom();
}
```

#### `updateDebugPanel(debug)`
```javascript
function updateDebugPanel(debug) {
  document.getElementById('debug-system-prompt').textContent = debug.system_prompt;
  document.getElementById('debug-user-message').textContent = debug.user_message;
  document.getElementById('debug-llm-response').textContent = 
    JSON.stringify(debug.llm_response, null, 2);
}
```

---

## Accessibility (Optional für Prototyp, aber Best Practice)

- **Keyboard Navigation**: Tab-Reihenfolge logisch
- **ARIA Labels**: 
  - `<button aria-label="Nachricht senden">`
  - `<div role="log" aria-live="polite">` für Chat-Container
- **Contrast**: Mindestens 4.5:1 (WCAG AA)

---

## Assets

### Icons/Images
- `bot-avatar.svg` – Chatbot-Avatar (optional: Unicode Emoji 🤖)
- `send-icon.svg` – Pfeil-Icon für Send-Button

### Static Files-Struktur
```
static/
├── css/
│   └── style.css
├── js/
│   └── app.js
└── images/
    └── bot-avatar.svg
```

---

## Implementierungs-Priorität

### Phase 1 (MVP)
1. ✅ Chat-Interface (Messages anzeigen + senden)
2. ✅ Basic Styling (Mobile-First, keine Frameworks)
3. ✅ Input-Bereich mit Send-Button

### Phase 2
4. ✅ Debug-Panel (Desktop-Ansicht)
5. ✅ Typing-Indikator

### Phase 3
6. ✅ Prompt-Config-Panel
7. ✅ Debug-Panel Toggle (Mobile)

### Phase 4 (Optional)
8. LocalStorage für Konversations-Historie
9. Markdown-Rendering für Bot-Antworten
10. Copy-to-Clipboard für Debug-Inhalte

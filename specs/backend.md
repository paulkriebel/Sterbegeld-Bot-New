# Backend-Spezifikation

## Zweck
Definition der Server-seitigen Logik, API-Endpunkte und Datenverwaltung für den Chatbot-Prototyp.

## Technologie-Stack

### Framework
**Flask** (Version ≥ 3.0)

**Begründung**:
- Einfacher als FastAPI für Template-Rendering
- Minimaler Boilerplate-Code
- Integrierter Development Server
- Große Community für Rapid Prototyping

### Dependencies
```txt
flask==3.0.0
flask-cors==4.0.0
openai==1.3.0
python-dotenv==1.0.0
pandas==2.1.0  # Optional: CSV-Handling
```

---

## Projektstruktur

```
/
├── app/
│   ├── __init__.py                 # Flask App Factory
│   ├── config.py                   # Configuration
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py               # REST Endpoints
│   │
│   ├── chatbot/
│   │   ├── __init__.py
│   │   ├── base.py                 # Abstract InsuranceChatbot
│   │   ├── llm_client.py           # OpenAI Wrapper
│   │   ├── prompt_builder.py      # Dynamic Prompt Assembly
│   │   └── conversation.py         # Conversation State (Stateless)
│   │
│   ├── products/
│   │   ├── __init__.py
│   │   └── sterbegeld/
│   │       ├── __init__.py
│   │       ├── chatbot.py          # SterbeGeldChatbot
│   │       ├── tariffs.py          # Tariff Logic
│   │       └── functions.py        # Function Calling Definitions
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py               # Logging Setup
│   │   └── validators.py           # Input Validation
│   │
│   └── templates/
│       └── index.html              # Main UI Template
│
├── data/
│   └── sterbegeld/
│       ├── tariffs.json            # Tariff Data
│       └── prompts/
│           ├── product_logic.txt
│           ├── tariff_table.txt
│           └── interaction_style.txt
│
├── static/                         # Frontend Assets (siehe frontend.md)
├── logs/                           # Log Files
├── .env                            # Environment Variables
├── requirements.txt
└── run.py                          # Entry Point
```

---

## API-Endpunkte

### 1. `GET /`
**Zweck**: Haupt-HTML-Interface ausliefern

**Response**:
- HTML-Template (`index.html`)
- Status: 200

**Implementierung**:
```python
@app.route('/')
def index():
    return render_template('index.html')
```

---

### 2. `POST /api/chat`
**Zweck**: Chatbot-Nachricht senden und Antwort erhalten

**Request Body** (JSON):
```json
{
  "message": "Ich bin 45 Jahre alt und möchte eine Versicherungssumme von 5000 Euro.",
  "conversation_history": [
    {"role": "assistant", "content": "Hallo! Wie alt sind Sie?"},
    {"role": "user", "content": "Ich bin 45 Jahre alt."}
  ],
  "custom_prompts": {
    "product_logic": "...",  // Optional: Override default
    "tariff_table": "...",
    "interaction_style": "..."
  }
}
```

**Response** (JSON):
```json
{
  "reply": "Vielen Dank! Wie würden Sie Ihren Gesundheitszustand beschreiben?",
  "conversation_history": [
    {"role": "assistant", "content": "Hallo! ..."},
    {"role": "user", "content": "Ich bin 45 Jahre alt."},
    {"role": "assistant", "content": "Vielen Dank! ..."}
  ],
  "debug": {
    "system_prompt": "Du bist ein Versicherungsberater...",
    "user_message": "Ich bin 45 Jahre alt...",
    "llm_response": {
      "id": "chatcmpl-...",
      "choices": [...],
      "usage": {"prompt_tokens": 150, "completion_tokens": 30}
    },
    "function_calls": [
      {"name": "tariff_search", "arguments": "..."}
    ]
  }
}
```

**Error Response** (JSON):
```json
{
  "error": "Invalid request",
  "message": "Message field is required",
  "status": 400
}
```

**Implementierung**:
```python
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    
    # Validate
    if not data.get('message'):
        return jsonify({'error': 'Message required'}), 400
    
    # Initialize Chatbot
    chatbot = SterbeGeldChatbot(
        custom_prompts=data.get('custom_prompts')
    )
    
    # Process message
    response = chatbot.process_message(
        message=data['message'],
        history=data.get('conversation_history', [])
    )
    
    return jsonify(response)
```

---

### 3. `POST /api/update-prompts`
**Zweck**: Kern-Inputs (Prompts) zur Laufzeit aktualisieren

**Request Body** (JSON):
```json
{
  "product_logic": "Sterbegeldversicherungen decken Bestattungskosten ab...",
  "tariff_table": "Tarif A: 10€/Monat, Tarif B: 15€/Monat...",
  "interaction_style": "Sei freundlich und stelle maximal eine Frage pro Antwort."
}
```

**Response** (JSON):
```json
{
  "status": "success",
  "message": "Prompts successfully updated"
}
```

**Implementierung**:
```python
# In-Memory Store (für Prototyp)
custom_prompts_store = {}

@app.route('/api/update-prompts', methods=['POST'])
def update_prompts():
    data = request.json
    custom_prompts_store.update(data)
    return jsonify({'status': 'success', 'message': 'Prompts updated'})
```

---

### 4. `GET /api/tariffs`
**Zweck**: Alle Tarife abrufen (für Debugging)

**Response** (JSON):
```json
{
  "tariffs": [
    {
      "id": "tariff_a",
      "name": "Sterbegeld Basis",
      "monthly_premium": 10.50,
      "coverage_amount": 3000,
      "age_range": [18, 65],
      "health_requirement": "none"
    },
    ...
  ]
}
```

**Implementierung**:
```python
@app.route('/api/tariffs', methods=['GET'])
def get_tariffs():
    tariffs = load_tariffs()
    return jsonify({'tariffs': tariffs})
```

---

### 5. `GET /health`
**Zweck**: Health-Check für Monitoring

**Response** (JSON):
```json
{
  "status": "healthy",
  "openai_api": "reachable",
  "timestamp": "2025-11-04T14:30:00Z"
}
```

---

## Core-Module

### 1. `app/chatbot/base.py`
**Abstrakte Basisklasse für alle Insurance-Chatbots**

```python
from abc import ABC, abstractmethod
from typing import List, Dict

class InsuranceChatbot(ABC):
    def __init__(self, custom_prompts: Dict[str, str] = None):
        self.custom_prompts = custom_prompts or {}
        self.llm_client = LLMClient()
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Build full system prompt from components"""
        pass
    
    @abstractmethod
    def get_function_definitions(self) -> List[Dict]:
        """Define available function calls"""
        pass
    
    def process_message(self, message: str, history: List[Dict]) -> Dict:
        """Main entry point for message processing"""
        # 1. Build prompt
        system_prompt = self.get_system_prompt()
        
        # 2. Call LLM
        response = self.llm_client.chat_completion(
            system=system_prompt,
            messages=history + [{"role": "user", "content": message}],
            functions=self.get_function_definitions()
        )
        
        # 3. Handle function calls
        if response.get('function_call'):
            function_result = self.execute_function(response['function_call'])
            # Second LLM call with function result
            response = self.llm_client.chat_completion(...)
        
        # 4. Return formatted response
        return {
            'reply': response['content'],
            'conversation_history': history + [...],
            'debug': {...}
        }
    
    @abstractmethod
    def execute_function(self, function_call: Dict) -> Dict:
        """Execute function and return result"""
        pass
```

---

### 2. `app/chatbot/llm_client.py`
**OpenAI API Wrapper**

```python
import openai
from app.utils.logger import logger

class LLMClient:
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.model = "gpt-5"  # ✅ GPT-5 verfügbar
    
    def chat_completion(self, system: str, messages: List[Dict], 
                        functions: List[Dict] = None) -> Dict:
        try:
            logger.debug(f"System Prompt: {system}")
            logger.debug(f"Messages: {messages}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": system}] + messages,
                functions=functions,
                function_call="auto" if functions else None,
                temperature=0.7,
                max_tokens=500
            )
            
            logger.debug(f"LLM Response: {response}")
            
            return {
                'content': response.choices[0].message.content,
                'function_call': response.choices[0].message.function_call,
                'raw_response': response.model_dump()
            }
        except Exception as e:
            logger.error(f"LLM Error: {e}")
            raise
```

---

### 3. `app/products/sterbegeld/chatbot.py`
**Konkrete Implementierung für Sterbegeldversicherung**

```python
from app.chatbot.base import InsuranceChatbot
from .tariffs import TariffSearchEngine
from .functions import FUNCTION_DEFINITIONS

class SterbeGeldChatbot(InsuranceChatbot):
    def __init__(self, custom_prompts=None):
        super().__init__(custom_prompts)
        self.tariff_engine = TariffSearchEngine()
    
    def get_system_prompt(self) -> str:
        # Load prompts
        product_logic = self.load_prompt('product_logic')
        tariff_table = self.load_prompt('tariff_table')
        interaction_style = self.load_prompt('interaction_style')
        
        # Override with custom if provided
        if self.custom_prompts:
            product_logic = self.custom_prompts.get('product_logic', product_logic)
            # ...
        
        # Combine
        return f"""
        Du bist ein Versicherungsberater für Sterbegeldversicherungen.
        
        # Produktlogik
        {product_logic}
        
        # Verfügbare Tarife
        {tariff_table}
        
        # Interaktionsstil
        {interaction_style}
        
        Deine Aufgabe: Führe ein natürliches Gespräch, um folgende Parameter zu erfragen:
        - Alter
        - Gesundheitszustand
        - Gewünschte Versicherungssumme
        
        Wenn alle Daten vorliegen, rufe die Funktion 'tariff_search' auf.
        """
    
    def load_prompt(self, name: str) -> str:
        path = f"data/sterbegeld/prompts/{name}.txt"
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def get_function_definitions(self) -> List[Dict]:
        return FUNCTION_DEFINITIONS
    
    def execute_function(self, function_call: Dict) -> Dict:
        if function_call['name'] == 'tariff_search':
            args = json.loads(function_call['arguments'])
            return self.tariff_engine.search(**args)
        else:
            raise ValueError(f"Unknown function: {function_call['name']}")
```

---

### 4. `app/products/sterbegeld/tariffs.py`
**Tarif-Suche und Ranking**

```python
import json
from typing import List, Dict

class TariffSearchEngine:
    def __init__(self):
        self.tariffs = self.load_tariffs()
    
    def load_tariffs(self) -> List[Dict]:
        with open('data/sterbegeld/tariffs.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def search(self, age: int, health: str, coverage: int) -> List[Dict]:
        """
        Filter and rank tariffs based on customer criteria.
        Returns top 3 cheapest matching tariffs.
        """
        matches = []
        
        for tariff in self.tariffs:
            # Filter by age
            if not (tariff['age_min'] <= age <= tariff['age_max']):
                continue
            
            # Filter by health requirement
            if not self.meets_health_requirement(health, tariff['health_requirement']):
                continue
            
            # Filter by coverage (exact match or higher)
            if tariff['coverage_amount'] < coverage:
                continue
            
            matches.append(tariff)
        
        # Sort by price (ascending)
        matches.sort(key=lambda t: t['monthly_premium'])
        
        return matches[:3]  # Top 3
    
    def meets_health_requirement(self, customer_health: str, 
                                  tariff_requirement: str) -> bool:
        health_hierarchy = {'excellent': 3, 'good': 2, 'fair': 1, 'poor': 0}
        return health_hierarchy.get(customer_health, 0) >= \
               health_hierarchy.get(tariff_requirement, 0)
```

---

### 5. `app/products/sterbegeld/functions.py`
**OpenAI Function Calling Definitions**

```python
FUNCTION_DEFINITIONS = [
    {
        "name": "tariff_search",
        "description": "Sucht passende Sterbegeld-Tarife basierend auf Kundendaten",
        "parameters": {
            "type": "object",
            "properties": {
                "age": {
                    "type": "integer",
                    "description": "Alter des Kunden in Jahren"
                },
                "health": {
                    "type": "string",
                    "enum": ["excellent", "good", "fair", "poor"],
                    "description": "Gesundheitszustand des Kunden"
                },
                "coverage": {
                    "type": "integer",
                    "description": "Gewünschte Versicherungssumme in Euro"
                }
            },
            "required": ["age", "health", "coverage"]
        }
    }
]
```

---

## Configuration (`app/config.py`)

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    
    # OpenAI
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-5')
    
    # App Settings
    MAX_MESSAGE_LENGTH = 500
    DEFAULT_LANGUAGE = 'de'
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'DEBUG')
    LOG_FILE = 'logs/app.log'
```

---

## Logging (`app/utils/logger.py`)

```python
import logging
from app.config import Config

def setup_logger():
    logger = logging.getLogger('chatbot')
    logger.setLevel(Config.LOG_LEVEL)
    
    # Console Handler
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    
    # File Handler
    file_handler = logging.FileHandler(Config.LOG_FILE, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logger()
```

---

## Entry Point (`run.py`)

```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

---

## Nicht-funktionale Anforderungen

### Performance
- **Timeout**: LLM-Requests max. 10 Sekunden
- **Rate Limiting**: (Optional) Max. 10 Requests/Minute pro IP

### Fehlerbehandlung
- **LLM-Fehler**: Graceful Fallback-Message
- **Datei-Fehler**: Clear Error Messages in Logs
- **Input-Validation**: Reject empty messages, too long messages

### Sicherheit
- **API-Key**: Nie in Logs oder Responses exposen
- **Input-Sanitization**: Verhindere Injection (basic)
- **CORS**: Nur localhost (für Prototyp)

---

## Testing (Optional für Prototyp)

### Unit Tests
```python
# tests/test_tariffs.py
def test_tariff_search():
    engine = TariffSearchEngine()
    results = engine.search(age=45, health='good', coverage=5000)
    assert len(results) > 0
    assert results[0]['monthly_premium'] < results[1]['monthly_premium']
```

### Integration Tests
```python
# tests/test_api.py
def test_chat_endpoint(client):
    response = client.post('/api/chat', json={
        'message': 'Ich bin 45 Jahre alt'
    })
    assert response.status_code == 200
    assert 'reply' in response.json
```

---

## Deployment

### Local Development
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create .env
echo "OPENAI_API_KEY=sk-..." > .env

# 3. Run server
python run.py
```

### Production (Future)
- Gunicorn/uWSGI statt Flask Dev Server
- Environment-based Config
- Proper Secrets Management (Vault, AWS Secrets Manager)

# 🏗️ Layered Architecture for Insurance Chatbots

## Overview

This application implements a **3-layer hierarchical architecture** for building scalable, reusable chatbots across multiple insurance products and workflows.

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: UNIVERSAL                                         │
│  Base rules for ALL insurance chatbots                      │
│  ├── interaction/base_patterns.txt                          │
│  ├── interaction/dos_donts.txt                              │
│  └── knowledge/insurance_basics.yaml                        │
└─────────────────────────────────────────────────────────────┘
                          ↓ inherits & can override
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: PRODUCT-SPECIFIC (e.g., Sterbegeld)              │
│  Product-specific rules and knowledge                       │
│  ├── config.yaml                                            │
│  ├── workflow_router.yaml                                   │
│  ├── prompts/interaction_rules.txt                          │
│  ├── prompts/objection_handling.txt                         │
│  ├── product_info.yaml                                      │
│  └── tariffs.json                                           │
└─────────────────────────────────────────────────────────────┘
                          ↓ inherits & can override
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: WORKFLOW-SPECIFIC (e.g., Tariff Comparison)      │
│  Workflow-specific behavior and output                      │
│  ├── behavior.txt                                           │
│  └── output_format.txt                                      │
└─────────────────────────────────────────────────────────────┘
```

## 🎯 Design Principles

### 1. **Explicit Hierarchy**
- **Layer 3 (Workflow)** > **Layer 2 (Product)** > **Layer 1 (Universal)**
- More specific layers **override** more general layers
- Ensures predictable behavior and easy debugging

### 2. **Override Mechanism**
Each layer can:
- ✅ **Override** specific rules from parent layers
- ✅ **Keep** specific rules from parent layers
- ✅ **Exclude** specific components from parent layers
- ✅ **Extend** parent layer rules with additional specifics

### 3. **Reusability**
- **Universal layer**: Write once, use across all products
- **Product layer**: Reuse across all workflows for that product
- **Workflow layer**: Mix and match workflows across products

### 4. **Scalability**
Adding a new product or workflow is easy:
- New product: Copy template, customize Layer 2
- New workflow: Create Layer 3 folder, define behavior
- No need to duplicate universal rules

## 📂 Directory Structure

```
data/
├── universal/                    # LAYER 1: Universal Rules
│   ├── interaction/
│   │   ├── base_patterns.txt    # Core interaction patterns
│   │   └── dos_donts.txt        # Universal rules
│   └── knowledge/
│       └── insurance_basics.yaml # General insurance concepts
│
├── products/                     # LAYER 2: Product-Specific
│   └── sterbegeld/
│       ├── config.yaml           # Product config + overrides
│       ├── workflow_router.yaml  # Workflow routing logic
│       ├── prompts/
│       │   ├── interaction_rules.txt     # Product-specific style
│       │   └── objection_handling.txt    # Product objections
│       ├── product_info.yaml     # Factual knowledge
│       └── tariffs.json          # Tariff data
│
└── workflows/                    # LAYER 3: Workflow-Specific
    └── tariff_info_comparison/
        ├── behavior.txt          # Workflow conversation flow
        └── output_format.txt     # Workflow output rules
```

## 🔧 Core Components

### `HierarchyComposer` Class
**Location**: `app/core/prompt_builder/hierarchy_composer.py`

**Main Methods**:
```python
# Build complete system prompt from all 3 layers
composer.build_system_prompt(
    product_id="sterbegeld",
    workflow_id="tariff_info_comparison",
    product_info={...}  # Optional: inject product knowledge
)

# Determine which workflow to activate based on user intent
composer.determine_workflow(
    product_id="sterbegeld",
    user_message="Ich möchte Tarife vergleichen"
)
```

### Workflow Routing
**Location**: `data/products/{product_id}/workflow_router.yaml`

Defines:
- Default workflow
- Available workflows with triggers
- Workflow-specific overrides

Example:
```yaml
workflow_routing:
  default_workflow: tariff_info_comparison
  workflows:
    - id: tariff_info_comparison
      name: Tarif-Informationen, Vergleich & Auswahl
      triggers:
        - "tarif"
        - "vergleich"
        - "kosten"
      overrides:
        emojis:
          max_per_message: 0  # Override: No emojis in tariff output
```

## 📝 Configuration Files

### Layer 1: Universal
#### `base_patterns.txt`
- Tonalität (Du vs. Sie)
- Multi-Turn-Dialog principles
- Error handling
- Data privacy

#### `dos_donts.txt`
- Universal communication rules
- Question asking patterns
- Example usage
- Legal boundaries

### Layer 2: Product-Specific
#### `config.yaml`
```yaml
product:
  id: sterbegeld
  name: Sterbegeldversicherung
  description: Absicherung der Bestattungskosten
  
  overrides:
    from_universal:
      emojis:
        usage: MINIMAL
        max_per_message: 1
        reason: Sensibles Thema Tod
      
      terminology:
        avoid_terms: ["wenn du stirbst", "wenn du tot bist"]
        preferred_terms: ["im Todesfall", "für den Ernstfall"]
  
  keep_from_universal:
    - questions.max_per_response
    - formality
    - data_privacy
```

#### `workflow_router.yaml`
Defines which workflow to activate based on user intent.

#### `prompts/interaction_rules.txt`
Product-specific communication style (e.g., empathy for Sterbegeld).

#### `prompts/objection_handling.txt`
How to handle common objections (e.g., "too expensive").

### Layer 3: Workflow-Specific
#### `behavior.txt`
- Conversation flow (phases)
- Parameter collection logic
- Decision tree

#### `output_format.txt`
- How to format responses
- Tariff presentation rules
- Bullet points, bolding, etc.

## 🔄 Override Mechanism

### How Overrides Work

1. **Product overrides Universal**:
   ```yaml
   # In product config.yaml
   overrides:
     from_universal:
       emojis:
         max_per_message: 1  # Universal has 2, product overrides to 1
   ```

2. **Workflow overrides Product** (and Universal):
   ```yaml
   # In workflow_router.yaml
   workflows:
     - id: tariff_info_comparison
       overrides:
         emojis:
           max_per_message: 0  # Tariff output: no emojis at all
   ```

3. **Keep specific rules from parent**:
   ```yaml
   keep_from_universal:
     - questions.max_per_response  # Keep this rule from universal
     - data_privacy                 # Keep this rule too
   ```

4. **Exclude specific components**:
   ```yaml
   exclude_from_universal:
     - insurance_basics  # Don't load universal insurance knowledge
   ```

### Override Priority Chain
```
Workflow Override > Product Override > Universal Default
```

## 🚀 Adding New Products/Workflows

### Adding a New Product (e.g., "Zahnzusatzversicherung")

1. **Create directory structure**:
   ```bash
   mkdir -p data/products/zahnzusatz/prompts
   ```

2. **Create `config.yaml`**:
   ```yaml
   product:
     id: zahnzusatz
     name: Zahnzusatzversicherung
     description: Ergänzung zur gesetzlichen Krankenversicherung
     
     overrides:
       from_universal:
         emojis:
           max_per_message: 2  # More friendly tone than Sterbegeld
   ```

3. **Create `workflow_router.yaml`**:
   ```yaml
   workflow_routing:
     default_workflow: tariff_info_comparison
     workflows:
       - id: tariff_info_comparison
         triggers: ["tarif", "vergleich", "kosten"]
   ```

4. **Add product-specific prompts**:
   - `prompts/interaction_rules.txt`
   - `prompts/objection_handling.txt`

5. **Add data**:
   - `product_info.yaml` (factual knowledge)
   - `tariffs.json` (tariff data)

### Adding a New Workflow (e.g., "Beratungsgespräch")

1. **Create workflow directory**:
   ```bash
   mkdir -p data/workflows/beratungsgespraech
   ```

2. **Create `behavior.txt`**:
   Define conversation flow, phases, decision logic.

3. **Create `output_format.txt`**:
   Define how responses should be formatted.

4. **Register in product's `workflow_router.yaml`**:
   ```yaml
   workflows:
     - id: beratungsgespraech
       name: Persönliches Beratungsgespräch
       triggers: ["beraten", "frage", "erklär mir"]
       overrides:
         emojis:
           max_per_message: 2  # More emojis in consultations
   ```

## 🧪 Testing

### Unit Tests
- `tests/test_hierarchy_composer.py`: Core composer logic
- `tests/test_tariff_engine.py`: Tariff search logic
- `tests/test_date_validation.py`: Date parsing/validation

### Integration Tests
- `tests/test_rounding_integration.py`: End-to-end rounding
- `tests/test_hierarchy_composer.py::TestLayerIntegration`: Layer file validation

### Running Tests
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_hierarchy_composer.py -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

## 📊 Benefits of This Architecture

| Benefit | Description |
|---------|-------------|
| **Scalability** | Add new products/workflows without duplicating code |
| **Maintainability** | Update universal rules once, apply everywhere |
| **Flexibility** | Each layer can override parent rules precisely |
| **Testability** | Each layer can be tested independently |
| **Clarity** | Clear separation of concerns (Universal → Product → Workflow) |
| **Reusability** | Workflows can be reused across products |

## 🔮 Future Enhancements

1. **Dynamic Workflow Switching**: Allow user to switch workflows mid-conversation
2. **Multi-Product Comparison**: Compare tariffs across product types
3. **A/B Testing**: Test different prompt variations per layer
4. **Version Control**: Track changes to prompts over time
5. **Analytics**: Measure which rules/overrides impact conversation quality

## 📚 Further Reading

- [SpecsForge Documentation](./specs/project-overview.md)
- [Chatbot Logic](./specs/chatbot-logic.md)
- [LLM Integration](./specs/llm-integration.md)
- [Frontend Design](./FRONTEND_REDESIGN.md)

---

**Last Updated**: November 2025  
**Architecture Version**: 2.0 (Layered)

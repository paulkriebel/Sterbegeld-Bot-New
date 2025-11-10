"""
Function Definitions for OpenAI Function Calling
"""

# tariff_search function definition
TARIFF_SEARCH_FUNCTION = {
    "name": "tariff_search",
    "description": "Search for suitable Sterbegeld insurance tariffs based on customer requirements",
    "parameters": {
        "type": "object",
        "properties": {
            "birth_date": {
                "type": "string",
                "description": "Customer's birth date in German format: DD.MM.YYYY (e.g., 15.05.1980) or DD. Month YYYY (e.g., 15. Mai 1980). NEVER use YYYY-MM-DD format."
            },
            "coverage_amount": {
                "type": "integer",
                "description": "Desired coverage amount in EUR (e.g., 5000)"
            },
            "health_declaration_required": {
                "type": "string",
                "enum": ["Ja", "Nein"],
                "description": "Whether health declaration is required (optional filter)"
            },
            "waiting_period_months": {
                "type": "string",
                "description": "Waiting period in months: 'Keine', '12', '18', '24' (optional filter)"
            },
            "contribution_free_from_age": {
                "type": "integer",
                "description": "Age when contributions become free: 65, 75, or 85 (optional filter)"
            },
            "surplus_regulation": {
                "type": "string",
                "enum": ["Bonuszahlung", "Beitragsrabatt", "Keine"],
                "description": "Type of surplus regulation (optional filter)"
            },
            "payment_method": {
                "type": "string",
                "enum": ["Monatlich", "Einmalig"],
                "description": "Payment method (optional filter)"
            }
        },
        "required": ["birth_date", "coverage_amount"]
    }
}


# show_form function definition
SHOW_FORM_FUNCTION = {
    "name": "show_form",
    "description": "Zeige ein Formular zur strukturierten Dateneingabe im Chat. Verwende dies wenn du Kundendaten sammeln möchtest.",
    "parameters": {
        "type": "object",
        "properties": {
            "form_type": {
                "type": "string",
                "enum": ["health_check", "personal_data", "policyholder", "beneficiary", "bank_details", "summary"],
                "description": "Typ des anzuzeigenden Formulars"
            },
            "context_message": {
                "type": "string",
                "description": "Deine persönliche Nachricht an den Kunden, die VOR dem Formular angezeigt wird. Erkläre kurz was jetzt passiert."
            },
            "prefill_data": {
                "type": "object",
                "description": "Optional: Daten zum Vorbefüllen des Formulars (z.B. aus vorherigen Angaben)"
            }
        },
        "required": ["form_type", "context_message"]
    }
}

# switch_workflow function definition
SWITCH_WORKFLOW_FUNCTION = {
    "name": "switch_workflow",
    "description": "Wechsle zu einem anderen Workflow wenn der Kunde das möchte (z.B. zurück zu Infos/Vergleich). Contract-Daten bleiben immer erhalten!",
    "parameters": {
        "type": "object",
        "properties": {
            "target_workflow": {
                "type": "string",
                "enum": ["info", "contract", "comparison"],
                "description": "Ziel-Workflow: 'info' für Produktinfos/Fragen, 'comparison' für Tarifvergleich, 'contract' für Vertragsabschluss"
            },
            "reason": {
                "type": "string",
                "description": "Grund für den Wechsel - wird dem Kunden angezeigt"
            }
        },
        "required": ["target_workflow", "reason"]
    }
}

# save_form_data function definition
SAVE_FORM_DATA_FUNCTION = {
    "name": "save_form_data",
    "description": "Speichere ausgefüllte Formulardaten und bestimme nächsten Schritt. Wird automatisch aufgerufen wenn User Formular absendet.",
    "parameters": {
        "type": "object",
        "properties": {
            "form_type": {
                "type": "string",
                "description": "Typ des ausgefüllten Formulars"
            },
            "data": {
                "type": "object",
                "description": "Die ausgefüllten Formulardaten"
            },
            "next_action": {
                "type": "string",
                "enum": ["show_next_form", "show_summary", "ask_question"],
                "description": "Was soll als Nächstes passieren?"
            }
        },
        "required": ["form_type", "data", "next_action"]
    }
}

# List of all available functions
AVAILABLE_FUNCTIONS = [
    TARIFF_SEARCH_FUNCTION,
    SHOW_FORM_FUNCTION,
    SWITCH_WORKFLOW_FUNCTION,
    SAVE_FORM_DATA_FUNCTION
]

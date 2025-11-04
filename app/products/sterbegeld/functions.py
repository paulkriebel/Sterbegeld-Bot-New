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
                "description": "Customer's birth date in YYYY-MM-DD format"
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


# List of all available functions
AVAILABLE_FUNCTIONS = [
    TARIFF_SEARCH_FUNCTION
]

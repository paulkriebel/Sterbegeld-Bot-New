"""
Sterbegeld Chatbot
Main chatbot implementation for Sterbegeldversicherung product
"""
import os
import logging
import yaml
from typing import List, Dict, Any, Optional

from app.core.llm_client import LLMClient
from app.products.sterbegeld.functions import AVAILABLE_FUNCTIONS
from app.products.sterbegeld.tariff_engine import search_tariffs

logger = logging.getLogger(__name__)


class SterbeGeldChatbot:
    """
    Chatbot for Sterbegeld insurance consultation
    """
    
    def __init__(self, api_key: str, model: str = 'gpt-5'):
        """
        Initialize chatbot
        
        Args:
            api_key: OpenAI API key
            model: LLM model name
        """
        self.llm_client = LLMClient(api_key=api_key, model=model)
        self.system_prompt = self._build_system_prompt()
        logger.info("SterbeGeldChatbot initialized")
    
    def _load_prompt_file(self, filename: str) -> str:
        """Load prompt from file"""
        filepath = os.path.join('data', 'sterbegeld', 'prompts', filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _load_yaml_file(self, filename: str) -> Dict[str, Any]:
        """Load YAML configuration file"""
        filepath = os.path.join('data', 'sterbegeld', filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _yaml_to_text(self, data: Dict[str, Any], indent: int = 0) -> str:
        """Convert YAML data to readable text for LLM prompt"""
        lines = []
        prefix = "  " * indent
        
        for key, value in data.items():
            # Format key as title
            title = key.replace('_', ' ').title()
            
            if isinstance(value, dict):
                lines.append(f"{prefix}**{title}:**")
                lines.append(self._yaml_to_text(value, indent + 1))
            elif isinstance(value, list):
                lines.append(f"{prefix}**{title}:**")
                for item in value:
                    if isinstance(item, dict):
                        # Handle dict items in list
                        for k, v in item.items():
                            item_title = k.replace('_', ' ').title()
                            if isinstance(v, str):
                                lines.append(f"{prefix}  - {item_title}: {v}")
                            else:
                                lines.append(f"{prefix}  - {item_title}: {v}")
                    else:
                        lines.append(f"{prefix}  - {item}")
            elif isinstance(value, str):
                # Multi-line strings
                if '\n' in value:
                    lines.append(f"{prefix}**{title}:**")
                    for line in value.strip().split('\n'):
                        lines.append(f"{prefix}  {line.strip()}")
                else:
                    lines.append(f"{prefix}**{title}:** {value}")
            elif isinstance(value, bool):
                lines.append(f"{prefix}**{title}:** {'Ja' if value else 'Nein'}")
            else:
                lines.append(f"{prefix}**{title}:** {value}")
        
        return '\n'.join(lines)
    
    def _build_system_prompt(self) -> str:
        """
        Build system prompt from templates
        Combines: product_info (YAML) + tariff_table + interaction_style
        """
        # Load structured product info from YAML
        product_data = self._load_yaml_file('product_info.yaml')
        product_logic = self._yaml_to_text(product_data['sterbegeldversicherung'])
        
        tariff_table = self._load_prompt_file('tariff_table.txt')
        interaction_style = self._load_prompt_file('interaction_style.txt')
        
        system_prompt = f"""Du bist Sophie, eine KI-Versicherungsberaterin von CHECK24, spezialisiert auf Sterbegeldversicherungen.

# 1. PRODUKTLOGIK
{product_logic}

# 2. VERFÜGBARE TARIFE
{tariff_table}

# 3. INTERAKTIONSSTIL
{interaction_style}

# 4. DEINE AUFGABE
1. WEICHENSTELLUNG: Frage zuerst, ob User direkt Tarife finden möchte ODER erst Fragen/Infos hat
2. PFLICHT-PARAMETER erfassen (BEIDE ZWINGEND):
   - Geburtsdatum - WICHTIG: Verwende IMMER deutsche Datumsformate:
     * DD.MM.YYYY (z. B. "15.05.1980")
     * DD. Monat JJJJ (z. B. "15. Mai 1980")
     * NIEMALS das ISO-Format YYYY-MM-DD in der Kundenansprache verwenden!
   - Gewünschte Versicherungssumme
3. OPTIONAL-PARAMETER aktiv anbieten:
   - Frage: "Möchtest du die Ergebnisse filtern?"
   - Beitragsfrei ab, Gesundheitserklärung, Wartezeit, Überschussregelung, Zahlweise
   - Falls User "nein": Sofort tariff_search() aufrufen
4. Rufe die Funktion `tariff_search` auf, um passende Tarife zu finden
5. GEBURTSDATUM-VALIDIERUNG:
   - Wenn die Funktion `tariff_search` einen Fehler zurückgibt (error: true), dann:
     * Gib die Fehlermeldung freundlich an den Kunden weiter
     * Frage nach dem korrekten Geburtsdatum im deutschen Format
     * Beispiel: "Das Datum liegt in der Zukunft. Bitte gib dein richtiges Geburtsdatum ein (z. B. 15.05.1980)."
6. VERSICHERUNGSSUMMEN-RUNDUNG:
   - Wenn in den Suchergebnissen `rounding_applied: true` steht, informiere den Kunden ZUERST über die Anpassung
   - Verwende die Nachricht aus `rounding_info.message` und formuliere sie natürlich in deinem Stil
   - Beispiel: "Ich habe deine Versicherungssumme von 4.500 € auf 5.000 € aufgerundet, da unsere Tarife nur mit runden Versicherungssummen angeboten werden."
7. Empfehle dem Kunden die günstigste Option (markiere mit "GÜNSTIGSTER", KEIN Emoji!)

WICHTIG: Halte dich strikt an den definierten Interaktionsstil! SPARSAM mit Emojis!
"""
        return system_prompt
    
    def _execute_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute function call
        
        Args:
            function_name: Name of function to execute
            arguments: Function arguments
            
        Returns:
            Function result
        """
        if function_name == 'tariff_search':
            logger.info(f"Executing tariff_search with args: {arguments}")
            
            # Import validation and rounding functions
            from app.products.sterbegeld.tariff_engine import (
                needs_rounding, 
                round_coverage_amount,
                validate_birth_date,
                parse_german_date
            )
            
            # Validate birth date (check for future dates and parse German formats)
            birth_date = arguments.get('birth_date')
            if birth_date:
                validation_result = validate_birth_date(birth_date)
                
                if not validation_result['valid']:
                    # Return error that LLM can communicate to user
                    return {
                        'error': True,
                        'error_type': 'invalid_birth_date',
                        'error_message': validation_result['error'],
                        'user_message': f"❌ {validation_result['error']}"
                    }
                
                # Convert to ISO format for tariff search
                arguments['birth_date'] = validation_result['iso_date']
                logger.info(f"Parsed birth date: {birth_date} -> {validation_result['iso_date']}")
            
            # Check if coverage amount needs rounding
            original_coverage = arguments.get('coverage_amount')
            rounding_info = None
            
            if original_coverage and needs_rounding(original_coverage):
                rounded_coverage = round_coverage_amount(original_coverage)
                rounding_info = {
                    'original_amount': original_coverage,
                    'rounded_amount': rounded_coverage,
                    'message': f'Hinweis: Die Tarife werden mit runden Versicherungssummen angeboten. Ich habe deine gewünschte Versicherungssumme von {original_coverage:,.0f} € auf {rounded_coverage:,.0f} € angepasst.'
                }
                # Update the arguments with rounded amount
                arguments['coverage_amount'] = rounded_coverage
                logger.info(f"Rounded coverage amount from {original_coverage} to {rounded_coverage}")
            
            results = search_tariffs(**arguments)
            
            # Add rounding info to results if rounding occurred
            if rounding_info:
                return {
                    'rounding_applied': True,
                    'rounding_info': rounding_info,
                    'tariffs': results
                }
            else:
                return {
                    'rounding_applied': False,
                    'tariffs': results
                }
        else:
            logger.error(f"Unknown function: {function_name}")
            return []
    
    def chat(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Process user message and generate response
        
        Args:
            user_message: User's message
            conversation_history: Optional conversation history
            
        Returns:
            Response dictionary with 'reply' and 'debug' info
        """
        # Initialize or truncate history
        if conversation_history is None:
            conversation_history = []
        
        conversation_history = self.llm_client.truncate_history(
            conversation_history,
            max_messages=20
        )
        
        # Build messages for LLM
        messages = [
            {'role': 'system', 'content': self.system_prompt}
        ]
        messages.extend(conversation_history)
        messages.append({'role': 'user', 'content': user_message})
        
        # Call LLM
        try:
            response = self.llm_client.chat_completion(
                messages=messages,
                functions=AVAILABLE_FUNCTIONS,
                function_call='auto'
            )
            
            # Check if function call was made
            if response['function_call']:
                function_name = response['function_call']['name']
                arguments = response['function_call']['arguments']
                
                # Execute function
                function_result = self._execute_function(function_name, arguments)
                
                # Add function call and result to messages
                # GPT-5 uses new "tools" format
                import json
                
                # Check if we have tool_calls (GPT-5) or function_call (legacy)
                if response.get('tool_calls'):
                    # GPT-5 format: role='assistant' with tool_calls
                    messages.append({
                        'role': 'assistant',
                        'content': None,
                        'tool_calls': response['tool_calls']
                    })
                    # GPT-5 format: role='tool' with tool_call_id
                    messages.append({
                        'role': 'tool',
                        'tool_call_id': response['function_call']['id'],
                        'content': json.dumps(function_result)
                    })
                else:
                    # Legacy format for other models
                    messages.append({
                        'role': 'assistant',
                        'content': None,
                        'function_call': {
                            'name': response['function_call']['name'],
                            'arguments': json.dumps(response['function_call']['arguments'])
                        }
                    })
                    messages.append({
                        'role': 'function',
                        'name': function_name,
                        'content': json.dumps(function_result)
                    })
                
                # Call LLM again with function result
                follow_up_response = self.llm_client.chat_completion(
                    messages=messages,
                    functions=AVAILABLE_FUNCTIONS,
                    function_call='none'  # Don't call functions again
                )
                
                final_reply = follow_up_response['content']
            else:
                final_reply = response['content']
            
            # Extract updated conversation history (without system prompt)
            # This ensures frontend and backend stay in sync with function calls
            updated_history = messages[1:]  # Skip system prompt at index 0
            
            # Add final bot reply to history
            updated_history.append({
                'role': 'assistant',
                'content': final_reply
            })
            
            return {
                'reply': final_reply,
                'history': updated_history,  # Return full history including function calls
                'debug': {
                    'system_prompt': self.system_prompt,
                    'user_message': user_message,
                    'llm_response': response,
                    'tokens_used': response['usage']['total_tokens']
                }
            }
            
        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            return {
                'reply': 'Entschuldigung, ich habe gerade technische Probleme. Bitte versuche es in einer Minute erneut.',
                'debug': {
                    'error': str(e)
                }
            }

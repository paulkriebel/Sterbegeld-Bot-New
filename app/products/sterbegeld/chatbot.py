"""
Sterbegeld Chatbot
Main chatbot implementation for Sterbegeldversicherung product
"""
import os
import logging
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
    
    def _build_system_prompt(self) -> str:
        """
        Build system prompt from templates
        Combines: product_logic + tariff_table + interaction_style
        """
        product_logic = self._load_prompt_file('product_logic.txt')
        tariff_table = self._load_prompt_file('tariff_table.txt')
        interaction_style = self._load_prompt_file('interaction_style.txt')
        
        system_prompt = f"""Du bist ein KI-Versicherungsberater, spezialisiert auf Sterbegeldversicherungen.

# 1. PRODUKTLOGIK
{product_logic}

# 2. VERFÜGBARE TARIFE
{tariff_table}

# 3. INTERAKTIONSSTIL
{interaction_style}

# 4. DEINE AUFGABE
1. WEICHENSTELLUNG: Frage zuerst, ob User direkt Tarife finden möchte ODER erst Fragen/Infos hat
2. PFLICHT-PARAMETER erfassen (BEIDE ZWINGEND):
   - Geburtsdatum (Format: YYYY-MM-DD)
   - Gewünschte Versicherungssumme
3. OPTIONAL-PARAMETER aktiv anbieten:
   - Frage: "Möchtest du die Ergebnisse filtern?"
   - Beitragsfrei ab, Gesundheitserklärung, Wartezeit, Überschussregelung, Zahlweise
   - Falls User "nein": Sofort tariff_search() aufrufen
4. Rufe die Funktion `tariff_search` auf, um passende Tarife zu finden
5. Empfehle dem Kunden die günstigste Option (markiere mit "GÜNSTIGSTER", KEIN Emoji!)

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
            results = search_tariffs(**arguments)
            return results
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
                messages.append({
                    'role': 'assistant',
                    'content': None,
                    'function_call': response['function_call']
                })
                messages.append({
                    'role': 'function',
                    'name': function_name,
                    'content': str(function_result)
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
            
            return {
                'reply': final_reply,
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

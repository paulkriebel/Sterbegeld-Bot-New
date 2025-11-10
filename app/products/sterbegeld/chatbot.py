"""
Sterbegeld Chatbot
Main chatbot implementation for Sterbegeldversicherung product
"""
import os
import logging
import yaml
from typing import List, Dict, Any, Optional

from app.core.llm_client import LLMClient
from app.core.prompt_builder import HierarchyComposer
from app.products.sterbegeld.functions import AVAILABLE_FUNCTIONS
from app.products.sterbegeld.tariff_engine import search_tariffs
from app.products.sterbegeld.contract_state_manager import ContractStateManager

logger = logging.getLogger(__name__)

# Global state managers (in production: use Redis/Database)
# Key: session_id, Value: ContractStateManager
contract_states = {}


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
        from pathlib import Path
        self.data_dir = Path('data/sterbegeld')  # Legacy path for tariff_table.txt
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
    
    def _build_system_prompt(self, workflow_id: str = "tariff_info_comparison") -> str:
        """
        Build system prompt using the new Hierarchical Architecture.
        
        NEW ARCHITECTURE (3 Layers):
        - Layer 1: Universal rules for all insurance chatbots
        - Layer 2: Product-specific rules (Sterbegeld)
        - Layer 3: Workflow-specific behavior (dynamically selected)
        
        Args:
            workflow_id: Which workflow to load (tariff_info_comparison or tariff_contract_completion)
        
        Returns:
            Complete system prompt with all layers composed
        """
        # Initialize HierarchyComposer
        from pathlib import Path
        composer = HierarchyComposer(data_dir='data')
        
        # Load product info YAML for knowledge injection
        product_info_path = Path('data/products/sterbegeld/knowledge/product_info.yaml')
        product_info = None
        if product_info_path.exists():
            with open(product_info_path, 'r', encoding='utf-8') as f:
                product_info = yaml.safe_load(f)
        
        # Build complete system prompt with all layers
        # Product: "sterbegeld"
        # Workflow: dynamically selected based on current state
        system_prompt_body = composer.build_system_prompt(
            product_id="sterbegeld",
            workflow_id=workflow_id,
            product_info=product_info
        )
        
        # Add identity and role at the top
        identity = """Du bist Sophie, eine Versicherungsberaterin von CHECK24, spezialisiert auf Sterbegeldversicherungen.

"""
        
        # Add tariff table (still needed for available tariffs overview)
        tariff_table = self._load_prompt_file('tariff_table.txt')
        tariff_section = f"""
======================================================================
VERFÜGBARE TARIFE (Übersicht)
======================================================================

{tariff_table}

"""
        
        # Add final critical reminder about response length
        final_reminder = """
======================================================================
🚨 KRITISCHE ERINNERUNG - ANTWORTLÄNGE
======================================================================

ABSOLUTE REGEL: Max. 2 kurze Absätze pro Antwort!
- 1 Absatz = 2-3 Sätze
- Nur das Wichtigste
- Keine unangefragten Zusatzinfos
- Bei Bedarf: User kann nachfragen

AUSNAHME: Nur Tarifpräsentation (Top 3) darf länger sein.

"""
        
        return identity + system_prompt_body + tariff_section + final_reminder
    
    def _execute_function(self, function_name: str, arguments: Dict[str, Any], session_id: str = None) -> Any:
        """
        Execute function call
        
        Args:
            function_name: Name of function to execute
            arguments: Function arguments
            session_id: Session ID for state management
            
        Returns:
            Function result
        """
        if function_name == 'show_form':
            logger.info(f"Executing show_form: {arguments.get('form_type')}")
            
            prefill_data = arguments.get('prefill_data', {})
            
            # For personal_data form, add birthdate from state manager if available
            if arguments.get('form_type') == 'personal_data' and session_id and session_id in contract_states:
                state = contract_states[session_id]
                if state.birthdate:
                    prefill_data['birthdate'] = state.birthdate
                    prefill_data['birthdate_readonly'] = True
                    logger.info(f"Prefilling birthdate: {state.birthdate}")
            
            return {
                'action': 'show_form',
                'form_type': arguments.get('form_type'),
                'context_message': arguments.get('context_message'),
                'prefill_data': prefill_data
            }
        
        elif function_name == 'switch_workflow':
            logger.info(f"Executing switch_workflow to: {arguments.get('target_workflow')}")
            
            # Update state manager if exists
            if session_id and session_id in contract_states:
                state = contract_states[session_id]
                state.switch_workflow(arguments.get('target_workflow'), preserve_state=True)
            
            return {
                'action': 'switch_workflow',
                'target_workflow': arguments.get('target_workflow'),
                'reason': arguments.get('reason'),
                'state_preserved': True
            }
        
        elif function_name == 'save_form_data':
            logger.info(f"Executing save_form_data: {arguments.get('form_type')}")
            
            # Save to state manager if exists
            if session_id and session_id in contract_states:
                state = contract_states[session_id]
                state.save_form_data(arguments.get('form_type'), arguments.get('data', {}))
                
                # Determine next step
                next_form = None
                if arguments.get('next_action') == 'show_next_form':
                    next_form = state.get_next_form()
                
                return {
                    'action': 'save_form_data',
                    'form_type': arguments.get('form_type'),
                    'saved': True,
                    'next_action': arguments.get('next_action'),
                    'next_form': next_form,
                    'progress': state.get_progress()
                }
            
            return {
                'action': 'save_form_data',
                'saved': False,
                'error': 'No active contract session'
            }
        
        elif function_name == 'tariff_search':
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
        conversation_history: Optional[List[Dict[str, str]]] = None,
        session_id: str = None
    ) -> Dict[str, Any]:
        """
        Process user message and generate response
        
        Args:
            user_message: User's message
            conversation_history: Optional conversation history
            session_id: Session ID for state management
            
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
        
        # Determine current workflow based on session state
        from app.api.chat_routes import contract_states
        current_workflow = "tariff_info_comparison"  # Default
        if session_id and session_id in contract_states:
            state = contract_states[session_id]
            if state.current_workflow == "contract":
                current_workflow = "tariff_contract_completion"
        
        # Build system prompt dynamically based on current workflow
        system_prompt = self._build_system_prompt(workflow_id=current_workflow)
        logger.info(f"Using workflow: {current_workflow} for session {session_id}")
        
        # Build messages for LLM
        messages = [
            {'role': 'system', 'content': system_prompt}
        ]
        messages.extend(conversation_history)
        messages.append({'role': 'user', 'content': user_message})
        
        # Call LLM
        try:
            # Store function result for debug/frontend
            function_result_for_debug = None
            
            response = self.llm_client.chat_completion(
                messages=messages,
                functions=AVAILABLE_FUNCTIONS,
                function_call='auto'
            )
            
            # Check if function call was made
            if response['function_call']:
                function_name = response['function_call']['name']
                arguments = response['function_call']['arguments']
                
                # Execute function (with session_id for state management)
                function_result = self._execute_function(function_name, arguments, session_id=session_id)
                function_result_for_debug = function_result  # Save for response
                
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
                    'tokens_used': response['usage']['total_tokens'],
                    'function_result': function_result_for_debug  # Include for frontend buttons
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

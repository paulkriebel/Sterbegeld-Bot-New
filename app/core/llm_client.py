"""
OpenAI LLM Client
Wrapper for OpenAI API with GPT-5
"""
from openai import OpenAI
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class LLMClient:
    """
    OpenAI GPT-5 Client
    Handles chat completions and function calling
    """
    
    def __init__(self, api_key: str, model: str = 'gpt-5'):
        """
        Initialize LLM Client
        
        Args:
            api_key: OpenAI API key
            model: Model name (default: gpt-5)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        logger.info(f"LLMClient initialized with model: {model}")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: str = 'auto',
        temperature: float = 0.7,
        max_tokens: int = 500
    ) -> Dict[str, Any]:
        """
        Create chat completion
        
        Args:
            messages: List of message dictionaries
            functions: Optional function definitions for function calling
            function_call: 'auto', 'none', or specific function
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            
        Returns:
            Response dictionary
        """
        try:
            # Build request parameters
            params = {
                'model': self.model,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens
            }
            
            # Add functions if provided
            if functions:
                params['functions'] = functions
                params['function_call'] = function_call
            
            # Make API call
            logger.debug(f"Calling OpenAI API with {len(messages)} messages")
            response = self.client.chat.completions.create(**params)
            
            # Extract response
            message = response.choices[0].message
            
            result = {
                'content': message.content,
                'function_call': None,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
            
            # Check for function call
            if hasattr(message, 'function_call') and message.function_call:
                import json
                result['function_call'] = {
                    'name': message.function_call.name,
                    'arguments': json.loads(message.function_call.arguments)
                }
                logger.info(f"Function call: {message.function_call.name}")
            
            logger.info(f"Response received. Tokens: {result['usage']['total_tokens']}")
            return result
            
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def truncate_history(
        self,
        messages: List[Dict[str, str]],
        max_messages: int = 20
    ) -> List[Dict[str, str]]:
        """
        Truncate conversation history to last N messages
        (Always keep system message)
        
        Args:
            messages: List of messages
            max_messages: Maximum number of messages to keep
            
        Returns:
            Truncated list of messages
        """
        if len(messages) <= max_messages + 1:  # +1 for system message
            return messages
        
        # Keep system message + last N user/assistant messages
        system_message = messages[0] if messages and messages[0]['role'] == 'system' else None
        recent_messages = messages[-(max_messages):]
        
        if system_message:
            return [system_message] + recent_messages
        return recent_messages

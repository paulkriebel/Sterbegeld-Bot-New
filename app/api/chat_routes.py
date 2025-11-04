"""
API Routes for Chat Endpoints
"""
from flask import Blueprint, jsonify, request, current_app
from app.products.sterbegeld.chatbot import SterbeGeldChatbot
import logging

logger = logging.getLogger(__name__)
bp = Blueprint('api', __name__, url_prefix='/api')

# Initialize chatbot (lazy loading)
_chatbot = None


def get_chatbot():
    """Get or create chatbot instance"""
    global _chatbot
    if _chatbot is None:
        api_key = current_app.config['OPENAI_API_KEY']
        model = current_app.config['OPENAI_MODEL']
        _chatbot = SterbeGeldChatbot(api_key=api_key, model=model)
    return _chatbot


@bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Sterbegeld Bot API is running',
        'openai_configured': current_app.config['OPENAI_API_KEY'] is not None
    }), 200


@bp.route('/chat', methods=['POST'])
def chat():
    """
    Main chat endpoint
    Processes user message and returns bot response
    
    Request JSON:
    {
        "message": "User message",
        "conversation_history": [...]  # Optional
    }
    
    Response JSON:
    {
        "reply": "Bot response",
        "debug": {...}
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({
                'error': 'Missing "message" field in request'
            }), 400
        
        user_message = data['message']
        conversation_history = data.get('conversation_history', [])
        
        # Validate message length
        max_length = current_app.config.get('MAX_MESSAGE_LENGTH', 500)
        if len(user_message) > max_length:
            return jsonify({
                'error': f'Message too long (max {max_length} characters)'
            }), 400
        
        # Get chatbot and process message
        chatbot = get_chatbot()
        response = chatbot.chat(
            user_message=user_message,
            conversation_history=conversation_history
        )
        
        logger.info(f"Chat request processed successfully")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

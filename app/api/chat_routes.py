"""
API Routes for Chat Endpoints
"""
from flask import Blueprint, jsonify, request, current_app, session
from app.products.sterbegeld.chatbot import SterbeGeldChatbot, contract_states
from app.products.sterbegeld.contract_state_manager import ContractStateManager
import logging
import uuid

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
        # Accept both 'history' (new) and 'conversation_history' (legacy)
        conversation_history = data.get('history', data.get('conversation_history', []))
        
        # Get session ID for state management
        session_id = data.get('session_id', session.get('session_id'))
        
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
            conversation_history=conversation_history,
            session_id=session_id
        )
        
        # Extract tariffs if function was called (for frontend buttons)
        tariffs_data = None
        debug = response.get('debug', {})
        if 'function_result' in debug:
            result = debug['function_result']
            if isinstance(result, dict) and 'tariffs' in result:
                tariffs_data = result['tariffs'][:3]  # Top 3 only
                logger.info(f"Extracted {len(tariffs_data)} tariffs for frontend buttons")
        
        # Add tariffs to response
        response['tariffs'] = tariffs_data
        
        # Add contract progress info if in contract workflow
        if session_id and session_id in contract_states:
            state = contract_states[session_id]
            step_info = state.get_step_info()
            response['contract_progress'] = step_info
            logger.info(f"Contract progress: Step {step_info['current_step']}/{step_info['total_steps']}")
        
        logger.info(f"Chat request processed successfully")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@bp.route('/contract/init', methods=['POST'])
def init_contract():
    """
    Initialize contract workflow
    
    Request JSON:
    {
        "tariff": {...},  # Selected tariff data
        "session_id": "..."  # Optional, will be created if not provided
    }
    
    Response JSON:
    {
        "session_id": "...",
        "message": "Contract initialized",
        "first_form": "health_check" or "personal_data"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'tariff' not in data:
            return jsonify({'error': 'Missing tariff data'}), 400
        
        tariff_data = data['tariff']
        birthdate = data.get('birthdate')  # Birthdate from tariff search
        
        # Get or create session ID
        session_id = data.get('session_id') or str(uuid.uuid4())
        session['session_id'] = session_id
        
        # Create state manager
        state = ContractStateManager()
        state.initialize_contract(tariff_data, birthdate=birthdate)
        contract_states[session_id] = state
        
        # Determine first form
        first_form = state.get_next_form()
        
        logger.info(f"Contract initialized for session {session_id}. First form: {first_form}")
        
        return jsonify({
            'session_id': session_id,
            'message': 'Contract workflow initialized',
            'first_form': first_form,
            'requires_health_check': tariff_data.get('health_declaration_required', False)
        }), 200
        
    except Exception as e:
        logger.error(f"Contract init error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


@bp.route('/contract/state', methods=['GET'])
def get_contract_state():
    """
    Get current contract state
    
    Query params:
        session_id: Session ID
    
    Response JSON:
    {
        "exists": bool,
        "progress": int,
        "completed_steps": [...],
        "next_form": "...",
        "can_complete": bool
    }
    """
    try:
        session_id = request.args.get('session_id') or session.get('session_id')
        
        if not session_id or session_id not in contract_states:
            return jsonify({'exists': False}), 200
        
        state = contract_states[session_id]
        summary = state.get_summary()
        
        return jsonify({
            'exists': True,
            'progress': summary['progress'],
            'completed_steps': summary['completed_steps'],
            'next_form': state.get_next_form(),
            'can_complete': summary['can_complete'],
            'current_workflow': state.current_workflow
        }), 200
        
    except Exception as e:
        logger.error(f"Get contract state error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500


@bp.route('/contract/form/submit', methods=['POST'])
def submit_form():
    """
    Submit form data
    
    Request JSON:
    {
        "session_id": "...",
        "form_type": "...",
        "data": {...}
    }
    
    Response JSON:
    {
        "success": bool,
        "next_form": "...",
        "progress": int,
        "message": "..."
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'form_type' not in data or 'data' not in data:
            return jsonify({'error': 'Missing required fields'}), 400
        
        session_id = data.get('session_id') or session.get('session_id')
        
        if not session_id or session_id not in contract_states:
            return jsonify({'error': 'No active contract session'}), 400
        
        state = contract_states[session_id]
        form_type = data['form_type']
        form_data = data['data']
        
        # Save form data
        success = state.save_form_data(form_type, form_data)
        
        if not success:
            return jsonify({'error': 'Failed to save form data'}), 400
        
        # Get next form
        next_form = state.get_next_form()
        
        return jsonify({
            'success': True,
            'next_form': next_form,
            'progress': state.get_progress(),
            'message': f'{form_type} saved successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Submit form error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

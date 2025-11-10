"""
Contract State Manager
Manages contract workflow state across conversation turns and workflow switches
"""
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class ContractStateManager:
    """
    Manages contract workflow state with support for:
    - Multi-step form data collection
    - Workflow switching with state preservation
    - Progress tracking
    - Data validation
    """
    
    # Define required steps and their order
    FORM_STEPS = [
        'health_check',      # Only if tariff requires it
        'personal_data',     # Always required
        'policyholder',      # Always required (might be same as personal)
        'beneficiary',       # Always required (might be legal succession)
        'bank_details'       # Always required
    ]
    
    def __init__(self):
        """Initialize empty state"""
        self.current_workflow = "contract"
        self.contract_data = {}
        self.completed_steps = []
        self.selected_tariff = None
        self.current_form = None
        self.previous_workflow = None
        self.birthdate = None  # Store birthdate from tariff search
    
    def initialize_contract(self, tariff_data: Dict[str, Any], birthdate: str = None):
        """
        Initialize contract workflow with selected tariff
        
        Args:
            tariff_data: The tariff the customer selected
            birthdate: Birthdate used for tariff search (DD.MM.YYYY format)
        """
        self.selected_tariff = tariff_data
        self.current_workflow = "contract"
        self.contract_data = {}
        self.completed_steps = []
        self.current_form = None
        self.birthdate = birthdate
        
        logger.info(f"Contract initialized with tariff: {tariff_data.get('name')}, birthdate: {birthdate}")
    
    def save_form_data(self, form_type: str, data: Dict[str, Any]) -> bool:
        """
        Save form data and mark step as completed
        
        Args:
            form_type: Type of form (health_check, personal_data, etc.)
            data: Form data to save
            
        Returns:
            True if saved successfully
        """
        # Validate form type
        if form_type not in self.FORM_STEPS:
            logger.error(f"Invalid form type: {form_type}")
            return False
        
        # Save data
        self.contract_data[form_type] = data
        
        # Mark as completed if not already
        if form_type not in self.completed_steps:
            self.completed_steps.append(form_type)
            logger.info(f"Step completed: {form_type}. Progress: {self.get_progress()}%")
        
        self.current_form = None
        return True
    
    def get_next_form(self) -> Optional[str]:
        """
        Determine next form to show based on completed steps
        
        Returns:
            Next form type or None if all steps completed
        """
        for step in self.FORM_STEPS:
            # Skip health check if not required by tariff
            if step == 'health_check':
                if not self.selected_tariff or not self.selected_tariff.get('health_declaration_required', False):
                    continue
            
            # Return first incomplete step
            if step not in self.completed_steps:
                return step
        
        # All steps completed
        return None
    
    def get_progress(self) -> int:
        """
        Calculate completion progress (0-100%)
        
        Returns:
            Progress percentage
        """
        # Determine which steps are required for this contract
        required_steps = self._get_required_steps()
        
        if not required_steps:
            return 0
        
        completed_count = len([s for s in self.completed_steps if s in required_steps])
        progress = int((completed_count / len(required_steps)) * 100)
        
        return min(100, progress)
    
    def _get_required_steps(self) -> List[str]:
        """Get list of required steps for current tariff"""
        required = ['personal_data', 'policyholder', 'beneficiary', 'bank_details']
        
        # Add health check if required by tariff
        if self.selected_tariff and self.selected_tariff.get('health_declaration_required', False):
            required.insert(0, 'health_check')
        
        return required
    
    def get_step_info(self) -> dict:
        """
        Get current step information for progress display
        
        Returns:
            Dictionary with:
            - current_step: Current step number (1-based)
            - total_steps: Total number of steps
            - step_name: Human-readable name of current step
            - next_step_name: Name of next step (or None)
        """
        required_steps = self._get_required_steps()
        
        # Map form types to German names
        step_names = {
            'health_check': 'Gesundheitserklärung',
            'personal_data': 'Versicherte Person',
            'policyholder': 'Versicherungsnehmer',
            'beneficiary': 'Begünstigter',
            'bank_details': 'Bankverbindung',
            'summary': 'Zusammenfassung'
        }
        
        # Find current step
        next_form = self.get_next_form()
        if next_form:
            current_step = required_steps.index(next_form) + 1
            step_name = step_names.get(next_form, next_form)
            
            # Find next step name
            next_step_name = None
            if current_step < len(required_steps):
                next_form_type = required_steps[current_step]
                next_step_name = step_names.get(next_form_type, next_form_type)
        else:
            # All steps completed
            current_step = len(required_steps)
            step_name = 'Abgeschlossen'
            next_step_name = None
        
        return {
            'current_step': current_step,
            'total_steps': len(required_steps),
            'step_name': step_name,
            'next_step_name': next_step_name
        }
    
    def switch_workflow(self, target_workflow: str, preserve_state: bool = True) -> bool:
        """
        Switch to another workflow
        
        Args:
            target_workflow: Target workflow ID (info, contract, comparison)
            preserve_state: Whether to preserve contract data
            
        Returns:
            True if switch successful
        """
        if not preserve_state:
            # Reset contract state
            self.contract_data = {}
            self.completed_steps = []
            self.current_form = None
            logger.info(f"Switching to {target_workflow} workflow (state cleared)")
        else:
            # Preserve state for later return
            logger.info(f"Switching to {target_workflow} workflow (state preserved)")
        
        self.previous_workflow = self.current_workflow
        self.current_workflow = target_workflow
        
        return True
    
    def return_to_contract(self) -> bool:
        """
        Return to contract workflow from another workflow
        
        Returns:
            True if contract has saved state to resume
        """
        if not self.selected_tariff:
            logger.warning("No contract to return to")
            return False
        
        self.current_workflow = "contract"
        logger.info(f"Returned to contract workflow. Progress: {self.get_progress()}%")
        return True
    
    def set_current_form(self, form_type: str):
        """Set which form is currently displayed"""
        self.current_form = form_type
    
    def can_complete_contract(self) -> bool:
        """
        Check if all required data has been collected
        
        Returns:
            True if contract can be finalized
        """
        required_steps = self._get_required_steps()
        return all(step in self.completed_steps for step in required_steps)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get complete contract data summary
        
        Returns:
            Dictionary with all collected data
        """
        return {
            'tariff': self.selected_tariff,
            'data': self.contract_data,
            'completed_steps': self.completed_steps,
            'progress': self.get_progress(),
            'can_complete': self.can_complete_contract()
        }
    
    def validate_data(self) -> tuple[bool, Optional[str]]:
        """
        Validate all collected data
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_steps = self._get_required_steps()
        
        # Check all required steps completed
        for step in required_steps:
            if step not in self.completed_steps:
                return False, f"Schritt fehlt: {step}"
        
        # Validate personal data
        if 'personal_data' in self.contract_data:
            personal = self.contract_data['personal_data']
            if not personal.get('firstname') or not personal.get('lastname'):
                return False, "Name unvollständig"
        
        # Validate bank details
        if 'bank_details' in self.contract_data:
            bank = self.contract_data['bank_details']
            if not bank.get('iban'):
                return False, "IBAN fehlt"
            # Basic IBAN validation
            iban = bank['iban'].replace(' ', '')
            if len(iban) != 22 or not iban.startswith('DE'):
                return False, "IBAN ungültig"
        
        return True, None
    
    def reset(self):
        """Reset to initial state"""
        self.__init__()
        logger.info("Contract state reset")

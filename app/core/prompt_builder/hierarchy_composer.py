"""
Hierarchical Prompt Composer for Layered Architecture

This module implements a 3-layer architecture for building prompts:
- Layer 1 (Universal): Base patterns and knowledge for all insurance chatbots
- Layer 2 (Product-Specific): Product-specific rules and knowledge (e.g., Sterbegeld)
- Layer 3 (Workflow-Specific): Workflow-specific behavior (e.g., Tariff Comparison)

Features:
- Explicit hierarchy: More specific layers override more general ones
- Override mechanism: Fine-grained control with keep/override rules
- YAML-based configuration for easy maintenance
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any


class HierarchyComposer:
    """
    Composes prompts from multiple layers with override capabilities.
    
    Architecture:
        Layer 1 (Universal) → Layer 2 (Product) → Layer 3 (Workflow)
        
    Override Priority:
        Workflow > Product > Universal
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the HierarchyComposer.
        
        Args:
            data_dir: Base directory for all data files (default: "data")
        """
        self.data_dir = Path(data_dir)
        self.universal_dir = self.data_dir / "universal"
        self.products_dir = self.data_dir / "products"
        self.workflows_dir = self.data_dir / "workflows"
        
    def build_system_prompt(
        self, 
        product_id: str, 
        workflow_id: str,
        product_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build a complete system prompt by composing all layers.
        
        Args:
            product_id: Product identifier (e.g., "sterbegeld")
            workflow_id: Workflow identifier (e.g., "tariff_info_comparison")
            product_info: Optional product info YAML dict (for knowledge injection)
            
        Returns:
            Complete system prompt string
        """
        # Load configuration files
        product_config = self._load_product_config(product_id)
        workflow_config = self._load_workflow_config(product_id, workflow_id)
        
        # Build prompt sections
        sections = []
        
        # === LAYER 1: UNIVERSAL ===
        sections.append("=" * 70)
        sections.append("LAYER 1: UNIVERSAL RULES FOR ALL INSURANCE CHATBOTS")
        sections.append("=" * 70)
        sections.append("")
        
        # Universal interaction rules (merged base_patterns + dos_donts)
        universal_interaction = self._load_universal_interaction()
        if universal_interaction and self._should_include("interaction_rules", product_config, workflow_config):
            sections.append(universal_interaction)
            sections.append("")
        
        # Universal insurance knowledge (if requested)
        if product_info and self._should_include("insurance_basics", product_config, workflow_config):
            universal_knowledge = self._load_universal_knowledge()
            if universal_knowledge:
                sections.append(universal_knowledge)
                sections.append("")
        
        # === LAYER 2: PRODUCT-SPECIFIC ===
        sections.append("=" * 70)
        sections.append(f"LAYER 2: PRODUCT-SPECIFIC RULES FOR {product_id.upper()}")
        sections.append("=" * 70)
        sections.append("")
        
        # Product-specific interaction rules
        product_interaction = self._load_product_interaction(product_id)
        if product_interaction:
            sections.append(product_interaction)
            sections.append("")
        
        # Product-specific objection handling
        product_objections = self._load_product_objections(product_id)
        if product_objections:
            sections.append(product_objections)
            sections.append("")
        
        # Product knowledge (from product_info.yaml)
        if product_info:
            sections.append("## PRODUKT-WISSEN:")
            sections.append("")
            sections.append(self._format_product_info(product_info))
            sections.append("")
        
        # Product-specific overrides
        product_overrides = product_config.get("overrides", {})
        if product_overrides:
            sections.append("## PRODUCT-SPECIFIC OVERRIDES:")
            for key, value in product_overrides.items():
                sections.append(f"- {key}: {value}")
            sections.append("")
        
        # === LAYER 3: WORKFLOW-SPECIFIC ===
        sections.append("=" * 70)
        sections.append(f"LAYER 3: WORKFLOW-SPECIFIC RULES FOR '{workflow_id}'")
        sections.append("=" * 70)
        sections.append("")
        
        # Workflow behavior
        workflow_behavior = self._load_workflow_behavior(workflow_id)
        if workflow_behavior:
            sections.append(workflow_behavior)
            sections.append("")
        
        # Workflow output format
        workflow_output = self._load_workflow_output_format(workflow_id)
        if workflow_output:
            sections.append(workflow_output)
            sections.append("")
        
        # Workflow-specific overrides
        workflow_overrides = workflow_config.get("overrides", {})
        if workflow_overrides:
            sections.append("## WORKFLOW-SPECIFIC OVERRIDES:")
            for key, value in workflow_overrides.items():
                sections.append(f"- {key}: {value}")
            sections.append("")
        
        # === HIERARCHY SUMMARY ===
        sections.append("=" * 70)
        sections.append("HIERARCHY & OVERRIDE RULES")
        sections.append("=" * 70)
        sections.append("")
        sections.append("Override Priority: WORKFLOW > PRODUCT > UNIVERSAL")
        sections.append("")
        sections.append("If a rule is defined in multiple layers:")
        sections.append("1. Use the MOST SPECIFIC (Workflow) version")
        sections.append("2. Fall back to PRODUCT version if not in Workflow")
        sections.append("3. Fall back to UNIVERSAL version if not in Product")
        sections.append("")
        
        return "\n".join(sections)
    
    def determine_workflow(self, product_id: str, user_message: str) -> str:
        """
        Determine which workflow to activate based on user intent.
        
        Args:
            product_id: Product identifier
            user_message: User's input message
            
        Returns:
            Workflow ID
        """
        router_config = self._load_workflow_router(product_id)
        
        # Get default workflow
        default_workflow = router_config.get("default_workflow", "tariff_info_comparison")
        
        # Check all workflows for matching triggers
        workflows = router_config.get("workflows", [])
        user_lower = user_message.lower()
        
        for workflow in workflows:
            workflow_id = workflow.get("id")
            triggers = workflow.get("triggers", [])
            if any(trigger.lower() in user_lower for trigger in triggers):
                return workflow_id
        
        return default_workflow
    
    # ===== PRIVATE HELPER METHODS =====
    
    def _load_product_config(self, product_id: str) -> Dict[str, Any]:
        """Load product configuration YAML."""
        config_path = self.products_dir / product_id / "config.yaml"
        config = self._load_yaml(config_path)
        # Handle nested structure: extract 'product' key if exists
        if "product" in config:
            return config["product"]
        return config
    
    def _load_workflow_config(self, product_id: str, workflow_id: str) -> Dict[str, Any]:
        """Load workflow configuration from product's workflow router."""
        router = self._load_workflow_router(product_id)
        workflows = router.get("workflows", [])
        
        # Workflows is a list, find the one matching workflow_id
        for workflow in workflows:
            if workflow.get("id") == workflow_id:
                return workflow
        
        return {}
    
    def _load_workflow_router(self, product_id: str) -> Dict[str, Any]:
        """Load workflow router configuration."""
        router_path = self.products_dir / product_id / "workflow_router.yaml"
        router = self._load_yaml(router_path)
        # Handle nested structure: extract 'workflow_routing' key if exists
        if "workflow_routing" in router:
            return router["workflow_routing"]
        return router
    
    def _load_universal_interaction(self) -> Optional[str]:
        """Load universal interaction rules (merged base_patterns + dos_donts)."""
        path = self.universal_dir / "interaction" / "universal_interaction_rules.txt"
        return self._load_text(path)
    
    def _load_universal_knowledge(self) -> Optional[str]:
        """Load universal insurance knowledge."""
        path = self.universal_dir / "knowledge" / "insurance_basics.yaml"
        yaml_data = self._load_yaml(path)
        if yaml_data:
            return self._format_yaml_as_text(yaml_data, "UNIVERSAL INSURANCE KNOWLEDGE")
        return None
    
    def _load_product_interaction(self, product_id: str) -> Optional[str]:
        """Load product-specific interaction rules."""
        path = self.products_dir / product_id / "prompts" / "interaction_rules.txt"
        return self._load_text(path)
    
    def _load_product_objections(self, product_id: str) -> Optional[str]:
        """Load product-specific objection handling."""
        path = self.products_dir / product_id / "prompts" / "objection_handling.txt"
        return self._load_text(path)
    
    def _load_workflow_behavior(self, workflow_id: str) -> Optional[str]:
        """Load workflow-specific behavior."""
        path = self.workflows_dir / workflow_id / "behavior.txt"
        return self._load_text(path)
    
    def _load_workflow_output_format(self, workflow_id: str) -> Optional[str]:
        """Load workflow-specific output format."""
        path = self.workflows_dir / workflow_id / "output_format.txt"
        return self._load_text(path)
    
    def _should_include(
        self, 
        component: str, 
        product_config: Dict[str, Any], 
        workflow_config: Dict[str, Any]
    ) -> bool:
        """
        Determine if a universal component should be included based on overrides.
        
        Args:
            component: Component name (e.g., "interaction_patterns")
            product_config: Product configuration
            workflow_config: Workflow configuration
            
        Returns:
            True if component should be included
        """
        # Check workflow-level exclusions first (highest priority)
        workflow_exclude = workflow_config.get("exclude_from_universal", [])
        if component in workflow_exclude:
            return False
        
        # Check product-level exclusions
        product_exclude = product_config.get("exclude_from_universal", [])
        if component in product_exclude:
            return False
        
        # Check product-level keep list
        product_keep = product_config.get("keep_from_universal", [])
        if product_keep and component not in product_keep:
            return False
        
        return True
    
    def _format_product_info(self, product_info: Dict[str, Any]) -> str:
        """Format product_info YAML as readable text."""
        return self._format_yaml_as_text(product_info, "PRODUCT INFORMATION")
    
    def _format_yaml_as_text(self, data: Dict[str, Any], title: str) -> str:
        """Convert YAML dict to formatted text."""
        lines = [f"### {title}", ""]
        lines.append("```yaml")
        lines.append(yaml.dump(data, allow_unicode=True, default_flow_style=False, sort_keys=False))
        lines.append("```")
        return "\n".join(lines)
    
    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load YAML file, return empty dict if not found."""
        if not path.exists():
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Could not load {path}: {e}")
            return {}
    
    def _load_text(self, path: Path) -> Optional[str]:
        """Load text file, return None if not found."""
        if not path.exists():
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"Warning: Could not load {path}: {e}")
            return None

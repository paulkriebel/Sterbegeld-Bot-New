"""
Tests for HierarchyComposer - Layered Prompt Architecture
"""

import pytest
import os
import yaml
from pathlib import Path

from app.core.prompt_builder import HierarchyComposer


class TestHierarchyComposer:
    """Test suite for the HierarchyComposer class"""
    
    @pytest.fixture
    def composer(self):
        """Create a HierarchyComposer instance"""
        return HierarchyComposer(data_dir="data")
    
    def test_composer_initialization(self, composer):
        """Test that composer initializes with correct directory paths"""
        assert composer.data_dir.name == "data"
        assert composer.universal_dir.name == "universal"
        assert composer.products_dir.name == "products"
        assert composer.workflows_dir.name == "workflows"
    
    def test_build_system_prompt_basic(self, composer):
        """Test building a basic system prompt"""
        prompt = composer.build_system_prompt(
            product_id="sterbegeld",
            workflow_id="tariff_info_comparison"
        )
        
        # Check that all three layers are present
        assert "LAYER 1: UNIVERSAL" in prompt
        assert "LAYER 2: PRODUCT-SPECIFIC" in prompt
        assert "LAYER 3: WORKFLOW-SPECIFIC" in prompt
        assert "HIERARCHY & OVERRIDE RULES" in prompt
    
    def test_build_system_prompt_with_product_info(self, composer):
        """Test building prompt with product info injection"""
        product_info = {
            "sterbegeldversicherung": {
                "definition": "Test definition"
            }
        }
        
        prompt = composer.build_system_prompt(
            product_id="sterbegeld",
            workflow_id="tariff_info_comparison",
            product_info=product_info
        )
        
        assert "PRODUKT-WISSEN" in prompt
        assert "sterbegeldversicherung" in prompt
    
    def test_layer_content_presence(self, composer):
        """Test that specific layer content is present"""
        prompt = composer.build_system_prompt(
            product_id="sterbegeld",
            workflow_id="tariff_info_comparison"
        )
        
        # Universal layer content
        assert "TONALITÄT" in prompt or "Tonalität" in prompt
        
        # Product layer content
        assert "EMPATHIE" in prompt or "Empathie" in prompt
        assert "sterbegeld" in prompt.lower()
        
        # Workflow layer content (updated for flexible workflow structure)
        assert "KONVERSATIONS-PRINZIPIEN" in prompt or "WORKFLOW-ZIEL" in prompt
        assert "PFLICHT-PARAMETER" in prompt
    
    def test_determine_workflow_default(self, composer):
        """Test workflow determination with default workflow"""
        workflow = composer.determine_workflow(
            product_id="sterbegeld",
            user_message="Hallo"
        )
        
        assert workflow == "tariff_info_comparison"
    
    def test_determine_workflow_with_trigger(self, composer):
        """Test workflow determination with specific trigger"""
        # Test with various trigger phrases from workflow_router.yaml
        test_cases = [
            "Ich möchte Tarife vergleichen",
            "Zeig mir passende Angebote",
            "Was kostet eine Sterbegeldversicherung?"
        ]
        
        for message in test_cases:
            workflow = composer.determine_workflow(
                product_id="sterbegeld",
                user_message=message
            )
            # Should return the correct workflow (tariff_info_comparison in this case)
            assert workflow in ["tariff_info_comparison"]
    
    def test_load_product_config(self, composer):
        """Test loading product configuration"""
        config = composer._load_product_config("sterbegeld")
        
        assert isinstance(config, dict)
        assert "id" in config
        assert config["id"] == "sterbegeld"
    
    def test_load_workflow_router(self, composer):
        """Test loading workflow router"""
        router = composer._load_workflow_router("sterbegeld")
        
        assert isinstance(router, dict)
        assert "default_workflow" in router
        assert "workflows" in router
    
    def test_override_mechanism(self, composer):
        """Test that overrides are properly indicated in the prompt"""
        prompt = composer.build_system_prompt(
            product_id="sterbegeld",
            workflow_id="tariff_info_comparison"
        )
        
        # Check for override priority message
        assert "Override Priority: WORKFLOW > PRODUCT > UNIVERSAL" in prompt
    
    def test_load_nonexistent_files_gracefully(self, composer):
        """Test that missing files are handled gracefully"""
        # This should not raise an exception
        prompt = composer.build_system_prompt(
            product_id="nonexistent_product",
            workflow_id="nonexistent_workflow"
        )
        
        # Should still return a prompt (even if mostly empty)
        assert isinstance(prompt, str)
        assert len(prompt) > 0


class TestLayerIntegration:
    """Integration tests for the layered architecture"""
    
    def test_all_layer_files_exist(self):
        """Verify that all required layer files exist"""
        base_path = Path("data")
        
        # Layer 1 (Universal) files
        assert (base_path / "universal/interaction/universal_interaction_rules.txt").exists()
        assert (base_path / "universal/knowledge/insurance_basics.yaml").exists()
        
        # Layer 2 (Product) files
        assert (base_path / "products/sterbegeld/config.yaml").exists()
        assert (base_path / "products/sterbegeld/workflow_router.yaml").exists()
        assert (base_path / "products/sterbegeld/prompts/interaction_rules.txt").exists()
        assert (base_path / "products/sterbegeld/prompts/objection_handling.txt").exists()
        
        # Layer 3 (Workflow) files
        assert (base_path / "workflows/tariff_info_comparison/behavior.txt").exists()
        assert (base_path / "workflows/tariff_info_comparison/output_format.txt").exists()
    
    def test_yaml_files_valid(self):
        """Test that all YAML files are valid and can be parsed"""
        base_path = Path("data")
        
        yaml_files = [
            base_path / "universal/knowledge/insurance_basics.yaml",
            base_path / "products/sterbegeld/config.yaml",
            base_path / "products/sterbegeld/workflow_router.yaml",
        ]
        
        for yaml_file in yaml_files:
            assert yaml_file.exists(), f"File not found: {yaml_file}"
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                assert data is not None, f"Failed to parse: {yaml_file}"
    
    def test_prompt_not_too_large(self):
        """Test that the composed prompt is not excessively large"""
        composer = HierarchyComposer(data_dir="data")
        prompt = composer.build_system_prompt(
            product_id="sterbegeld",
            workflow_id="tariff_info_comparison"
        )
        
        # Check prompt length (should be reasonable for LLM context)
        # Using a generous limit of 50,000 characters
        assert len(prompt) < 50000, f"Prompt too large: {len(prompt)} characters"
        
        # But not too small either (should have actual content)
        assert len(prompt) > 1000, f"Prompt too small: {len(prompt)} characters"

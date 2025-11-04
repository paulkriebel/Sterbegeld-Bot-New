"""
Tests for Tariff Schema Validation
TDD: Red-Green-Refactor
"""
import json
import os
import pytest


def test_tariff_schema_validation():
    """
    TEST: Tarif-JSON hat alle Pflichtfelder
    RED Phase: Dieser Test wird initially fehlschlagen
    """
    # Path to tariffs.json
    tariff_file = os.path.join('data', 'sterbegeld', 'tariffs.json')
    
    # Check file exists
    assert os.path.exists(tariff_file), f"Tariff file not found: {tariff_file}"
    
    # Load JSON
    with open(tariff_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Check structure
    assert 'tariffs' in data, "JSON must have 'tariffs' key"
    tariffs = data['tariffs']
    assert isinstance(tariffs, list), "'tariffs' must be a list"
    assert len(tariffs) >= 5, "Must have at least 5 example tariffs"
    
    # Required fields (from specs/tariff-data.md)
    required_fields = [
        'name',
        'provider',
        'age_min',
        'age_max',
        'coverage_amount',
        'monthly_premium',
        'health_declaration_required',
        'contribution_free_from_age',
        'waiting_period_months',
        'surplus_regulation',
        'payment_method'
    ]
    
    # Validate each tariff
    for i, tariff in enumerate(tariffs):
        for field in required_fields:
            assert field in tariff, f"Tariff {i} missing required field: {field}"
        
        # Type validation
        assert isinstance(tariff['name'], str), f"Tariff {i}: name must be string"
        assert isinstance(tariff['provider'], str), f"Tariff {i}: provider must be string"
        assert isinstance(tariff['age_min'], int), f"Tariff {i}: age_min must be int"
        assert isinstance(tariff['age_max'], int), f"Tariff {i}: age_max must be int"
        assert isinstance(tariff['coverage_amount'], int), f"Tariff {i}: coverage_amount must be int"
        assert isinstance(tariff['monthly_premium'], (int, float)), f"Tariff {i}: monthly_premium must be number"
        assert isinstance(tariff['health_declaration_required'], bool), f"Tariff {i}: health_declaration_required must be bool"
        assert isinstance(tariff['contribution_free_from_age'], (int, type(None))), f"Tariff {i}: contribution_free_from_age must be int or null"
        assert isinstance(tariff['waiting_period_months'], int), f"Tariff {i}: waiting_period_months must be int"
        assert isinstance(tariff['surplus_regulation'], str), f"Tariff {i}: surplus_regulation must be string"
        assert isinstance(tariff['payment_method'], str), f"Tariff {i}: payment_method must be string"
        
        # Value validation
        assert tariff['age_min'] >= 18, f"Tariff {i}: age_min must be >= 18"
        assert tariff['age_max'] <= 99, f"Tariff {i}: age_max must be <= 99"
        assert tariff['age_min'] < tariff['age_max'], f"Tariff {i}: age_min must be < age_max"
        assert tariff['coverage_amount'] >= 2000, f"Tariff {i}: coverage_amount must be >= 2000"
        assert tariff['monthly_premium'] > 0, f"Tariff {i}: monthly_premium must be > 0"
        assert tariff['waiting_period_months'] >= 0, f"Tariff {i}: waiting_period_months must be >= 0"


def test_tariff_json_structure():
    """Test that tariffs.json is valid JSON"""
    tariff_file = os.path.join('data', 'sterbegeld', 'tariffs.json')
    
    with open(tariff_file, 'r', encoding='utf-8') as f:
        data = json.load(f)  # Should not raise JSONDecodeError
        assert data is not None

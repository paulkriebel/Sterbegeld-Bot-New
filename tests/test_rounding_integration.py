"""
Integration tests for insurance sum rounding feature
Tests the end-to-end flow of rounding in the chatbot
"""
import pytest
from app.products.sterbegeld.tariff_engine import round_coverage_amount, needs_rounding


def test_rounding_exact_amounts():
    """Test that exact valid amounts don't get rounded"""
    assert round_coverage_amount(1000) == 1000
    assert round_coverage_amount(5000) == 5000
    assert round_coverage_amount(12500) == 12500
    assert round_coverage_amount(20000) == 20000
    assert needs_rounding(1000) == False
    assert needs_rounding(20000) == False


def test_rounding_between_amounts():
    """Test rounding up between valid amounts"""
    assert round_coverage_amount(1500) == 2000
    assert round_coverage_amount(4500) == 5000
    assert round_coverage_amount(7800) == 8000
    assert round_coverage_amount(11000) == 12500
    assert round_coverage_amount(13500) == 15000
    assert needs_rounding(4500) == True


def test_rounding_edge_case_below_minimum():
    """Test that amounts below 1000€ round up to 1000€"""
    assert round_coverage_amount(100) == 1000
    assert round_coverage_amount(500) == 1000
    assert round_coverage_amount(999) == 1000
    assert needs_rounding(500) == True


def test_rounding_edge_case_above_maximum():
    """Test that amounts above 20000€ are capped at 20000€"""
    assert round_coverage_amount(21000) == 20000
    assert round_coverage_amount(25000) == 20000
    assert round_coverage_amount(50000) == 20000
    assert needs_rounding(25000) == True


def test_rounding_between_10k_and_12_5k():
    """Test the special gap between 10k and 12.5k"""
    assert round_coverage_amount(10001) == 12500
    assert round_coverage_amount(10500) == 12500
    assert round_coverage_amount(11000) == 12500
    assert round_coverage_amount(12000) == 12500
    assert round_coverage_amount(12499) == 12500


def test_rounding_all_valid_amounts_list():
    """Verify all valid coverage amounts are recognized"""
    valid_amounts = [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, 12500, 15000, 20000]
    
    for amount in valid_amounts:
        assert needs_rounding(amount) == False, f"Amount {amount} should not need rounding"
        assert round_coverage_amount(amount) == amount, f"Amount {amount} should stay the same"

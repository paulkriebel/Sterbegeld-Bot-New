"""
Tests for birth date validation
"""
import pytest
from datetime import date, timedelta
from app.products.sterbegeld.tariff_engine import (
    parse_german_date,
    is_future_date,
    validate_birth_date
)


def test_parse_german_date_dd_mm_yyyy():
    """Test parsing DD.MM.YYYY format"""
    assert parse_german_date("15.05.1980") == "1980-05-15"
    assert parse_german_date("01.01.2000") == "2000-01-01"
    assert parse_german_date("31.12.1999") == "1999-12-31"


def test_parse_german_date_with_text_month():
    """Test parsing dates with text month (e.g., 05. Mai 1969)"""
    assert parse_german_date("05. Mai 1969") == "1969-05-05"
    assert parse_german_date("15. Januar 1980") == "1980-01-15"
    assert parse_german_date("31. Dezember 1999") == "1999-12-31"


def test_parse_german_date_iso_format_fallback():
    """Test that ISO format (YYYY-MM-DD) still works as fallback"""
    assert parse_german_date("1980-05-15") == "1980-05-15"
    assert parse_german_date("2000-01-01") == "2000-01-01"


def test_is_future_date():
    """Test detection of future dates"""
    # Future dates should return True
    tomorrow = date.today() + timedelta(days=1)
    assert is_future_date(tomorrow.strftime("%Y-%m-%d")) == True
    
    next_year = date.today().replace(year=date.today().year + 1)
    assert is_future_date(next_year.strftime("%Y-%m-%d")) == True
    
    # Past dates should return False
    assert is_future_date("1980-05-15") == False
    assert is_future_date("2000-01-01") == False
    
    # Today should return False (not in the future)
    today = date.today()
    assert is_future_date(today.strftime("%Y-%m-%d")) == False


def test_validate_birth_date_valid():
    """Test validation of valid birth dates"""
    result = validate_birth_date("15.05.1980")
    assert result['valid'] == True
    assert result['iso_date'] == "1980-05-15"
    assert 'error' not in result


def test_validate_birth_date_future():
    """Test validation rejects future dates"""
    tomorrow = date.today() + timedelta(days=1)
    future_date_str = tomorrow.strftime("%d.%m.%Y")
    
    result = validate_birth_date(future_date_str)
    assert result['valid'] == False
    assert 'error' in result
    assert 'zukunft' in result['error'].lower() or 'future' in result['error'].lower()


def test_validate_birth_date_invalid_format():
    """Test validation rejects invalid date formats"""
    result = validate_birth_date("invalid-date")
    assert result['valid'] == False
    assert 'error' in result


def test_validate_birth_date_today():
    """Test that today's date is accepted (edge case for newborns)"""
    today = date.today()
    today_str = today.strftime("%d.%m.%Y")
    
    result = validate_birth_date(today_str)
    # Today should be valid (not in the future)
    assert result['valid'] == True

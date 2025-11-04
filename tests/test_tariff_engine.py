"""
Tests for Tariff Search Engine
TDD: Red-Green-Refactor
"""
import pytest
from datetime import datetime, date


def test_filter_by_age():
    """
    TEST 1: Altersfilter - Nur Tarife im Altersbereich zurückgeben
    RED Phase: Wird fehlschlagen da filter_by_age() noch nicht existiert
    """
    from app.products.sterbegeld.tariff_engine import filter_by_age
    
    # Mock tariffs
    tariffs = [
        {'name': 'Tarif A', 'age_min': 18, 'age_max': 65},
        {'name': 'Tarif B', 'age_min': 40, 'age_max': 85},
        {'name': 'Tarif C', 'age_min': 50, 'age_max': 99},
    ]
    
    # Test: Age 45 sollte Tarif A und B zurückgeben
    result = filter_by_age(tariffs, 45)
    assert len(result) == 2
    assert result[0]['name'] == 'Tarif A'
    assert result[1]['name'] == 'Tarif B'
    
    # Test: Age 80 sollte nur Tarif B und C zurückgeben
    result = filter_by_age(tariffs, 80)
    assert len(result) == 2
    assert result[0]['name'] == 'Tarif B'
    assert result[1]['name'] == 'Tarif C'
    
    # Test: Age 17 sollte keine Tarife zurückgeben
    result = filter_by_age(tariffs, 17)
    assert len(result) == 0
    
    # Test: Age 100 sollte keine Tarife zurückgeben
    result = filter_by_age(tariffs, 100)
    assert len(result) == 0


def test_calculate_age_from_birthdate():
    """
    TEST: Alter aus Geburtsdatum berechnen
    """
    from app.products.sterbegeld.tariff_engine import calculate_age_from_birthdate
    
    # Test mit bekanntem Datum
    # Jemand geboren am 15.05.1980 ist heute (Nov 2025) 45 Jahre alt
    age = calculate_age_from_birthdate('1980-05-15')
    assert age == 45
    
    # Jemand geboren am 01.01.2000 ist 25 Jahre alt
    age = calculate_age_from_birthdate('2000-01-01')
    assert age == 25


def test_filter_by_coverage():
    """
    TEST 2: Versicherungssummen-Filter - Tarife >= gewünschter Summe
    RED Phase: Wird fehlschlagen da filter_by_coverage() noch nicht existiert
    """
    from app.products.sterbegeld.tariff_engine import filter_by_coverage
    
    # Mock tariffs
    tariffs = [
        {'name': 'Tarif A', 'coverage_amount': 3000},
        {'name': 'Tarif B', 'coverage_amount': 5000},
        {'name': 'Tarif C', 'coverage_amount': 8000},
    ]
    
    # Test: Gewünschte Summe 5000 sollte Tarif B und C zurückgeben
    result = filter_by_coverage(tariffs, 5000)
    assert len(result) == 2
    assert result[0]['name'] == 'Tarif B'
    assert result[1]['name'] == 'Tarif C'
    
    # Test: Gewünschte Summe 3000 sollte alle zurückgeben
    result = filter_by_coverage(tariffs, 3000)
    assert len(result) == 3
    
    # Test: Gewünschte Summe 10000 sollte keinen Tarif zurückgeben
    result = filter_by_coverage(tariffs, 10000)
    assert len(result) == 0


def test_filter_by_optional_params():
    """
    TEST 3: Optional-Parameter-Filter - Gesundheitserklärung, Wartezeit, etc.
    """
    from app.products.sterbegeld.tariff_engine import filter_by_optional_params
    
    # Mock tariffs
    tariffs = [
        {
            'name': 'Tarif A',
            'health_declaration_required': False,
            'waiting_period_months': 24,
            'contribution_free_from_age': 85,
            'surplus_regulation': 'Bonuszahlung',
            'payment_method': 'Monatlich'
        },
        {
            'name': 'Tarif B',
            'health_declaration_required': True,
            'waiting_period_months': 0,
            'contribution_free_from_age': 65,
            'surplus_regulation': 'Keine',
            'payment_method': 'Monatlich'
        },
        {
            'name': 'Tarif C',
            'health_declaration_required': False,
            'waiting_period_months': 18,
            'contribution_free_from_age': None,
            'surplus_regulation': 'Keine',
            'payment_method': 'Einmalig'
        }
    ]
    
    # Test: Keine Gesundheitserklärung
    result = filter_by_optional_params(tariffs, health_declaration_required='Nein')
    assert len(result) == 2
    assert result[0]['name'] == 'Tarif A'
    assert result[1]['name'] == 'Tarif C'
    
    # Test: Keine Wartezeit
    result = filter_by_optional_params(tariffs, waiting_period_months='Keine')
    assert len(result) == 1
    assert result[0]['name'] == 'Tarif B'
    
    # Test: Zahlweise Monatlich
    result = filter_by_optional_params(tariffs, payment_method='Monatlich')
    assert len(result) == 2
    
    # Test: Keine Filter (alle zurückgeben)
    result = filter_by_optional_params(tariffs)
    assert len(result) == 3


def test_rank_tariffs():
    """
    TEST 4: Ranking - Sortierung nach Preis (günstigster zuerst)
    """
    from app.products.sterbegeld.tariff_engine import rank_tariffs
    
    # Mock tariffs (unsortiert)
    tariffs = [
        {'name': 'Tarif B', 'monthly_premium': 25.50},
        {'name': 'Tarif A', 'monthly_premium': 10.20},
        {'name': 'Tarif C', 'monthly_premium': 17.80},
    ]
    
    # Test: Sortierung aufsteigend nach Preis
    result = rank_tariffs(tariffs)
    assert len(result) == 3
    assert result[0]['name'] == 'Tarif A'  # Günstigster
    assert result[1]['name'] == 'Tarif C'
    assert result[2]['name'] == 'Tarif B'  # Teuerster
    
    # Test: Top 2
    result = rank_tariffs(tariffs, top_n=2)
    assert len(result) == 2
    assert result[0]['name'] == 'Tarif A'
    assert result[1]['name'] == 'Tarif C'


def test_search_tariffs_integration():
    """
    TEST 5: Integration - Kompletter Tarif-Such-Flow
    """
    from app.products.sterbegeld.tariff_engine import search_tariffs
    
    # Test mit echten Tarifen aus tariffs.json
    result = search_tariffs(
        birth_date='1980-05-15',  # 45 Jahre alt
        coverage_amount=5000
    )
    
    # Sollte mindestens 1 Tarif finden
    assert len(result) > 0
    
    # Erster Tarif sollte günstigster sein
    if len(result) >= 2:
        assert result[0]['monthly_premium'] <= result[1]['monthly_premium']
    
    # Mit optionalen Parametern
    result = search_tariffs(
        birth_date='1980-05-15',
        coverage_amount=5000,
        health_declaration_required='Nein'
    )
    
    # Alle zurückgegebenen Tarife sollten keine Gesundheitserklärung erfordern
    for tariff in result:
        assert tariff['health_declaration_required'] == False

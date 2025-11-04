"""
Tariff Search Engine
Handles filtering, ranking, and searching of insurance tariffs
"""
import json
import os
from datetime import datetime, date
from typing import List, Dict, Any, Optional


def calculate_age_from_birthdate(birth_date_str: str) -> int:
    """
    Calculate age from birth date string
    
    Args:
        birth_date_str: Birth date in YYYY-MM-DD format
        
    Returns:
        Age in years
    """
    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age


def filter_by_age(tariffs: List[Dict[str, Any]], age: int) -> List[Dict[str, Any]]:
    """
    Filter tariffs by age range
    
    Args:
        tariffs: List of tariff dictionaries
        age: Customer age in years
        
    Returns:
        List of tariffs that match the age criteria
    """
    filtered = []
    for tariff in tariffs:
        if tariff['age_min'] <= age <= tariff['age_max']:
            filtered.append(tariff)
    return filtered


def filter_by_coverage(tariffs: List[Dict[str, Any]], desired_coverage: int) -> List[Dict[str, Any]]:
    """
    Filter tariffs by coverage amount (>= desired amount)
    
    Args:
        tariffs: List of tariff dictionaries
        desired_coverage: Desired coverage amount in EUR
        
    Returns:
        List of tariffs with coverage >= desired_coverage
    """
    filtered = []
    for tariff in tariffs:
        if tariff['coverage_amount'] >= desired_coverage:
            filtered.append(tariff)
    return filtered


def filter_by_optional_params(
    tariffs: List[Dict[str, Any]],
    health_declaration_required: Optional[str] = None,
    waiting_period_months: Optional[str] = None,
    contribution_free_from_age: Optional[int] = None,
    surplus_regulation: Optional[str] = None,
    payment_method: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Filter tariffs by optional parameters
    
    Args:
        tariffs: List of tariff dictionaries
        health_declaration_required: "Ja" or "Nein" (None = ignore)
        waiting_period_months: "Keine", "12", "18", "24" etc. (None = ignore)
        contribution_free_from_age: Age when contributions stop (None = ignore)
        surplus_regulation: "Bonuszahlung", "Beitragsrabatt", "Keine" (None = ignore)
        payment_method: "Monatlich" or "Einmalig" (None = ignore)
        
    Returns:
        Filtered list of tariffs
    """
    filtered = tariffs.copy()
    
    # Filter by health declaration
    if health_declaration_required is not None:
        required = (health_declaration_required.lower() == 'ja')
        filtered = [t for t in filtered if t['health_declaration_required'] == required]
    
    # Filter by waiting period
    if waiting_period_months is not None:
        if waiting_period_months.lower() == 'keine':
            filtered = [t for t in filtered if t['waiting_period_months'] == 0]
        else:
            try:
                months = int(waiting_period_months)
                filtered = [t for t in filtered if t['waiting_period_months'] == months]
            except ValueError:
                pass  # Invalid value, ignore filter
    
    # Filter by contribution free age
    if contribution_free_from_age is not None:
        filtered = [t for t in filtered if t.get('contribution_free_from_age') == contribution_free_from_age]
    
    # Filter by surplus regulation
    if surplus_regulation is not None:
        filtered = [t for t in filtered if t['surplus_regulation'] == surplus_regulation]
    
    # Filter by payment method
    if payment_method is not None:
        filtered = [t for t in filtered if t['payment_method'] == payment_method]
    
    return filtered


def rank_tariffs(tariffs: List[Dict[str, Any]], top_n: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Rank tariffs by monthly premium (cheapest first)
    
    Args:
        tariffs: List of tariff dictionaries
        top_n: Return only top N tariffs (None = all)
        
    Returns:
        Sorted list of tariffs (cheapest first)
    """
    sorted_tariffs = sorted(tariffs, key=lambda t: t['monthly_premium'])
    
    if top_n is not None:
        return sorted_tariffs[:top_n]
    
    return sorted_tariffs


def load_tariffs() -> List[Dict[str, Any]]:
    """
    Load tariffs from JSON file
    
    Returns:
        List of tariff dictionaries
    """
    tariff_file = os.path.join('data', 'sterbegeld', 'tariffs.json')
    with open(tariff_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['tariffs']


def search_tariffs(
    birth_date: str,
    coverage_amount: int,
    health_declaration_required: Optional[str] = None,
    waiting_period_months: Optional[str] = None,
    contribution_free_from_age: Optional[int] = None,
    surplus_regulation: Optional[str] = None,
    payment_method: Optional[str] = None,
    top_n: int = 3
) -> List[Dict[str, Any]]:
    """
    Main search function - filters and ranks tariffs
    
    Args:
        birth_date: Birth date in YYYY-MM-DD format
        coverage_amount: Desired coverage amount in EUR
        health_declaration_required: Optional filter
        waiting_period_months: Optional filter
        contribution_free_from_age: Optional filter
        surplus_regulation: Optional filter
        payment_method: Optional filter
        top_n: Number of top results to return (default: 3)
        
    Returns:
        List of top N matching tariffs, sorted by price
    """
    # Load all tariffs
    tariffs = load_tariffs()
    
    # Calculate age from birth date
    age = calculate_age_from_birthdate(birth_date)
    
    # Apply filters
    tariffs = filter_by_age(tariffs, age)
    tariffs = filter_by_coverage(tariffs, coverage_amount)
    tariffs = filter_by_optional_params(
        tariffs,
        health_declaration_required=health_declaration_required,
        waiting_period_months=waiting_period_months,
        contribution_free_from_age=contribution_free_from_age,
        surplus_regulation=surplus_regulation,
        payment_method=payment_method
    )
    
    # Rank by price and return top N
    return rank_tariffs(tariffs, top_n=top_n)

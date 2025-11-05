"""
Tariff Search Engine
Handles filtering, ranking, and searching of insurance tariffs
"""
import json
import os
import re
from datetime import datetime, date
from typing import List, Dict, Any, Optional


# Valid insurance sums (Versicherungssummen) in EUR
VALID_COVERAGE_AMOUNTS = [
    1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000,
    12500, 15000, 20000
]

# German month names mapping
GERMAN_MONTHS = {
    'januar': '01', 'februar': '02', 'märz': '03', 'april': '04',
    'mai': '05', 'juni': '06', 'juli': '07', 'august': '08',
    'september': '09', 'oktober': '10', 'november': '11', 'dezember': '12'
}


def needs_rounding(coverage_amount: int) -> bool:
    """
    Check if a coverage amount needs to be rounded to a valid value
    
    Args:
        coverage_amount: Coverage amount in EUR
        
    Returns:
        True if rounding is needed, False if it's already a valid amount
    """
    return coverage_amount not in VALID_COVERAGE_AMOUNTS


def round_coverage_amount(coverage_amount: int) -> int:
    """
    Round coverage amount to the next valid insurance sum
    
    Rules:
    - If amount is already valid, return as-is
    - If amount is below minimum (1000), round up to 1000
    - If amount is above maximum (20000), cap at 20000
    - Otherwise, round UP to the next available valid amount
    
    Args:
        coverage_amount: Desired coverage amount in EUR
        
    Returns:
        Rounded coverage amount (one of VALID_COVERAGE_AMOUNTS)
    """
    # If already valid, return as-is
    if coverage_amount in VALID_COVERAGE_AMOUNTS:
        return coverage_amount
    
    # Cap at maximum
    if coverage_amount > VALID_COVERAGE_AMOUNTS[-1]:
        return VALID_COVERAGE_AMOUNTS[-1]
    
    # Round up to next valid amount
    for valid_amount in VALID_COVERAGE_AMOUNTS:
        if valid_amount >= coverage_amount:
            return valid_amount
    
    # Fallback (should never reach here)
    return VALID_COVERAGE_AMOUNTS[-1]


def parse_german_date(date_str: str) -> str:
    """
    Parse German date formats and convert to ISO format (YYYY-MM-DD)
    
    Supported formats:
    - DD.MM.YYYY (e.g., "15.05.1980")
    - DD. Month YYYY (e.g., "05. Mai 1969", "15. Januar 1980")
    - YYYY-MM-DD (ISO format as fallback)
    
    Args:
        date_str: Date string in German format
        
    Returns:
        Date in ISO format (YYYY-MM-DD)
        
    Raises:
        ValueError: If date format is invalid or date doesn't exist
    """
    date_str = date_str.strip()
    
    # Try DD.MM.YYYY format
    if re.match(r'^\d{1,2}\.\d{1,2}\.\d{4}$', date_str):
        try:
            parsed = datetime.strptime(date_str, '%d.%m.%Y')
            return parsed.strftime('%Y-%m-%d')
        except ValueError as e:
            raise ValueError(f"Ungültiges Datum: {date_str}")
    
    # Try DD. Month YYYY format (e.g., "05. Mai 1969")
    match = re.match(r'^(\d{1,2})\.\s*(\w+)\s+(\d{4})$', date_str, re.IGNORECASE)
    if match:
        day, month_name, year = match.groups()
        month_name_lower = month_name.lower()
        
        if month_name_lower not in GERMAN_MONTHS:
            raise ValueError(f"Unbekannter Monat: {month_name}")
        
        month = GERMAN_MONTHS[month_name_lower]
        iso_date = f"{year}-{month}-{day.zfill(2)}"
        
        # Validate the date actually exists
        try:
            datetime.strptime(iso_date, '%Y-%m-%d')
            return iso_date
        except ValueError:
            raise ValueError(f"Ungültiges Datum: {date_str}")
    
    # Try ISO format as fallback (YYYY-MM-DD)
    if re.match(r'^\d{4}-\d{1,2}-\d{1,2}$', date_str):
        try:
            parsed = datetime.strptime(date_str, '%Y-%m-%d')
            return parsed.strftime('%Y-%m-%d')
        except ValueError:
            raise ValueError(f"Ungültiges Datum: {date_str}")
    
    raise ValueError(f"Datumsformat nicht erkannt: {date_str}. Bitte verwende DD.MM.YYYY oder DD. Monat YYYY")


def is_future_date(date_str: str) -> bool:
    """
    Check if a date (in ISO format YYYY-MM-DD) is in the future
    
    Args:
        date_str: Date string in ISO format (YYYY-MM-DD)
        
    Returns:
        True if date is in the future, False otherwise
    """
    try:
        birth_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        return birth_date > date.today()
    except ValueError:
        return False


def validate_birth_date(date_str: str) -> Dict[str, Any]:
    """
    Validate birth date (German format) and check if it's not in the future
    
    Args:
        date_str: Date string in German format
        
    Returns:
        Dictionary with validation result:
        - valid: bool - Whether the date is valid
        - iso_date: str - Date in ISO format (if valid)
        - error: str - Error message (if invalid)
    """
    try:
        # Parse German date to ISO format
        iso_date = parse_german_date(date_str)
        
        # Check if date is in the future
        if is_future_date(iso_date):
            return {
                'valid': False,
                'error': 'Das Geburtsdatum liegt in der Zukunft. Bitte gib ein gültiges Geburtsdatum ein.'
            }
        
        # Date is valid
        return {
            'valid': True,
            'iso_date': iso_date
        }
        
    except ValueError as e:
        return {
            'valid': False,
            'error': str(e)
        }


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

import pytest

from pathlib import Path

from unittest.mock import Mock, patch

from lunch_line.menu_parser import (
    extract_meal_data_from_tables,
    calculate_week_dates,
    map_meal_keys_to_dates,
    run
)


def test_extract_meal_data_empty_table():
    """Test handling of empty tables."""
    mock_page = Mock()
    mock_page.extract_tables.return_value = []
    
    result = extract_meal_data_from_tables(mock_page)
    assert result == {}


def test_calculate_week_dates():
    """Test date range extraction from text."""
    text = """WEEKLY MENU
    28 July 2025 - 01 August 2025
    Some other text"""
    
    start_date, end_date = calculate_week_dates(text)
    
    assert start_date.year == 2025
    assert start_date.month == 7
    assert start_date.day == 28
    assert end_date.year == 2025
    assert end_date.month == 8
    assert end_date.day == 1


@pytest.mark.parametrize("test_header", [
    """WEEKLY MENU
    July 28, 2025 - August 1, 2025
    Some other text""",
    """WEEKLY MENU
    07-28-2025 - 08-01-2025""",
    """WEEKLY MENU
    2025-07-28 - 2025-08-01""",
])
def test_calculate_week_dates_invalid_format(test_header):
    """Test handling of invalid date format."""
    assert calculate_week_dates(test_header) is None


def test_map_meal_keys_to_dates():
    """Test remapping of day keys to ISO dates."""
    from datetime import date
    
    meal_data = {
        'Mon (28)': {'BREAKFAST': 'Eggs & Toast', 'LUNCH': 'Pizza'},
        'Tue (29)': {'BREAKFAST': 'Cereal', 'LUNCH': 'Pasta'}
    }
    start_date = date(2025, 7, 28)
    end_date = date(2025, 8, 1)
    
    result = map_meal_keys_to_dates(meal_data, start_date, end_date)
    
    assert result == {
        '2025-07-28': {'BREAKFAST': 'Eggs & Toast', 'LUNCH': 'Pizza'},
        '2025-07-29': {'BREAKFAST': 'Cereal', 'LUNCH': 'Pasta'}
    }


def test_run_with_real_pdf():
    """Test the main run function with a real sample PDF from tests/data."""
    pdf_path = Path(__file__).parent / "data" / "test_menu.pdf"

    result = run(str(pdf_path))

    assert result == {
        '2024-05-28': {
            'BREAKFAST': 'multigrain Cereal, Apple Slices, Milk', 
            'LUNCH': 'DB cheese pizza, Cucumbers, Peaches, Milk', 
            'PM SNACK': 'Cheese Its, Milk',
            }, 
        '2024-05-29': {
            'BREAKFAST': 'English Muffin W/ Butter And Jelly, Oranges, Milk', 
            'LUNCH': 'beef taco, sweet peppers, pineapple, Milk',
            'PM SNACK': 'Graham Crackers, Milk',
            }, 
        '2024-05-30': {
            'BREAKFAST': 'Bagel With Cream Cheese, Grapes, Milk', 
            'LUNCH': 'Corn Dogs, Green Beans, Tator Tots, Pears, Milk', 
            'PM SNACK': 'Pretzels, Milk',
            }, 
        '2024-05-31': {
            'BREAKFAST': 'multigrain Cereal, Mixed Fruit, Milk', 
            'LUNCH': 'chicken sandwich, Corn, French Fries, Tropical Fruit, Milk', 
            'PM SNACK': 'Cheese Stick, Crackers, Water'
            }
        }

def test_run_with_invalid_pdf():
    """Test handling of invalid PDF files."""
    with patch('pdfplumber.open', side_effect=Exception("Invalid PDF")):
        result = run("invalid.pdf")
    
    assert result is None


def test_run_file_not_found():
    """Test handling of non-existent files."""
    with patch('pdfplumber.open', side_effect=FileNotFoundError):
        result = run("nonexistent.pdf")
    
    assert result is None

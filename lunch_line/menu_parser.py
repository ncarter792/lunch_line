import logging
import re
import sys

from collections import defaultdict
from datetime import date, timedelta

import pdfplumber


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_meal_data_from_tables(page):
    """Parse a menu table where the first row contains day headers and
    each body cell contains its own section headers (Breakfast, Lunch, PM Snack).

    """
    try:
        tables = page.extract_tables()
    except Exception as e:
        logger.error(f"Extracting menu table failed: {e}")
        return {}

    if not tables:
        logger.error("Menu is empty.")
        return {}

    menu_table = tables[0]
    meals = ['BREAKFAST', 'LUNCH', 'PM SNACK']

    headers = menu_table[0]
    table_data = [dict(zip(headers, row)) for row in menu_table[1:]]

    parsed_meals = defaultdict(dict)

    section_pattern = re.compile(r'(BREAKFAST|LUNCH|PM\s*SNACK)\s*:?', re.IGNORECASE)
    for i in table_data:
        for k, v in i.items():
            if section_pattern.match(v):
                meal_name = section_pattern.match(v)
                meal_content = v[meal_name.end():].strip().replace('\n', ' ')
                parsed_meals[k][meal_name.group(1)] = meal_content
            
    # Keep only days where at least one meal has content
    pruned = {
        d: v for d, v in parsed_meals.items()
        if any(v.get(k, '').strip() for k in meals)
    }
    
    return pruned


def calculate_week_dates(header_text):
    """Calculate the actual dates for the week"""
    # Extract date range from text like "28 July 2025 - 01 August 2025"
    date_pattern = r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})\s*-\s*(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})'
    match = re.search(date_pattern, header_text)
    
    if not match:
        logger.error(f"Extracting menu date range failed: {header_text}")
        return None

    else:
        start_day = int(match.group(1))
        start_month = match.group(2)
        start_year = int(match.group(3))
        end_day = int(match.group(4))
        end_month = match.group(5)
        end_year = int(match.group(6))
        
        # Convert month name to number
        months = {
            'January': 1, 'February': 2, 'March': 3, 'April': 4,
            'May': 5, 'June': 6, 'July': 7, 'August': 8,
            'September': 9, 'October': 10, 'November': 11, 'December': 12
        }
        start_date = date(start_year, months.get(start_month), start_day)
        end_date = date(end_year, months.get(end_month), end_day)
    
    return start_date, end_date


def map_meal_keys_to_dates(meal_data, start_date, end_date, date_format="%Y-%m-%d"):
    """Map keys like 'Tue (28)' to ISO dates within the given range by matching day-of-month.

    - meal_data: dict keyed by strings such as 'Tue (28)'.
    - start_date/end_date: datetime.date, inclusive range.
    - date_format: output key format, default '%Y-%m-%d'.

    Returns a new dict with updated keys where possible.
    """
    # Map day-of-month to date object for the range
    day_to_date = {
        (start_date + timedelta(days=i)).day: (start_date + timedelta(days=i))
        for i in range((end_date - start_date).days + 1)
    }

    day_num_re = re.compile(r"\((\d{1,2})\)")
    remapped = {}
    for day, meals in meal_data.items():
        m = day_num_re.search(day or "")
        if m:
            d = int(m.group(1))
            dt = day_to_date.get(d)
            new_key = dt.strftime(date_format) if dt else day
        else:
            new_key = day

        remapped[new_key] = meals

    return remapped

def run(infile):
    try:
        with pdfplumber.open(infile) as pdf:
            if not pdf.pages:
                logger.error("PDF has no pages")
                return None
            page = pdf.pages[0]

            start_date, end_date = calculate_week_dates(page.extract_text())
            meal_data = extract_meal_data_from_tables(page)
            meal_data = map_meal_keys_to_dates(meal_data, start_date, end_date)

    except Exception as e:
        logger.error(f"Failed to parse PDF: {str(e)}")
        return None

    return meal_data

if __name__ == '__main__': 
    infile = sys.argv[1]
    run(infile)
import logging
import sys

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from menu_parser import run


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CALENDAR_ID = ['secret'] # TODO - move to Secrets Manager

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def ensure_token(credentials_path="credentials.json", token_path="token.json"):
    creds = None
    try:
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    except Exception:
        pass

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())
    return creds

def setup_google_calendar(credentials_path="credentials.json", token_path="token.json"):
    """Initialize Google Calendar API client"""
    creds = ensure_token(credentials_path, token_path)
    return build("calendar", "v3", credentials=creds)


def create_calendar_events(calendar_service, meal_data, calendar_id=CALENDAR_ID):
    """Create Google Calendar events for meals"""
    if not calendar_service:
        logger.error("Google Calendar service not initialized")
        return False

    print(meal_data)

    try:
        for day, meals in meal_data.items():
            
            # Create breakfast event
            if meals['BREAKFAST']:
                breakfast_event = {
                    'summary': f"🍳 School Breakfast: {meals['BREAKFAST'][:50]}...",
                    'description': f"Breakfast Menu:\n{meals['BREAKFAST']}",
                    'start': {
                        'date': day,
                    },
                    'end': {
                        'date': day,
                    },
                    'colorId': '2',  # Green
                }
                
                calendar_service.events().insert(
                    calendarId=calendar_id, 
                    body=breakfast_event
                ).execute()
            
            # Create lunch event
            if meals['LUNCH']:
                lunch_event = {
                    'summary': f"🍽️ School Lunch: {meals['LUNCH'][:50]}...",
                    'description': f"Lunch Menu:\n{meals['LUNCH']}",
                    'start': {
                        'date': day,
                    },
                    'end': {
                        'date': day,
                    },
                    'colorId': '3',  # Purple
                }
                
                calendar_service.events().insert(
                    calendarId=calendar_id, 
                    body=lunch_event
                ).execute()
            
            # Create snack event
            if meals['PM SNACK']:
                snack_event = {
                    'summary': f"🥨 School Snack: {meals['PM SNACK'][:50]}...",
                    'description': f"PM Snack:\n{meals['PM SNACK']}",
                    'start': {
                        'date': day,
                    },
                    'end': {
                        'date': day,
                    },
                    'colorId': '4',  # Flamingo
                }
                
                calendar_service.events().insert(
                    calendarId=calendar_id, 
                    body=snack_event
                ).execute()
        
        logger.info("Successfully created calendar events.")
        return True
        
    except Exception as e:
        logger.error(f"Failed to create calendar events: {str(e)}")
        return False

if __name__ == '__main__': 
    meal_data = run(sys.argv[1])
    calendar_service = setup_google_calendar()
    create_calendar_events(calendar_service, meal_data)

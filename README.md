# Lunch Line

A Python tool that 1) watches for incoming emails containing school lunch menus, 2) parses school lunch menu PDFs and, 3) populates a shared Google Calendar that other parents can subscribe to. This provides an easy way for families to stay informed about daily breakfast, lunch, and snack plans through their personal calendar applications.

## Features
- Parse a weekly menu PDF and extract meals per day
- Map weekday headers like `Tue (28)` to real calendar dates (e.g., `2024-05-28`)
- Create all‑day Google Calendar events for Breakfast, Lunch, and PM Snack
- Share the calendar with other parents who can subscribe to stay updated
- Automatic updates when new menu PDFs are processed

Note: The source modules may evolve. This README outlines the setup and typical usage patterns for the project.

## Requirements
- Python 3.9+
- A Google Cloud project with the Google Calendar API enabled
- OAuth Client ID (Desktop) credentials

## Shared Calendar for Parents

One of the key benefits of this tool is the ability to populate a shared Google Calendar that multiple parents can subscribe to. Here's how it works:

1. **Single Source of Truth**: One parent or school administrator maintains the calendar
2. **Easy Subscription**: Other parents can subscribe to the calendar using the public URL
3. **Automatic Updates**: Any updates to the menu are automatically reflected in the calendar
4. **Platform Agnostic**: Works with any calendar application that supports Google Calendar (iPhone, Android, Outlook, etc.)

To share the calendar with other parents:
1. After running the script, go to Google Calendar
2. Find the calendar in "My calendars"
3. Click the three dots next to it and select "Settings and sharing"
4. Under "Access permissions," check "Make available to public"
5. Share the "Public URL to this calendar" with other parents

Parents can then subscribe to this calendar by:
1. Opening their calendar application
2. Selecting "Add calendar" → "From URL"
3. Pasting the public URL

## Setup
1. Create and activate a virtual environment
   - Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - macOS/Linux (bash):
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

2. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

3. Enable Google Calendar API and download credentials
   - In Google Cloud Console:
     - Create a project (or use an existing one).
     - APIs & Services → Enable APIs & Services → enable “Google Calendar API”.
     - OAuth consent screen → configure (External) and publish for testing/production as needed.
     - Credentials → Create Credentials → OAuth client ID → Application type: Desktop app.
     - Download the client file and save it as `credentials.json` at the project root.

4. Generate `token.json` (first‑time OAuth)
   - The first time you run a script that initializes the Calendar client, you will be prompted to authorize in your browser. That process writes `token.json` to the project root for future runs.
   - Keep both `credentials.json` and `token.json` private. Do not commit them.

## Usage

Depending on how you organize your source code, typical commands look like:

- Parse a menu PDF (example):
  ```bash
  python -m lunch_line.menu_parser path/to/menu.pdf
  ```
  This should print or return a dictionary shaped like:
  ```python
  {
    "2024-05-28": {"BREAKFAST": "...", "LUNCH": "...", "PM SNACK": "..."},
    "2024-05-29": {...},
    ...
  }
  ```

- Create calendar events (example):
  ```bash
  python -m lunch_line.populate_calendar path/to/menu.pdf
  ```
  Typical behavior:
  - The script will ensure OAuth via `credentials.json` → `token.json` flow.
  - It will insert all‑day events into your primary calendar (or a named calendar you choose) for each meal.

If you prefer to separate parsing and calendar population:
- First run the parser and save JSON.
- Then run a calendar script that reads that JSON and inserts events.

## Project structure
```
.
├─ lunch_line/
│  └─ __init__.py
├─ tests/
│  └─ __init__.py
├─ requirements.txt
├─ credentials.json        # not committed; provided by you
├─ token.json              # generated after first OAuth run; not committed
└─ README.md
```

Your source modules (e.g., `menu_parser.py`, `populate_calendar.py`) typically live inside `lunch_line/`.

## Configuration
- Calendar
  - If targeting a specific calendar by name, resolve its `calendarId` first by listing calendars via the API and matching by `summary`. Then call `events.insert(..., calendarId=<id>)`.
  - If using the primary calendar, pass `calendarId="primary"`.
- Dates
  - Use ISO date strings (`YYYY-MM-DD`) for all‑day events (`start.date` / `end.date`).

## Troubleshooting
- No module named 'google'
  - Install the correct packages:
    ```bash
    pip install --upgrade google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2
    ```
  - Do not install the package named `google` (it is not the client library).

- 404 Not Found when inserting events
  - You likely passed a calendar name (summary) instead of a `calendarId`. Look up the `calendarId` via `calendarList().list().execute()`.

- `file_cache is only supported with oauth2client<4.0.0`
  - This is a benign info log line from the discovery cache.

- Access/permission issues
  - Ensure your OAuth consent screen and scopes include `https://www.googleapis.com/auth/calendar` and the account you authorize has write access to the target calendar.

## Security
- Never commit `credentials.json` or `token.json`.
- Treat the refresh token as sensitive. Revoke in the Google Account security settings if compromised.

## Development
- Formatting/linting (optional): add tools like `black`, `ruff`, and `mypy`.
- Testing: add `pytest` tests under `tests/`.

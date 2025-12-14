# Lunch Line

A Python tool that
  1) watches for weekly incoming emails containing attachments with school lunch menus
  2) parses school lunch menu PDFs
  3) populates a shared Google Calendar that other parents can subscribe to. 

This provides an easy way for families to stay informed about daily breakfast, lunch, and snack plans through their personal calendar applications.

*Note: This app is currently a work-in-progress prototype. It is not fully wired (yet).*

## Features
- Parse a weekly menu PDF and extract meals per day
- Map weekday headers like `Tue (28)` to real calendar dates (e.g., `2024-05-28`)
- Create all‑day Google Calendar events for Breakfast, Lunch, and PM Snack
- Share the calendar with other parents who can subscribe to stay updated
- Automatic updates when new menu PDFs are processed

## Requirements
- Python 3.9+
- A Google Cloud project with the Google Calendar API enabled
- OAuth Client ID (Desktop) credentials

## Shared Calendar for Parents

One of the key benefits of this tool is the ability to populate a shared Google Calendar that multiple parents can subscribe to:

1. **Easy Subscription**: Other parents can subscribe to the calendar by scanning a QR code
2. **Automatic Updates**: Any updates to the menu are automatically reflected in the calendar
3. **Platform Agnostic**: Works with any calendar application that supports Google Calendar (iPhone, Android, Outlook, etc.)

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
   uv install
   ```

## Deployment 
TODO.

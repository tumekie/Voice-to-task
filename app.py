import streamlit as st
from transcriber import record_and_transcribe
import dateparser
from datetime import datetime, timedelta
from dateparser.search import search_dates
import os.path
import pytz
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('googleCredentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('calendar', 'v3', credentials=creds)

def create_event(summary, start_time):
    service = get_calendar_service()
    end_time = start_time + timedelta(hours=1)

    event = {
        'summary': summary,
        'start': {'dateTime': start_time.isoformat(), 'timeZone': str(LOCAL_TZ)},
        'end': {'dateTime': end_time.isoformat(), 'timeZone': str(LOCAL_TZ)},
    }

    created_event = service.events().insert(calendarId='primary', body=event).execute()
    return created_event.get('htmlLink')

LOCAL_TZ = pytz.timezone('America/Chicago')  # Replace with your timezone!

def parse_task(text):
    results = search_dates(text, settings={'PREFER_DATES_FROM': 'future'})
    if results:
        matched_text, dt = results[0]  # Take the first datetime found
        if dt.tzinfo is None:
            dt = LOCAL_TZ.localize(dt)

        # Remove matched datetime text from the task title
        cleaned_text = text.replace(matched_text, "").strip(" ,.-")
        if not cleaned_text:
            cleaned_text = "New Task"  # Fallback title
        return cleaned_text, dt
    else:
        return text, None

st.title("🎤 Voice to Google Calendar Task")

if st.button("Record Task (10 sec)"):
    transcription = record_and_transcribe()
    st.markdown(f"**You said:** {transcription}")

    task_title, task_date = parse_task(transcription)
    if task_date:
        event_link = create_event(task_title, task_date)
        st.success(f"Task added: {task_title} at {task_date.strftime('%Y-%m-%d %H:%M')}")
        st.markdown(f"[Open event in Google Calendar]({event_link})")
    else:
        st.warning("Could not detect a date/time in your task. Please try again and include a time.")

from __future__ import print_function
import datetime
import os.path
import sys
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'private_key/gcal Py html Parser-7ddf822e4fdb.json'

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/")
def index():
    return render_template("index.html", eventlist=get_dates(10))

# Getting the list of maximum <max_number> events
def get_dates(max_number):
    # Credentials for Google Calendar API
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Building a API object
    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming', max_number, 'events')
    events_result = service.events().list(calendarId='8mkdbklaaet84afcnf0v4kvjcs@group.calendar.google.com', timeMin=now,
                                        maxResults=max_number, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        return
        
    eventlist = []

    for event in events:
        evnt = {}
        
        # .get() tries to get first argument value from dictionary, second argument is alternative!
        start = event['start'].get('dateTime', event['start'].get('date'))
        start_dttm = datetime.fromisoformat(start)
        evnt['start_date'] = start_dttm.date().strftime("%d.%m.%Y")
        evnt['start_time'] = start_dttm.time().strftime("%H:%M")
        evnt['title'] = event['summary']
        evnt['description'] = event['description']
        evnt['location'] = event['location']

        eventlist.append(evnt)

    for event in eventlist:
        print(event)

    return eventlist

get_dates(20)
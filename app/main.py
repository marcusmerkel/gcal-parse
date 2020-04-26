from __future__ import print_function
import datetime
import os.path
import pickle
from datetime import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from flask import Flask, flash, jsonify, redirect, render_template, request
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

TEST_CAL_ID = "8mkdbklaaet84afcnf0v4kvjcs@group.calendar.google.com"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    else:
        performer = {}
        performer["name"] = request.form.get("performerName")
        if performer["name"] != "":
            performer["familyName"] = performer["name"].split(" ")[-1]
            performer["givenName"] = performer["name"].replace(" " + performer["familyName"], "")
        cal_id = request.form.get("calendarID")
        max_num = request.form.get("maxNumber")
        categories = request.form.get("categories").split(", ")
        return render_template("calendar.html", eventList=get_dates(cal_id, max_num, categories), performer=performer)
        

# Getting the list of maximum <max_number> events
def get_dates(calendar_id, max_number, categories):
    # Credentials for Google Calendar API
    creds = None

    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming', max_number, 'events')
    events_result = service.events().list(calendarId=calendar_id, timeMin=now, maxResults=max_number, singleEvents=True, orderBy='startTime').execute() # pylint: disable=maybe-no-member
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
        return
        
    eventList = []

    for event in events:
        evnt = {}
        
        # .get() tries to get first argument value from dictionary, second argument is alternative!
        start = event['start'].get('dateTime', event['start'].get('date'))
        start_dttm = datetime.fromisoformat(start)

        end = event['end'].get('dateTime', event['end'].get('date'))
        end_dttm = datetime.fromisoformat(end)

        evnt['start_dttm_iso'] = start
        evnt['start_date'] = start_dttm.date().strftime("%d.%m.%Y")
        evnt['start_day'] = start_dttm.date().strftime("%-d")
        evnt['start_month'] = start_dttm.date().strftime("%b")
        evnt['end_dttm_iso'] = end
        evnt['start_weekday'] = start_dttm.time().strftime("%A")
        if start_dttm.time().strftime("%H:%M") == "00:00" and end_dttm.time().strftime("%H:%M") == "00:00":
            evnt['start_time'] = "whole day"
            evnt['end_time'] = ""
        else:
            evnt['start_time'] = start_dttm.time().strftime("%H:%M")
            evnt['end_time'] = end_dttm.time().strftime("%H:%M")

        evnt['title'] = event['summary'].replace(": ", ":\n", 1)

        if 'description' in event.keys():
            desc = event['description']
            evnt['description'] = desc.replace("\n\n\n", "\n\n")
            for category in categories:
                if category in desc:
                    evnt['type'] = category
        else:
            evnt['description'] = event['summary']
            evnt['type'] = ""

        if not 'location' in event.keys():
            evnt['location'] = ""
        else:
            loc = event['location']
            evnt['location'] = loc
            if len(loc.split(", ", 1)) > 1:
                evnt['locationName'] = loc.split(", ", 1)[0]
                evnt['locationAddress'] = loc.split(", ", 1)[1]
            else:
                evnt['locationName'] = loc
                evnt['locationAddress'] = ""
            evnt['locationMapsSearch'] = "https://google.com/maps/search/" + evnt['locationName'].replace(" ", "+")

        eventList.append(evnt)

    return eventList
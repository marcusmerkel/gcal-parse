from __future__ import print_function
import datetime
import os.path
import sys
import locale
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.auth.transport.requests import Request

from flask import Flask, flash, jsonify, redirect, render_template, request
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = 'private_key/gcal Py html Parser-7ddf822e4fdb.json'

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Set Language to Local
locale.setlocale(locale.LC_ALL, '')

@app.route("/")
def index():
    performer = {}
    performer["name"] = "Marcus Merkel"
    performer["givenName"] = "Marcus"
    performer["familyName"] = "Merkel"
    return render_template("index.html", eventList=get_dates(20), performer=performer)

# Getting the list of maximum <max_number> events
def get_dates(max_number):
    # Credentials for Google Calendar API
    creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Building a API object
    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming', max_number, 'events')
    events_result = service.events().list(calendarId='8mkdbklaaet84afcnf0v4kvjcs@group.calendar.google.com', timeMin=now, maxResults=max_number, singleEvents=True, orderBy='startTime').execute() # pylint: disable=maybe-no-member
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

        starttime = event['start'].get('time')

        evnt['start_dttm_iso'] = start
        evnt['start_date'] = start_dttm.date().strftime("%d.%m.%Y")
        evnt['start_day'] = start_dttm.date().strftime("%-d")
        evnt['start_month'] = start_dttm.date().strftime("%b")
        evnt['end_dttm_iso'] = end
        evnt['start_weekday'] = start_dttm.time().strftime("%A")
        if not starttime:
            evnt['start_time'] = "00:00"
            evnt['end_time'] = "23:59"
        else:
            evnt['start_time'] = start_dttm.time().strftime("%H:%M")
            evnt['end_time'] = end_dttm.time().strftime("%H:%M")

        evnt['title'] = event['summary']

        if 'description' in event.keys():
            evnt['description'] = event['description'].replace("\n\n\n", "\n\n")
            desc = event['description']
            if "Operette" in desc:
                evnt['type'] = "Operette"
            elif "Musical" in desc:
                evnt['type'] = "Musical"
            elif "Konzert" in desc:
                evnt['type'] = "Konzert"
            elif "Kammer" in desc:
                evnt['type'] = "Kammermusik"
            elif "Lieder" in desc:
                evnt['type'] = "Lied"
            elif "Oper" in desc and not "Operette" in desc:
                evnt['type'] = "Oper"
        else:
            evnt['description'] = event['summary']
            evnt['type'] = ""

        evnt['opus'] = ""
        for word in event['summary'].split(" "):
            if word.isupper():
                evnt['opus'] = evnt['opus'] + word + " "

        if not 'location' in event.keys():
            evnt['location'] = ""
        else:
            loc = event['location']
            evnt['location'] = loc
            evnt['locationName'] = loc.split(", ", 1)[0]
            evnt['locationAddress'] = loc.split(", ", 1)[1]
            evnt['locationMapsSearch'] = "https://google.com/maps/search/" + evnt['locationName'].replace(" ", "+")

        eventList.append(evnt)

    for event in eventList:
        print(event['opus'])

    return eventList

if __name__ == '__main__':
    app.debug = True
    app.run(host = 'http://marcus-macbook-pro-16.local/', port = 8888)
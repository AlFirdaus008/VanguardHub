from flask import flash, Blueprint, render_template, redirect, request, session, url_for, make_response, jsonify
from google_auth_oauthlib.flow import Flow, InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import csv
import os
import base64
import pickle
from .activity import log_activity
from .profile import get_user_profile
from dotenv import load_dotenv

scheduling_bp = Blueprint('scheduling', __name__)

# Specify the path to the .env file
env_path = os.path.join(os.getcwd(), 'VanguardHub', 'webb','config', '.env')
load_dotenv(dotenv_path=env_path)


CLIENT_SECRETS_FILE = os.getenv('CLIENT_SECRETS_FILE')
API_NAME = 'calendar'
API_VERSION = 'v3'
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/userinfo.email',
    'openid',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/userinfo.profile'
]

file_path_users = os.path.join(os.getcwd(), 'VanguardHub', 'webb', 'static', 'data', 'users.csv')

token_path = os.path.join(os.getcwd(), 'VanguardHub', 'webb','config', 'token.pickle')

def generate_nonce():
    return base64.b64encode(os.urandom(16)).decode('utf-8')

# Check if the user's credentials are stored in a pickle file
def get_credentials():
    credentials = None
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            credentials = pickle.load(token)
            print("Credentials loaded.")

    if credentials:
        # Check if the credentials are expired
        if credentials.expired:
            print("Credentials are expired.")
            if credentials.refresh_token:
                print("Refreshing credentials...")
                credentials.refresh(Request())
                print("Credentials refreshed.")
            else:
                print("No refresh token available. Credentials cannot be refreshed.")
                credentials = None  # Invalidate credentials if they cannot be refreshed
        else:
            print("Credentials are valid and not expired.")

    # If credentials are None (either not found or invalid), we won't save them here
    if credentials:
        # Save the credentials to a file
        with open(token_path, 'wb') as token:
            pickle.dump(credentials, token)
            print("Token saved successfully.")
    else:
        print("No valid credentials to save.")

    return credentials

# Route to authorize user with Google
@scheduling_bp.route('/authorize')
def authorize():
    session.clear()
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES, redirect_uri = url_for('scheduling.oauth2callback', _external=True))
    authorization_url, state = flow.authorization_url(
        access_type='offline',  # Requesting offline access
        include_granted_scopes='true',
        prompt='consent'  # Forces user consent
    )
    print(f"Redirecting to: {authorization_url}")
    session['state'] = state
    return redirect(authorization_url)

# OAuth2 callback
@scheduling_bp.route('/oauth2callback')
def oauth2callback():
    print('on it')
    flow = Flow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES, state=session['state'])
    flow.redirect_uri = url_for('scheduling.oauth2callback', _external=True)
    authorization_response = request.url
    print(f"Authorization Response: {authorization_response}")

    # Attempt to fetch the token
    try:
        flow.fetch_token(authorization_response=authorization_response)
        credentials = flow.credentials
        print("Full credentials response:", credentials)

        # Check if a refresh token was received
        if credentials.refresh_token:
            print("Refresh token received.")
        else:
            print("No refresh token received.")
        
        # Save the credentials to a file
        with open(token_path, 'wb') as token:
            pickle.dump(credentials, token)
        print("Token saved successfully.")

        return redirect(url_for('scheduling.create_calendar'))
        
    except Exception as e:
        print(f"Error fetching token: {str(e)}")
        flash("Failed to fetch token. Please try again.", 'danger')
        return redirect(url_for('scheduling.authorize'))

# Show user's calendar events
@scheduling_bp.route('/scheduling', methods=['GET', 'POST'])
def scheduling():
    numid = session['numid']
    if 'numid' not in session:
        print("No numid in session, redirecting...")
        return redirect(url_for('login.login'))  # If no username in session, redirect to login
    
    credentials = get_credentials()

    if not credentials or credentials.expired:
        return redirect(url_for('scheduling.authorize'))

    service = build(API_NAME, API_VERSION, credentials=credentials)

    # Use the new calendarId from session, or fallback to a default value
    # Get the calendar ID from session (this should be set when a new calendar is created)
    calendar_id = get_calendar_id_from_csv(file_path_users, numid)



    # Fetch events from the specified calendar
    events = service.events().list(
        calendarId=calendar_id,
        timeMin='2024-01-01T00:00:00Z',
        maxResults=20,
        singleEvents=True,
        orderBy='startTime'
    ).execute().get('items', [])

    # Check if the user can edit the calendar (based on role)
    can_edit_shared = session.get('user_role') != 'member'
     

    # Render the calendar template
    return render_template(
        'calendar.html',
        shared_events=events,  # Using the new calendar's events
        can_edit_shared=can_edit_shared,  # Check if user can edit
    )


def load_users_from_csv(file_path):
    users = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file, delimiter=';')
        for row in csv_reader:
            users.append({
                'numid': row['numid'],
                'email': row['email'],
                'role': row['role'],
                'password': row['password']  # Assuming you're using this for auth
            })
    return users

# Load users at startup or when necessary
users = load_users_from_csv(file_path_users)

# Function to get the role of a user by email
def get_user_role(email):
    for user in users:
        if user['email'] == email:
            return user['role']
    return None  # Return None if user not found

def is_member():
    return session.get('user_role') == 'member'

# Check if user can edit shared calendar
def can_edit_shared_calendar():
    return session.get('user_role') != 'member'

@scheduling_bp.route('/scheduling/create_calendar')
def create_calendar():
    numid = session['numid']
    credentials = get_credentials()

    if not credentials or credentials.expired:
        return redirect(url_for('scheduling.authorize'))
     

    service = build(API_NAME, API_VERSION, credentials=credentials)

    # Create a new calendar
    calendar = service.calendars().insert(
        body={
            'summary': 'Vanguard',  # Name of the new calendar
            'timeZone': 'Etc/GMT+7',
        }
    ).execute()

    new_calendar_id = calendar['id']  # Get the calendarId of the new calendar
    print(f"New calendar created: {calendar['summary']} with calendarId: {new_calendar_id}")
    save_calendar_id_to_csv(file_path_users, numid, new_calendar_id)
    # Store the calendarId in session so that /calendar can access it
    session['new_calendar_id'] = new_calendar_id

    # Redirect to /calendar to display events for the new calendar
    return redirect(url_for('scheduling.scheduling'))

# Initialize the Calendar API
def get_google_calendar_service():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', ['https://www.googleapis.com/auth/calendar'])
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    # Build the service
    service = build('calendar', 'v3', credentials=creds)
    return service



@scheduling_bp.route('/scheduling/get-events')
def get_events():
    numid = session['numid']
    # Print statement to indicate the route is hit
    print("Fetching events from Google Calendar...")

    # Load the credentials from pickle file
    credentials = None
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            credentials = pickle.load(token)

    # If no credentials found, return an error
    if not credentials or credentials.expired:
        print("User is not authenticated or credentials are expired.")
        return jsonify([]), 401

    # Refresh credentials if expired
    if credentials.expired and credentials.refresh_token:
        print("Refreshing credentials...")
        credentials.refresh(Request())

    # Build the Google Calendar service using the credentials
    service = build('calendar', 'v3', credentials=credentials)


    # Fetch the user's calendar events
    try:
        # Get the calendar ID from the session
        calendar_id = get_calendar_id_from_csv(file_path_users, numid)

        # If no calendar ID is found, return an error
        if not calendar_id:
            print("No calendar ID found in session.")
            return jsonify({'error': 'No calendar ID found'}), 400

        # Build the Google Calendar service
        service = build('calendar', 'v3', credentials=credentials)

        # Fetch events from the specified calendar
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin='2024-01-01T00:00:00Z',
            maxResults=20,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        print(f"Found {len(events)} events in the calendar.")

        # Convert Google Calendar events to FullCalendar format
        fullcalendar_events = []
        for event in events:
            fullcalendar_events.append({
                'id': event['id'],
                'title': event.get('summary', 'No Title'),
                'start': event['start'].get('dateTime', event['start'].get('date')),
                'end': event['end'].get('dateTime', event['end'].get('date'))
            })

        print(f"Returning {len(fullcalendar_events)} events to the frontend.")
        return jsonify(fullcalendar_events)

    except Exception as e:
        print(f"Error fetching events: {e}")
        return jsonify([]), 500



@scheduling_bp.route('/scheduling/add-event', methods=['POST'])
def add_event():
    numid = session['numid']
    # Load credentials from pickle file
    credentials = None
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            credentials = pickle.load (token)

    # If no credentials found or credentials are expired, return an error
    if not credentials or credentials.expired:
        print("User not authenticated or credentials expired.")
        return jsonify({'error': 'User not authenticated'}), 401

    # Refresh credentials if expired
    if credentials.expired and credentials.refresh_token:
        print("Refreshing credentials...")
        credentials.refresh(Request())
    
    new_calendar_id = get_calendar_id_from_csv(file_path_users, numid)  # Retrieve the calendarId from session
    if new_calendar_id:
        print(f"Using Calendar ID: {new_calendar_id}")
    else:
        print("Calendar ID not found.")

    try:
        # Print to check if the request is hitting the route
        print("Add event request received.")

        # Get event data from the request
        event_data = request.json
        print(f"Received event data: {event_data}")

        # Extract event details from the frontend
        title = event_data.get('title')
        start = event_data.get('start')
        end = event_data.get('end')

        # Ensure all necessary fields are present
        if not title or not start or not end:
            print("Missing title, start, or end time in event data.")
            return jsonify({'error': 'Missing event details'}), 400

        # Print event details before making API call
        print(f"Adding event: Title={title}, Start={start}, End={end}")

        # Build the Google Calendar service using the loaded credentials
        service = build('calendar', 'v3', credentials=credentials)

        # Prepare the event for Google Calendar
        event = {
            'summary': title,
            'start': {
                'dateTime': start,
                'timeZone': 'Etc/GMT+7',  # Adjust timeZone as needed
            },
            'end': {
                'dateTime': end,
                'timeZone': 'Etc/GMT+7',  # Adjust timeZone as needed
            }
        }

        # Insert the event into the user's Google Calendar
        calendar_event = service.events().insert(calendarId=new_calendar_id, body=event).execute()
        print(f"Event successfully added: {calendar_event}")

        numid = session['numid'] 
        user_data = get_user_profile(numid)
        nickname = user_data.get('Nickname') 
        log_activity(numid, nickname, 'Event Change', 'has added a new event')

        # Return the event data to the frontend
        return jsonify({
            'id': calendar_event['id'],
            'title': calendar_event.get('summary', ''),
            'start': calendar_event['start'].get('dateTime', calendar_event['start'].get('date')),
            'end': calendar_event['end'].get('dateTime', calendar_event['end'].get('date'))
        })

    except Exception as e:
        print(f"Error adding event: {e}")
        return jsonify({'error': 'Failed to create event'}), 500

@scheduling_bp.route('/scheduling/update-event', methods=['POST'])
def update_event():
    numid = session['numid']
    credentials = get_credentials()

    if not credentials or credentials.expired:
        return jsonify({'error': 'User not authenticated'}), 401

    try:
        # Load the event details from the request
        event_data = request.json
        event_id = event_data.get('id')
        title = event_data.get('title')
        start = event_data.get('start')
        end = event_data.get('end')

        if not event_id or not title or not start or not end:
            return jsonify({'error': 'Missing event details'}), 400

        # Build the Google Calendar service
        service = build('calendar', 'v3', credentials=credentials)

        new_calendar_id = get_calendar_id_from_csv(file_path_users, numid)
        if not new_calendar_id:
            return jsonify({'error': 'Calendar ID not found'}), 400

        # Prepare the updated event data
        event = {
            'summary': title,
            'start': {
                'dateTime': start,
                'timeZone': 'Etc/GMT+7',
            },
            'end': {
                'dateTime': end,
                'timeZone': 'Etc/GMT+7',
            }
        }

        # Update the event in Google Calendar
        updated_event = service.events().update(
            calendarId=new_calendar_id,
            eventId=event_id,
            body=event
        ).execute()

        numid = session['numid'] 
        user_data = get_user_profile(numid)
        nickname = user_data.get('Nickname') 
        log_activity(numid, nickname, 'Event Change', 'has updated an event')
        # Return the updated event details
        return jsonify({
            'id': updated_event['id'],
            'title': updated_event.get('summary', ''),
            'start': updated_event['start'].get('dateTime', updated_event['start'].get('date')),
            'end': updated_event['end'].get('dateTime', updated_event['end'].get('date'))
        })

    except Exception as e:
        print(f"Error updating event: {e}")
        return jsonify({'error': 'Failed to update event'}), 500

@scheduling_bp.route('/scheduling/delete-event', methods=['POST'])
def delete_event():
    # Load credentials from pickle file
    numid = session['numid']
    credentials = None
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            credentials = pickle.load(token)

    if not credentials or credentials.expired:
        return jsonify({'error': 'User not authenticated'}), 401

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

    try:
        # Retrieve the event ID from the frontend request
        event_data = request.json
        event_id = event_data.get('id')

        if not event_id:
            return jsonify({'error': 'Event ID is required'}), 400

        # Get the calendar ID from session
        calendar_id = get_calendar_id_from_csv(file_path_users, numid)
        if not calendar_id:
            return jsonify({'error': 'Calendar ID not found'}), 400

        # Build the Google Calendar service
        service = build('calendar', 'v3', credentials=credentials)

        # Call the Google Calendar API to delete the event
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        numid = session['numid'] 
        user_data = get_user_profile(numid)
        nickname = user_data.get('Nickname') 
        log_activity(numid, nickname, 'Event Change', 'has deleted an event')
        return jsonify({'success': True, 'message': 'Event deleted successfully'})

    except Exception as e:
        print(f"Error deleting event: {e}")
        return jsonify({'error': 'Failed to delete event'}), 500

def save_calendar_id_to_csv(file_path, numid, calendar_id):
    updated_users = []
    
    # Read the CSV and update the calendar ID for the matching user
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file, delimiter=';')
        for row in csv_reader:
            if row['numid'] == numid:
                row['calendar_id'] = calendar_id  # Add or update calendar_id for the user
            updated_users.append(row)
    
    # Write the updated rows back to the CSV file
    with open(file_path, mode='w', newline='') as file:
        fieldnames = updated_users[0].keys()  # Get the field names from the existing file
        csv_writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
        
        csv_writer.writeheader()  # Write the header
        csv_writer.writerows(updated_users)  # Write the updated data

    print(f"Calendar ID {calendar_id} saved successfully for user {numid}.")

def get_calendar_id_from_csv(file_path, numid):
    with open(file_path, mode='r') as file:
        csv_reader = csv.DictReader(file, delimiter=';')
        for row in csv_reader:
            if row['numid'] == numid:
                return row.get('calendar_id')  # Return the calendar_id if found
    return None  # Return None if no matching user or no calendar_id is found

from flask import Blueprint, render_template, url_for, session
import csv
import os
from datetime import datetime, timedelta


activity_feed_bp = Blueprint('activity_feed', __name__)
file_path_activity = os.path.join(os.getcwd(), 'VanguardHub', 'webb', 'static', 'data', 'activity.csv')
file_path_profile = os.path.join(os.getcwd(), 'VanguardHub', 'webb', 'static', 'data', 'profile.csv')

@activity_feed_bp.route('/activity_feed')
def activity():
    numid = session['numid']
    activities = []

    if os.path.exists(file_path_activity):
        with open(file_path_activity, 'r') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                row['Photo'] = f"uploads/{row['NIM']}_profile.jpg"
                # Parse the timestamp into a datetime object
                row['Timestamp'] = datetime.strptime(row['Timestamp'], '%Y-%m-%d %H:%M:%S')
                activities.append(row)

    # Get today's date, start of the current week, and start of the current month
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    start_of_week = today - timedelta(days=today.weekday())  # Monday as the start of the week
    start_of_month = today.replace(day=1)

    grouped_activities = {
        'Today': [],
        'Yesterday': [],
        'This Week': [],
        'This Month': [],
        'Older': []
    }

    for activity in activities:
        activity_date = activity['Timestamp'].date()

        if activity_date == today:
            grouped_activities['Today'].append(activity)
        elif activity_date == yesterday:
            grouped_activities['Yesterday'].append(activity)
        elif start_of_week <= activity_date < today:
            grouped_activities['This Week'].append(activity)
        elif start_of_month <= activity_date < start_of_week:
            grouped_activities['This Month'].append(activity)
        else:
            grouped_activities['Older'].append(activity)

    return render_template('activity_feed.html', grouped_activities=grouped_activities)


def log_activity(nim, username, activity_type, description):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file_exists = os.path.exists(file_path_activity)
    activity_url = get_activity_url(activity_type, nim)
    activty_badge = get_activity_badge(activity_type, nim)
    if not file_exists or os.stat(file_path_activity).st_size == 0:  # File is empty
            with open(file_path_activity, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow(['Timestamp', 'NIM', 'Username', 'Type', 'Description', 'URL', 'Badge'])  # Write header
    with open(file_path_activity, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow([timestamp, nim, username, activity_type, description, activity_url, activty_badge])  # Save numid and hashed password

def get_activity_url(activity_type, nim):
    # Define mappings between activity types and their corresponding URLs
    activity_url_map = {
        'Event Change': 'scheduling.scheduling',
        'Profile Change': 'profile.profile',     
    }
    
    # Return the URL if the activity_type is mapped, otherwise return None
    if activity_type in activity_url_map:
        if activity_type == 'Profile Change':
            return url_for(activity_url_map[activity_type], nim=nim)
        return url_for(activity_url_map[activity_type])
    return None

def get_activity_badge(activity_type, nim):
    # Define mappings between activity types and their corresponding URLs
    activity_url_map = {
        'Event Change': 'fa-solid fa-calendar-days',
        'Profile Change': 'fa-solid fa-pen',        
    }
    
    # Return the URL if the activity_type is mapped, otherwise return None
    if activity_type in activity_url_map:
        if activity_type == 'Profile Change':
            return activity_url_map[activity_type]
        return activity_url_map[activity_type]
    return None

    with open(file_path_profile, mode='r') as file:
        csv_reader = csv.reader(file, delimiter=';')
        for row in csv_reader:
            if row[2].strip().lower() == nim.strip().lower():  # Comparing username (first column)
                # Return the row as a dictionary-like object (mapping column names manually)
                user_data = {
                    'Photo': row[10].replace('\\', '/'),
                }

                return user_data
    # If no user found
    print("No user found with that username.")
    return None

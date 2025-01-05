from flask import Blueprint, request, render_template, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import csv
import re
import os

settings_bp = Blueprint('settings', __name__)

file_path_users = os.path.join(os.getcwd(), 'webb','data', 'users.csv')
file_path_profile = os.path.join(os.getcwd(), 'webb','data', 'profile.csv')

# Helper function to update email in CSV
import csv
import os

def update_email_in_csv(current_email, new_email):
    updated = False
    users = []
    profiles = []


    # Read users.csv with semicolon delimiter
    with open(file_path_users, 'r', newline='') as file:
        users = list(csv.DictReader(file, delimiter=';'))

    # Read profile.csv with semicolon delimiter
    with open(file_path_profile, 'r', newline='') as file:
        profiles = list(csv.DictReader(file, delimiter=';'))

    # Update the email in users.csv
    for user in users:
        if user['email'] == current_email:
            user['email'] = new_email
            updated = True

    # Update the email in profile.csv
    for profile in profiles:
        if profile['email'] == current_email:
            profile['email'] = new_email

    if updated:
        # Write the updated list back to users.csv
        with open(file_path_users, 'w', newline='') as file:
            fieldnames = ['email', 'password']  # Adjust to your file's columns
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            writer.writerows(users)

        # Write the updated list back to profile.csv
        with open(file_path_profile, 'w', newline='') as file:
            fieldnames = ['email', 'name', 'other_column']  # Adjust to your file's columns
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            writer.writerows(profiles)

    return updated


# Helper function to update password in CSV
def update_password_in_csv(email, new_password):
    updated = False
    with open(file_path_users, 'r') as file:
        users = list(csv.DictReader(file))
    
    # Update the password in CSV
    for user in users:
        if user['email'] == email:
            user['password'] = generate_password_hash(new_password)
            updated = True

    if updated:
        # Write the updated list back to the CSV
        with open(file_path_users, 'w', newline='') as file:
            fieldnames = ['email', 'password']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(users)
    return updated

# Change email route
@settings_bp.route('/change_email', methods=['POST'])
def change_email():
    current_email = request.form.get('current_email')
    new_email = request.form.get('new_email')
    
    # Simple email validation
    if not current_email or not new_email:
        flash('Both fields are required.', 'warning')
        return redirect(url_for('settings.settings_page'))

    # Update email in CSV
    if update_email_in_csv(current_email, new_email):
        flash('Email updated successfully!', 'success')
    else:
        flash('Error: Current email not found.', 'danger')

    return redirect(url_for('settings.settings_page'))

# Change password route
@settings_bp.route('/change_password', methods=['POST'])
def change_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')

    # Password validation rule
    if not new_password or not re.fullmatch(r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$', new_password):
        flash('Password must be at least 8 characters long, include at least one capital letter, one number, and one special character.', 'danger')
        return redirect(url_for('settings.settings_page'))

    if new_password != confirm_password:
        flash('Passwords do not match.', 'warning')
        return redirect(url_for('settings.settings_page'))

    # Check current password and update new password
    email = request.form.get('email')  # Assuming you track the current user's email somehow (session or passed in the form)
    
    with open(file_path_users, 'r') as file:
        users = list(csv.DictReader(file))
        user = next((u for u in users if u['email'] == email), None)

    if user and check_password_hash(user['password'], current_password):
        if update_password_in_csv(email, new_password):
            flash('Password updated successfully!', 'success')
        else:
            flash('Error updating password.', 'danger')
    else:
        flash('Current password is incorrect.', 'danger')

    return redirect(url_for('settings.settings_page'))

# Settings page route
@settings_bp.route('/settings')
def settings():
    return render_template('settings.html')

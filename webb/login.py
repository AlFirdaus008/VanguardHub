from flask import render_template, redirect, url_for, session, flash, request, Blueprint, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import csv
import os
import re
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from . import mail


login_bp = Blueprint('login', __name__)

file_path_roles = os.path.join(os.getcwd(),'data', 'roles.csv')
file_path_users = os.path.join(os.getcwd(),'data', 'users.csv')
file_path_profile = os.path.join(os.getcwd(),'data', 'profile.csv')

@login_bp.route('/')
def home():
    return render_template('firstpage.html')


@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'warning' in session:  
        flash(session['warning'], 'warning')
        session.pop('warning', None)
    
    user_info = session.get('user_info')
    if user_info:
        return redirect(url_for('login.dashboard'))

    if request.method == 'POST':
        form_action = request.form.get('form_action')
        numid = request.form.get('numid')
        password = request.form.get('password')
        
        if not numid or not password:
            flash('Please fill all the requirements.', 'warning')
            return redirect(url_for('login.login'))
        


        if form_action == 'signup':
            password = request.form.get('password')
            email = request.form.get('email')

            # if not re.fullmatch(r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$', password):
            #     flash('Password must be at least 8 characters long, include at least one capital letter, one number, and one special character.', 'danger')
            #     return redirect(request.url)
            
            if not email:
                flash('Please fill all the requirements.', 'warning')
                return redirect(url_for('login.login'))

            if check_if_user_exists(email):
                flash('Email already registered. Please log in.', 'warning')
            elif check_if_user_exists(numid):
                flash('numid already exists. Please choose a different numid.', 'warning')
            else:
                # Save the user info temporarily in the session
                session['pending_signup'] = {'numid': numid, 'email': email, 'password': password}
                
                # Send confirmation email
                send_confirmation_email(email)
                flash('A confirmation email has been sent to your email. Please confirm to complete signup.', 'info')
                return redirect(url_for('login.login'))

        elif form_action == 'login':
            user = check_user_password(numid, password)
            if user:
                session['numid'] = numid
                flash('Login successful!', 'success')
                return redirect(url_for('login.dashboard'))
            else:
                flash('Invalid numid or password. Please try again.', 'danger')

    return render_template('login.html')


# Function to send confirmation email with token
def send_confirmation_email(email):
    secret_key = current_app.config['SECRET_KEY']
    s = URLSafeTimedSerializer(secret_key)
    token = s.dumps(email, salt='email-confirm-salt')
    confirm_url = url_for('login.confirm_email', token=token, _external=True)

    msg = Message('Confirm Your Email', recipients=[email])
    msg.body = f'Please click the following link to confirm your email: {confirm_url}'
    
    try:
        mail.send(msg)
        print(f"Confirmation email sent to {email}")
    except Exception as e:
        print(f"Error sending confirmation email: {e}")

@login_bp.route('/confirm_email/<token>')
def confirm_email(token):
    secret_key = current_app.config['SECRET_KEY']
    s = URLSafeTimedSerializer(secret_key)
    
    try:
        email = s.loads(token, salt='email-confirm-salt', max_age=3600)  # Token expires in 1 hour
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('login.login'))

    pending_signup = session.get('pending_signup')
    if pending_signup and pending_signup['email'] == email:
        # Save the user to CSV with hashed password
        hashed_password = generate_password_hash(pending_signup['password'])
        role = assign_roles_based_on_numid(pending_signup['numid'])
        save_user_to_csv(pending_signup['numid'], email, role, hashed_password)

        session.pop('pending_signup', None)  # Clear pending signup after confirmation
        flash('Your email has been confirmed! You can now log in.', 'success')
        return redirect(url_for('login.login'))

    flash('Confirmation failed. Please try signing up again.', 'danger')
    return redirect(url_for('login.login'))



# dashboard page route
@login_bp.route('/dashboard')
def dashboard():
    if 'numid' not in session:
        return redirect(url_for('login.login'))  # Redirect to login if not authenticated
    return render_template('dashboard.html', user=session['numid'])


# Function to save user to CSV (signup)
def save_user_to_csv(numid, email, role, hashed_password):
    
    try:
        # Save user data to users.csv
        file_exists = os.path.exists(file_path_users)
        if not file_exists or os.stat(file_path_users).st_size == 0:  # File is empty
            with open(file_path_users, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow(['numid', 'email', 'role', 'hashed_password'])  # Write header
        with open(file_path_users, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow([numid, email, role, hashed_password])  # Save numid and hashed password
        
        # Now update the email in file_path_profile based on numid (which matches NIM)
        updated_profiles = []
        user_found = False

        with open(file_path_profile, mode='r', encoding='utf-8') as file:
            profiles = list(csv.DictReader(file, delimiter=";"))  # Read profiles as dictionaries
            for profile in profiles:
                if profile['NIM'] == numid:  # Find the profile where NIM matches numid
                    user_found = True
                    profile['Email'] = email  # Update the email in the profile
                updated_profiles.append(profile)

        if user_found:
            with open(file_path_profile, mode='w', newline='', encoding='utf-8') as file:
                fieldnames = updated_profiles[0].keys()
                writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=";")
                writer.writeheader()  # Write the header
                writer.writerows(updated_profiles)  # Write the updated profile data
        else:
            print(f"No profile found with NIM: {numid}")

    except Exception as e:
        print(f"Error saving to CSV: {e}")


def check_if_user_exists(value):
    try:
        with open(file_path_users, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            # Check if the value contains "@" to decide if it's an email or numid
            if "@" in value:
                # Checking by email (row[1] assumed to be the email field)
                for row in reader:
                    if row[1] == value:
                        return True
            else:
                # Checking by numid (row[0] assumed to be the numid field)
                for row in reader:
                    if row[0] == value:
                        return True
    except FileNotFoundError:
        return False


# Function to check user password (login)
def check_user_password(numid, password):
    try:
        with open(file_path_users, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter = ';')
            for row in reader:
                print(row)
                if row[0] == numid and check_password_hash(row[3], password):
                    return True
    except FileNotFoundError:
        return False

def assign_roles_based_on_numid(numid):
    try:
        # Read the Excel file
        df = pd.read_csv(file_path_roles, delimiter=';')

        df['id'] = df['id'].astype(str).str.strip().str.lower()
        numid = numid.strip().lower()
        # Check if the numid exists in the Excel file and return the corresponding roles
        role_row = df[df['id'] == numid]

        if not role_row.empty:
            # Get roles as a comma-separated string
            roles = role_row.iloc[0]['role'].split(',')  # Split by commas to get multiple roles
            return [role.strip() for role in roles]  # Return roles as a list of strings
        else:
            return ['guest']  # Default role for unrecognized numids
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return ['guest']

@login_bp.route('/logout')
def logout():
    # Remove all the data from the session to log out the user
    session.clear()
    
    # Optionally, display a logout success message
    flash('You have successfully logged out.', 'info')
    
    # Redirect the user to the login page or homepage
    return redirect(url_for('login.login'))  # Assuming 'login' is the name of your login route

@login_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    secret_key = current_app.config['SECRET_KEY']
    s = URLSafeTimedSerializer(secret_key)
    if request.method == 'POST':
        email = request.form['email']
        if check_if_user_exists(email):  # Assuming the check_if_user_exists function checks by email
            token = s.dumps(email, salt='password-reset-salt')
            reset_url = url_for('login.reset_password', token=token, _external=True)
            send_reset_email(email, reset_url)  # Function to send email
            return jsonify({'status': 'success', 'message': 'Password reset link has been sent to your email.'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Email does not exist in our records.'}), 400


def send_reset_email(email, reset_url):
    msg = Message('Password Reset Request', recipients=[email],)
    msg.body = f'Click the link to reset your password: {reset_url}'
    try:
        mail.send(msg)
        print(f"Password reset email sent to {email}")
    except Exception as e:
        print(f"Error sending email: {e}")

import re

@login_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    secret_key = current_app.config['SECRET_KEY']
    s = URLSafeTimedSerializer(secret_key)
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)  # Token expires in 1 hour
    except:
        flash('The password reset link is invalid or has expired.', 'danger')
        return redirect(url_for('login.login'))

    if request.method == 'POST':
        password = request.form['password']

        # Password validation rule
        if not re.fullmatch(r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$', password):
            flash('Password must be at least 8 characters long, include at least one capital letter, one number, and one special character.', 'danger')
            return redirect(request.url)

        hashed_password = generate_password_hash(password)
        update_password_in_csv(email, hashed_password)  # Update the password in the CSV
        flash('Your password has been updated!', 'success')
        return redirect(url_for('login.login'))

    return render_template('reset_password.html')

def update_password_in_csv(email, hashed_password):
    try:
        users = []
        with open(file_path_users, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                if row[1] == email:  # Assuming row[1] is the email field
                    row[3] = hashed_password  # Update the password
                users.append(row)

        # Rewrite the entire CSV with the updated password
        with open(file_path_users, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerows(users)
    except Exception as e:
        print(f"Error updating password: {e}")

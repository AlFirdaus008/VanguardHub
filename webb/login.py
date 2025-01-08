from flask import render_template, redirect, url_for, session, flash, request, Blueprint, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer
import pandas as pd
import csv
import os
import re
from . import mail

login_bp = Blueprint('login', __name__)

# File paths
file_path_roles = os.path.join(os.getcwd(), 'VanguardHub', 'webb', 'static', 'data', 'roles.csv')
file_path_users = os.path.join(os.getcwd(), 'VanguardHub', 'webb', 'static', 'data', 'users.csv')
file_path_profile = os.path.join(os.getcwd(), 'VanguardHub', 'webb', 'static', 'data', 'profile.csv')

# Caesar Cipher Implementation
def caesar_encrypt(password, shift=3):
    """
    Encrypt password using Caesar cipher with custom shift value
    """
    encrypted = ""
    for char in password:
        if char.isupper():
            encrypted += chr((ord(char) + shift - 65) % 26 + 65)
        elif char.islower():
            encrypted += chr((ord(char) + shift - 97) % 26 + 97)
        elif char.isdigit():
            encrypted += str((int(char) + shift) % 10)
        else:
            encrypted += char
    return encrypted

def caesar_decrypt(encrypted_password, shift=3):
    """
    Decrypt password using Caesar cipher
    """
    return caesar_encrypt(encrypted_password, -shift)

# Route Handlers
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
            email = request.form.get('email')
            
            if not email:
                flash('Please fill all the requirements.', 'warning')
                return redirect(url_for('login.login'))

            if check_if_user_exists(email):
                flash('Email already registered. Please log in.', 'warning')
            elif check_if_user_exists(numid):
                flash('numid already exists. Please choose a different numid.', 'warning')
            else:
                # Store signup data temporarily
                session['pending_signup'] = {
                    'numid': numid,
                    'email': email,
                    'password': password
                }
                send_confirmation_email(email)
                flash('A confirmation email has been sent. Please confirm to complete signup.', 'info')
                return redirect(url_for('login.login'))

        elif form_action == 'login':
            if check_user_password(numid, password):
                session['numid'] = numid
                flash('Login successful!', 'success')
                return redirect(url_for('login.dashboard'))
            else:
                flash('Invalid numid or password.', 'danger')

    return render_template('login.html')

@login_bp.route('/confirm_email/<token>')
def confirm_email(token):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    
    try:
        email = s.loads(token, salt='email-confirm-salt', max_age=3600)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('login.login'))

    pending_signup = session.get('pending_signup')
    if pending_signup and pending_signup['email'] == email:
        # Encrypt and hash password before saving
        encrypted_password = caesar_encrypt(pending_signup['password'])
        hashed_password = generate_password_hash(encrypted_password)
        role = assign_roles_based_on_numid(pending_signup['numid'])
        
        save_user_to_csv(pending_signup['numid'], email, role, hashed_password)
        session.pop('pending_signup', None)
        
        flash('Email confirmed! You can now log in.', 'success')
        return redirect(url_for('login.login'))

    flash('Confirmation failed. Please try signing up again.', 'danger')
    return redirect(url_for('login.login'))

@login_bp.route('/dashboard')
def dashboard():
    if 'numid' not in session:
        return redirect(url_for('login.login'))
    return render_template('dashboard.html', user=session['numid'])

@login_bp.route('/logout')
def logout():
    session.clear()
    flash('You have successfully logged out.', 'info')
    return redirect(url_for('login.login'))

@login_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    
    if request.method == 'POST':
        email = request.form['email']
        if check_if_user_exists(email):
            token = s.dumps(email, salt='password-reset-salt')
            reset_url = url_for('login.reset_password', token=token, _external=True)
            send_reset_email(email, reset_url)
            return jsonify({'status': 'success', 'message': 'Password reset link sent to your email.'}), 200
        return jsonify({'status': 'error', 'message': 'Email not found.'}), 400

@login_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=3600)
    except:
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('login.login'))

    if request.method == 'POST':
        password = request.form['password']
        if not re.fullmatch(r'^(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$', password):
            flash('Password must be at least 8 characters long with at least one capital letter, number, and special character.', 'danger')
            return redirect(request.url)

        encrypted_password = caesar_encrypt(password)
        hashed_password = generate_password_hash(encrypted_password)
        update_password_in_csv(email, hashed_password)
        
        flash('Password updated successfully!', 'success')
        return redirect(url_for('login.login'))

    return render_template('reset_password.html')

# Helper Functions
def send_confirmation_email(email):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = s.dumps(email, salt='email-confirm-salt')
    confirm_url = url_for('login.confirm_email', token=token, _external=True)
    
    msg = Message('Confirm Your Email', recipients=[email])
    msg.body = f'Please click the following link to confirm your email: {confirm_url}'
    
    try:
        mail.send(msg)
        print(f"Confirmation email sent to {email}")
    except Exception as e:
        print(f"Error sending confirmation email: {e}")

def send_reset_email(email, reset_url):
    msg = Message('Password Reset Request', recipients=[email])
    msg.body = f'Click the link to reset your password: {reset_url}'
    
    try:
        mail.send(msg)
        print(f"Reset email sent to {email}")
    except Exception as e:
        print(f"Error sending reset email: {e}")

def save_user_to_csv(numid, email, role, hashed_password):
    calendar_id = '744c55ae571b4d19f7c11745ace2e0715de978588e8b6ef0b8bfb083a9cf2e38@group.calendar.google.com'
    try:
        # Create users.csv if it doesn't exist
        if not os.path.exists(file_path_users) or os.stat(file_path_users).st_size == 0:
            with open(file_path_users, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow(['numid', 'email', 'role', 'hashed_password'])

        # Save user data
        with open(file_path_users, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=";")
            writer.writerow([numid, email, role, hashed_password, calendar_id])

        # Update profile if exists
        updated_profiles = []
        user_found = False
        
        with open(file_path_profile, mode='r', encoding='utf-8') as file:
            profiles = list(csv.DictReader(file, delimiter=";"))
            for profile in profiles:
                if profile['NIM'] == numid:
                    user_found = True
                    profile['Email'] = email
                updated_profiles.append(profile)

        if user_found:
            with open(file_path_profile, mode='w', newline='', encoding='utf-8') as file:
                fieldnames = updated_profiles[0].keys()
                writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=";")
                writer.writeheader()
                writer.writerows(updated_profiles)
                
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def check_if_user_exists(value):
    try:
        with open(file_path_users, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            next(reader)  # Skip header
            for row in reader:
                if "@" in value:  # Check email
                    if row[1] == value:
                        return True
                else:  # Check numid
                    if row[0] == value:
                        return True
        return False
    except FileNotFoundError:
        return False

def check_user_password(numid, password):
    try:
        with open(file_path_users, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            next(reader)  # Skip header
            encrypted_password = caesar_encrypt(password)
            for row in reader:
                if row[0] == numid and check_password_hash(row[3], encrypted_password):
                    return True
        return False
    except FileNotFoundError:
        return False

def update_password_in_csv(email, hashed_password):
    try:
        users = []
        with open(file_path_users, 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            users.append(next(reader))  # Save header
            for row in reader:
                if row[1] == email:
                    row[3] = hashed_password
                users.append(row)

        with open(file_path_users, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=';')
            writer.writerows(users)
    except Exception as e:
        print(f"Error updating password: {e}")

def assign_roles_based_on_numid(numid):
    try:
        df = pd.read_csv(file_path_roles, delimiter=';')
        df['id'] = df['id'].astype(str).str.strip().str.lower()
        numid = numid.strip().lower()
        
        role_row = df[df['id'] == numid]
        if not role_row.empty:
            roles = role_row.iloc[0]['role'].split(',')
            return [role.strip() for role in roles]
        return ['guest']
    except Exception as e:
        print(f"Error reading roles file: {e}")
        return ['guest']
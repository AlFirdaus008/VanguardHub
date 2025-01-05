from flask import Blueprint, render_template, redirect, request, session, url_for, flash, jsonify
from datetime import date
from dateutil.relativedelta import relativedelta
from PIL import Image
import io
import csv
import os
import base64
from datetime import datetime
from activity import log_activity


profile_bp = Blueprint('profile', __name__)

file_path_users = os.path.join(os.getcwd(),'data', 'users.csv')
file_path_profile = os.path.join(os.getcwd(),'data', 'profile.csv')

@profile_bp.route('/<nim>')
def profile(nim):
    if 'numid' not in session:
        return redirect(url_for('login.login'))  # If no username in session, redirect to login

    # Proceed to print session['username'] if 'username' is in session
    print("Session username:", session['numid'])
    user_data = get_user_profile(nim)
    age = age_count(user_data.get('DOB'))
    print("User data:", user_data, 'age:', age)  # Debugging the result from the CSV
    numid = session['numid']
    
    if user_data:
        user_data['Age'] = age
        return render_template('profile.html', user=user_data, numid = numid, age=age)
    else:
        flash('You may have been logged out, please relogin.', 'info')
        return redirect(url_for('login.login'))


def get_user_profile(nim):
    with open(file_path_profile, mode='r') as file:
        csv_reader = csv.reader(file, delimiter=';')
        for row in csv_reader:
            if row[2].strip().lower() == nim.strip().lower():  # Comparing username (first column)
                # Return the row as a dictionary-like object (mapping column names manually)
                user_data = {
                    'Name': row[0],
                    'DOB':  datetime.strptime(row[1], '%d/%m/%Y').strftime('%Y-%m-%d'),
                    'NIM': row[2], 
                    'pddikti': row[3],
                    'Instagram': row[4],
                    'Role': row[5],
                    'Whatsapp': row[6].lstrip("'"),
                    'Email': row[7],
                    'Nickname': row[8], 
                    'About': row[9], 
                    'Photo': f"uploads/{row[2]}_profile.jpg",
                    'Linkname': row[11],
                    'Links': row[12]
                }

                return user_data
    # If no user found
    print("No user found with that username.")
    return None


def age_count(dob_str):
    print(dob_str)
    if dob_str is None:
        print("DOB not found for the user.")
        return None

    try:
        dob = dob_str.split('-')
        dob = [int(i) for i in dob]
        print(dob)
        birth_date = date(dob[0], dob[1], dob[2])  # dob[2]: year, dob[1]: month, dob[0]: day
        age = relativedelta(date.today(), birth_date).years
        print(age)
        return age
    except ValueError:
        print("DOB format is incorrect. Expected format: DD/MM/YYYY.")
        return None


@profile_bp.route('/profile/change_profile', methods=['POST'])
def change_profile():
    if 'numid' not in session:
        return redirect(url_for('login.login'))  # Redirect if no user is logged in
    
    numid = session['numid']  # Use 'numid' from session as the unique identifier for the user
    
    # Get new values from the form
    nickname = request.form.get('nickname')
    dob = request.form.get('dob')
    whatsapp = request.form.get('whatsapp')
    about_me = request.form.get('about_me')
    cropped_image_data = request.form.get('cropped_image')  # This is the base64 string from the cropped image
    
    updated_profile = []  # To hold updated profile data
    user_found = False
    changes = []  # To track which fields were changed

    # Check if the cropped image is provided
    if cropped_image_data:
        app_root = os.path.dirname(os.path.abspath(__file__))
        upload_folder = os.path.join(app_root, 'static', 'uploads')
        
        # Ensure upload directory exists
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        
        # Decode and save the cropped image
        img_data = base64.b64decode(cropped_image_data.split(',')[1])  # Assuming the base64 string includes the "data:image/png;base64," prefix
        photo_filename = f"{numid}_profile.jpg"  # Use unique file name
        photo_filepath = os.path.join(upload_folder, photo_filename)
        
        with open(photo_filepath, 'wb') as f:
            f.write(img_data)
    
    # Read the current profile data
    with open(file_path_profile, 'r') as file:
        profiles = list(csv.DictReader(file, delimiter=';'))  # Read profile CSV
        
        for profile in profiles:
            if profile['NIM'] == numid:  # Match user by 'NIM' (or 'numid')
                user_found = True
                # Update profile fields if new data is provided
                if nickname and nickname != profile['Nickname']:
                    profile['Nickname'] = nickname
                    changes.append('nickname')
                
                if dob and datetime.strptime(dob, '%Y-%m-%d').strftime('%d/%m/%Y') != profile['DOB']:
                    profile['DOB'] = datetime.strptime(dob, '%Y-%m-%d').strftime('%d/%m/%Y')
                    changes.append('date of birth')
                
                if whatsapp and whatsapp != profile['Whatsapp']:
                    profile['Whatsapp'] = whatsapp
                    changes.append('phone number')
                
                if about_me and about_me != profile['About']:
                    profile['About'] = about_me
                    changes.append("bio")
                
                # Save the image path if cropped image exists
                if cropped_image_data:
                    profile['Photo'] = os.path.join('uploads', photo_filename)
                    changes.append('profile photo')

                updated_profile.append(profile)
            else:
                updated_profile.append(profile)  # Keep other profiles unchanged

    if not user_found:
        return "User profile not found", 404  # Return error if user is not found

    # Save the updated profile data back to the profile CSV
    with open(file_path_profile, 'w', newline='') as file:
        fieldnames = updated_profile[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(updated_profile)

    # Generate a log message based on what has changed
    if changes:
        change_description = ', '.join(changes[:-1])
        if len(changes) > 1:
            change_description += f", and {changes[-1]}"
        else:
            change_description = changes[0]
        log_activity(numid, nickname, 'Profile Change', 'has changed their {change_description}')
    else:
        log_activity(numid, nickname, 'Profile Change', 'updated their profile with no specific changes')

    return redirect(url_for('profile.profile', nim=numid))  # Redirect back to the profile page


@profile_bp.route('/profile/change_profile/change_photo', methods=['POST'])
def change_photo():
    if 'numid' not in session:
        return redirect(url_for('login.login'))  
    

    
    cropped_image_data = request.form.get('cropped_image')
    
    updated_profile = []  
    user_found = False 
    
    if cropped_image_data:
        # Decode the base64 image data
        image_data = cropped_image_data.split(',')[1] 
        image_bytes = io.BytesIO(base64.b64decode(image_data))
        
        # Open the image using PIL (Python Imaging Library)
        img = Image.open(image_bytes)

        # Define the path to save the cropped image
        app_root = os.path.dirname(os.path.abspath(__file__))
        upload_folder = os.path.join(app_root, 'static', 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        filename = f"profile_{numid}.png"
        file_path = os.path.join(upload_folder, filename)

        # Save the image to the disk
        img.save(file_path)

        # Read the current profile data from CSV
        with open(file_path_profile, 'r') as file:
            profiles = list(csv.DictReader(file, delimiter=';'))  
            
            for profile in profiles:
                if profile['NIM'] == numid:  
                    user_found = True
                    # Update the user's photo path
                    profile['Photo'] = os.path.join('uploads', filename)
                
                updated_profile.append(profile)  
        
        # If the user wasn't found, return an error
        if not user_found:
            return "User profile not found", 404

        # Save the updated profile data back to the profile CSV
        with open(file_path_profile, 'w', newline='') as file:
            fieldnames = updated_profile[0].keys()
            writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')

            writer.writeheader()
            writer.writerows(updated_profile)  

    numid = session['numid'] 
    user_data = get_user_profile(numid)
    nickname = user_data.get('Nickname') 
    log_activity(numid, nickname, 'Profile Change', 'has changed their profile photo')
    return redirect(url_for('profile.profile', nim=numid))  

@profile_bp.route('/profile/add_link', methods=['POST'])
def add_link():
    if 'numid' not in session:
        return redirect(url_for('login.login'))  

    numid = session['numid'] 
    user_data = get_user_profile(numid)
    nickname = user_data.get('Nickname') 

    new_link = request.form.get('additional-link')  
    new_link_name = request.form.get('name-link')  
    
    if not new_link:
        return "No link provided", 400  
    
    updated_profile = [] 
    user_found = False
    
    # Read the current profile data
    with open(file_path_profile, 'r') as file:
        profiles = list(csv.DictReader(file, delimiter=';'))  
        
        for profile in profiles:
            if profile['NIM'] == numid:  
                user_found = True
                # Add the new link to the profile
                if 'Links' in profile and profile['Links'].strip():
                    profile['Links'] += f';{new_link}'  
                else:
                    profile['Links'] = new_link  
                # Add the new link name
                if 'Linkname' in profile and profile['Linkname'].strip():
                    profile['Linkname'] += f';{new_link_name}'  
                else:
                    profile['Linkname'] = new_link_name  

                updated_profile.append(profile)
            else:
                updated_profile.append(profile)  
    
    if not user_found:
        return "User profile not found", 404 
    
    # Save the updated profile data back to the profile CSV
    with open(file_path_profile, 'w', newline='') as file:
        fieldnames = updated_profile[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(updated_profile)  

    log_activity(numid, nickname, 'Profile Change', 'has add a new link to their profile')
    return redirect(url_for('profile.profile', nim=numid))  



@profile_bp.route('/profile/delete_link', methods=['POST'])
def delete_link():
    print("Delete link request received!")
    
    # Check if user is logged in
    if 'numid' not in session:
        return redirect(url_for('login.login'))  
    
    numid = session['numid'] 
    user_data = get_user_profile(numid)
    nickname = user_data.get('Nickname') 
 
    data = request.get_json()  
    link_index = data.get('index')  
    
    if not link_index:
        print('No index provided')
        return jsonify({"success": False, "message": "No link index provided"}), 400  
    
    updated_profile = []  
    user_found = False
    
    # Read the current profile data
    with open(file_path_profile, 'r') as file:
        profiles = list(csv.DictReader(file, delimiter=';')) 
        
        for profile in profiles:
            if profile['NIM'] == numid: 
                user_found = True
                
                # Get the current links and names
                links = profile.get('Links', '').split(';')
                linknames = profile.get('Linkname', '').split(';')
                
                # Remove the link and link name at the specified index
                if int(link_index) < len(links):
                    links.pop(int(link_index))
                    linknames.pop(int(link_index))
                
                # Update the profile's Links and Linkname fields
                profile['Links'] = ';'.join(links)
                profile['Linkname'] = ';'.join(linknames)
                
                updated_profile.append(profile)
            else:
                updated_profile.append(profile)  
    
    if not user_found:
        return jsonify({"success": False, "message": "User profile not found"}), 404  # Return JSON error if user not found
    
    # Save the updated profile data back to the profile CSV
    with open(file_path_profile, 'w', newline='') as file:
        fieldnames = updated_profile[0].keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(updated_profile)  

    log_activity(numid, nickname, 'Profile Change', 'has delete a link from their profile')
    return jsonify({"success": True, "message": "Link deleted successfully"}), 200  # Return success message

from flask import Flask, render_template, Blueprint
import os
import csv

main_members = Blueprint('members', __name__)

@main_members.route('/')
def home():
    file_path_members = os.path.join(os.getcwd(),'data', 'members.csv')
    members = []
    with open(file_path_members, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            members.append(row)
    return render_template("members.html", members = members)

@main_members.route('/sidebars.html')
def sidebars():
    return render_template('sidebars.html')

@main_members.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@main_members.route('/courses.html')
def courses():
    return render_template('courses.html')

@main_members.route('/class_schedule.html')
def schedule():
    return render_template('class_schedule.html')

@main_members.route('/management_class.html')
def management_class():
    return render_template('management_class.html')

@main_members.route('/members.html')
def members():
    file_path_members = os.path.join(os.getcwd(),'data', 'members.csv')
    members = []
    with open(file_path_members, mode='r') as file:
        csv_reader = csv.DictReader(file, delimiter=';')
        for row in csv_reader:
            members.append(row)
    print(members)
    return render_template("members.html", members = members)

@main_members.route('/home_team_project.html')
def team_project():
    return render_template('home_team_project.html')


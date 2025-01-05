from flask import Flask, render_template, Blueprint, request, jsonify
import csv
import os
from datetime import datetime

# Buat Blueprint
main_courses = Blueprint('courses', __name__)
file_path_tasks = os.path.join(os.getcwd(), 'webb','data', 'tasks.csv')
if not os.path.exists(file_path_tasks):
    with open(file_path_tasks, 'w', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['name', 'deadline', 'source', 'link'])
# Route untuk halaman home
@main_courses.route('/courses')
def courses():
    return render_template("courses.html")

@main_courses.route('/courses/add_task', methods=['POST'])
def add_task():
    data = request.json
    task_name = data.get('name')
    task_deadline = data.get('deadline')
    task_source = data.get('source')
    task_link = data.get('link')

    if not all([task_name, task_deadline, task_source, task_link]):
        return jsonify({'error': 'All fields are required'}), 400

    with open(file_path_tasks, 'a', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow([task_name, task_deadline, task_source, task_link])

    return jsonify({'message': 'Task added successfully'}), 201

# Endpoint to retrieve tasks
@main_courses.route('/courses/get_tasks', methods=['GET'])
def get_tasks():
    tasks = []
    with open(file_path_tasks, 'r') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            tasks.main_coursesend(row)

    return jsonify(tasks)

# Endpoint to delete a task by name
@main_courses.route('/courses/delete_task', methods=['POST'])
def delete_task():
    data = request.json
    task_name = data.get('name')

    if not task_name:
        return jsonify({'error': 'Task name is required'}), 400

    updated_tasks = []
    task_found = False

    with open(file_path_tasks, 'r') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            if row['name'] != task_name:
                updated_tasks.main_coursesend(row)
            else:
                task_found = True

    if not task_found:
        return jsonify({'error': 'Task not found'}), 404

    with open(file_path_tasks, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['name', 'deadline', 'source', 'link'])
        writer.writeheader()
        writer.writerows(updated_tasks)

    return jsonify({'message': 'Task deleted successfully'}), 200

@main_courses.route('/courses/akso')
def akso():
    return render_template('info_course_akso.html')

@main_courses.route('/courses/english')
def english():
    return render_template('info_course_english.html')

@main_courses.route('/courses/litdig')
def litdig():
    return render_template('info_course_litdig.html')

@main_courses.route('/courses/matdas')
def matdas():
    return render_template('info_course_matdas.html')

@main_courses.route('/courses/matdis')
def matdis():
    return render_template('info_course_matdis.html')

@main_courses.route('/courses/matriks')
def matriks():
    return render_template('info_course_matriks.html')

@main_courses.route('/courses/pancasila')
def pancasila():
    return render_template('info_course_pancasila.html')

@main_courses.route('/courses/pemdas')
def pemdas():
    return render_template('info_course_pemdas.html')

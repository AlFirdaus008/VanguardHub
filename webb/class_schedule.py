from flask import Flask, render_template, Blueprint

main_class_schedule = Blueprint('class_schedule', __name__)

# Route for the home page
@main_class_schedule.route('/')
def home():
    return render_template("class_schedule.html")

@main_class_schedule.route('/sidebars.html')
def sidebars():
    return render_template('sidebars.html')

@main_class_schedule.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@main_class_schedule.route('/courses.html')
def courses():
    return render_template('courses.html')

@main_class_schedule.route('/class_schedule.html')
def schedule():
    return render_template('class_schedule.html')

@main_class_schedule.route('/management_class.html')
def management_class():
    return render_template('management_class.html')

@main_class_schedule.route('/members.html')
def members():
    return render_template('members.html')

@main_class_schedule.route('/home_team_project.html')
def team_project():
    return render_template('home_team_project.html')

if __name__ == '__main__':
    main_class_schedule.run(debug=True)
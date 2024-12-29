from flask import Flask, render_template, Blueprint

main_team_project = Blueprint('team_project', __name__)

@main_team_project.route('/')
def home():
    return render_template("home_team_project.html")

@main_team_project.route('/sidebars.html')
def sidebars():
    return render_template('sidebars.html')

@main_team_project.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@main_team_project.route('/courses.html')
def courses():
    return render_template('courses.html')

@main_team_project.route('/class_schedule.html')
def schedule():
    return render_template('class_schedule.html')

@main_team_project.route('/management_class.html')
def management_class():
    return render_template('management_class.html')

@main_team_project.route('/members.html')
def members():
    return render_template('members.html')

@main_team_project.route('/home_team_project.html')
def team_project():
    return render_template('home_team_project.html')

@main_team_project.route('/team_project_pemdas.html')
def team_project_pemdas():
    return render_template('team_project_pemdas.html')

if __name__ == '__main__':
    main_team_project.run(debug=True)

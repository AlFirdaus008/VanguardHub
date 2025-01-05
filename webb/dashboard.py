from flask import Flask, render_template, Blueprint

main_dashboard = Blueprint('dashboard', __name__)

@main_dashboard.route('/')
def home():
    return render_template("firstpage.html")

@main_dashboard.route('/sidebars.html')
def sidebars():
    return render_template('sidebars.html')

@main_dashboard.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@main_dashboard.route('/courses.html')
def courses():
    return render_template('courses.html')

@main_dashboard.route('/class_schedule.html')
def schedule():
    return render_template('class_schedule.html')

@main_dashboard.route('/management_class.html')
def management_class():
    return render_template('management_class.html')

@main_dashboard.route('/members.html')
def members():
    return render_template('members.html')

@main_dashboard.route('/home_team_project.html')
def team_project():
    return render_template('home_team_project.html')

if __name__ == '__main__':
    main_dashboard.run(debug=True)

from flask import Flask, render_template, Blueprint

# Buat Blueprint
main_courses = Blueprint('courses', __name__)

# Route untuk halaman home
@main_courses.route('/')
def home():
    return render_template("courses.html")

@main_courses.route('/sidebars.html')
def sidebars():
    return render_template('sidebars.html')

@main_courses.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@main_courses.route('/courses.html')
def courses():
    return render_template('courses.html')

@main_courses.route('/class_schedule.html')
def schedule():
    return render_template('class_schedule.html')

@main_courses.route('/management_class.html')
def management_class():
    return render_template('management_class.html')

@main_courses.route('/members.html')
def members():
    return render_template('members.html')

@main_courses.route('/home_team_project.html')
def team_project():
    return render_template('home_team_project.html')

@main_courses.route('/info_course_akso.html')
def akso():
    return render_template('info_course_akso.html')

@main_courses.route('/info_course_english.html')
def english():
    return render_template('info_course_english.html')

@main_courses.route('/info_course_litdig.html')
def litdig():
    return render_template('info_course_litdig.html')

@main_courses.route('/info_course_matdas.html')
def matdas():
    return render_template('info_course_matdas.html')

@main_courses.route('/info_course_matriks.html')
def matriks():
    return render_template('info_course_matriks.html')

@main_courses.route('/info_course_pancasila.html')
def pancasila():
    return render_template('info_course_pancasila.html')

@main_courses.route('/info_course_pemdas.html')
def pemdas():
    return render_template('info_course_pemdas.html')


# Buat instance Flask
app = Flask(__name__)

# Daftarkan Blueprint ke aplikasi Flask
app.register_blueprint(main_courses)

# Jalankan aplikasi
if __name__ == '__main__':
    app.run(debug=True)

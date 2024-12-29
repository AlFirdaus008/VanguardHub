from flask import Flask, render_template, Blueprint

# Buat Blueprint
main_management_class = Blueprint('management_class', __name__)

# Route untuk halaman home
@main_management_class.route('/')
def home():
    return render_template("management_class.html")

@main_management_class.route('/sidebars.html')
def sidebars():
    return render_template('sidebars.html')

@main_management_class.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@main_management_class.route('/courses.html')
def courses():
    return render_template('courses.html')

@main_management_class.route('/class_schedule.html')
def schedule():
    return render_template('class_schedule.html')

@main_management_class.route('/management_class.html')
def management_class():
    return render_template('management_class.html')

@main_management_class.route('/members.html')
def members():
    return render_template('members.html')

@main_management_class.route('/home_team_project.html')
def home_team_project():
    return render_template('home_team_project.html')

@main_management_class.route('/manage_class_month.html')
def manage_class_month():
    return render_template('manage_class_month.html')

# Buat instance Flask
app = Flask(__name__, static_folder='static')

# Daftarkan Blueprint ke aplikasi Flask
app.register_blueprint(main_management_class)

# Jalankan aplikasi
if __name__ == '__main__':
    app.run(debug=True)

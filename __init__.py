from flask import Flask
from flask_dance.contrib.google import make_google_blueprint
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv
from flask_mail import Mail
import os

env_path = os.path.join(os.getcwd(),'projek', 'config', '.env')
load_dotenv(dotenv_path=env_path)

mail = Mail()
app = Flask(__name__)
def create_app():
    google_bp = make_google_blueprint(
        client_id=os.getenv('client_id'),
        client_secret=os.getenv('client_secret'),
        redirect_to='google_authorized',
        scope= ["openid", "https://www.googleapis.com/auth/userinfo.email"]
    )
    from login import login_bp
    from profile import profile_bp
    from scheduling import scheduling_bp
    from courses import main_courses
    from members import main_members
    from management_class import main_management_class
    from team_project import main_team_project
    from settings import settings_bp
    from activity import activity_feed_bp

    PREFERRED_URL_SCHEME = 'https' 
    app.register_blueprint(google_bp, url_prefix='/google_login')
    app.register_blueprint(scheduling_bp, url_prefix='/dashboard')
    app.register_blueprint(profile_bp, url_prefix='/dashboard')
    app.register_blueprint(settings_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(activity_feed_bp, url_prefix='/dashboard')
    app.register_blueprint(main_members, url_prefix='/dashboard')
    app.register_blueprint(main_courses, url_prefix='/dashboard')
    app.register_blueprint(main_management_class, url_prefix='/dashboard')
    app.register_blueprint(main_team_project, url_prefix='/dashboard')

    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.secret_key = os.getenv('secret_key')
    


    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    mail.init_app(app)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
from flask import Flask
import os

app = Flask(__name__)
def create_app():
    
    from .dashboard import main_dashboard
    from .courses import main_courses
    from .class_schedule import main_class_schedule
    from .management_class import main_management_class
    from .members import main_members
    from .team_project import main_team_project

    app.register_blueprint(main_dashboard)
    app.register_blueprint(main_courses)
    app.register_blueprint(main_class_schedule)
    app.register_blueprint(main_management_class)
    app.register_blueprint(main_members)
    app.register_blueprint(main_team_project)

    return app
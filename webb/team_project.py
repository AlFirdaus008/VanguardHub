from flask import Flask, render_template, Blueprint

main_team_project = Blueprint('team_project', __name__)

@main_team_project.route('/home_team_project')
def team_project():
    return render_template('home_team_project.html')

@main_team_project.route('/team_project_pemdas')
def team_project_pemdas():
    return render_template('team_project_pemdas.html')



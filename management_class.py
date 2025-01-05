from flask import render_template, Blueprint


main_management_class = Blueprint('management_class', __name__)


@main_management_class.route('/management_class')
def management_class():
    return render_template('management_class.html')

@main_management_class.route('/manage_class_month')
def manage_class_month():
    return render_template('manage_class_month.html')


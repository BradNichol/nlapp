from flask import Blueprint, render_template, flash

errors = Blueprint('errors', __name__)

@errors.app_errorhandler(404)
def page_not_found(error):
    flash("404 Page Not Found")
    return render_template('errors.html'), 404


@errors.app_errorhandler(500)
def server_error(error):
    flash("500 Internal Server Error")
    return render_template('errors.html'), 404

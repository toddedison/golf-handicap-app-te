from flask import Blueprint, render_template

static_pages_bp = Blueprint('static_pages', __name__)


@static_pages_bp.route('/')
def home():
    return render_template('static_pages/home.html')


@static_pages_bp.route('/about')
def about():
    return render_template('static_pages/about.html')


@static_pages_bp.route('/help')
def help():
    return render_template('static_pages/help.html')


@static_pages_bp.route('/privacy')
def privacy():
    return render_template('static_pages/privacy.html')


@static_pages_bp.route('/contact')
def contact():
    return render_template('static_pages/contact.html')

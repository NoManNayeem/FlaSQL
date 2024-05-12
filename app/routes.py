from flask import flash, render_template, redirect, url_for, flash, Blueprint, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .forms import RegistrationForm, LoginForm
from .models import User

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        # Redirect to the dashboard page if the user is logged in
        return redirect(url_for('main.dashboard'))
    # Render the landing page if the user is not logged in
    return render_template('public/landing.html')

from flask import render_template
from flask_login import login_required

@main.route('/dashboard')
@login_required
def dashboard():
    # Dummy data for the statistics cards
    stats = {
        'user_count': '10k+',
        'revenue': '$550K',
        'alerts': '5 Critical'
    }

    # Dummy data for charts
    line_chart_data = {
        'labels': ['January', 'February', 'March', 'April', 'May'],
        'data': [1200, 1900, 1700, 2200, 2500]
    }

    doughnut_chart_data = {
        'labels': ['Red', 'Blue', 'Yellow'],
        'data': [50, 30, 20]
    }

    # Pass the data to the template
    return render_template('private/dashboard.html',
                           stats=stats,
                           line_chart_data=line_chart_data,
                           doughnut_chart_data=doughnut_chart_data)



@main.route('/about')
def about():
    # Ensure you have a 'dashboard.html' template
    return render_template('public/about.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('public/register.html', title='Register', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))  # Redirect to the main index if user is already authenticated

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):  # Assuming verify_password method exists in User model
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next', None)  # Default to None if 'next' not present in URL
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('main.dashboard'))  # Redirect to dashboard after successful login
        else:
            flash('Login Unsuccessful. Please check email and password.', 'danger')  # Show error message
    return render_template('public/login.html', title='Login', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))  # Redirect to the landing page (index) after logout

@main.app_errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('public/404.html'), 404
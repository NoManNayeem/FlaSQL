from flask import flash, render_template, redirect, url_for, flash, Blueprint, request
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .forms import RegistrationForm, LoginForm
from .models import User
from .utils.dbInfo import get_server_metrics



main = Blueprint('main', __name__)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('public/landing.html')



'''
@main.route('/dashboard')
@login_required
def dashboard():
    # Fetch server metrics
    server_metrics = get_server_metrics()

    print("----------------Server Metrics----------------")
    print(server_metrics)
    print("----------------Server Metrics----------------")
    # Pass the server metrics data to the template
    return render_template('private/dashboard.html', server_metrics=server_metrics)
'''




@main.route('/about')
def about():
    return render_template('public/about.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Use the password setter of the User model
        user = User(username=form.username.data, email=form.email.data)
        user.password = form.password.data  # This automatically hashes the password
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
        if user and user.verify_password(form.password.data):  # Now using verify_password method
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
    # Note that we set the 404 status explicitly
    return render_template('public/404.html'), 404







#-----------------DB Monitoring Views-----------------#

from .utils.dbSummery import get_Server_Details

@main.route('/dashboard')
@login_required
def dashboard():
    # # Fetch server metrics
    # server_metrics = get_Server_Details()
    
    # print("----------------Server Metrics----------------")
    # print(server_metrics)
    # print("----------------Server Metrics----------------")
    
    # Pass the server metrics data to the template
    # return render_template('private/dashboard.html', server_metrics=server_metrics)
    return render_template('private/dashboard.html')



@main.route('/database-status')
@login_required
def database_status():
    return render_template('private/database_status.html')

@main.route('/disk-space-monitoring')
@login_required
def disk_space_monitoring():
    return render_template('private/disk_space_monitoring.html')

@main.route('/backup-status')
@login_required
def backup_status():
    return render_template('private/backup_status.html')

@main.route('/sql-server-services')
@login_required
def sql_server_services():
    return render_template('private/sql_server_services.html')

@main.route('/error-logs')
@login_required
def error_logs():
    return render_template('private/error_logs.html')

@main.route('/configuration-settings')
@login_required
def configuration_settings():
    return render_template('private/configuration_settings.html')

@main.route('/performance-monitoring')
@login_required
def performance_monitoring():
    return render_template('private/performance_monitoring.html')

@main.route('/index-fragmentation')
@login_required
def index_fragmentation():
    return render_template('private/index_fragmentation.html')

@main.route('/historical-data')
@login_required
def historical_data():
    return render_template('private/historical_data.html')

@main.route('/alerts-notifications')
@login_required
def alerts_notifications():
    return render_template('private/alerts_notifications.html')

@main.route('/reports')
@login_required
def reports():
    return render_template('private/reports.html')

@main.route('/maintenance-tasks')
@login_required
def maintenance_tasks():
    return render_template('private/maintenance_tasks.html')

@main.route('/security-compliance')
@login_required
def security_compliance():
    return render_template('private/security_compliance.html')

@main.route('/automation-scheduling')
@login_required
def automation_scheduling():
    return render_template('private/automation_scheduling.html')

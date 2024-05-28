from flask import flash, render_template, redirect, url_for, flash, Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from .forms import RegistrationForm, LoginForm
from .models import User, MSSQLConnection




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




#-------------------Connect DB-------------------#
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from .models import db, MSSQLConnection


@main.route('/connections', methods=['GET', 'POST'])
def connections():
    if request.method == 'POST':
        if request.form.get('form_type') == 'create':
            server = request.form.get('server')
            database = request.form.get('database')
            username = request.form.get('username')
            password = request.form.get('password')
            driver = request.form.get('driver')
            trusted_connection = request.form.get('trusted_connection')
            active = 'active' in request.form

            new_connection = MSSQLConnection(
                server=server,
                database=database,
                username=username,
                password=password,
                driver=driver,
                trusted_connection=trusted_connection,
                active=active
            )
            db.session.add(new_connection)
            if active:
                new_connection.set_active()
            db.session.commit()
            flash('Connection created successfully!', 'success')
        elif request.form.get('form_type') == 'edit':
            connection_id = request.form.get('id')
            connection = MSSQLConnection.query.get_or_404(connection_id)
            connection.server = request.form.get('server')
            connection.database = request.form.get('database')
            connection.username = request.form.get('username')
            connection.password = request.form.get('password')
            connection.driver = request.form.get('driver')
            connection.trusted_connection = request.form.get('trusted_connection')
            connection.active = 'active' in request.form
            if connection.active:
                connection.set_active()
            db.session.commit()
            flash('Connection updated successfully!', 'success')
    
    connections = MSSQLConnection.query.all()
    return render_template('private/connections.html', connections=connections)

@main.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    connection = MSSQLConnection.query.get_or_404(id)
    db.session.delete(connection)
    db.session.commit()
    flash('Connection deleted successfully!', 'success')
    return redirect(url_for('main.connections'))

@main.route('/get_connection/<int:id>', methods=['GET'])
def get_connection(id):
    connection = MSSQLConnection.query.get_or_404(id)
    connection_data = {
        'id': connection.id,
        'server': connection.server,
        'database': connection.database,
        'username': connection.username,
        'password': connection.password,
        'driver': connection.driver,
        'trusted_connection': connection.trusted_connection,
        'active': connection.active
    }
    return jsonify(connection_data)


#-----------------DB Monitoring Views-----------------#
from .models import MSSQLConnection 
from .utils.dbStatus import connect_to_db



@main.route('/dashboard')
def dashboard():
    # Check if there are any MSSQLConnection objects
    all_connections = MSSQLConnection.query.all()
    if not all_connections:
        flash('No database connections found. Please add a connection.', 'warning')
        return redirect(url_for('main.connections'))

    # Check if there is an active connection
    active_connection = MSSQLConnection.query.filter_by(active=True).first()
    if not active_connection:
        flash('No active database connection found. Please activate a connection.', 'warning')
        return redirect(url_for('main.connections'))

    # If there is an active connection, fetch the details
    db_details = connect_to_db()
    if db_details:
        return render_template('private/dashboard.html', db_details=db_details)
    else:
        flash('Unable to connect to the database with the active connection.', 'danger')
        return render_template('private/dashboard.html', error="Unable to connect to the database.")


@main.route('/database-status')
# @login_required
def database_status():
    return render_template('private/database_status.html')

@main.route('/disk-space-monitoring')
# @login_required
def disk_space_monitoring():
    return render_template('private/disk_space_monitoring.html')

@main.route('/backup-status')
# @login_required
def backup_status():
    return render_template('private/backup_status.html')

@main.route('/sql-server-services')
# @login_required
def sql_server_services():
    return render_template('private/sql_server_services.html')

@main.route('/error-logs')
# @login_required
def error_logs():
    return render_template('private/error_logs.html')

@main.route('/configuration-settings')
# @login_required
def configuration_settings():
    return render_template('private/configuration_settings.html')

@main.route('/performance-monitoring')
# @login_required
def performance_monitoring():
    return render_template('private/performance_monitoring.html')

@main.route('/index-fragmentation')
# @login_required
def index_fragmentation():
    return render_template('private/index_fragmentation.html')

@main.route('/historical-data')
# @login_required
def historical_data():
    return render_template('private/historical_data.html')

@main.route('/alerts-notifications')
# @login_required
def alerts_notifications():
    return render_template('private/alerts_notifications.html')

@main.route('/reports')
# @login_required
def reports():
    return render_template('private/reports.html')

@main.route('/maintenance-tasks')
# @login_required
def maintenance_tasks():
    return render_template('private/maintenance_tasks.html')

@main.route('/security-compliance')
# @login_required
def security_compliance():
    return render_template('private/security_compliance.html')

@main.route('/automation-scheduling')
# @login_required
def automation_scheduling():
    return render_template('private/automation_scheduling.html')

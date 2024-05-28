from flask_login import UserMixin
from datetime import datetime
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
import urllib.parse

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    _password = db.Column('password', db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_admin = db.Column(db.Boolean, default=False)
    is_confirmed = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self._password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self._password, password)

    def __repr__(self):
        return f'<User {self.username}>'






import urllib.parse


class MSSQLConnection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server = db.Column(db.String(100), nullable=False)
    database = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), nullable=True)
    password = db.Column(db.String(100), nullable=True)
    driver = db.Column(db.String(100), default='ODBC Driver 17 for SQL Server')
    trusted_connection = db.Column(db.String(10), default='yes')
    active = db.Column(db.Boolean, default=False)

    def get_connection_string(self):
        if self.trusted_connection.lower() == 'yes':
            params = urllib.parse.quote_plus(
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"Trusted_Connection={self.trusted_connection};"
            )
        else:
            params = urllib.parse.quote_plus(
                f"DRIVER={{{self.driver}}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
            )
        return f"mssql+pyodbc:///?odbc_connect={params}"

    def set_active(self):
        # Ensure only one connection can be active at a time
        MSSQLConnection.query.update({MSSQLConnection.active: False})
        self.active = True
        db.session.commit()

    def __repr__(self):
        return f'<MSSQLConnection {self.server} - {self.database}>'
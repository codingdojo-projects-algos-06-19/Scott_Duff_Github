from flask import flash
from sqlalchemy.sql import func
from config import db
import re


name_REGEX = re.compile(r'^[a-zA-Z0-9]+$')
email_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
message_REGEX = re.compile(r'^[a-zA-Z][a-zA-Z0-9\s.]+$')


users_events = db.Table('users_events',
                        db.Column('user_id', db.Integer,
                                  db.ForeignKey('user.id'),
                                  primary_key=True),
                        db.Column('event_id', db.Integer,
                                  db.ForeignKey('event.id'),
                                  primary_key=True))


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    email = db.Column(db.String(90))
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(),
                           onupdate=func.now())
    events_for_users = db.relationship('Event', secondary=users_events)

    @classmethod
    def validate_user(cls, user_data):
        is_valid = True
        # Email Validation
        if not email_REGEX.match(user_data['regEmail']):
            is_valid = False
            flash("Invalid email address.")
        checkForEmail = user_data['regEmail']
        doesEmailExist = User.query.filter_by(email=checkForEmail).first()
        if doesEmailExist:
            is_valid = False
            flash("Email already exists.")
        # Password Validation
        if len(user_data['regPassword']) < 5:
            is_valid = False
            flash("Password must be at least 5 characters.")
        if (user_data['regPassword']) != (user_data['regConfirmPassword']):
            is_valid = False
            flash("Password and confirm password do not match.")
        # First Name Validation
        if len(user_data['regFirstName']) <= 2:
            is_valid = False
            flash("First Name must be 3 or more characters.")
        if not name_REGEX.match(user_data['regFirstName']):
            is_valid = False
            flash("First Name must contain only letters and numbers.")
        # Last Name Validation
        if len(user_data['regLastName']) <= 2:
            is_valid = False
            flash("Last Name must be 3 or more characters.")
        if not name_REGEX.match(user_data['regLastName']):
            is_valid = False
            flash("Last Name must contain only letters and numbers.")
        return is_valid

    @classmethod
    def validate_update_user(cls, user_data):
        is_valid = True
        # Password Validation
        if len(user_data['updatePassword']) < 5:
            is_valid = False
            flash("Password must be at least 5 characters.")
        if (user_data['updatePassword']) != (user_data['updateConfirmPassword']):
            is_valid = False
            flash("Password and confirm password do not match.")
        # First Name Validation
        if len(user_data['updateFirstName']) <= 2:
            is_valid = False
            flash("First Name must be 3 or more characters.")
        if not name_REGEX.match(user_data['updateFirstName']):
            is_valid = False
            flash("First Name must contain only letters and numbers.")
        # Last Name Validation
        if len(user_data['updateLastName']) <= 2:
            is_valid = False
            flash("Last Name must be 3 or more characters.")
        if not name_REGEX.match(user_data['updateLastName']):
            is_valid = False
            flash("Last Name must contain only letters and numbers.")
        return is_valid


class Event(db.Model):
    __tablename__ = "event"
    id = db.Column(db.Integer, primary_key=True)
    game = db.Column(db.String(45))
    platform = db.Column(db.String(45))
    location = db.Column(db.String(90))
    event_date = db.Column(db.DateTime)
    event_time = db.Column(db.DateTime)
    max_players = db.Column(db.Integer)
    current_players = db.Column(db.Integer)
    event_poster = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(),
                           onupdate=func.now())
    users_for_events = db.relationship('User', secondary=users_events)

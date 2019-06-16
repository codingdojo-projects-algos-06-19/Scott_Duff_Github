from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
import re
from datetime import datetime
from sqlalchemy import desc


app = Flask(__name__)
app.secret_key = "secretkey"


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game_compiler.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)


migrate = Migrate(app, db)


bcrypt = Bcrypt(app)


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


# signup HTML
@app.route("/")
def signUp():
    return render_template("signup.html")


# User Registration Function
@app.route("/add/user", methods=['POST'])
def add_user():
    is_valid = True
    # Email Validation
    if not email_REGEX.match(request.form['regEmail']):
        is_valid = False
        flash("Invalid email address.")
    checkForEmail = request.form['regEmail']
    doesEmailExist = User.query.filter_by(email=checkForEmail).first()
    if doesEmailExist:
        is_valid = False
        flash("Email already exists.")
    # Password Validation
    if len(request.form['regPassword']) < 5:
        is_valid = False
        flash("Password must be at least 5 characters.")
    if (request.form['regPassword']) != (request.form['regConfirmPassword']):
        is_valid = False
        flash("Password and confirm password do not match.")
    # First Name Validation
    if len(request.form['regFirstName']) <= 2:
        is_valid = False
        flash("First Name must be 3 or more characters.")
    if not name_REGEX.match(request.form['regFirstName']):
        is_valid = False
        flash("First Name must contain only letters and numbers.")
    # Last Name Validation
    if len(request.form['regLastName']) <= 2:
        is_valid = False
        flash("Last Name must be 3 or more characters.")
    if not name_REGEX.match(request.form['regLastName']):
        is_valid = False
        flash("Last Name must contain only letters and numbers.")
    # User Created
    if is_valid:
        flash("User successfully registered!")
        pw_hash = bcrypt.generate_password_hash(request.form['regPassword'])
        create_new_user = User(first_name=request.form['regFirstName'],
                               last_name=request.form['regLastName'],
                               email=request.form['regEmail'],
                               password=pw_hash)
        db.session.add(create_new_user)
        db.session.commit()
        session['login'] = True
        get_user_info = User.query.filter_by(email=request.form['regEmail']).first()
        session['userid'] = get_user_info.id
        session['name'] = f"{get_user_info.first_name} {get_user_info.last_name}"
    return redirect("/welcome/user")


# User Login Function
@app.route("/login/user", methods=['POST'])
def login_user():
    checkForEmail = request.form['loginEmail']
    doesEmailExist = User.query.filter_by(email=checkForEmail).first()
    print(doesEmailExist)
    if doesEmailExist:
        if bcrypt.check_password_hash(doesEmailExist.password, request.form['loginPassword']):
            get_user_info = User.query.filter_by(email=request.form['loginEmail']).first()
            session['userid'] = get_user_info.id
            flash("Successfully logged in.")
            session['login'] = True
            session['name'] = f"{get_user_info.first_name} {get_user_info.last_name}"
            return redirect('/welcome/user')
    flash("You could not be logged in")
    print("*" * 50)
    return redirect("/")


# user_welcome HTML
@app.route("/welcome/user")
def welcome_user():
    if 'login' not in session:
        flash("Your are not logged in!")
        return redirect("/")
    else:
        todays_datetime = datetime(datetime.today().year, datetime.today().month, datetime.today().day)
        eventDateQuery = Event.query.filter(Event.users_for_events.any(id=session['userid']), Event.event_date == todays_datetime).order_by('event_date').all()
        eventQuery = Event.query.filter(Event.users_for_events.any(id=session['userid'])).order_by('event_date').all()
        return render_template("user_welcome.html", eventQuery=eventQuery, eventDateQuery=eventDateQuery)


# User Logout Function
@app.route("/logout/user")
def logout_user():
    session.clear()
    flash("Your are now logged out!")
    return redirect("/")


# user_account HTML
@app.route("/account/user/<id>")
def account_user(id):
    editUserQuery = User.query.get(id)
    return render_template("user_account.html", editUserQuery=editUserQuery)


# User Update Function
@app.route("/update/user/<id>", methods=['POST'])
def update_user(id):
    is_valid = True
    # First Name Validation
    if len(request.form['updateFirstName']) <= 2:
        is_valid = False
        flash("First Name must be 3 or more characters.")
    if not name_REGEX.match(request.form['updateFirstName']):
        is_valid = False
        flash("First Name must contain only letters and numbers.")
    # Last Name Validation
    if len(request.form['updateLastName']) <= 2:
        is_valid = False
        flash("Last Name must be 3 or more characters.")
    if not name_REGEX.match(request.form['updateLastName']):
        is_valid = False
        flash("Last Name must contain only letters and numbers.")
    # Password Validation
    if len(request.form['updatePassword']) < 5:
        is_valid = False
        flash("Password must be at least 5 characters.")
    if (request.form['updatePassword']) != (request.form['updateConfirmPassword']):
        is_valid = False
        flash("Password and confirm password do not match.")
    if is_valid:
        flash("User successfully updated")
        pw_hash = bcrypt.generate_password_hash(request.form['updatePassword'])
        user_to_update = User.query.get(id)
        user_to_update.first_name = request.form['updateFirstName']
        user_to_update.last_name = request.form['updateLastName']
        user_to_update.password = pw_hash
        db.session.commit()
    return redirect("/account/user/" + id)


# search_events HTML
@app.route("/event/search")
def event_search():
    eventQuery = Event.query.order_by('event_date')
    return render_template("event_search.html", eventQuery=eventQuery)


# create_event HTML
@app.route("/event/create")
def event():
    return render_template("event_create.html")


# Event Creation Function
@app.route("/add/event", methods=['POST'])
def add_event():
    Date = datetime.strptime(request.form['regDate'], '%Y-%m-%d')
    Time = datetime.strptime(request.form['regTime'], '%H:%M')
    create_new_event = Event(game=request.form['regGame'],
                             platform=request.form['regPlatform'],
                             location=request.form['regLocation'],
                             event_date=Date,
                             event_time=Time,
                             max_players=request.form['regPlayers'],
                             current_players=1,
                             event_poster=session['userid'])
    db.session.add(create_new_event)
    db.session.commit()
    event = Event.query.order_by(desc('created_at')).first()
    user = User.query.get(session['userid'])
    user.events_for_users.append(event)
    db.session.commit()
    return redirect("/event/search")


# Event Update Function
@app.route("/update/event/<id>", methods=['POST'])
def update_event(id):
    Date = datetime.strptime(request.form['updateDate'], '%Y-%m-%d')
    Time = datetime.strptime(request.form['updateTime'], '%H:%M')
    event_to_update = Event.query.get(id)
    event_to_update.game = request.form['updateGame']
    event_to_update.platform = request.form['updatePlatform']
    event_to_update.location = request.form['updateLocation']
    event_to_update.max_players = request.form['updatePlayers']
    event_to_update.event_date = Date
    event_to_update.event_time = Time
    db.session.commit()
    return redirect("/event/search")


# event_details HTML
@app.route("/event/details/<id>")
def event_details(id):
    eventPlayerQuery = User.query.join(User.events_for_users).filter(Event.id == id).all()
    eventQuery = Event.query.get(id)
    return render_template("event_details.html", event=eventQuery, eventPlayerQuery=eventPlayerQuery)


# event_view HTML
@app.route("/event/view/<id>")
def event_view(id):
    eventPlayerQuery = User.query.join(User.events_for_users).filter(Event.id == id).all()
    eventQuery = Event.query.get(id)
    return render_template("event_view.html", event=eventQuery, eventPlayerQuery=eventPlayerQuery)


# Join Event Function
@app.route("/join/event/<id>")
def join_event(id):
    eventToJoin = Event.query.get(id)
    userToJoin = User.query.get(session['userid'])
    if (User.query.join(User.events_for_users).filter(User.id == session['userid'], Event.id == id)).first():
        flash("You have already joined!")
    else:
        if (eventToJoin.current_players < eventToJoin.max_players):
            userToJoin.events_for_users.append(eventToJoin)
            eventToJoin.current_players += 1
            db.session.commit()
        else:
            flash("Player limit reached!")
    return redirect("/event/search")


# Delete Event Function
@app.route("/delete/event/<id>")
def deleteEvent(id):
    delete_event = Event.query.get(id)
    db.session.delete(delete_event)
    db.session.commit()
    return redirect("/event/search")


# Leave Event Function
@app.route("/leave/event/<id>")
def leaveEvent(id):
    if (User.query.join(User.events_for_users).filter(User.id == session['userid'], Event.id == id)).first():
        removeUser = User.query.get(session['userid'])
        removeEvent = Event.query.get(id)
        removeEvent.current_players -= 1
        removeUser.events_for_users.remove(removeEvent)
        db.session.commit()
    else:
        flash("You are not part of this event.")
    return redirect("/event/details/" + id)


if __name__ == "__main__":
    app.run(debug=True)

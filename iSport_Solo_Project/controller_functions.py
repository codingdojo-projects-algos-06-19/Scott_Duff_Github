from flask import render_template, request, redirect, session, flash
from config import app, db
from datetime import datetime
from sqlalchemy import desc
from config import bcrypt


from models import User, Event


# signup HTML
@app.route("/")
def signUp():
    return render_template("signup.html")


# User Registration Function
@app.route("/add/user", methods=['POST'])
def add_user():
    validation_check = User.validate_user(request.form)
    if not validation_check:
        flash("User not created!")
    else:
        # User Created
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
    if 'login' not in session:
        flash("Your are not logged in!")
        return redirect("/")
    else:
        editUserQuery = User.query.get(id)
        return render_template("user_account.html", editUserQuery=editUserQuery)


# User Update Function
@app.route("/update/user/<id>", methods=['POST'])
def update_user(id):
    validation_check = User.validate_update_user(request.form)
    if not validation_check:
        flash("User not updated!")
    else:
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
    if 'login' not in session:
        flash("Your are not logged in!")
        return redirect("/")
    else:
        eventQuery = Event.query.order_by('event_date')
        return render_template("event_search.html", eventQuery=eventQuery)


# create_event HTML
@app.route("/event/create")
def event():
    if 'login' not in session:
        flash("Your are not logged in!")
        return redirect("/")
    else:
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
    if 'login' not in session:
        flash("Your are not logged in!")
        return redirect("/")
    else:
        eventPlayerQuery = User.query.join(User.events_for_users).filter(Event.id == id).all()
        eventQuery = Event.query.get(id)
        return render_template("event_details.html", event=eventQuery, eventPlayerQuery=eventPlayerQuery)


# event_view HTML
@app.route("/event/view/<id>")
def event_view(id):
    if 'login' not in session:
        flash("Your are not logged in!")
        return redirect("/")
    else:
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
def delete_event(id):
    delete_event = Event.query.get(id)
    db.session.delete(delete_event)
    db.session.commit()
    return redirect("/event/search")


# Leave Event Function
@app.route("/leave/event/<id>")
def leave_event(id):
    if (User.query.join(User.events_for_users).filter(User.id == session['userid'], Event.id == id)).first():
        removeUser = User.query.get(session['userid'])
        removeEvent = Event.query.get(id)
        removeEvent.current_players -= 1
        removeUser.events_for_users.remove(removeEvent)
        db.session.commit()
    else:
        flash("You are not part of this event.")
    return redirect("/event/details/" + id)

from config import app
from controller_functions import signUp, add_user, login_user, welcome_user
from controller_functions import logout_user, account_user, update_user
from controller_functions import event_search, event, add_event, update_event
from controller_functions import event_details, event_view, join_event
from controller_functions import delete_event, leave_event


app.add_url_rule("/", view_func=signUp)
app.add_url_rule("/add/user", view_func=add_user, methods=['POST'])
app.add_url_rule("/login/user", view_func=login_user, methods=['POST'])
app.add_url_rule("/welcome/user", view_func=welcome_user)
app.add_url_rule("/logout/user", view_func=logout_user)
app.add_url_rule("/account/user/<id>", view_func=account_user)
app.add_url_rule("/update/user/<id>", view_func=update_user, methods=['POST'])
app.add_url_rule("/event/search", view_func=event_search)
app.add_url_rule("/event/create", view_func=event)
app.add_url_rule("/add/event", view_func=add_event, methods=['POST'])
app.add_url_rule("/update/event/<id>", view_func=update_event, methods=['POST'])
app.add_url_rule("/event/details/<id>", view_func=event_details)
app.add_url_rule("/event/view/<id>", view_func=event_view)
app.add_url_rule("/join/event/<id>", view_func=join_event)
app.add_url_rule("/delete/event/<id>", view_func=delete_event)
app.add_url_rule("/leave/event/<id>", view_func=leave_event)

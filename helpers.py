from flask import redirect, render_template, session
from functools import wraps
from datetime import datetime

def apology(message, code=400):
    def escape(s):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def get_date(d, t):
    day, month, year = d.split("/")
    hour, minute = t.split(":")
    return datetime(int(year), int(month), int(day), int(hour), int(minute), 0)

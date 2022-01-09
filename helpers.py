import os
import requests
import urllib.parse
from cs50 import SQL
db = SQL("sqlite:///memories.db")

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    #I believe that this returns a rendering of a meme
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    if session.get("user_id") == None:
        print("not logged in")
        return render_template("error.html", top=code, bottom=escape(message),no_friend_requests = None, no_post_requests = None), code
    print("logged in")
    return render_template("error.html", top=code, bottom=escape(message),no_friend_requests = count_friend_requests(), no_post_requests = count_post_requests()), code

def success(message):
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    # If not logged in
    if session.get("user_id")== None:
        return render_template("success.html", bottom=escape(message),no_friend_requests = None, no_post_requests = None)
    return render_template("success.html", bottom=escape(message),no_friend_requests = count_friend_requests(), no_post_requests = count_post_requests())


def sad(message):
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("sad.html", bottom=escape(message),no_friend_requests = count_friend_requests(), no_post_requests = count_post_requests())

def count_friend_requests():
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
    f_requests_a = db.execute("SELECT friend1, friend_id, requester, date, time FROM friends WHERE friend2 = ? AND approved = 0", username)
    f_requests_b = db.execute("SELECT friend2, friend_id, requester, date, time FROM friends WHERE friend1 = ? AND approved = 0", username)


        #Query the users database for the first names of any requesters and make the attribute "requester_username" equal to the username of the requester
    for f_request in f_requests_a:
        f_request["friend_name"] = db.execute("SELECT firstname FROM users WHERE username = ?", f_request["friend1"])[0]["firstname"]
        f_request["friend_username"] = f_request["friend1"]
    for f_request in f_requests_b:
        f_request["friend_name"] = db.execute("SELECT firstname FROM users WHERE username = ?", f_request["friend2"])[0]["firstname"]
        f_request["friend_username"] = f_request["friend2"]


    f_requests = f_requests_a + f_requests_b
    f_requests = [f_request for f_request in f_requests if f_request["requester"] != username]
    if not f_requests:
        return ""
    else:

        return len(f_requests)

def count_post_requests():
    current_user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
    post_requests = db.execute("SELECT * FROM posts WHERE receiver = ? AND approved = 0", current_user)

    if not post_requests:
        return ""
    return len(post_requests)

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def alpha(friend1, friend2):
    friends = [friend1, friend2]
    friends.sort()
    return friends[0]

def beta(friend1, friend2):
    friends = [friend1, friend2]
    friends.sort()
    return friends[1]



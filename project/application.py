import os
import string
from datetime import date, datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash


from helpers import apology, login_required, alpha, beta, success, sad, count_friend_requests, count_post_requests

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response



# Configure session to use filesystem  - i.e. locally (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///memories.db")

@app.route("/", methods=["GET","POST"])
@login_required
def index():
    current_user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
    # make a lists of all the posts which were either sent or received by this user
    posts = db.execute("SELECT * FROM posts WHERE receiver = ? AND approved = 1 ORDER BY date, time DESC", current_user)
    if not posts:
        return sad("no memories yet. Make some friends first!")
    if request.method =="GET":
        return render_template("index.html", posts = posts, no_friend_requests = count_friend_requests(), no_post_requests = count_post_requests())






@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    # Load the page when GET request
    if request.method == "GET":
        return render_template("register.html")
    # When the form is submitted, do this
    else:
        firstname = request.form.get("firstname")
        username = request.form.get("username")
        password1 = request.form.get("password")
        password2 = request.form.get("confirmation")
        names = db.execute("SELECT username FROM users")
        # Check that username is entered
        if not firstname:
            return apology("must provide first name")
        if not username:
            return apology("must provide username")
        # Check that the username does not match a current username
        for name in names:
            if username == name:
                return apology("Username already taken")

        # Check that pw is entered
        if not password1:
            return apology("must provide password")
        if password1 != password2:

            return apology("passwords do not match")

        # Check that pw fulfills all requirements

        if len(password1)<8:
            return apology("password must contain at least 8 characters")
        containsUppercase = False
        containsNumber = False
        containsSymbol = False
        containsLowercase = False
        symbols = string.punctuation
        for character in password1:
            if character.isupper():
                containsUppercase = True
            if character.islower():
                containsLowercase = True
            if character.isnumeric():
                containsNumber = True
            if character in string.punctuation:
                containsSymbol = True
        if containsUppercase == False:
            return apology("Password needs to contain at least 1 uppercase character")
        if containsLowercase == False:
            return apology("Password needs to contain at least 1 lowercase character")
        if containsNumber == False:
            return apology("Password needs to contain at least 1 number")
        if containsSymbol == False:
            return apology("Password needs to contain at least 1 special character")

        db.execute("INSERT INTO users (firstname, username, hash) VALUES (?,?,?)", firstname,username, generate_password_hash(password1))

        return redirect("/login")

@app.route("/addfriends", methods=["GET", "POST"])
@login_required
def add_friends():
    if request.method == "GET":
        return render_template("addfriends.html", no_friend_requests = count_friend_requests(), no_post_requests = count_post_requests())
    else:
        requester = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
        requestee = request.form.get("username")
        friend2  = db.execute("SELECT username FROM users WHERE username = ?", requestee)[0]["username"]


        # Check for trolling
        if requestee != friend2:
            return apology("Requested username does not match a friend's username")
        today = date.today()
        today_date = today.strftime("%d/%m/%Y")
        today_time = datetime.now().time()

        #Check that this request hasn't already been sent before or already friends with this user -
        f_requests = db.execute("SELECT * FROM friends WHERE friend1 = ? AND friend2 = ?", alpha(requester, requestee), beta(requester, requestee))
        for f_request in f_requests:

            if f_request["friend1"] ==alpha(requester, requestee) and f_request["friend2"]==beta(requester, requestee):
                if f_request["approved"] ==0:
                    return apology("Already requested before")
                else:
                    return apology("Already friends")
        # When successful, immediately update the friends
        db.execute("INSERT INTO friends (friend1, friend2, date, time, requester) VALUES (?,?,?,?,?)", alpha(requester, requestee), beta(requester, requestee), today_date, today_time, requester)
        return success("Friend request sent!")




@app.route("/search")
@login_required
def search():
    q = request.args.get("q")
    # if an argument is entered, return the json, otherwise return empty
    if q:
        users = db.execute("SELECT * FROM users WHERE username LIKE ? AND id != ?", q + "%", session["user_id"])
    else:
        users = []
    return jsonify(users)

#Search for friends
@app.route("/f_search")
@login_required
def f_search():
    q = request.args.get("q")
    # if an argument is entered, return the json, otherwise return empty
    if q:
        current_user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
        users1 = db.execute("SELECT friend2 FROM friends WHERE friend1 = ? AND friend2 LIKE ? AND approved = 1", current_user, q + "%")
        users2 = db.execute("SELECT friend1 FROM friends WHERE friend2 = ? AND friend1 LIKE ? AND approved = 1", current_user, q + "%")
        users = []
        # users stores list of all relevant usernames
        for user in users1:
            users.append(user["friend2"])
        for user in users2:
            users.append(user["friend1"])
    else:
        users = []
    return jsonify(users)


@app.route("/friend_requests", methods = ["GET", "POST"])
@login_required
def friend_requests():
    #Get the current user's username
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
    if request.method == "GET":
        #Query the friends database for any requests involving the user who is logged in
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
            return sad("no friend requests")
        return render_template("friend_requests.html", friend_requests = f_requests, no_friend_requests = count_friend_requests(), no_post_requests = count_post_requests())
    if request.method == "POST":

        if "accept" in request.form.get("answer"):
            today = date.today()
            today_date = today.strftime("%d/%m/%Y")
            today_time = datetime.now().time()
            db.execute("UPDATE friends SET approved = 1, date = ?, time = ? WHERE friend_id = ?", today_date, today_time, request.form.get("answer").removesuffix("accept"))

            return success("Friend request accepted!")
        elif "reject" in request.form.get("answer"):
            db.execute("DELETE FROM friends WHERE friend_id = ?",request.form.get("answer").removesuffix("reject"))
            return success("Friend request deleted!")
        else:
            return apology("Not a valid option")


@app.route("/friends", methods = ["GET", "POST"])
@login_required
def friends():
    #Get the current user's username

    current_user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]

    if request.method == "GET":
    # Render a table with all of the user's friends
        beta_friend_usernames = db.execute("SELECT friend2, friend_id, date FROM friends WHERE friend1 = ? AND approved = 1", current_user)
        alpha_friend_usernames = db.execute("SELECT friend1, friend_id, date FROM friends WHERE friend2 = ? AND approved = 1", current_user)

        #Create a list of the usernames of all the friends
        usernames = []
        for friend in beta_friend_usernames:
            usernames.append(friend["friend2"])
        for friend in alpha_friend_usernames:
            usernames.append(friend["friend1"])
        # lump together beta and alpha friends
        FRIENDS= beta_friend_usernames + alpha_friend_usernames
        if not FRIENDS:
            return sad("no friends yet :(")
        # Iterate through both these lists at the same time, querying the database for the firstname and adding the first name to the FRIENDS list
        for (username, FRIEND) in zip(usernames, FRIENDS):
            #query for first names of all friends
            friend = db.execute("SELECT firstname,username FROM users WHERE username = ?", username)
            #add this to FRIENDS
            FRIEND["firstname"] = friend[0]["firstname"]
            FRIEND["username"] = friend[0]["username"]
        return render_template("friends.html", friends = FRIENDS,no_friend_requests = count_friend_requests(), no_post_requests = count_post_requests())

    # Delete the friend who has been asked to be deleted - still yet to make this work
    if request.method == "POST":
        db.execute("DELETE from FRIENDS where friend_id = ?", request.form.get("delete"))
        return success("Friend deleted")

@app.route("/postmemories", methods = ["GET", "POST"])
@login_required
def postmemories():
    if request.method == "GET":
        return render_template("postmemories.html", no_friend_requests = count_friend_requests(), no_post_requests = count_post_requests())
    if request.method == "POST":
        current_user =  current_user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
        receivers = []
        keys = request.form.keys()
        print(keys)
        # Check friend has been added
        if not keys:
            return apology("Please select at least 1 friend to send this memory to.")
        if not request.form.get("memorycontent"):
            return apology("Please enter some content in the memory")
        content = request.form.get("memorycontent")
        keys = [key for key in keys if key.startswith("addedUsername")]

        # Iterate over the form inputs and append the name of the recipients to the receivers list
        for key in keys:
            receivers.append(request.form.get(key))

        # TODO - put the info into the database
        #Calculate date and time
        today = date.today()
        today_date = today.strftime("%d/%m/%Y")
        today_time = datetime.now().time()
        users = db.execute("SELECT username FROM users")
        for receiver in receivers:
            #TODO sanitation for invalid recipient
            db.execute("INSERT into posts (sender, receiver, content, date, time) VALUES (?,?,?,?,?)", current_user, receiver, content, today_date, today_time)
        return success("Memory sent!")





@app.route("/post_requests", methods = ["GET", "POST"])
@login_required
def post_requests():
    current_user = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]["username"]
    post_requests = db.execute("SELECT * FROM posts WHERE receiver = ? AND approved = 0", current_user)
    if request.method == "GET":
        if not post_requests:
            return sad("No requests")
        return render_template("post_requests.html", post_requests = post_requests, no_friend_requests = count_friend_requests(), no_post_requests = count_post_requests())
    if request.method == "POST":
        if "accept" in request.form.get("answer"):
            #approve
            db.execute("UPDATE posts SET approved = 1 WHERE id = ?", request.form.get("answer").removesuffix("accept"))
            return success("Post request accepted!")
        elif "reject" in request.form.get("answer"):
            #delete
            db.execute("DELETE FROM posts WHERE id = ?", request.form.get("answer").removesuffix("reject"))
            return success("Post request deleted!")
        else:
            return apology("not a valid option")


@app.route("/accesslinks")
@login_required
def accesslinks():
    return render_template("accesslinks.html",no_friend_requests = count_friend_requests(), no_post_requests = count_post_requests())






def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
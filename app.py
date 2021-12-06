# Adding comment
#CREATE TABLE items (person_id INTEGER, file BLOB, name TEXT NOT NULL, description Text NOT NULL, FOREIGN KEY(person_id) REFERENCES users(id));
import os
import base64
from io import BytesIO #Converts data from Database into bytes

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from helpers import apology, login_required, usd, cc_validate

UPLOAD_FOLDER = '/path/to/the/uploads'


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///hmart.db")

def decode(table):
    decoded = []
    for row in table:
        decoded.append(row["file"].decode())
    for count, value in enumerate(decoded):
        table[count]["file"] = value
    return table

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/")
@login_required
def index():
    """Show all items for sale in tables"""
    table = decode(db.execute("SELECT * FROM items WHERE file != ''"))
    username = db.execute("SELECT username FROM users WHERE id = ?", session["user_id"])[0]
    return render_template("index.html", table=table, username=username)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy selected item"""

    if request.method == "POST":

        creditcard = str(request.form.get("card"))
        rows = db.execute("SELECT * FROM users WHERE id = ?", session["user_id"])

        # Check password is correct
        if not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("incorrect password", 403)

        # Check if credit card is valid i.e. 4003600000000014 with Luhn's algorithm
        if not cc_validate(creditcard):
            return apology("invalid creditcard", 403)

        # Update "past" and "items" databases - by inserting into "past" and deleting item from "items" 
        item_id = request.form.get("item_id")
        
        table = db.execute("SELECT * FROM items WHERE id = ?", item_id)[0]
        file = table["file"]
        name = table["name"]
        desc = table["description"]
        price = table["price"]
        category = table["category"]
        db.execute("INSERT INTO past (person_id, file, name, description, price, category) VALUES (?, ?, ?, ?, ?, ?)", session["user_id"], file, name, desc, price, category)

        db.execute("DELETE FROM items WHERE id = ?", item_id)
        return redirect("/")        
    else:
        item_id = request.args.get("item_id")
        currentItem = db.execute("SELECT * FROM items WHERE id = ?", item_id)[0]
        value = currentItem["file"].decode()
        currentItem["file"] = value
        return render_template("buy.html", value=value, currentItem=currentItem)


@app.route("/yourlistings")
@login_required
def yourlistings():
    """Show your current listings"""
    
    # Queries for all the past items listed for selling and passes it to the html file
    yourlistings = decode(db.execute("SELECT * FROM items WHERE person_id = ?", session["user_id"]))
    return render_template("yourlistings.html", yourlistings=yourlistings)

@app.route("/yourpurchases")
@login_required
def yourpurchases():
    """Show your past purchases"""

    # Queries for all the transactions and passes it to the html file, where it is displayed
    yourpurchases = decode(db.execute("SELECT * FROM past WHERE person_id = ?", session["user_id"]))
    return render_template("yourpurchases.html", yourpurchases=yourpurchases)

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
    """Register user"""

    if request.method == "POST":

        # Filters for username and password to ensure it exists and matches confirmation, respectively
        if not request.form.get("username"):
            return apology("must provide username", 400)
        rows = db.execute("SELECT username FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) != 0:
            return apology("username taken", 400)
        if not request.form.get("password"):
            return apology("must provide password", 400)
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must match", 400)

        # Stores the username and generates password hash, then adds it to database, storing id as session
        username = request.form.get("username")
        passwordHash = generate_password_hash(request.form.get("password"))
        key = db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, passwordHash)
        session["user_id"] = key
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell something"""

    if request.method == "POST":
        # checks that all fields are filled
        if not request.files.get("img") or not request.form.get("name") or not request.form.get("desc") or not request.form.get("price") or not request.form.get("category"):
            return apology("must fill all fields", 400)

        # Updates items table with new item
        imagefile = request.files.get("img")
        data = imagefile.read()
        render_pic = base64.b64encode(data)
        name = request.form.get("name")
        desc = request.form.get("desc")
        price = request.form.get("price")
        category = request.form.get("category")
        db.execute("INSERT INTO items (person_id, file, name, description, price, category) VALUES (?, ?, ?, ?, ?, ?)", session["user_id"], render_pic, name, desc, price, category)
        return redirect("/")
    else:
        return render_template("sell.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Imports datetime in order to track date and time of transactions
import datetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///hmart.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


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
    """Show portfolio of stocks"""

    # Queries for current cash to display directly to users below list of stocks
    cash = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])

    # Queries for current cash in order add values of stock to it to find total value
    cashCurrent = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
    totalCurrent = cashCurrent[0]

    # Finds each non-dupilicate stock, sums their shares, and finds the total value of each stock owned
    stocks = []
    total = db.execute("SELECT symbol, name, SUM(shares) FROM stocks WHERE userid = ? GROUP BY symbol", session["user_id"])
    for i in range(len(total)):
        currentPrice = lookup(total[i]["symbol"])["price"]
        totalValue = currentPrice * total[i]["SUM(shares)"]
        dict = {"symbol": total[i]["symbol"], "name": total[i]["name"], "shares": total[i]
                ["SUM(shares)"], "price": currentPrice, "TOTAL": totalValue}
        stocks.append(dict)
        currentTotal = totalCurrent["cash"] + totalValue
        totalCurrent.update({"cash": currentTotal})
    
    return render_template("index.html", stocks=stocks, cash=cash, total=totalCurrent)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    if request.method == "POST":

        # Filters for getting allowed number of stocks to buy
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)
        symbol = request.form.get("symbol")
        if lookup(symbol) == None:
            return apology("invalid symbol", 400)
        shares = request.form.get("shares")
        try:
            float(shares)
        except:
            return apology("shares must be numbers", 400)
        if float(shares).is_integer() == False or float(shares) <= 0:
            return apology("shares must be positive integers", 400)
        
        # Lookups the all the current info about the stock user wants to buy and inserts the data into the stocks table tagged with user's id
        dict = lookup(symbol)
        name = dict["name"]
        price = dict["price"]
        symbolCap = dict["symbol"]
        userid = session["user_id"]
        time = datetime.datetime.now()
        cashCurrent = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        total = price * float(shares)
        cashRemaining = cashCurrent[0]["cash"] - total
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cashRemaining, session["user_id"])

        # Only inserts into table if the user has enough cash available
        if cashRemaining >= 0:
            db.execute("INSERT INTO stocks (symbol, name, shares, price, TOTAL, userid, datetime) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       symbolCap, name, float(shares), price, total, userid, time)
            return redirect("/")
        else:
            return apology("not enough cash", 400)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Queries for all the transactions and passes it onto the html file, where it is displayed
    history = db.execute("SELECT symbol, shares, price, datetime FROM stocks WHERE userid = ?", session["user_id"])
    return render_template("history.html", history=history)


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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    
    if request.method == "POST":

        # Checks for if the symbol exists and passes on the stock's info to html file
        symbol = request.form.get("symbol")
        if lookup(symbol) == None:
            return apology("invalid symbol", 400)
        dict = lookup(symbol)
        return render_template("quoted.html", name=dict["name"], price=dict["price"], symbol=dict["symbol"])
    else:
        return render_template("quote.html")


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
    """Sell shares of stock"""

    if request.method == "POST":

        # Filters for getting allowed number of stocks to sell
        if not request.form.get("symbol"):
            return apology("must provide symbol", 400)
        symbol = request.form.get("symbol")
        sumShares = db.execute("SELECT SUM(shares) FROM stocks WHERE userid = ? AND symbol = ? GROUP BY symbol",
                               session["user_id"], symbol)
        if sumShares[0]["SUM(shares)"] < 0:
            return apology("no shares of stock", 400)
        shares = int(request.form.get("shares"))
        if shares <= 0:
            return apology("must sell positive shares", 400)
        if shares > sumShares[0]["SUM(shares)"]:
            return apology("selected too many shares", 400)

        # Looks up all the info for the stock user wants to sell
        dict = lookup(symbol)
        symbolCap = dict["symbol"]
        name = dict["name"]
        sharesNeg = -1 * shares
        price = dict["price"]
        userid = session["user_id"]
        time = datetime.datetime.now()
        total = price * shares

        # Inserts into the stock table the negative value of shares wanting to be sold
        db.execute("INSERT INTO stocks (symbol, name, shares, price, TOTAL, userid, datetime) VALUES (?, ?, ?, ?, ?, ?, ?)",
                   symbolCap, name, sharesNeg, price, total, userid, time)
        
        # Updates users cash to correctly reflect the amount of money made by selling stock
        cashEarned = shares * price
        cashCurrent = db.execute("SELECT cash FROM users WHERE id = ?", session["user_id"])
        cashNew = cashCurrent[0]["cash"] + cashEarned
        db.execute("UPDATE users SET cash = ? WHERE id = ?", cashNew, session["user_id"])
        return redirect("/")
    else:
        
        # Passes on info on stocks user currently owns to the html file, where dropdown displays these stocks
        symbols = db.execute("SELECT symbol FROM stocks WHERE userid = ? GROUP BY symbol", session["user_id"])
        return render_template("sell.html", symbols=symbols)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
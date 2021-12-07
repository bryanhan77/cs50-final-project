import os
import requests
import urllib.parse
import math

from flask import redirect, render_template, request, session
from functools import wraps
from cs50 import get_int

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


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

def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"

# Validate card with Luhn's algorithm
def cc_validate(card):
    # Ask for number and convert to string
    card = str(card)
    digits = len(card)
    total = 0
    for i in range(digits):
        if i % 2 == 0:
            total = total + int(card[digits - 1 - i])
        else:
            total = total + math.floor((2 * int(card[digits - 1 - i])) / 10) + (2 * int(card[digits - 1 - i])) % 10

    front = int(card[0]) * 10 + int(card[1])  # That is, front two numbers
    if total % 10 == 0:
        if digits == 15 and (front == 34 or front == 37): # AMEX
            return True
        elif (digits == 13 or digits == 16) and int(card[0]) == 4: # VISA
            return True
        elif (digits == 16 and (front > 50 or front < 56)): # Mastercard
            return True
        else:
            return False
    else:
        return False

    
# Decode SQL table image files so that it is renderable in the html files.
# decode() takes in an array of dits where each dict represents an item. 
def decode(table):
    decoded = [] # holds decoded png files 
    for row in table:
        decoded.append(row["file"].decode())
    for count, value in enumerate(decoded):
        table[count]["file"] = value
    return table


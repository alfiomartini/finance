import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session, url_for
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """

        # this replacement is needed because certain  characters
        #  have a special meaning the interpretation of an URL by the browser.
        # Thus, these special characters need to be replaced in the sequence s, 
        # and thus have their special meaning 'escaped', i.e., treated as simple
        # characters 
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.
    https://www.datacamp.com/community/tutorials/decorators-python
    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        print('entered login required')
        # We use session.get("user_id") to check if the key exists in the session.
        if session.get("user_id") is None:
            print('session user id is None')
            return redirect(url_for('login'))
        else:
             print('session user id', session['user_id'])
             return f(*args, **kwargs)
    return wrapper


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("FINANCE_KEY")
        response = requests.get(f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        # response is a json object. json() is a json decoder, i.e,
        # maps json back to object format
        # see https://requests.readthedocs.io/en/master/user/quickstart/
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


def usd(value):
    """Format value as USD."""
     # https://realpython.com/python-f-strings/
    # https://www.w3schools.com/python/ref_string_format.asp
    # use comma as a thousand separator
    # 2 digits after the decimal point
    float_str = "${:,.2f}".format(value)
    return float_str

# https://iexcloud.io/docs/api/#historical-prices
def chart_data(symbol, range):
    # accepted range string values : '1m', '6m', '5d'

    # Contact API
    try:
        api_key = os.environ.get("FINANCE_KEY")
        json_response = requests.get(f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/chart/{range}?token={api_key}")
        json_response.raise_for_status()
    except requests.RequestException:
        return None
    else:
        # response is in json notation. json() is a json decoder, i.e,
        # maps json back to object format
        # see https://requests.readthedocs.io/en/master/user/quickstart/
        return json_response

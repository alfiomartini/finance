import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
# Whether to check for modifications of the template source and reload it automatically.
# By default the value is None which means that Flask checks original file only in debug mode.
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
# see https://roadmap.sh/guides/http-caching
# see https://pythonise.com/series/learning-flask/python-before-after-request
@app.after_request
def after_request(response):
    # Cache-Control specifies how long and in what manner should the content be cached. 
    # no-store specifies that the content is not to be cached by any of the caches
    # (public, private, server)
    # must-revalidate avoids that. If this directive is present, it means that stale content 
    # cannot be served in any case and the data must be re-validated from the server before serving.
    # no-cache indicates that the cache can be maintained but the cached content is to be re-validated 
    # (using ETag for example) from the server before being served. 
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    # how long a cache content should be considered fresh? never.
    response.headers["Expires"] = 0
    # stops the response from being cached. It might not necessarily work.
    # Pre HTPP/1.1
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters['usd'] = usd

# Configure session to use local filesystem (instead of signed cookies)
# mkdtemp() creates a temporary directory in the most secure manner possible. 
# There are no race conditions in the directory’s creation. The directory is 
# readable, writable, and searchable only by the creating user ID.
# The user of mkdtemp() is responsible for deleting the temporary directory and its 
# contents when done with it.

app.config["SESSION_FILE_DIR"] = mkdtemp()
# session is cleared after exiting the browser
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# enables foreign key constraints at runtime
#db.execute('PRAGMA foreign_keys = ON')

# Make sure API key is set
# set API_KEY=pk_01aaacabc1964f3690742bddf2c3695d
# list keys: set
# pk_01aaacabc1964f3690742bddf2c3695d
if not os.environ.get("FINANCE_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # a list of dictionaries
    summary = []
    # balance (stocks total value + chas)
    sum = 0
    # query database 
    # each row has the total number of shares for each symbol 
    rows = db.execute('''select symbol, sum(number) as shares from transactions
                         where id = ? 
                         group by symbol''', (session['user_id'],))
    user = db.execute('select * from users where id = ?', (session['user_id'],))
    for row in rows:
        dict = {}
         
        # get object from iex cloud
        symbol_data = lookup(row['symbol'])
        # build dictionary
        dict['symbol'] = symbol_data['symbol']
        dict['name'] = symbol_data['name']
        dict['shares'] = row['shares']
        # get  the latest price
        dict['price'] = symbol_data['price']
        dict['total'] = dict['price'] * dict['shares']
        # total value of shares  in dollars
        sum += dict['total']
        # update list of data
        summary.append(dict)
    cash = user[0]['cash']
    sum += cash
    return render_template('summary.html', rows = summary, cash=cash, sum=sum)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    # queryes data base for the symbols of the companies's shares for each user
    colSymb = db.execute('select symbol from transactions where id = ? group by symbol',
                              (session['user_id'],))
    # refine into a known list of symbols to be used as a context menu in the template
    listSymb = list(map(lambda x: x['symbol'], colSymb))
    if request.method == 'POST':
        symbol = request.form.get('symbol').upper()
        data = lookup(symbol)
        if data == None:
            return apology('Unknown symbol.', 404)
        # latest price
        price = data['price']
        shares = int(request.form.get('shares'))
        if shares < 0:
            return apology('You must provide a positive number.', 400)
        row = db.execute('select * from users where id = ?', session['user_id'])
        cash = row[0]['cash']
        shares_value = shares * price
        if (cash - shares_value) < 0 :
            return apology("You can't afford this buy at current price", 400)
        new_cash = cash - shares_value
        db.execute('update users set cash = ? where id = ?', 
                    new_cash, session['user_id'])
        db.execute('''insert into transactions(id, symbol, number, type, price) 
                    values(?,?,?,'bought', ?)''', 
                    session['user_id'], symbol, shares, price)
        flash('Bought!')
        return redirect('/')
    else:
        return render_template('buy.html', symbols = listSymb)


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    # query database and build a list of known symbols for a context menu
    colSymb = db.execute('select symbol from transactions where id = ? group by symbol',
                              (session['user_id'],))
    listSymb = list(map(lambda x: x['symbol'], colSymb))
    if request.method == 'POST':
        symbol = request.form.get('symbol').upper()
        data = lookup(symbol)
        # if data == None:
            #return apology('Unknown symbol.', 404)
        shares = int(request.form.get('shares'))
        if shares < 0:
            return apology('You must provide a positive number.', 400)
        if symbol not in listSymb:
            return apology('You do not own shares of this company.')
        # get the latest price
        price = data['price']
        rowSymb = db.execute('''select symbol, sum(number) as shares 
                              from transactions where id = ? group by symbol
                              having symbol = ?''', session['user_id'],symbol)
        sharesSymb = rowSymb[0]['shares']
        if shares > sharesSymb:
            return apology("You can't buy that many shares.", 400)
        user = db.execute('select * from users where id = ?', session['user_id'])
        cash = user[0]['cash']
        shares_value = shares * price
        new_cash = cash  + shares_value
        db.execute('update users set cash = ? where id = ?', new_cash, session['user_id'])
        db.execute('''insert into transactions(id, symbol, number, type, price) 
                       values(?,?,?, 'sold', ?)''',
                       session['user_id'], symbol, -shares, price)
        flash('Sold!')
        return redirect('/')
    else:
        return render_template('sell.html', symbols=listSymb)

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # list of dictionaries
    history = []
    rows = db.execute('''select symbol, number, price, datetime(date,'localtime') as loc_date
                         from transactions 
                         where id = ? 
                         order by loc_date''', (session['user_id'],))
    for row in rows:
        dict = {}
        dict['symbol'] = row['symbol']
        dict['shares'] = row['number']
        # Get the price at the time of the transaction
        dict['price'] = row['price']
        dict['date'] = row['loc_date']
        history.append(dict)

    return render_template('history.html', rows = history)


@app.route("/quote/<int:quote_id>", methods=["GET"])
@login_required
def quote(quote_id):
    # 0 indicates that the page was called from the navbar
    # there is no company with id 0 in the database.
    if quote_id == 0:
        return render_template('quote.html')
    else:
        row = db.execute('select * from companies where id = ?',(quote_id,))
        print(row)
        if row:
            return render_template('quote_result.html', company=row[0])
        else:
            print('No rows')
            return ""


# Utilities routes

# this route is requested during register to validate a new user. 
@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    name = request.args.get('username')
    if len(name) < 1:
        return jsonify(False)
    # query database to see if there are any row with this username
    row = db.execute("select * from users where username = ?", (name,))
    if len(row) == 0:
        avail = True
    else:
        avail = False
    return jsonify(avail)

@app.route("/search/<string:query>")
def search(query):
    # take care of upper and lower case
    query = query.lower() + '%'
    companies = db.execute("""select * from companies
                             where lower(name) like  ?
                             or lower(symbol) like ?
                             order by symbol""", (query,query))
    html = render_template("search.html", companies=companies)
    return html


# Authentication Routes

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("You must provide a username.", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("You must provide a password.", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], 
                                   request.form.get("password")):
            return apology("Invalid username and/or password", 403)

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
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            return apology("You must provide a user name.", 403)
        row = db.execute("select * from users where username = ?", (username,))
        if len(row) == 1:
            return apology('This user is already registered.', 403)
         # just to make it sure. It could never happen
        elif len(row) > 1:
            return apology('Duplicates in the database', 403) # code? 
        password = request.form.get('password')
        if not password:
            return apology("You must provide a passord", 403)
        confirmation = request.form.get('confirmation')
        if not confirmation:
            return apology("You must confirm your passord.", 403)
        hash_passw = generate_password_hash(password)
        if not check_password_hash(hash_passw, confirmation):
            return apology('Passwords do not match.', 403)
        else:
            db.execute('insert into users(username, hash) values(?,?)', 
                           username, hash_passw)
            flash("You are registered.")
            return render_template('registered.html')
    else:
        return render_template('register.html')


@app.route('/change', methods=['GET', 'POST'])
@login_required
def change():
    if request.method == 'POST':
        # access post parameters
        old = request.form.get('oldpassword')
        new = request.form.get('newpassword')
        conf = request.form.get('confirmation')
        # see if new and confirmation password match
        if new != conf:
            return apology("New passord and confirmation don't match.", 403)
        # query database to access user data
        row = db.execute("select * from users where id = ?", 
              (session['user_id'],))
        oldhash = row[0]['hash']
        if not check_password_hash(oldhash, old):
            return apology('Current password is wrong.', 403)
        newhash = generate_password_hash(new)
        # update database with new user password 
        db.execute('update users set hash = ? where id = ?',
                    (newhash, session['user_id'],))
        return redirect('/logout')
    else:
        return render_template('change.html')


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == '__main__':
    app.run(debug=True)

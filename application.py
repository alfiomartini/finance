import os
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask import url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from helpers import apology, login_required, lookup, usd, chart_data

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

# app.config["SESSION_FILE_DIR"] = mkdtemp()
# session is cleared after exiting the browser
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
# list keys: set
if not os.environ.get("FINANCE_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    summary = []
    sum = 0
    # query database 
    # each row has the total number of shares for each symbol 
    rows = db.execute('''select symbol, sum(number) as shares from transactions
                         where id = ? 
                         group by symbol''', (session['user_id'],))
    user = db.execute('select * from users where id = ?', (session['user_id'],))
    print('user', user)
    for row in rows:
        dict = {}
         
        # get object from iex cloud
        symbol_data = lookup(row['symbol'])
        # print('symbol data', symbol_data)
        if 'price' in symbol_data:
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
        else:
            message = 'Sorry, there was a problem with your request. Try again.'
            return render_template('failure.html', message=message)
    cash = user[0]['cash']
    print('printing summary now')
    return render_template('summary.html', rows = summary, cash=cash, sum=sum)


@app.route("/buy", methods=["GET", "POST"])
@app.route("/buy/<string:symbol>", methods=['GET'])
@login_required
def buy(symbol=None):
    """Buy shares of stock"""
    # queryes data base for the symbols of the companies's shares for each user
    companies = db.execute('select * from companies order by symbol')
    # refine into a known list of symbols to be used as a context menu in the template
    if request.method == 'POST':
        symbol = request.form.get('symbol').upper()
        data = lookup(symbol)
        if data == None:
            return render_template('failure.html', message='Unknown symbol.')
        # latest price
        price = data['price']
        shares = int(request.form.get('shares'))
        if shares < 0:
            return render_template('failure', message='You must provide a positive number.')
        row = db.execute('select * from users where id = ?', (session['user_id'],))
        cash = row[0]['cash']
        shares_value = shares * price
        if (cash - shares_value) < 0 :
            return render_template('failure.html', message="You can't afford this buy at current price")
        new_cash = cash - shares_value
        db.execute('update users set cash = ? where id = ?', 
                    new_cash, session['user_id'])
        db.execute('''insert into transactions(id, symbol, number, type, price) 
                    values(?,?,?,'bought', ?)''', 
                    session['user_id'], symbol, shares, price)
        flash('Bought!')
        return redirect(url_for('index'))
    else:
        if not symbol:
            symbol = 'unknown'
        return render_template('buy.html', companies = companies, symbol=symbol)


@app.route("/sell", methods=["GET", "POST"])
@app.route("/sell/<string:symbol>", methods=['GET'])
@login_required
def sell(symbol = None):
    # query database and build a list of known symbols for a context menu
    sold_symbols = db.execute('select symbol from transactions where id = ? group by symbol',
                              (session['user_id'],))
    
    listSymb = list(map(lambda x: x['symbol'], sold_symbols))
    if request.method == 'POST':
        symbol = request.form.get('symbol').upper()
        data = lookup(symbol)
        if data == None:
            return render_template('failure.html', message='Unknown symbol.')
        shares = int(request.form.get('shares'))
        if shares < 0:
            return render_template('failure.html', message ='You must provide a positive number.')
        if symbol not in listSymb:
            return render_template('failure.html', message='You do not own shares of this company.')
        # get the latest price
        price = data['price']
        rowSymb = db.execute('''select symbol, sum(number) as shares 
                              from transactions where id = ? group by symbol
                              having symbol = ?''', session['user_id'],symbol)
        sharesSymb = rowSymb[0]['shares']
        if shares > sharesSymb:
            return render_template('failure.html', message="You can't buy that many shares.")
        user = db.execute('select * from users where id = ?', (session['user_id'],))
        cash = user[0]['cash']
        shares_value = shares * price
        new_cash = cash  + shares_value
        db.execute('update users set cash = ? where id = ?', new_cash, session['user_id'])
        db.execute('''insert into transactions(id, symbol, number, type, price) 
                       values(?,?,?, 'sold', ?)''',
                       session['user_id'], symbol, -shares, price)
        flash('Sold!')
        return redirect(url_for('index'))
    else:
        if not symbol:
            symbol = 'unknown'
        return render_template('sell.html', symbols=listSymb, symbol=symbol)

@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    
    history = []
    rows = db.execute('''select symbol, number, price, datetime(date,'localtime') as loc_date
                         from transactions 
                         where id = ? 
                         order by loc_date desc''', (session['user_id'],))
    for row in rows:
        dict = {}
        dict['symbol'] = row['symbol']
        dict['shares'] = row['number']
        # Get the price at the time of the transaction
        dict['price'] = row['price']
        dict['date'] = row['loc_date']
        history.append(dict)

    return render_template('history.html', rows = history)

@app.route("/quote", methods =["GET","POST"])
@app.route("/quote/<int:quote_id>", methods=["GET"])
@login_required
def quote(quote_id = None):
    if request.method == 'POST':
        symbol = request.form.get('symbol').upper()
        data = lookup(symbol)
        if data == None:
            return render_template('failure.html', message='Unknown symbol.')
        else:
            return render_template('quoted.html', data=data)
    else:
        if not quote_id:
            return render_template('quote.html')
        else:
            row = db.execute('select * from companies where id = ?',(quote_id,))
            print(row)
            if row:
                return render_template('quote_result.html', company=row[0])
            else:
                # print('No rows')
                return render_template('failure.html', 
                       message='Sorry, this company does not exist.')
      
@app.route('/add', methods=['GET','POST'])
@login_required
def add():
    if request.method == 'POST':
        amount = int(request.form.get('cash'))
        row = db.execute('select * from users where id = ?', (session['user_id'],))
        current = row[0]['cash']
        new_cash = current + amount
        db.execute('update users set cash = ? where id = ?', new_cash, session['user_id'])
        return redirect(url_for('index'))
    else:
        return render_template('add.html')

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
@login_required
def search(query):
    # take care of upper and lower case
    query = query.lower() + '%'
    companies = db.execute("""select * from companies
                             where lower(name) like  ?
                             or lower(symbol) like ?
                             order by symbol""", (query,query))
    html = render_template("search.html", companies=companies)
    return html


@app.route('/chart', methods = ['GET'])
@app.route('/chart/<string:symbol>/<string:range>', methods=['GET'])
@login_required
def chart(symbol=None, range=None):
    if symbol and range:
       json_resp = chart_data(symbol, range)
       if json_resp:
            # maps a json string to a python object
            json_obj = json_resp.json()
            chart = {}
            labels = []
            data = []
            for item in json_obj:
                # transforms a date string to a date object
                date = datetime.strptime(item['date'], '%Y-%m-%d')
                # transforms a date object to a date string
                date_str = date.strftime('%m/%d')
                labels.append(date_str)
                data.append(item['close'])
            chart['labels'] = labels
            chart['data'] = data
            chart['symbol'] = symbol
            return jsonify(chart)
       else:
           return jsonify({})
    else:
        return render_template('chart.html')


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
            return render_template('failure.html', message="You must provide a username.")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template('failure.html', message="You must provide a password.")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], 
                                   request.form.get("password")):
            return render_template('failure.html', message="Invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
    
        return redirect(url_for('index'))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect(url_for('index'))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            return render_template('failure.html', message="You must provide a user name.")
        row = db.execute("select * from users where username = ?", (username,))
        if len(row) == 1:
            return render_template('failure.html', message='This user is already registered.')
         # just to make it sure. It could never happen
        elif len(row) > 1:
            return render_template('failure.html', message='Duplicates in the database') 
        password = request.form.get('password')
        if not password:
            return render_template('failure.html', message="You must provide a passord")
        confirmation = request.form.get('confirmation')
        if not confirmation:
            return render_template('failure.html', message="You must confirm your passord.")
        hash_passw = generate_password_hash(password)
        if not check_password_hash(hash_passw, confirmation):
            return render_template('failure.html', message='Passwords do not match.')
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
            return render_template('failure.html', messahe="New passord and confirmation don't match.")
        # query database to access user data
        row = db.execute("select * from users where id = ?", 
              (session['user_id'],))
        oldhash = row[0]['hash']
        if not check_password_hash(oldhash, old):
            return render_template('failure.html', message='Current password is wrong.')
        newhash = generate_password_hash(new)
        # update database with new user password 
        db.execute('update users set hash = ? where id = ?',
                    (newhash, session['user_id'],))
        return redirect(url_for('logout'))
    else:
        return render_template('change.html')


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return render_template('failure.html', message= f"{e.name}, {e.code}")


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

if __name__ == '__main__':
    app.run(debug=False)

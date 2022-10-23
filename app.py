from flask import Flask, request, session, redirect, url_for, render_template, flash
import psycopg2  # pip install psycopg2
import psycopg2.extras
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'cairocoders-ednalan'

DB_HOST = "127.0.0.1"
DB_NAME = "flask"
DB_USER = "postgres"
DB_PASS = "1234"

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)


@app.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)

        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()

        if account:
            password_rs = account['password']
            print(password_rs)
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                # Account doesnt exist or username/password incorrect
                flash('Incorrect username/password')
        else:
            # Account doesnt exist or username/password incorrect
            flash('Incorrect username/password')

    return render_template('login.html')


@app.route('/register/', methods=['GET', 'POST'])
def register():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        _hashed_password = generate_password_hash(password)

        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)
        # If account exists show error and validation checks
        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not username or not password or not email:
            flash('Please fill out the form!')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute("INSERT INTO users (fullname, username, password, email) VALUES (%s,%s,%s,%s)",
                           (fullname, username, _hashed_password, email))
            conn.commit()
            flash('You have successfully registered!')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash('Please fill out the form!')
    # Show registration form with message (if any)
    return render_template('register.html')


@app.route('/logout/')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('login'))

@app.route("/write-blog/", methods=["GET", "POST"])
def write_blog():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == "POST":
        blogpost = request.form
        title = blogpost["title"]
        body = blogpost["body"]
        author = session["Name"]
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO blog (title, body, author) VALUES (%s, %s, %s)",
            (title, body, author),
        )
        conn.commit()
        cursor.close()
        flash("Your blogpost is successfully posted!", "success")
        return redirect("/")
    return render_template("write-blog.html")


"""@app.route('/write-blog/')
def write_blog():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Check if user is loggedin
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM blog WHERE blog_id = %s', [session['id']])
        
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('write-blog.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))
"""
@app.route('/my-blogs/')
def my_blogs():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        my_blogs = cursor.fetchone()
        return render_template('my-blogs.html', my_blogs=my_blogs)
    return redirect(url_for('my-blogs.html', my_blogs = my_blogs))




@app.route('/blogs/')
def blogs():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        blogs = cursor.fetchone()
        return render_template('blogs.html', blogs=blogs)
    return redirect(url_for('login') )

@app.route('/edit-blog/')
def edit_blog():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Check if user is loggedin
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('edit-blog.html', account=account)

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/profile/')
def profile():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Check if user is loggedin
    if 'loggedin' in session:
        cursor.execute('SELECT * FROM users WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route("/delete-blog/<int:id>")
def delete_blog(id):
    cursor = conn.cursor (cursor_factory=psycopg2.extras.DictCursor)
    if 'loggedin' in session:
        cursor.execute("DELETE FROM blog WHERE blog_id = {}".format('id'))
        conn.commit()
    flash("Your blog has been deleted!", "success")
    return redirect("/my-blogs")



if __name__ == "__main__":
    app.run(debug=True)
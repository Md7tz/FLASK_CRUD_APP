from flask import Flask, flash, render_template, redirect, url_for, session, request, logging
from flask_mysqldb import MySQL
from forms import RegisterForm, LoginForm, ArticleForm
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = '1314afasf'

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'swift'
app.config['MYSQL_DB'] = 'swiftcrudapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# Check if user logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('.login'))
        return f(*args, **kwargs)
    return decorated_function

# Home
@app.route('/')
def index():
    return render_template('home.html')

# About
@app.route('/about')
def about():
    return render_template('about.html')

# Articles
@app.route('/articles')
def articles():
    # Create Cursor
    curs = mysql.connection.cursor()

    # Check if there is data
    result = curs.execute("SELECT * FROM articles;")

    # Get articles 
    articles = curs.fetchall()
    
    # Close cursor
    curs.close()

    if result > 0:
        return render_template('articles.html', articles=articles)
    else: 
        msg = 'No Articles Found'
        return render_template('articles.html', msg=msg)

# Single articles
@app.route('/articles/<string:id>')
def article(id):
    # Create Cursor
    curs = mysql.connection.cursor()

    # fetch article by id
    curs.execute('SELECT * FROM articles WHERE id = %s;', [id])
    article = curs.fetchone()

    return render_template('article.html', article=article)

# User Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)

    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = generate_password_hash(form.password.data, 'sha256')

        # Create cursor
        cur = mysql.connection.cursor()

        # Execute query
        cur.execute('INSERT INTO users(name, email, username, password) VALUES (%s, %s, %s, %s);', (name, email, username, password))

        # Commit
        mysql.connection.commit()

        # close cursor
        cur.close()

        flash('You are now registered and can login', 'success')
        return redirect(url_for('.index'))
    return render_template('auth/register.html', form=form)

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST' and form.validate():
        # Get Form fields
        username = form.username.data
        password_candidate = form.password.data

        # Create cursor
        cur = mysql.connection.cursor()

        # Check if rows is effected
        result = cur.execute('SELECT * FROM users WHERE users.username = %s;', [username])

        if result > 0:
            # Get stored row of data
            data = cur.fetchone()

            # Get Stored hash
            password = data['password']

            # close cursor
            cur.close()

            # compare passwords
            if check_password_hash(password, password_candidate):
                session['logged_in'] = True
                session['username'] = data['username']
                session['name'] = data['name']

                flash('You are now logged in', 'success')
                return redirect(url_for('.dashboard'))
            else:
                error = "The password that you've entered is incorrect."
                return render_template('auth/login.html', error=error)
        else:
            error = 'Username not found'
            return render_template('auth/login.html', error=error)
    return render_template('auth/login.html')

# Dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    # Create cursor
    cur = mysql.connection.cursor()

    # check if there is results
    result = cur.execute('SELECT * FROM articles;')

    # Get articles
    articles = cur.fetchall()

    # Close cursor
    cur.close()

    if result > 0:
        return render_template('dashboard.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg=msg) 

# Add Article
@app.route('/add_article', methods=['GET', 'POST'])
@login_required
def add_article():
    form = ArticleForm(request.form)

    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        
        # Create cursor
        cur = mysql.connection.cursor()

        # Insert data
        cur.execute('INSERT INTO articles(title, body, author) VALUES(%s, %s, %s);', (title, body, session['username']))

        # Commit
        mysql.connection.commit()

        # close cursor
        cur.close()

        flash('Article Created', 'success')
        return redirect(url_for('.dashboard'))
    return render_template('add_article.html', form=form)

# Edit Article
@app.route('/edit_article/<string:id>', methods=['GET','POST'])
@login_required
def edit_article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # Get article by id
    cur.execute('SELECT * FROM articles WHERE id = %s', [id])
    article = cur.fetchone()

    # Create form
    form = ArticleForm(request.form)

    # populate fields
    form.title.data = article['title'] 
    form.body.data = article['body']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']

        # Update table
        cur.execute('UPDATE articles SET title = %s, body = %s WHERE id = %s', (title, body, id))

        # Commit
        mysql.connection.commit()

        # close cursor
        cur.close()

        flash(f'Article {id} Updated', 'success')
        return redirect(url_for('.dashboard'))
    return render_template('edit_article.html', form=form)
    
# Delete Article
@app.route('/delete_article/<string:id>', methods=['POST'])
@login_required
def delete_article(id):
    # Create cursor
    cur = mysql.connection.cursor()

    # delete data
    cur.execute('DELETE FROM articles WHERE id = %s', [id])

    # Commit
    mysql.connection.commit()

    # close cursor
    cur.close()

    flash('Article Deleted', 'success')
    return redirect(url_for('.dashboard'))

# Logout
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('.login'))

if __name__ == '__main__':
    app.run(debug=True)
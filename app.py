from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import date
from datetime import time
from datetime import datetime


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://flask-blog:password@localhost:8889/flask-blog'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = '2d9b6941f4497350b2d8c7ae1321a312'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

now = datetime.now()

current_year = now.strftime("%Y")
current_day = now.strftime("%a %B %d, %Y")
current_time = now.strftime("%X")

## Create Global Variables ###
@app.context_processor
def context_processor():
    return dict(current_year=current_year, current_day=current_day, current_time=current_time)


# posts = [
#     {
#         'author': 'Reginald Beninche',
#         'title': 'Blog Post 1',
#         'content': 'First post content',
#         'date_posted': 'November 28th, 2018'
#     },
#     {
#         'author': 'Naromie Simeon',
#         'title': 'Blog Post 2',
#         'content': 'Second post content',
#         'date_posted': 'April 15th, 2019'
#     }
# ]

class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    post_title = db.Column(db.String(120))
    post_body = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now)
    subscriber_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, post_title, post_body, subscriber):
        self.post_title = post_title
        self.post_body = post_body
        self.subscriber = subscriber


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    posts = db.relationship('Post', backref='subscriber')

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password = password


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


# @app.route("/")
# def display_form():
#     posts = Post.query.order_by(Post.date_posted.desc())
#     return render_template('blogs.html', posts=posts)


@app.route("/login", methods=["GET", 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            return redirect(url_for('display_blogs'))
        else:
            return '<h1>Error!</h1>'

    return render_template('login.html')


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['password-confirm']
        username_error = ''
        email_error = ''
        password_error = ''
        confirm_password_error = ''

        # Username validation

        if username == '':
            username_error = "Username cannot be left empty"
        elif len(username) < 3:
            username_error = "Username cannot be less than 3 characters"
        elif len(username) > 20:
            username_error = "Username cannot be more than 20 characters"
        elif ' ' in username:
            username_error = "Username contains space"
        # End of Username validation

        # Email validation

        if email == '':
            email_error = "Email cannot be left empty"
        elif "@" not in email:
            email_error = "Email does not have '@'"
        elif "." not in email:
            email_error = "email does not contain any '. (Period)'"
        elif ' ' in email:
            email_error = "email contains space"
        elif len(email) < 3:
            username_error = "Email cannot have less than 3 characters"
        elif len(email) > 20:
            username_error = "Email cannot have more than 20 characters"
        # End of Email validation

        # Password validation

        if password == '':
            password_error = "Password field cannot be left empty"
        elif len(password) < 3:
            password_error = "Password cannot be less than 3 characters"
        elif len(password) > 20:
            password_error = "Password cannot be more than 20 characters"
        elif ' ' in password:
            password_error = "Password contains space"
        if not password_error:
            if confirm_password == '':
                confirm_password_error = "Please Confirm your password"
            elif confirm_password != password:
                confirm_password_error = "Password does not match"
        # End of Password validation

        if not username_error and not email_error and not password_error and not confirm_password_error:
            existing_user = User.query.filter_by(email=email).first()
            if not existing_user:
                new_user = User(email, username, password)
                db.session.add(new_user)
                db.session.commit()
                session['email'] = email
                return redirect('/thank_you?username=' + username)
            else:
                return "<h1>Duplicate User</h1>"
        else:
            return render_template('signup.html', username_error=username_error, email_error=email_error, password_error=password_error, confirm_password_error=confirm_password_error)
    else:
        return render_template('signup.html')


@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')


@app.route("/")
@app.route("/blogs")
def display_blogs():

    # posts = Post.query.all()
    posts = Post.query.order_by(Post.date_posted.desc())
    return render_template('blogs.html', posts=posts)


@app.route("/newpost", methods=['GET', 'POST'])
def add_new_post():

    if request.method == 'POST':
        post_title = request.form['title']
        post_body = request.form['body']
        post_title_error = ''
        post_body_error = ''
        if post_title == '':
            post_title_error = "Title cannot be left empty"
        if post_body == '':
            post_body_error = "Please type your post Here!"
        if not post_title_error and not post_body_error:
            subscriber = User.query.filter_by(email=session['email']).first()
            new_post = Post(post_title, post_body, subscriber)
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('display_blogs'))
        else:
            return render_template('newpost.html', post_title_error=post_title_error, post_body_error=post_body_error)
    else:
        return render_template('newpost.html')


@app.route("/thank_you")
def thank_you():
    username = request.args.get("username")
    return render_template('thankyou.html', username=username)


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('single-blog.html', post=post)


if __name__ == "__main__":
    app.run(debug=True)

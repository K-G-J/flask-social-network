from flask import (Flask, g, render_template, flash, redirect, url_for)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                         login_required)

import forms
import models

DEBUG = True
PORT = 8000
HOST = '127.0.0.1'

app = Flask(__name__)
app.secret_key = 'wghwuibjhyeweobsbaj153647!%##*&^#%'

login_manager = LoginManager()
login_manager.init_app(app)
# if not logged in, redirect to login view
login_manager.login_view = 'login'


# function to look up the user
@login_manager.user_loader
def load_user(userid):
    try:
        return models.User.get(models.User.id == userid)
    # if no record of user is in database return none
    except models.DoesNotExist:
        return None


@app.before_request
def before_request():
    """Connect to the database before each request."""
    # set up global variables to have available everywhere
    g.db = models.DATABASE
    # connect to database before every request
    g.db.connect()


@app.after_request
def after_request(response):
    """Close the database connection after each request."""
    g.db.close()
    return response


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.RegisterForm()
    if form.validate_on_submit():
        # add message category of success
        flash('Yay, you registered!', 'success')
        models.User.create_user(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        return redirect(url_for('index'))
    # if form data is invalid
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if form.validate_on_submit():
        try:
            user = models.User.get(models.User.email == form.email.data)
        except models.DoesNotExist:
            flash("Your email or password doesn't match!", 'error')
        else:
            if check_password_hash(user.password, form.password.data):
                # creates session of user's browser with cookie
                login_user(user)
                flash("You've been logged in!", 'success')
                return redirect(url_for('index'))
            else:
                # password check is incorrect
                flash("Your email or password doesn't match!", 'error')
    # if form data is invalid
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    # deletes cookie on user's browser
    logout_user()
    flash("You've been logged out! Come back soon!", 'success')
    return redirect(url_for('index'))


@app.route('/')
def index():
    return 'Hey'


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='kennethlove',
            email='kenneth@teamtreehouse.com',
            password='password',
            admin=True
        )
    except ValueError:
        pass
    app.run(debug=DEBUG, host=HOST, port=PORT)

from flask import (Flask, g, render_template, flash, redirect, url_for, abort)
from flask_bcrypt import check_password_hash
from flask_login import (LoginManager, login_user, logout_user,
                         login_required, current_user)

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
    # find current user
    g.user = current_user


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


@app.route('/new_post', methods=['GET', 'POST'])
@login_required
def post():
    form = forms.PostForm()
    if form.validate_on_submit():
        # get the global user
        models.Post.create(user=g.user._get_current_object(),
                           content=form.content.data.strip())
        flash('Message posted! Thanks!', 'success')
        return redirect(url_for('index'))
    return render_template('post.html', form=form)


@app.route('/')
def index():
    stream = models.Post.select().limit(100)
    return render_template('stream.html', stream=stream)


@app.route('/stream')
@app.route('/stream/<username>')
def stream(username=None):
    template = 'stream.html'
    # if username different than user in route render stream for that user
    if username and username != current_user.username:
        try:
            # find username is 'like' not case sensitive
            user = models.User.select().where(models.User.username**username).get()
        except models.DoesNotExist:
            # abort with error 404
            abort(404)
        else:
            stream = user.posts.limit(100)
    # render stream for current user
    else:
        stream = current_user.get_stream().limit(100)
        user = current_user
    # regardless, if username, set template to a user stream
    if username:
        template = 'user_stream.html'
    return render_template(template, stream=stream, user=user)


@app.route('/post/<int:post_id>')
def view_post(post_id):
    posts = models.Post.select().where(models.Post.id == post_id)
    if posts.count() == 0:
        # abort if the post does not exist
        abort(404)
    return render_template('stream.html', stream=posts)


@app.route('/follow/<username>')
@login_required
def follow(username):
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        abort(404)
    else:
        try:
            models.Relationship.create(
                from_user=g.user._get_current_object(),
                to_user=to_user
            )
        # cannot unfollow user twice
        except models.IntegrityError:
            abort(404)
        else:
            flash(f"You're now following {to_user.username}!", 'success')
    return redirect(url_for('stream', username=to_user.username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    try:
        to_user = models.User.get(models.User.username**username)
    except models.DoesNotExist:
        pass
    else:
        try:
            models.Relationship.get(
                from_user=g.user._get_current_object(),
                to_user=to_user
            ).delete_instance()
        # cannot follow user twice
        except models.IntegrityError:
            pass
        else:
            flash(f"You've unfollowed {to_user.username}!", 'success')
    return redirect(url_for('stream', username=to_user.username))


# renders view anytime a 404 is triggered
@app.errorhandler(404)
def not_found(error):
    # send back 404 status code
    return render_template('404.html'), 404


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

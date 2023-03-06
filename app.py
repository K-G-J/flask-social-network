from flask import Flask, g
from flask_login import LoginManager

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


if __name__ == '__main__':
    models.initialize()
    models.User.create_user(
        name='kennethlove',
        email='kenneth@teamtreehouse.com',
        passowrd='password',
        admin=True
    )
    app.run(debug=DEBUG, host=HOST, port=PORT)

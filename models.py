import datetime

from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import *


DATABASE = SqliteDatabase('social.db')


class User(UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        # view newest users first
        order_by = ('-joined_at',)

    # describes method that belongs to a class that can create the class it belongs to (cls = class), creates class instance before calling method
    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            # use cls instead of self to not have to create user instance first
            cls.create(username=username, email=email,
                       password=generate_password_hash(password), is_admin=admin)
        except IntegrityError:
            # raise error if not unique values
            raise ValueError('User already exists')


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User], safe=True)
    DATABASE.close()

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

    def get_posts(self):
        return Post.select().where(Post.user == self)

    def get_stream(self):
        return Post.select().where((Post.user == self))

    # describes method that belongs to a class that can create the class it belongs to (cls = class), creates class instance before calling method
    @classmethod
    def create_user(cls, username, email, password, admin=False):
        try:
            # remove creation if it does not go through
            with DATABASE.transaction():
                # use cls instead of self to not have to create user instance first
                cls.create(username=username, email=email,
                           password=generate_password_hash(password), is_admin=admin)
        except IntegrityError:
            # raise error if not unique values
            raise ValueError('User already exists')


class Post(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(
        # model key points to
        User,
        # what related model calls this model
        related_name='posts',
    )
    content = TextField()

    class Meta:
        database = DATABASE
        # has to be a tuple
        order_by = ('-timestamp',)


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Post], safe=True)
    DATABASE.close()

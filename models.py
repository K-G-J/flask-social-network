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
        return Post.select().where(
            # find all posts where the user is inside of the people user is following or where posts belong to user
            (Post.user << self.following()) |
            (Post.user == self)
        )

    def following(self):
        """The users that we are following."""
        return (
            # select all the relationships to user where from_user is self
            User.select().join(
                Relationship, on=Relationship.to_user
            ).where(
                Relationship.from_user == self
            )
        )

    def followers(self):
        """Get users following the current user."""
        return (
            # select all the relationships where to_user is self
            User.select().join(
                Relationship, on=Relationship.from_user
            ).where(
                Relationship.to_user == self
            )
        )

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


class Relationship(Model):
    # current user following
    from_user = ForeignKeyField(User, related_name='relationships')
    # users who follow current user
    to_user = ForeignKeyField(User, related_name='related_to')

    class Meta:
        database = DATABASE
        # unique index
        indexes = (
            (('from_user', 'to_user'), True),
        )


def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Post, Relationship], safe=True)
    DATABASE.close()

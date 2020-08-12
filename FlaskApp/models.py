from FlaskApp.config import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    twitter_handler = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(70), nullable=False)
    access_token = db.Column(db.String(100), unique=True, nullable=True)
    access_token_secret = db.Column(db.String(100), unique=True, nullable=True)
    friends = db.relationship('FriendsHandler', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email})"

class FriendsHandler(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_twitter_handler = db.Column(db.String(50), nullable=False)

class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tweet_id = db.Column(db.String(20), unique=True)
    text = db.Column(db.String(500), nullable=False)


class TwitterMsg(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recipient_id = db.Column(db.String(19), nullable=False)
    msg_id = db.Column(db.String(19), unique=True)
    name = db.Column(db.String(25), nullable=False)
    text = db.Column(db.String(300), nullable=False)
    img_url = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime)

    def __repr__(self):
        return f"Msg('{self.name}', '{self.text})"
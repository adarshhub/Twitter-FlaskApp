from flask import render_template, url_for, redirect, flash, request, session
from FlaskApp.forms import LoginForm, RegistrationForm, TweetForm, MessageForm
from FlaskApp.models import User, TwitterMsg, Tweet
from FlaskApp.token import consumer_token, consumer_secret
from FlaskApp import app, db, bcrypt
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from FlaskApp.twitterAPI import post_tweet, my_timeline, send_msg, fetch_messages, create_api, get_my_id
import requests, tweepy

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

auth = tweepy.OAuthHandler(consumer_token, consumer_secret)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        session['email'] = form.email.data
        session['password'] = hashed_pw
        try:
            redirect_url = auth.get_authorization_url()
        except tweepy.TweepError:
            flash("Error! Communicating with Twitter", 'info')
            return redirect(url_for('signup'))
        return redirect(redirect_url)
    return render_template("signup.html", title="signup", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            session['id'] = user.id
            create_api(user.access_token, user.access_token_secret)
            return redirect(url_for('index'))
        else:
            flash("Login unsuccessfull. Check email or password.", 'danger')
    return render_template("login.html", title="login", form=form)


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = TweetForm()
    if form.validate_on_submit():
        if post_tweet(form.msg.data):
            flash("Successfull.", 'success')
        else:
            flash("Unsuccessfull. Please Try again.", 'danger')
    all_tweets = my_timeline()

    #filtering tweets
    my_friends = current_user.friends
    friends_tweets = [tweet for tweet in all_tweets if tweet.user.screen_name in [x.friend_twitter_handler for x in my_friends]]
    store_tweets_into_db(friends_tweets)
    return render_template("index.html", title="home", form=form, tweets=friends_tweets)

def store_tweets_into_db(tweets):
    for _tweet in tweets:
        if db.session.query(Tweet).filter_by(tweet_id=_tweet.id).scalar() is None:
            _tweet_id = str(_tweet.id)
            tweet = Tweet(tweet_id=_tweet_id, text=_tweet.text)
            db.session.add(tweet)
            db.session.commit()


@app.route('/logout')
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))

@app.route('/message', methods=['GET', 'POST'])
@login_required
def message():
    form = MessageForm()
    if form.validate_on_submit():
        if send_msg(form.to.data, form.msg.data):
            flash("Successfull.", 'success')
        else:
            flash("Unsuccessfull. Please Try again.", 'danger')
    fetch_messages()
    my_id = get_my_id()
    msgs = TwitterMsg.query.filter_by(recipient_id=my_id).all()
    return render_template("message.html", title="home", form=form, msgs=msgs)

#callback url
@app.route('/twitter_auth', methods=['GET', 'POST'])
def twitter_auth():
    verifier = request.args.get('oauth_verifier')
    try:
        auth.get_access_token(verifier)
        temp_user = User.query.filter_by(access_token=auth.access_token).first()
        if temp_user:
            flash("This twitter account is already registered!", 'info')
            return redirect(url_for('login'))
        user = User(email=session['email'], password=session['password'])
        user.access_token = auth.access_token
        user.access_token_secret = auth.access_token_secret
        auth.set_access_token(auth.access_token, auth.access_token_secret)
        api = tweepy.API(auth)
        user.twitter_handler = api.me().screen_name
        db.session.add(user)
        db.session.commit()
        session.clear()
        flash("Regisration Successfull.", 'success')
        return redirect(url_for('login'))
    except tweepy.TweepError:
        flash("Something Went wrong please try", 'info')
        return redirect(url_for('signup'))


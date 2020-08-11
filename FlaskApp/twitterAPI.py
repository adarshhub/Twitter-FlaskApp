import twitter
from datetime import datetime
from FlaskApp import db
from FlaskApp.token import consumer_token, consumer_secret
from FlaskApp.models import TwitterMsg, User

my_id = ''
my_name = ''
my_twitter_handler = ''
api = None

def create_api(access_token, access_token_secret):
    global api, my_id, my_name
    api = twitter.Api(consumer_key=consumer_token,
                    consumer_secret=consumer_secret,
                    access_token_key=access_token,
                    access_token_secret=access_token_secret)
    api.DEFAULT_CACHE_TIMEOUT= 60
    my_credentials = api.VerifyCredentials()
    my_id = my_credentials.id
    my_name = my_credentials.name
    my_twitter_handler = my_credentials.screen_name
    print(f'---------------"{my_twitter_handler}"-------------------')

def get_my_id():
    return my_id

def get_my_twitter_handler():
    return my_twitter_handler

def my_timeline():
    tweets = api.GetHomeTimeline()
    return tweets


def my_tweets():
    tweets = api.GetUserTimeline(my_id)
    return tweets
    
def post_tweet(msg):
    tweet =  api.PostUpdate(msg)
    if(tweet):
        return True
    else:
        return False

def my_friends():
    my_friends = api.GetFriends()
    return my_friends


def getUserName_Pic(twitter_id):
	user = api.GetUser(twitter_id)
	name = user.name
	pic = user.profile_image_url 
	return name, pic

def fetch_messages():
    msgs = api.GetDirectMessages(return_json=True)
    for msg in msgs['events']:
        if(db.session.query(TwitterMsg).filter_by(msg_id=msg['id']).scalar() is None and str(msg['message_create']['sender_id']) != str(my_id)):
            twittermsg = TwitterMsg()
            twittermsg.msg_id = msg['id']
            twittermsg.recipient_id = msg['message_create']['target']['recipient_id']
            twittermsg.text = msg['message_create']['message_data']['text']
            twittermsg.name, twittermsg.img_url = getUserName_Pic(msg['message_create']['sender_id'])
            twittermsg.created_at = datetime.fromtimestamp(int(msg['created_timestamp'][:-3]))
            db.session.add(twittermsg)
            db.session.commit()

def send_msg(to, msg):
    try:
        if api.PostDirectMessage(screen_name=to,text=msg,return_json=True):
            return True
        else:
            return False
    except:
        return False

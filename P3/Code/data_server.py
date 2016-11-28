from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import tweepy
from stop_words import get_stop_words
from nltk.tokenize import RegexpTokenizer
import os


sentimentFilename = os.listdir('../Data/SentiScores')[0]

sentimentDict = {}
with open('../Data/SentiScores/'+sentimentFilename,'r') as f:
    wordsAndScores = f.read().split('\n')
    for pair in wordsAndScores:
        newPair = pair.split("\t")
        sentimentDict[newPair[0]] = int(newPair[1])


#API keys and tokens needed to stream data
consumer_key = "C4dBBifR4t8LlusHpNPxFfKdA"
consumer_secret = "dTsmQHFK9hsIPw7FVkUYZOp4wrgVnqiAVENukLvdqo1nQOqDhX"
access_token = "786328362667040768-huE0Wpegdwh1rsMCpAztfmRqgFhY3mi"
access_token_secret = "jbwxN7z5PahWAgLZgcQAd4gY6i9scKX1WtU3yIlo0G9Nz"

auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_token_secret)
api = tweepy.API(auth)

tweet_target_number = 1000

app = Flask(__name__)
app.config['SECRET_KEY'] = 'helloTHERE'
socketio = SocketIO(app)

def getTweet():
    socketio.emit("getTweet")

#Create a stream to collect tweets with
class MyStreamListener(tweepy.StreamListener):

    #Class Constructor
    def __init__(self, api=None):
        #Inherit from Parent class
        super(MyStreamListener,self).__init__()
        #Set an attribute of the current number of tweets collected
        self.current_tweets_collected = 0
        self.current_tweets = []
        self.stopGettingTweet = False

    #When a status is received by code from stream
    def on_status(self,status):
        if self.stopGettingTweet:
            print("Finally Halting")
            return False
        #Encode the line to utf-8 so it can be written to csv
        #Also remove new lines so that each line has one tweet
        tweetToWrite = status.text.encode("ascii","ignore").replace('\n',' ').strip()
        #Print the tweet to see it on the screen
        #Increment the number of tweets seen
        self.current_tweets_collected += 1
        self.current_tweets.append(tweetToWrite)
        getTweet()
        #Check current number of tweets collected. If enough have been
        #Collected end process, if not continue
        if(self.current_tweets_collected >= tweet_target_number):
            return False
        else:
            return True

    #If an error is hit and the API wants us to stop, return
    #False and stop
    def on_error(self,status_code):
        if status_code == 420:
            return False

    def on_stop_stream(self):
        print("Setting Stop Getting Tweets to True")
        self.stopGettingTweet = True

tweetListener = MyStreamListener()
currentNum = 0
unique = []
tweet_remove = ['rt','co']
totalPos = 0.0
totalNeg = 0.0
en_stop = get_stop_words('en')
tokenizer = RegexpTokenizer(r'\w+')

def clean_tweet_and_get_data(tweet):
    #Set to lower and split the tweet into parts
    global totalPos, totalNeg, unique, tweet_remove, en_stop, tokenizer, sentimentDict
    rawPos = 0
    rawNeg = 0
    tweet_parts = tweet.lower().split(' ')
    tweet_parts = [i for i in tweet_parts if not '@' in i]
    tweet_parts = [i for i in tweet_parts if not 'http' in i]
    tweet_parts = tokenizer.tokenize(' '.join(tweet_parts))
    tweet_parts = [i for i in tweet_parts if not i in en_stop]
    tweet_parts = [i for i in tweet_parts if not i in tweet_remove]
    if tweet_parts not in unique:
        unique.append(tweet_parts)
    for part in tweet_parts:
        if part in sentimentDict:
            currentScore = sentimentDict[part]
            if currentScore < 0:
                totalNeg -= currentScore
                rawNeg -= currentScore
            else:
                totalPos += currentScore
                rawPos += currentScore
    return [rawPos,rawNeg]

@app.route('/')
def hello_world():
    return render_template('main.html')

@socketio.on('connection')
def cool():
    print('Connection Made!')

@socketio.on('stopStream')
def stopTheStream():
    print('Stream Stopping')
    tweetListener.on_stop_stream()
    emit('done')

@socketio.on('stream')
def stream(data):
    global currentNum, tweetListener, tweet_remove, totalPos, totalNeg, unique
    currentNum = 0
    unique = []
    totalPos = 0.0
    totalNeg = 0.0
    tweet_remove = ['rt','co']
    for item in data["topic"].lower().split(" "):
        tweet_remove.append(item)
    tweetListener = MyStreamListener()
    tweetStream = tweepy.Stream(api.auth,tweetListener)
    tweetStream.filter(languages=["en"],track=[data["topic"]],async = True)
    if len(tweetListener.current_tweets) > 0:
        tweetToLookAt = tweetListener.current_tweets.pop()
        print(tweetToLookAt)
        s = clean_tweet_and_get_data(tweetToLookAt)
        currentNum += 1
        emit('tweet',{'rawtweet': tweetToLookAt,
                      'avgPos': float(totalPos)/float(currentNum),
                      'avgNeg': float(totalNeg)/float(currentNum),
                      'unique': float(len(unique)) / float(currentNum),
                      'rawPos': s[0],
                      'rawNeg': s[1]})

@socketio.on('okay')
def sendMore():
    global currentNum, tweetListener, tweet_remove, totalPos, totalNeg, unique
    if currentNum >= tweet_target_number:
        emit('done')
        return
    while len(tweetListener.current_tweets) > 0:
        tweetToLookAt = tweetListener.current_tweets.pop()
        print(tweetToLookAt)
        s = clean_tweet_and_get_data(tweetToLookAt)
        currentNum += 1
        emit('tweet',{'rawtweet': tweetToLookAt,
                      'avgPos': float(totalPos)/float(currentNum),
                      'avgNeg': float(totalNeg)/float(currentNum),
                      'unique': float(len(unique)) / float(currentNum),
                      'rawPos': s[0],
                      'rawNeg': s[1]})

if __name__ == '__main__':
    socketio.run(app,port=55222,debug=False)

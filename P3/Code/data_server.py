from flask import Flask, render_template, request
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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'helloTHERE'
socketio = SocketIO(app,ping_timeout=500)

def getTweet(sid):
    socketio.emit("getTweet",room=sid)

#Create a stream to collect tweets with
class MyStreamListener(tweepy.StreamListener):

    #Class Constructor
    def __init__(self,sid,tweet_target_number=100,api=None):
        #Inherit from Parent class
        super(MyStreamListener,self).__init__()
        #Set an attribute of the current number of tweets collected
        self.current_tweets_collected = 0
        self.current_tweets = []
        self.stopGettingTweet = False
        self.sid = sid
        self.tweet_target_number = tweet_target_number

    #When a status is received by code from stream
    def on_status(self,status):
        if self.stopGettingTweet:
            print("Finally Halting for "+self.sid+"!")
            return False
        #Encode the line to utf-8 so it can be written to csv
        #Also remove new lines so that each line has one tweet
        tweetToWrite = status.text.encode("ascii","ignore").replace('\n',' ').strip()
        #Print the tweet to see it on the screen
        #Increment the number of tweets seen
        self.current_tweets_collected += 1
        #Check current number of tweets collected. If enough have been
        #Collected end process, if not continue
        if(self.current_tweets_collected > self.tweet_target_number):
            print("Ending stream because target num of tweets met.")
            return False
        else:
            self.current_tweets.append(tweetToWrite)
            getTweet(self.sid)
            return True

    #If an error is hit and the API wants us to stop, return
    #False and stop
    def on_error(self,status_code):
        if status_code == 420:
            return False

    def on_stop_stream(self):
        print("Setting Stop Getting Tweets to True for "+self.sid+"!")
        self.stopGettingTweet = True

userData = {}
userListeners = {}
en_stop = get_stop_words('en')
tokenizer = RegexpTokenizer(r'\w+')

def clean_tweet_and_get_data(tweet,sid):
    #Set to lower and split the tweet into parts
    global userData, en_stop, tokenizer, sentimentDict
    rawPos = 0
    rawNeg = 0
    tweet_parts = tweet.lower().split(' ')
    tweet_parts = [i for i in tweet_parts if not '@' in i]
    tweet_parts = [i for i in tweet_parts if not 'http' in i]
    tweet_parts = tokenizer.tokenize(' '.join(tweet_parts))
    tweet_parts = [i for i in tweet_parts if not i in en_stop]
    tweet_parts = [i for i in tweet_parts if not i in userData[sid]['tweet_remove']]
    if tweet_parts not in userData[sid]['unique']:
        userData[sid]['unique'].append(tweet_parts)
    for part in tweet_parts:
        if part in sentimentDict:
            currentScore = sentimentDict[part]
            if currentScore < 0:
                userData[sid]['totalNeg'] -= currentScore
                rawNeg -= currentScore
            else:
                userData[sid]['totalPos'] += currentScore
                rawPos += currentScore
    return [rawPos,rawNeg]

@app.route('/')
def main_page():
    return render_template('main.html')

@socketio.on('connection')
def cool():
    global userData,userListeners
    print('Connection Made by '+request.sid+'!')
    userData[request.sid] = {'totalPos': 0.0, 'totalNeg': 0.0,'unique': [],'currentNum': 0, 'tweet_remove': ['rt','co'],'tweet_target_number': 100, 'stillGoing': False}
    userListeners[request.sid] = MyStreamListener(request.sid)

@socketio.on('disconnect')
def cool():
    print('Disconnection by '+request.sid+'!')
    del userData[request.sid]
    userListeners[request.sid].on_stop_stream()
    del userListeners[request.sid]

@socketio.on('stopStream')
def stopTheStream():
    print('Stream Stopping for '+request.sid+'!')
    userListeners[request.sid].on_stop_stream()
    emit('done',room=request.sid)

@socketio.on('stream')
def stream(data):
    global userData, userListeners
    userData[request.sid]['stillGoing'] = True
    userData[request.sid]['currentNum'] = 0
    userData[request.sid]['unique'] = []
    userData[request.sid]['totalPos'] = 0.0
    userData[request.sid]['totalNeg'] = 0.0
    userData[request.sid]['tweet_remove'] = ['rt','co']
    for item in data["topic"].lower().split(" "):
        userData[request.sid]['tweet_remove'].append(item)
    try:
        userData[request.sid]['tweet_target_number'] = int(data['numTweets'])
    except ValueError:
        print("Invalid number for "+request.sid+". Setting it to 100.")
        userData[request.sid]['tweet_target_number'] = 100
    userListeners[request.sid].on_stop_stream()
    userListeners[request.sid] = MyStreamListener(request.sid,userData[request.sid]['tweet_target_number'])
    tweetStream = tweepy.Stream(api.auth,userListeners[request.sid])
    tweetStream.filter(languages=["en"],track=[data["topic"]],async = True)
    print("Starting stream for "+request.sid+"!")
    if len(userListeners[request.sid].current_tweets) > 0:
        tweetToLookAt = userListeners[request.sid].current_tweets.pop()
        s = clean_tweet_and_get_data(tweetToLookAt,request.sid)
        userData[request.sid]['currentNum'] += 1
        print("#"+str(userData[request.sid]['currentNum'])+" - "+request.sid+" - "+str(tweetToLookAt))
        emit('tweet',{'rawtweet': tweetToLookAt,
                      'avgPos': float(userData[request.sid]['totalPos'])/float(userData[request.sid]['currentNum']),
                      'avgNeg': float(userData[request.sid]['totalNeg'])/float(userData[request.sid]['currentNum']),
                      'unique': float(len(userData[request.sid]['unique'])) / float(userData[request.sid]['currentNum']),
                      'rawPos': s[0],
                      'rawNeg': s[1],
                      'current': userData[request.sid]['currentNum']},room=request.sid)

@socketio.on('okay')
def sendMore():
    global userData, userListeners
    if userData[request.sid]['currentNum'] >= userData[request.sid]['tweet_target_number'] and len(userListeners[request.sid].current_tweets) == 0 and userData[request.sid]['stillGoing']:
        print("Done sending tweets to "+request.sid+"!")
        userData[request.sid]['stillGoing'] = False
        emit('done',room=request.sid)
    elif len(userListeners[request.sid].current_tweets) > 0:
        tweetToLookAt = userListeners[request.sid].current_tweets.pop()
        s = clean_tweet_and_get_data(tweetToLookAt,request.sid)
        userData[request.sid]['currentNum'] += 1
        print("#"+str(userData[request.sid]['currentNum'])+" - "+request.sid+" - "+str(tweetToLookAt))
        emit('tweet',{'rawtweet': tweetToLookAt,
                      'avgPos': float(userData[request.sid]['totalPos'])/float(userData[request.sid]['currentNum']),
                      'avgNeg': float(userData[request.sid]['totalNeg'])/float(userData[request.sid]['currentNum']),
                      'unique': float(len(userData[request.sid]['unique'])) / float(userData[request.sid]['currentNum']),
                      'rawPos': s[0],
                      'rawNeg': s[1],
                      'current': userData[request.sid]['currentNum']},room=request.sid)

if __name__ == '__main__':
    socketio.run(app,port=55222,debug=False)

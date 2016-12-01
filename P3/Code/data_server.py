#data_server.py

#Import flask for web server and functions
from flask import Flask, render_template, request
#Import socket io for socket communications
from flask_socketio import SocketIO, emit
#Import tweepy to stream tweets
import tweepy
#Import get_stop_words to remove stop words from tweets
from stop_words import get_stop_words
#Import tokenizer to split up tweets into words
from nltk.tokenize import RegexpTokenizer
#Import model building to get regression model and sentimentDict
import model_building as mb
#Get Sentiment Dict
sentimentDict = mb.import_sentiment_dict()

#API keys and tokens needed to stream data
consumer_key = "C4dBBifR4t8LlusHpNPxFfKdA"
consumer_secret = "dTsmQHFK9hsIPw7FVkUYZOp4wrgVnqiAVENukLvdqo1nQOqDhX"
access_token = "786328362667040768-huE0Wpegdwh1rsMCpAztfmRqgFhY3mi"
access_token_secret = "jbwxN7z5PahWAgLZgcQAd4gY6i9scKX1WtU3yIlo0G9Nz"

#Autheniticate our identity with twitter and set up API access
auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
auth.set_access_token(access_token,access_token_secret)
api = tweepy.API(auth)

#Create Flask app
app = Flask(__name__)
#Create a secret key for Socket io
app.config['SECRET_KEY'] = 'helloTHERE'
#Make flask app also a socket io app with 500 second timeout
socketio = SocketIO(app,ping_timeout=500)

#Called by MyStreamListener to notify browser to ask for a tweet
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
        #Set an attribute to hold all tweets received by stream that have not
        #been analyzed
        self.current_tweets = []
        #Set an attribute that can stop streaming if necessary
        self.stopGettingTweet = False
        #Set the session id of requester
        self.sid = sid
        #Set an attribute for the requested number of tweets
        self.tweet_target_number = tweet_target_number

    #When a status is received by code from stream
    def on_status(self,status):
        #If stopGettingTweet is true, end the stream
        if self.stopGettingTweet:
            print("Finally Halting for "+self.sid+"!")
            return False
        #Encode the line to ascii and remove new lines and extra spaces at beginning
        #and end of the string
        tweetToWrite = status.text.encode("ascii","ignore").replace('\n',' ').strip()
        #Increment the number of tweets seen
        self.current_tweets_collected += 1
        #Check current number of tweets collected. If enough have been
        #Collected end process. If not continue and tell the browser to
        #ask for this tweet
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
    #If the user wants to stop the stream, set stopGettingTweet to True
    def on_stop_stream(self):
        print("Setting Stop Getting Tweets to True for "+self.sid+"!")
        self.stopGettingTweet = True

#Global variable to collect all of the users' data
userData = {}
#Global variable to track all of the stream listeners
userListeners = {}
#Global variable that has a list of stop words
en_stop = get_stop_words('en')
#Global tokenizer for when trying to split up tweets
tokenizer = RegexpTokenizer(r'\w+')

#Function that cleans tweets and gets sentiment scores
def clean_tweet_and_get_data(tweet,sid):
    #Get global variables and their assignments
    global userData, en_stop, tokenizer, sentimentDict
    #Variable to track positive sentiment of tweet
    rawPos = 0
    #Variable to track negative sentiment of tweet
    rawNeg = 0
    #Split tweet up by spaces and make words lower
    tweet_parts = tweet.lower().split(' ')
    #Remove usernames from tweet
    tweet_parts = [i for i in tweet_parts if not '@' in i]
    #Remove links from tweet
    tweet_parts = [i for i in tweet_parts if not 'http' in i]
    #Join all remaining parts together by spaces and then split tweet apart so
    #there is just an array of words in the tweet
    tweet_parts = tokenizer.tokenize(' '.join(tweet_parts))
    #Remove any stop words from the tweet
    tweet_parts = [i for i in tweet_parts if not i in en_stop]
    #Remove any words that are in tweet remove
    tweet_parts = [i for i in tweet_parts if not i in userData[sid]['tweet_remove']]
    #If this tweet has not been seen before
    if tweet_parts not in userData[sid]['unique']:
        #Add the tweet to the user's unique list
        userData[sid]['unique'].append(tweet_parts)
    #For each word in the tweet
    for part in tweet_parts:
        #If the tweet is in the sentiment dictionary
        if part in sentimentDict:
            #Get the score of the word in the sentiment dict
            currentScore = sentimentDict[part]
            #If the score is negative add it to the negative raw score and total Score
            if currentScore < 0:
                userData[sid]['totalNeg'] -= currentScore
                rawNeg -= currentScore
            #If the score is positive add it to the negative raw score and total Score
            else:
                userData[sid]['totalPos'] += currentScore
                rawPos += currentScore
    #Return the raw positive and negative scores for tweet
    return [rawPos,rawNeg]

#If browser asks for homepage, give them the homepage
@app.route('/')
def main_page():
    return render_template('main.html')

#When a browser is connected to the server
@socketio.on('connection')
def connect():
    #Get global variables and their values
    global userData,userListeners
    #Print to console the connection and session id
    print('Connection Made by '+request.sid+'!')
    #Create an entry in user data to track their data
    userData[request.sid] = {'totalPos': 0.0, 'totalNeg': 0.0,'unique': [],'currentNum': 0, 'tweet_remove': ['rt','co'],'tweet_target_number': 100, 'stillGoing': False}
    #Create a default stream listener for their connection
    userListeners[request.sid] = MyStreamListener(request.sid)

#When a browser is disconnected from the server
@socketio.on('disconnect')
def disconnect():
    #Get global variables and their values
    global userData,userListeners
    #Print that the session disconnected
    print('Disconnection by '+request.sid+'!')
    #Delete that session's data from the data dict
    del userData[request.sid]
    #Stop the stream listener for that user
    userListeners[request.sid].on_stop_stream()
    #Delete that stream listener from the listener dict
    del userListeners[request.sid]

#When the user wants to stop the current stream
@socketio.on('stopStream')
def stopTheStream():
    #Get global variables and their values
    global userListeners
    #Print that the stream is stopping for the session
    print('Stream Stopping for '+request.sid+'!')
    #Stop the stream for the user
    userListeners[request.sid].on_stop_stream()
    #Emit that the stream of data has ended to the browser
    emit('done',room=request.sid)

#When user makes a query in the browser
@socketio.on('stream')
def stream(data):
    #Get global variables and their values
    global userData, userListeners, model
    #Set stream still going to True
    userData[request.sid]['stillGoing'] = True
    #Set current number of tweets received to 0
    userData[request.sid]['currentNum'] = 0
    #Set the unique tweets to a blank list
    userData[request.sid]['unique'] = []
    #Set total positive to 0
    userData[request.sid]['totalPos'] = 0.0
    #Set total negative to 0
    userData[request.sid]['totalNeg'] = 0.0
    #Start tweet remove list with rt and co
    userData[request.sid]['tweet_remove'] = ['rt','co']
    #For each word in the topic query, add them to tweet remove
    for item in data["topic"].lower().split(" "):
        userData[request.sid]['tweet_remove'].append(item)
    #Try to set the number they asked for to tweet target. If it's not a number
    #Or if an errror occurs set the value to 100
    try:
        userData[request.sid]['tweet_target_number'] = int(data['numTweets'])
    except ValueError:
        print("Invalid number for "+request.sid+". Setting it to 100.")
        userData[request.sid]['tweet_target_number'] = 100
    #If there is currently a stream going, stop it
    userListeners[request.sid].on_stop_stream()
    #Start the stream for the topic that was asked for
    userListeners[request.sid] = MyStreamListener(request.sid,userData[request.sid]['tweet_target_number'])
    tweetStream = tweepy.Stream(api.auth,userListeners[request.sid])
    tweetStream.filter(languages=["en"],track=[data["topic"]],async = True)
    #Print that the stream is starting for the user
    print("Starting stream for "+request.sid+"!")
    #If there is a tweet to send to the browser
    if len(userListeners[request.sid].current_tweets) > 0:
        #Get the oldest tweet in the list and pop it from the list
        tweetToLookAt = userListeners[request.sid].current_tweets.pop()
        #Get the raw positive and negative values of the tweet and modify averages
        s = clean_tweet_and_get_data(tweetToLookAt,request.sid)
        #Increase the current number of the tweet
        userData[request.sid]['currentNum'] += 1
        #Print the tweet to the console
        print("#"+str(userData[request.sid]['currentNum'])+" - "+request.sid+" - "+str(tweetToLookAt))
        #Send the tweet to the browser
        emit('tweet',{'rawtweet': tweetToLookAt,
                      'avgPos': float(userData[request.sid]['totalPos'])/float(userData[request.sid]['currentNum']),
                      'avgNeg': float(userData[request.sid]['totalNeg'])/float(userData[request.sid]['currentNum']),
                      'unique': float(len(userData[request.sid]['unique'])) / float(userData[request.sid]['currentNum']),
                      'rawPos': s[0],
                      'rawNeg': s[1],
                      'modelAvgPos': model["avgPos"],
                      'modelAvgNeg': model["avgNeg"],
                      'modelUnique': model["unique"],
                      'modelIntercept': model["intercept"],
                      'current': userData[request.sid]['currentNum']},room=request.sid)

#When browser asks for a tweet
@socketio.on('okay')
def sendMore():
    #Get global variables and their values
    global userData, userListeners, model
    #If the requested nuber of tweets has been sent, there isn't any more tweets to pop, and the user data says stillgoing
    if userData[request.sid]['currentNum'] >= userData[request.sid]['tweet_target_number'] and len(userListeners[request.sid].current_tweets) == 0 and userData[request.sid]['stillGoing']:
        #Print that the server is done sending tweets
        print("Done sending tweets to "+request.sid+"!")
        #Set still going to false
        userData[request.sid]['stillGoing'] = False
        #Tell the browser that it is done
        emit('done',room=request.sid)
    #Else if there is still tweets to send
    elif len(userListeners[request.sid].current_tweets) > 0:
        #Get the oldest tweet in the list and pop it from the list
        tweetToLookAt = userListeners[request.sid].current_tweets.pop()
        #Get the raw positive and negative values of the tweet and modify averages
        s = clean_tweet_and_get_data(tweetToLookAt,request.sid)
        #Increase the currentNumber of tweets by 1
        userData[request.sid]['currentNum'] += 1
        #Print the tweet out to the console
        print("#"+str(userData[request.sid]['currentNum'])+" - "+request.sid+" - "+str(tweetToLookAt))
        #Send the tweet to the browser
        emit('tweet',{'rawtweet': tweetToLookAt,
                      'avgPos': float(userData[request.sid]['totalPos'])/float(userData[request.sid]['currentNum']),
                      'avgNeg': float(userData[request.sid]['totalNeg'])/float(userData[request.sid]['currentNum']),
                      'unique': float(len(userData[request.sid]['unique'])) / float(userData[request.sid]['currentNum']),
                      'rawPos': s[0],
                      'rawNeg': s[1],
                      'modelAvgPos': model["avgPos"],
                      'modelAvgNeg': model["avgNeg"],
                      'modelUnique': model["unique"],
                      'modelIntercept': model["intercept"],
                      'current': userData[request.sid]['currentNum']},room=request.sid)

#If we are running this file in particular
if __name__ == '__main__':
    #Get the global variable model
    global model
    print("Building Regression Model")
    #Get the regression model for the tweet data
    model = mb.getModelForWebsite()
    print("Server running on localhost:55222!")
    #Start the server up
    socketio.run(app,port=55222,debug=False)

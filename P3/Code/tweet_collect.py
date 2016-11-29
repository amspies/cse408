#tweet_collect.py

#Import tweepy in order to connect to Twitter API
import tweepy
#Import csv so we can write data to a file
import csv
#Import to get time functions
import datetime

#API keys and tokens needed to stream data
consumer_key = "C4dBBifR4t8LlusHpNPxFfKdA"
consumer_secret = "dTsmQHFK9hsIPw7FVkUYZOp4wrgVnqiAVENukLvdqo1nQOqDhX"
access_token = "786328362667040768-huE0Wpegdwh1rsMCpAztfmRqgFhY3mi"
access_token_secret = "jbwxN7z5PahWAgLZgcQAd4gY6i9scKX1WtU3yIlo0G9Nz"

#Set up the API authorization
auth = tweepy.OAuthHandler(consumer_key,consumer_secret)
#Set up the access tokens
auth.set_access_token(access_token,access_token_secret)
#Send the auth data to the API and setup an API connection
api = tweepy.API(auth)

def collect_tweets_from_five_days_ago(tweet_num,topic):
    #Name file for topic
    fileName = "../Data/Tweets/"+ topic.replace(" ","_") + ".csv"
    #Get today's date
    today = datetime.datetime.today()
    #Get date from 5 days ago
    fiveDaysAgo = today - datetime.timedelta(days=5)
    #Create a string for the function
    fiveString = fiveDaysAgo.strftime("%Y-%m-%d")
    #Get date from 4 days ago
    fourDaysAgo = today - datetime.timedelta(days=4)
    #Create a string for the function
    fourString = fourDaysAgo.strftime("%Y-%m-%d")
    #Set a variable to track the number of tweets collected
    tweets_collected = 0

    #For each tweet that matches the search query
    for tweet in tweepy.Cursor(api.search,q=topic,since=fiveString,until=fourString,lang="en").items():
        #Remove new lines, unicode specific characters, and extra whitespace
        tweetToWrite = tweet.text.encode("ascii","ignore").replace('\n',' ').strip()
        #Increment tweets_collected
        tweets_collected += 1
        #Print out the tweet to console with tweet collect num
        print(str(tweets_collected)+": "+tweetToWrite)
        #Open csv file to write to
        with open(fileName,'ab') as csvfile:
            #Create a csv writer to write the tweet
            csvWriter = csv.writer(csvfile)
            #write the tweet to a row in the csv file
            csvWriter.writerow([tweetToWrite])
        #If we have the requested number of tweets break the loop
        if(tweets_collected >= tweet_num):
            break

    return True

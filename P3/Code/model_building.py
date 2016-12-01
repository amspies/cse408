#model_building.py

#Import os for file system manipulation
import os
#Import pandas for Data Frames
import pandas as pd
#Import get_stop_words to remove stop words
from stop_words import get_stop_words
#Import tokenizer to create tokens of tweets
from nltk.tokenize import RegexpTokenizer
#Import LinearRegression to create regression model
from sklearn.linear_model import LinearRegression

#Setup list of products we want to use for model
TRAINING = ["Almost Christmas","Arrival Movie","Batman Telltale","Billy Lynn",
            "Bleed for this","Dishonored 2","Doctor Strange","Edge of Seventeen",
            "Fantastic Beasts","Hacksaw Ridge","Infinite Warfare","Planet Coaster",
            "Pokemon Sun","Trolls Movie","Watch Dogs 2"]

#Function to get the sentimentDict
def import_sentiment_dict():
    #Find the name of the file in the sentiment score folder
    sentimentFilename = os.listdir('../Data/SentiScores')[0]
    #Create a starting empty dict
    sentimentDict = {}
    #Open up the sentiment file
    with open('../Data/SentiScores/'+sentimentFilename,'r') as f:
        #Read in the whole file and split it up by lines
        wordsAndScores = f.read().split('\n')
        #For each line of data
        for pair in wordsAndScores:
            #Split up the line by tabs
            newPair = pair.split("\t")
            #Sent the key to be the word to score and the value as the score of
            #the word
            sentimentDict[newPair[0]] = int(newPair[1])
    #Return the sentiment dictionary
    return sentimentDict

#Create a dataframe of features for each of the products
def import_dataframe_of_media_attributes(sentimentDict):
    #Get all of the filenames in the tweets folder
    filenames = os.listdir('../Data/Tweets')
    #Create lists for each of the attributes we want to track
    names = []
    uniquePercent = []
    avgPosScore = []
    avgNegScore = []
    avgUniquePosScore = []
    avgUniqueNegScore = []
    wordCounts = []
    #Get the english stop words list
    en_stop = get_stop_words('en')
    #Create a tokenizer in order to split tweets into just words
    tokenizer = RegexpTokenizer(r'\w+')
    #For each filename in the file
    for filename in filenames:
        #Create a doct to track the word counts
        currentWordDoc = {}
        #Create an initial tweet_remove list
        tweet_remove = ['rt','co']
        #Setup initial values to track for product
        totalPos = 0.0
        totalNeg = 0.0
        totalUniquePos = 0.0
        totalUniqueNeg = 0.0
        #Set unique tweet list to blank
        unique = []
        #Get the name of the project
        name = filename.split(".")[0]
        #Add the topic query words to the tweet_remove list
        for item in name.lower().split("_"):
            tweet_remove.append(item)
        #Change to a dataframe
        listOfTweets = pd.read_csv('../Data/Tweets/'+filename,header=None)
        #Get total number of tweets in dataset
        totalNum = len(listOfTweets)
        #For each row in the dataframe
        for index, row in listOfTweets.iterrows():
            #Have Variable to check if unique
            isItUnique = False
            #Get the tweet
            tweet = row[0]
            #Set to lower and split the tweet into parts
            tweet_parts = tweet.lower().split(' ')
            #Remove usernames from tweet
            tweet_parts = [i for i in tweet_parts if not '@' in i]
            #Remove links from tweet
            tweet_parts = [i for i in tweet_parts if not 'http' in i]
            #Join the tweet parts by spaces and only get words
            tweet_parts = tokenizer.tokenize(' '.join(tweet_parts))
            #Remove stop words from the tweet
            tweet_parts = [i for i in tweet_parts if not i in en_stop]
            #Remove words in the tweet_remove list from the tweet
            tweet_parts = [i for i in tweet_parts if not i in tweet_remove]
            #If the tweet has not been seen append the tweet to the unique
            #tweet list
            if tweet_parts not in unique:
                unique.append(tweet_parts)
                isItUnique = True
            #For each word in the tweet
            for part in tweet_parts:
                #If it is in the sentiment dict
                if part in sentimentDict:
                    #If the word has a count already increase count by one
                    #If not, set count to one
                    if part in currentWordDoc:
                        currentWordDoc[part] += 1
                    else:
                        currentWordDoc[part] = 1
                    #Get sentiment score for word and add it to the corresponding
                    #values
                    currentScore = sentimentDict[part]
                    if currentScore < 0:
                        totalNeg -= currentScore
                        if isItUnique:
                            totalUniqueNeg -= currentScore
                    else:
                        totalPos += currentScore
                        if isItUnique:
                            totalUniquePos += currentScore
        #Add product specific attributes to the corresponding lists
        names.append(name.replace("_"," "))
        avgPosScore.append(totalPos / float(totalNum))
        avgNegScore.append(totalNeg / float(totalNum))
        uniquePercent.append(float(len(unique))/float(totalNum))
        avgUniquePosScore.append(totalUniquePos/float(len(unique)))
        avgUniqueNegScore.append(totalUniqueNeg/float(len(unique)))
        wordCounts.append(currentWordDoc)
    #Create a list for metacritic scores
    mcScore = [0] * len(names)
    #For each name that corresponds to a metacritic score and that movie's value
    #to the mcScore list
    with open("../Data/MCScores/MCScores.txt") as scoreFile:
        for line in scoreFile:
            lineArray = line.split(",")
            mcScore[names.index(lineArray[0])] = int(lineArray[1])
    #Create dict with all of the lists
    dataDF = {'names':names, 'avgPos': avgPosScore, 'avgNeg': avgNegScore, 'unique':uniquePercent, 'mcScore':mcScore,'avgUniquePosScore':avgUniquePosScore,'avgUniqueNegScore':avgUniqueNegScore}
    #Turn the dict into a dataframe
    dataDF = pd.DataFrame(dataDF)
    #Return the dataframe
    return dataDF

#Function to test the current model
def testModel(testDF,model):
    #Create a list to track all of the percent error values
    percentError = []
    #For each row in the test dataframe
    for index, row in testDF.iterrows():
        #Calculate the predicted value
        predictedValue = model["intercept"]
        for i in range(0,len(model['coef'])):
            predictedValue += (model['coef'][i] * row[model['variables'][i]])
        #Get the actual score from the test df
        actualValue = row[model['predict']]
        #Print out the predicted score and the actual score
        print(row['names'] + " Predicted Value: " + str(predictedValue))
        print(row['names'] + " Actual Value: " + str(actualValue))
        #Get the percent error, append it to the list and print it to the screen
        percentErrorValue =  abs(predictedValue-actualValue) / abs(actualValue)
        percentError.append(percentErrorValue)
        print('Percent Error: '+str(percentErrorValue)+"\n")
    #Get average error, print it to the screen, and return it
    averageError = sum(percentError) / float(len(percentError))
    print("Average Percent Error: "+str(averageError))
    return averageError

#Create the regression model for the dependent variables and predicted variable provided
#and using the dataframe and sklearn, output coefficient values and intercept value
def get_regression_model(df,variableColumns,predictColumn):
    x = df[variableColumns]
    y = df[predictColumn]
    lm = LinearRegression()
    lm.fit(x,y)
    return {"intercept": lm.intercept_, "coef":lm.coef_, "variables":variableColumns, "predict":predictColumn}

#Use this function to get the linear regression model for website so the
#metacritic score can be calculated
def getModelForWebsite():
    sentimentDict = import_sentiment_dict()
    data = import_dataframe_of_media_attributes(sentimentDict)
    trainingData = data[data['names'].isin(TRAINING)]
    model = get_regression_model(trainingData,["avgNeg","avgPos","unique"],"mcScore")
    return {"intercept": model["intercept"],"avgNeg": model["coef"][model["variables"].index("avgNeg")],
            "avgPos":model["coef"][model["variables"].index("avgPos")], "unique":model["coef"][model["variables"].index("unique")]}

def main():
    #Get the sentiment dict
    sentimentDict = import_sentiment_dict()
    #Get the dataframe of features using the sentiment dict
    data = import_dataframe_of_media_attributes(sentimentDict)
    #Get training data
    trainingData = data[data['names'].isin(TRAINING)]
    #Get test data
    testData = data[~data['names'].isin(TRAINING)]
    #Get the regression model using training data and print it to the screen
    model = get_regression_model(trainingData,["avgNeg","avgPos","unique"],"mcScore")
    print("Intercept: "+str(model['intercept']))
    for i in range(0,len(model['coef'])):
        print(model['variables'][i]+": "+str(model['coef'][i]))
    print(" ")
    #Test the regression model with the test data
    testModel(testData,model)

#If this is the file that is running, call the main function
if __name__ == '__main__':
    main()

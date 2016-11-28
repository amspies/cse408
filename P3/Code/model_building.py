import os
import pandas as pd
from stop_words import get_stop_words
from nltk.tokenize import RegexpTokenizer
from sklearn.linear_model import LinearRegression

TRAINING = ["Almost Christmas","Arrival Movie","Batman Telltale","Billy Lynn",
            "Bleed for this","Dishonored 2","Doctor Strange","Edge of Seventeen",
            "Fantastic Beasts","Hacksaw Ridge","Infinite Warfare","Planet Coaster",
            "Pokemon Sun","Trolls Movie","Watch Dogs 2"]

def import_sentiment_dict():
    sentimentFilename = os.listdir('../Data/SentiScores')[0]
    sentimentDict = {}
    with open('../Data/SentiScores/'+sentimentFilename,'r') as f:
        wordsAndScores = f.read().split('\n')
        for pair in wordsAndScores:
            newPair = pair.split("\t")
            sentimentDict[newPair[0]] = int(newPair[1])
    return sentimentDict

def import_dataframe_of_media_attributes(sentimentDict):
    filenames = os.listdir('../Data/Tweets')
    names = []
    uniquePercent = []
    avgPosScore = []
    avgNegScore = []
    avgUniquePosScore = []
    avgUniqueNegScore = []
    wordCounts = []
    en_stop = get_stop_words('en')
    tokenizer = RegexpTokenizer(r'\w+')
    #For each filename in the file
    for filename in filenames:
        currentWordDoc = {}
        tweet_remove = ['rt','co']
        totalPos = 0.0
        totalNeg = 0.0
        totalUniquePos = 0.0
        totalUniqueNeg = 0.0
        unique = []
        #Get the name of the project
        name = filename.split(".")[0]
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
            tweet_parts = [i for i in tweet_parts if not '@' in i]
            tweet_parts = [i for i in tweet_parts if not 'http' in i]
            tweet_parts = tokenizer.tokenize(' '.join(tweet_parts))
            tweet_parts = [i for i in tweet_parts if not i in en_stop]
            tweet_parts = [i for i in tweet_parts if not i in tweet_remove]
            if tweet_parts not in unique:
                unique.append(tweet_parts)
                isItUnique = True
            for part in tweet_parts:
                if part in sentimentDict:
                    if part in currentWordDoc:
                        currentWordDoc[part] += 1
                    else:
                        currentWordDoc[part] = 1
                    currentScore = sentimentDict[part]
                    if currentScore < 0:
                        totalNeg -= currentScore
                        if isItUnique:
                            totalUniqueNeg -= currentScore
                    else:
                        totalPos += currentScore
                        if isItUnique:
                            totalUniquePos += currentScore
        names.append(name.replace("_"," "))
        avgPosScore.append(totalPos / float(totalNum))
        avgNegScore.append(totalNeg / float(totalNum))
        uniquePercent.append(float(len(unique))/float(totalNum))
        avgUniquePosScore.append(totalUniquePos/float(len(unique)))
        avgUniqueNegScore.append(totalUniqueNeg/float(len(unique)))
        wordCounts.append(currentWordDoc)
    mcScore = [0] * len(names)
    with open("../Data/MCScores/MCScores.txt") as scoreFile:
        for line in scoreFile:
            lineArray = line.split(",")
            mcScore[names.index(lineArray[0])] = int(lineArray[1])
    dataDF = {'names':names, 'avgPos': avgPosScore, 'avgNeg': avgNegScore, 'unique':uniquePercent, 'mcScore':mcScore,'avgUniquePosScore':avgUniquePosScore,'avgUniqueNegScore':avgUniqueNegScore}
    dataDF = pd.DataFrame(dataDF)
    return dataDF

def testModel(testDF,model):
    percentError = []
    for index, row in testDF.iterrows():
        predictedValue = model["intercept"]
        for i in range(0,len(model['coef'])):
            predictedValue += (model['coef'][i] * row[model['variables'][i]])
        actualValue = row[model['predict']]
        print(row['names'] + " Predicted Value: " + str(predictedValue))
        print(row['names'] + " Actual Value: " + str(actualValue))
        percentErrorValue =  abs(predictedValue-actualValue) / abs(actualValue)
        percentError.append(percentErrorValue)
        print('Percent Error: '+str(percentErrorValue)+"\n")
    averageError = sum(percentError) / float(len(percentError))
    print("Average Percent Error: "+str(averageError))
    return averageError

def get_regression_model(df,variableColumns,predictColumn):
    x = df[variableColumns]
    y = df[predictColumn]
    lm = LinearRegression()
    lm.fit(x,y)
    return {"intercept": lm.intercept_, "coef":lm.coef_, "variables":variableColumns, "predict":predictColumn}

def main():
    sentimentDict = import_sentiment_dict()
    data = import_dataframe_of_media_attributes(sentimentDict)
    trainingData = data[data['names'].isin(TRAINING)]
    testData = data[~data['names'].isin(TRAINING)]
    model = get_regression_model(trainingData,["avgNeg","avgPos","unique"],"mcScore")
    print("Intercept: "+str(model['intercept']))
    for i in range(0,len(model['coef'])):
        print(model['variables'][i]+": "+str(model['coef'][i]))
    print(" ")
    testModel(testData,model)


if __name__ == '__main__':
    main()

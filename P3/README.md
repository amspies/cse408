# Instructions for running the project

The following are the instructions needed to run the project on your computer. For all
parts, Python 2 and pip are needed in order to get it running.

If you don't have Python 2, here is the link to download Python 2: https://www.python.org/downloads/

If you don't have pip, here is a link to a file to help install pip: https://pip.pypa.io/en/stable/installing/

There's other ways to install both of these tools, but we just wanted to give some possible options.

## tweet_collect.py
To run tweet_collect.py, just run the following commands:

```bash
sudo pip install tweepy
python
```

Then in python REPL terminal, write the following lines of code:

```python
import tweet_collect as tc
numTweets = 1000 #Enter number of tweets you want to collect here
topic = "ENTER TOPIC STRING HERE"
tc.collect_tweets_from_five_days_ago(numTweets,topic)
```
This will create a csv file in the Data/Tweets folder with a filename
based on the topic you searched. It may not return the number of tweets
requested if there wasn't enough public tweets to meet your request. If
that's the case, you can always go into the code and change the timespan
of the request.

## model_building.py

model_building.py is the file used to build the regression model for the
website, and when it is ran as the main file, it also serves as a file that
tests the current model. In order to run it, enter the following bash
commands:

```bash
sudo pip install pandas
sudo pip install stop-words
sudo pip install -U nltk
sudo pip install -U numpy
sudo pip install -U scikit-learn
python model_building.py
```

## data_server.py

The data server is the web server that serves as a user interface to stream
live tweets from twitter and get a Metacritic score prediction. To run it,
enter the following bash commands:

```bash
sudo pip install Flask
sudo pip install flask-socketio
sudo pip install tweepy
sudo pip install pandas
sudo pip install -U nltk
sudo pip install stop-word
sudo pip install -U numpy
sudo pip install -U scikit-learn
python data_server.py
```

The server should then be running at http://localhost:55222 when the terminal
states that it is ready.

## Model_Building_Notebook.ipynb

In order to open this file, you will need to be able run Jupyter Notebooks.

If you dont have jupyter just run the command:

```bash
pip install jupyter
jupyter notebook
```

This will open the jupyter notebook in the browser, and from there you can
navigate to the proper file.

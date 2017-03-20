#!/usr/bin/python3

import json
from pprint import pprint
from textblob import TextBlob

#read the tweets
with open('georeferenced_formatted.json') as data_file:    
    tweets = json.load(data_file)

#Add polarity and subjectibity for each tweet
with open('data.json', 'w') as outfile:
    for tweet in tweets[:10]:#number_of_tweets):
        blob = TextBlob(tweet["text"])
        tweet["polarity"] = blob.sentiment.polarity
        tweet["subjectivity"] = blob.sentiment.subjectivity
    json.dump(tweets, outfile)

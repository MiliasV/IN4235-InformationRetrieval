#!/usr/bin/python3

import json
from pprint import pprint
from textblob import TextBlob
from langdetect import detect
from wordcloud import WordCloud
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from os import path
import nltk
from nltk.corpus import stopwords
import string



###########
#Functions#
###########
def wordCloud(text, img):
    my_mask = np.array(Image.open(img))
    wc = WordCloud(background_color="black", max_words=2000, mask=my_mask)
    wc.generate(text)

    plt.figure(figsize=(15,8))
    plt.imshow(wc)
    plt.axis("off")
    plt.show()


######################################################################################

# set with english stopWords
# If you do not have it:
#   ==> import nltk
#   ==> nltk.download() to download the stopwords list
stops = set(stopwords.words("english"))
# add https in stopWord list
stops.add("https")

# read the tweets
with open('georeferenced_formatted.json') as data_file:    
    tweets = json.load(data_file)

filtered_tweets = []
print(len(tweets))

for index, tweet in enumerate(tweets):
    print(index)
    # Detect tweet's language
    try:
        lan = detect(tweet["text"])
    except:
        #if language is undefined, language is "NA"
        print (tweet["text"])
        lan = "NA"#
    #Keep only english tweets
    if lan=="en":
        #Add polarity, subjectibity and filtered text for each tweet
        blob = TextBlob(tweet["text"])
        tweet["polarity"] = blob.sentiment.polarity
        tweet["subjectivity"] = blob.sentiment.subjectivity
        word_list = nltk.word_tokenize(tweet["text"])
        filtered_words = ' '.join([word.lower() for word in word_list if word.lower() not in stops if len(word)>2 if word not in string.punctuation])
        tweet["filtered_text"] = filtered_words
        filtered_tweets.append(tweet)


with open('en_tweets.json', 'w') as outfile:
    json.dump(filtered_tweets, outfile)

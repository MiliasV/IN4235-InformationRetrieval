from shapely.geometry import shape
from textblob import TextBlob
from geojson import Feature, Point, FeatureCollection
from nltk.corpus import stopwords
import geojson
import geopandas
import json
import nltk
import re
import string

input_tweets_file = 'collected_tweets.json'
output_tweets_file = 'processed_tweets.geojson'
ams_boundary_file = 'amsterdam_boundary.geojson'

ams_geojson = geopandas.read_file(ams_boundary_file)
ams_boundary = ams_geojson.ix[0].geometry

stopwords = stopwords.words("english")
stopwords.extend(string.punctuation)
stopwords.extend([
    # Stopwords connected to the location
    'amsterdam', 'netherlands', 'holland', 'noord-holland', 'iamsterdam',
    'nederland', 'amsterdam…', 'ánsterdan',
    # Alarm system
    'p2000', 'rit',
    # "Trending" variations
    'trndnl', 'trends',  'trending', 'trend',
    # Misc
    '...', 'photo', 'posted', 'travel', 'twitter'
    # HTML markup
    'amp'
])
stopwords_set = set(stopwords)

punctuation_set = set(string.punctuation)


def isValidTweet(tweet):
    """
    Validate an input tweet
        """
    # We only consider geolocated tweets
    if tweet['coordinates'] is None:
        return False

    # Within the boundaries of the city of Amsterdam
    tweet_location = shape(tweet['coordinates'])
    if not tweet_location.within(ams_boundary):
        return False

    # For which the language is English
    tweet_blob = TextBlob(tweet['text'])
    try:
        tweet_lang = tweet_blob.detect_language()
    except:
        return False

    if tweet_lang != 'en':
        return False

    return True


def enrichWithAttributes(tweet):
    """
    Add sentiment and words information to tweet
    """
    # Use a Regular Expression to remove the t.co URLs from
    # the text of the tweet
    regex_tco_url = r'https?:\/\/t\.co\/\w+'
    text_nourl = re.sub(regex_tco_url, '', tweet['text'])
    tweet_blob = TextBlob(text_nourl)
    tweet['polarity'] = tweet_blob.sentiment.polarity

    def isValidToken(token):
        return len(token) > 2 and \
           token.lower() not in stopwords_set and \
           token not in punctuation_set

    word_list = nltk.word_tokenize(text_nourl)
    valid_word_list = filter(isValidToken, word_list)
    valid_word_list_lower = map(lambda t: t.lower(), valid_word_list)

    tweet['tokens'] = list(valid_word_list_lower)

    return tweet


def tweetToFeature(tweet):
    """
    Convert a tweet to a GeoJSON Feature
    """
    point = Point(tweet['coordinates']['coordinates'])
    properties = {
        'text': tweet['text'],
        'sentiment': tweet['polarity'],
        'tokens': tweet['tokens']
    }
    feature = Feature(geometry=point, id=tweet['id'], properties=properties)

    return feature


# Read the JSON file with the tweets into a list of dictionaries
with open(input_tweets_file) as input_tweets_f:
    tweets = json.load(input_tweets_f)

# Filter out invalid tweets
valid_tweets = filter(isValidTweet, tweets)
# Enrich dataset with sentiments
valid_tweets_enriched = map(enrichWithAttributes, valid_tweets)
# Create GeoJSON feature collection
feature_collection = FeatureCollection([tweetToFeature(tweet)
                                        for tweet in valid_tweets_enriched])

# Save the GeoJSON feature collection to the output file
with open(output_tweets_file, 'w') as output_tweets_f:
    output_tweets_f.write(geojson.dumps(feature_collection))

import praw
import tweepy
from apify_client import ApifyClient
import string
import re
import nltk
#nltk.download('stopwords')
#nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
from more_itertools import take
from nltk.corpus import wordnet

import json 
import sys
import praw
import os
import joblib

from textblob import TextBlob

from .preprocessing import Processing
import model_building.lda as lda
from model_building.bert_intent_classification import bert
from .google_vision import google_vision, image_describer

from dotenv import load_dotenv
load_dotenv()

# Text processing

def processing(text):

    text = Processing.deEmojify(text)
    text = text.replace('\n', ' ')
    text = text.replace('\t', ' ')
    text = re.sub(r'http\S+', '', text)
    
    text = Processing.remove_punctuation(text)
    text = text.lower()
    text = Processing.tokenization(text)
    text = Processing.remove_stopwords(text)
    text = Processing.lemmatizer(text)
    
    return text[0]

def instagram_post_descriptions(items):
    posts_features = []
    for item in items:

        post_features = {}
        
        post_features['source'] = 'Instagram'

        if item['#debug']['pageType'] == "user":
            post_features['url'] = item['#debug']['request']['url']
            post_features['userUsername'] = item['#debug']['userUsername']
            post_features['userFullName'] = item['#debug']['userFullName']
        
        post_features['pageType'] = item['#debug']['pageType']
        #elif item['#debug']['pageType'] == "hashtag":
        
        post_features['type'] = item['type']
        
        if item['type'] == 'Image':
            post_features['displayUrl'] = item['displayUrl']

        features = ['caption', 'hashtags', 'mentions', 'url', 'commentsCount', 'latestComments', 'firstComment', 'alt', 'likesCount', 'timestamp', 'locationName', 'locationId', 'images']
        for i in features: 
            try: 
                post_features[i] = item[i]
            except: 
                pass

        posts_features.append(post_features)
    return posts_features

def calling_analysis(overall):

    l = []
    for channel in overall.keys():
        for post in overall[channel]:

            # Translate to english ?!

            text = post['text']
            text = Processing.deEmojify(text)
            text = text.replace('\n', ' ')
            text = text.replace('\t', ' ')
            text = re.sub(r'http\S+', '', text)
            
            # TextBlob

            polarity, subjectivity = Processing.text_blob(text)
            post['polarity'] = polarity
            post['subjectivity'] = subjectivity

            # NER

            entities = Processing.named_entity_recognition(text)
            post['entities'] = entities 

            text = Processing.remove_punctuation(text)
            text = text.lower()
            text = Processing.tokenization(text)
            text = Processing.remove_stopwords(text)
            text = Processing.lemmatizer(text)
            post['text'] = text[0]
            
            words = [m for m in post['text'].split(' ') if ((m.isnumeric() == False) and (wordnet.synsets(m)))]
            l.append (words)

            for k,v in post.items():
                if (isinstance(v, (str))) and (v != 'text'):
                    post[k] = v.replace('\n', ' ')
                    post[k] = v.replace('\t', ' ')
                    post[k] = Processing.deEmojify(v)
                    post[k] = Processing.remove_punctuation(v)
                    
    # LDA

    # NT specificies the N of topics, and W the number of words upon which they are tho be based
    NT = 3
    W = 20
    #df = lda.LDA(NT, W, l)

    i = 0
    for channel in overall.keys():
        for post in overall[channel]:
            row = df.iloc[0]
            for col in df.columns: 
                post[col] = row[col]
            i += 1
        
    
    # BERT
    # maybe it is faster to run with all texts in one list - rather than looped

    #        text = post['text']
    #        intent = bert(text)
    #        post['Intent'] = intent

    # Google Vision

            if 'image_url' in post.keys(): 
                image = post['image_url']
                image_results = google_vision(image)
                image_details = image_describer(image_results)
                
                post['image_details'] = image_details

                # classify word i.e. logo, action, scene, object; and count the overall occurence

    return overall

# Retrieving Functions

def reddit(keywords, n, subreddits = ["all"]):
    """
    Unless otherwise specified r/all subreddit is considered. 
    """
    reddit_list = []

    username = os.environ['REDDIT_USERNAME']
    password = os.environ['REDDIT_PASSWORD']
    clientid = os.environ['REDDIT_CLIENTID']
    clientsecret = os.environ['REDDIT_SECRET']


    reddit = praw.Reddit(client_id=clientid,
    client_secret=clientsecret,
    password=password,
    user_agent='Reddit search data extractor by /u/' + username + '',
    username=username)

    sortsub = "relevance"

    subreddit_list = subreddits

    for subs in subreddit_list:
        for search in keywords:
            startNum = 0
            i = 0

            for submission in reddit.subreddit(subs.strip()).search(search, sort=sortsub):
                i += 1

                dic = {}
                dic['source'] = 'Reddit'
                features = ['created_utc', 'id', 'link_flair_text', 'name', 'num_comments', 'permalink', 'score', 'selftext', 'subreddit', 'title', 'upvote_ratio', 'url']
                for attr in features:
                    dic[attr] = getattr(submission, attr)

                comment_list = []
                for comment in submission.comments:
                    try:
                        comment_list.append(comment.body)
                    except: 
                        pass
                dic["comments"] = comment_list
                
                if not submission.is_self:
                    try:
                        if not 'is_video' in dir(submission):
                            image_urls = [submission.url]
                        elif 'media_metadata' in dir(submission):
                            image_dict = submission.media_metadata
                            image_urls = [image_item['s']['u'] for image_item in image_dict.values()]
                        dic["image_url"] = image_urls
                    except: 
                        pass 

                reddit_list.append(dic)

                if i == n:
                    break

        return reddit_list

def twitter(keywords, n):

    TWITTER_API_KEY = os.environ['TWITTER_API_KEY']
    TWITTER_API_SECRET_KEY = os.environ['TWITTER_API_SECRET_KEY']
    TWITTER_ACCESS_TOKEN = os.environ['TWITTER_ACCESS_TOKEN']
    TWITTER_ACCESS_TOKEN_SECRET = os.environ['TWITTER_ACCESS_TOKEN_SECRET']
    
    auth = tweepy.OAuthHandler(TWITTER_API_KEY, TWITTER_API_SECRET_KEY)
    auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)

    query = " OR ".join(keywords) + " -filter:retweets"
    #query = " OR ".join(keywords) + " filter:media -filter:retweets"

    tweets = tweepy.Cursor(api.search_tweets, q=query, include_entities=True).items(n)
    
    tweets_description = []
    for tweet in tweets: 
        tweet_description = {}
        tweet_description['source'] = 'Twitter'

        features = ['created_at', 'text', 'geo', 'coordinates', 'place', 'contributors', 'is_quote_status', 'retweet_count', 'favorite_count', 'possibly_sensitive', 'lang']
        included_features = [i for i in features if i in tweet._json]

        for i in included_features: 
            tweet_description[i] = tweet._json[i]

        if 'extended_entities' in tweet._json:
            if 'media' in tweet._json['entities'].keys():
                tweet_description['media_url'] = [i['media_url_https'] for i in tweet._json['extended_entities']['media'] if i['type'] == 'photo']
        elif 'entities' in tweet._json: 
            if 'media' in tweet._json['entities'].keys():
                tweet_description['media_url'] = [i['media_url_https'] for i in tweet._json['entities']['media'] if i['type'] == 'photo']
                
        if 'entities' in tweet._json:
            tweet_description['hashtags'] = tweet._json['entities']['hashtags']
            tweet_description['symbols'] = tweet._json['entities']['symbols']
            tweet_description['user_mentions'] = tweet._json['entities']['user_mentions']
            tweet_description['url'] = [i['url'] for i in tweet._json['entities']['urls']]

        if 'user' in tweet._json:
            users = tweet._json['user']
            user_features = ['name', 'screen_name', 'location', 'description', 'followers_count', 'friends_count', 'listed_count', 'created_at', 'favourites_count', 'verified', 'statuses_count', 'profile_background_image_url', 'profile_image_url', 'profile_banner_url']
            included_user_features = [i for i in user_features if i in users]

            for i in included_user_features: 
                tweet_description['user_' + i] = users[i]

        tweets_description.append(tweet_description)
        
    return tweets_description

def instagram_hashtag(keywords, n):
    APIFY_KEY = os.environ['APIFY_KEY']
    apify_client = ApifyClient(APIFY_KEY)
    
    items = []

    # Prepare the actor input
    run_input = {
        "hashtags": keywords,
        "resultsLimit": n,
    }

    # Run the actor and wait for it to finish
    run = apify_client.actor("zuzka/instagram-hashtag-scraper").call(run_input=run_input)

    # Fetch and print actor results from the run's dataset (if there are any)
    for item in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
        items.append(item)
       
    posts_features = instagram_post_descriptions(items)
        
    return posts_features


def instagram_account_scraper(username):
    items = []
    client = ApifyClient("apify_api_zXq5HtBOUL1pDAvLx7Slgn0FQsORNi2idd4l")

    # Prepare the actor input
    run_input = {
        "username": [username],
        "resultsLimit": N,
    }

    # Run the actor and wait for it to finish
    run = client.actor("zuzka/instagram-post-scraper").call(run_input=run_input)

    # Fetch and print actor results from the run's dataset (if there are any)
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        items.append(item)
        
    return items


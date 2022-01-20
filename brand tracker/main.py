import data_aggregation.scraper as scraper
import data_aggregation.socialme as socialmedia
import data_aggregation.restructuring_some as restructuring_some
import data_aggregation.image_retrieval as image_retrieval

import json 
import sys


params = json.loads(sys.argv[1])

#User Input
KEYWORD = params['keyword'].strip().lower()
KEYWORDS = [KEYWORD]

LEN_MIN = len(KEYWORD) if len(KEYWORD) < 4 else 4
N = int(params['nResults'].strip())

overall = {}

# EXECUTION scraper.py

# NOW THE QUESTION ARISES: DO WE MAKE N CALLS FOR EACH KEYWORD - OR - WHERE POSSIBLE E.G. THENEWSAPI GO WITH 'OR'
# KEYWORD_EXTENDED = semrush_keywords(KEYWORD, N)

overall_scraper = {}
overall_scraper['techradar'] = scraper.techradar(KEYWORD, N, LEN_MIN)
#overall_scraper['slashdot'] = scraper.slashdot(KEYWORD, N, LEN_MIN)
#overall_scraper['reddit'] = scraper.reddit(KEYWORD, N, LEN_MIN)
#overall_scraper['thenewsapi'] = scraper.thenewsapi(KEYWORD, LEN_MIN)
#overall_scraper['semrush'] = scraper.semrush_scraping(KEYWORD, N, LEN_MIN)

overall_scraper = {k:v for k,v in overall_scraper.items() if v}
sorted_articles = scraper.to_sorted_list(overall_scraper, KEYWORD)
scraper.add_article_db(sorted_articles, KEYWORD)
overall_scraper['sorted_articles'] = sorted_articles

overall['scraper'] = overall_scraper

# EXECUTION socialmedia.py

overall_socialmedia = {}

overall_socialmedia['reddit'] = socialmedia.reddit(KEYWORDS, N)
overall_socialmedia['twitter'] = socialmedia.twitter(KEYWORDS, N)
overall_socialmedia['instagram'] = socialmedia.instagram_hashtag(KEYWORDS, N)
    
overall_socialmedia['reddit'] = restructuring_some.cleaning_reddit(overall_socialmedia['reddit'])
overall_socialmedia['twitter'] = restructuring_some.cleaning_twitter(overall_socialmedia['twitter'])
overall_socialmedia['instagram'] = restructuring_some.cleaning_instagram(overall_socialmedia['instagram'])

overall_socialmedia = socialmedia.calling_analysis(overall_socialmedia)

overall['social_media'] = overall_socialmedia


# EXECUTION image_retrieval.py

""" This by itself is worthless. Needs to be ran through vision - and clustered/ classified """

overall_imageretrieval = {}
#overall_imageretrieval['google'] = image_retrieval.google_image_search(KEYWORD)
#overall_imageretrieval['bing'] = image_retrieval.bing_image_search(KEYWORD)

#overall['imageretrieval'] = overall_imageretrieval


##########################################################################################

params['overall'] = overall
print(params)

# ToDo:
# Database integration
# Neural Prophet 
    # Need for way more (granular) data. E.g. current twitter subscription only allows for the past seven days. 
# Causal Impact (Need for pre-defined unrelated yet correlated timeseries)
    # Depending on scenario we could take e.g. competitors keyword, other keyword, other market, overall action 
# Clustering/ classification of google vision image descriptor
    # Logic not clear to me yet. What classes to? As per mock-up? 
    # Logos - Objects - Actions - Scenes
    # Each image can fall into multiple categories
        # client.logo_detection
    # Google vision shows great accuracy - but not necessarily in terms of classification towards our objectives
# Enable customer direct data dump
    # Everything possible. Should be aligned with what client has availble. needs to follow certain (stringent) guidelines

# Entire project takes up over 5GB (pretrained models make up 90% of that)
# To be deleted: training_1\cp.ckpt.data-00000-of-00001
# To big to push to bitbucket

# I fear that at scale unsupervised training wont be feasible. Under the assumption that for unsupervised for than for supervised, modelling has to happen life
# i am using both mysql and sqlalchemy - should convert to only using one


from collections import Counter
import requests
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
from datetime import datetime, date

import re
from nltk.corpus import wordnet
from more_itertools import take

import json 
import sys

import praw
import os
import joblib

import mysql
import mysql.connector
from urllib.parse import urlparse

from .semrush_base import SemrushClient
from .preprocessing import Processing

import pymysql
from sqlalchemy.sql import text
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database

from dotenv import load_dotenv
load_dotenv()

#DB credentials
HOSTNAME="eu-cdbr-west-01.cleardb.com"
DBNAME="heroku_1b392502415228b"
UNAME=os.environ["DB_USER"]
PWD=os.environ["DB_PWD"]

EXPORT_COLUMNS = "Ab,Ac,Ad,Am,At,Bm,Cg,Cm,Co,Cp,Cr,Cv,Db,Dn,Ds,Dt,Fk,Fp,Fl,FKn,FPn,Hs,Ip,Kd,Lc,Li,Np,Nq,Nr,Oc,Of,Om,Or,Xn, \
Ot,P0,P1,P2,P3,P4,Pc,Pd,Ph,Po,Pp,Pr,Rh,Rk,Rr,Rt,Sh,Sn,Sv,Tc,Tg,Td,Tm,Tr,Ts,Tt,Um,Un,Ur,Vu,ads_count,ads_overall, \
advertisers_count,advertisers_overall,anchor,avg_positions,domain,domain_overall,external_num,first_seen,image_alt, \
internal_num,last_seen,media_ads_count,media_ads_overall,media_type,publishers_count,publishers_overall,redirect_url, \
response_code,source_title,source_size,source_url,target_title,target_url,target_url,text,text_ads_count,text_ads_overall, \
times_seen,title,type,visible_url,ascore,domain_ascore,page_ascore,category_name,neighbour,similarity,common_refdomains, \
domains_num,backlinks_num"


ALL_LINKS = []
TODAY = datetime.today()

# SUPPORTING FUNCTIONS

def semrush_keywords(keyword, n):
    result = client.phrase_related(keyword, database, display_limit=n, export_columns=export_columns)
    df = result_to_df_sql(result, 'phrase_related')
    
    df['Related_Relevance'] = pd.to_numeric(df['Related_Relevance'])

    keywords = np.unique(df.loc[(df['Related_Relevance'] > 0.1), 'Keyword'].values).tolist()
    keywords.append(keyword)
    
    return keywords

def result_to_df_sql(result, fn) :
    # Create SQLAlchemy engine to connect to MySQL Database
    engine = create_engine("mysql+pymysql://{user}:{pw}@{host}/{db}".format(host=HOSTNAME, db=DBNAME, user=UNAME, pw=PWD))

    df = pd.DataFrame(result)
    df.columns = df.columns.str.replace(' ','_')
    
    with engine.connect() as con:
        
        rs = con.execute("""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = '{0}'
            """.format(fn))
        
        if rs.fetchone()[0] != 1:
            table_attributes_list = []
            for column in df.columns: 
                table_attributes_list.append(f"{column} VARCHAR(255)")
            table_attributes = ", ".join(table_attributes_list)
            
            con.execute("CREATE TABLE {} ({})".format(fn, table_attributes))
        
    
        df.to_sql(fn, con=engine, if_exists='append', index=False)

        # Delete Duplicates
        statement1 = text("""CREATE TABLE xx AS SELECT DISTINCT * FROM {}""".format(fn))
        con.execute(statement1)
        statement2 = text("""DROP TABLE {}""".format(fn))
        con.execute(statement2)
        statement3 = text("""ALTER TABLE xx RENAME TO {}""".format(fn))
        con.execute(statement3)

    
    return df

def bs4(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content.decode('utf-8', 'ignore'), "html.parser")
    return soup

def to_sorted_list(overall, keyword):
    all_articles = []
    for source in overall.keys():
        for article in overall[source]:
            article['source'] = source
            if not keyword in article['content']: 
                article['content'][keyword] = 0
            all_articles.append(article)

    index_length = list(range(0, len(all_articles)))
    df1 = pd.DataFrame(all_articles, index=index_length)

    df = df1
    df['keyword_count'] = df1['content'].apply(lambda x: x[keyword])
    df['delta_published_at'] = df1['time'].apply(lambda x: (TODAY - datetime.strptime(x, '%m-%d-%Y')).days)
    df = df[['source', 'polarity','subjectivity', 'keyword_count', 'weighting', 'delta_published_at']]


    df.loc[:, 'weighting'] = pd.to_numeric(df['weighting'], errors='coerce')
    df.loc[:, 'weighting']  = df['weighting'].fillna(0)

    for col in df.columns:
        df.loc[:, col] = pd.to_numeric(df[col], errors='ignore')
    
    df = pd.get_dummies(df)

    dummy_cols = ["source_techradar", "source_slashdot", "source_reddit", "source_thenewsapi", "source_semrush"]
    for col in [i for i in dummy_cols if i not in df.columns]:
        df[col] = 0

    model = joblib.load("saved_model\latest_xgb.cls")
    df['user_vote_prediction'] = model.predict(df)

    df1 = df1.assign(user_vote_prediction = pd.Series(df['user_vote_prediction']).values)
    df1 = df1.assign(keyword_count = pd.Series(df['keyword_count']).values)
    df1 = df1.sort_values(["user_vote_prediction", "keyword_count", "subjectivity"], ascending = (False, False, True))
    df1= df1.drop(columns=['keyword_count'])
    sorted_articles = df1.to_dict('records')

    return sorted_articles

def add_article_db(sorted_articles, keyword):

    mydb = mysql.connector.connect(
        host=HOSTNAME,
        user=UNAME,
        passwd=PWD,
        database=DBNAME,
        charset = 'utf8',
        auth_plugin='mysql_native_password'
    )   

    if mydb.is_connected():
        cursor = mydb.cursor()
        cursor.execute("SELECT link FROM articles")
        result_set = cursor.fetchall()
        l = []
        for row in result_set:
            l.append(row[0])

        for i in sorted_articles: 
            if not i['link'] in l: 
                domain = urlparse(i['link']).netloc
                keyword_count = i['content'][keyword]
                user_vote = 0
                time = datetime.strptime(i['time'], '%m-%d-%Y')
                
                
                delta_published_at = (TODAY - datetime.strptime(i['time'], '%m-%d-%Y')).days

                mycursor = mydb.cursor()
                sql = "INSERT INTO articles (keyword, link, domain, source, published_at, delta_published_at, polarity, subjectivity, keyword_count, source_weighting, user_vote) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (keyword, i['link'], domain, i['source'], time, delta_published_at, i['polarity'], i['subjectivity'], keyword_count, i['weighting'], user_vote)
                mycursor.execute(sql, val)
                mydb.commit()
                mycursor.close()

    mydb.close()

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
    
    return text

def word_count(content, keyword, len_min):
    text = ' '.join(content)
    s_ = [x for x in text.split(" ") if len(x) >= len_min]
    dic = dict(sorted(Counter(s_).items(), key = lambda item: item[1], reverse = True))
    dic = {k: v for k, v in dic.items() if not k.isdigit()}

    keys_pop = []
    for w in dic.keys():
        syns = wordnet.synsets(w)
        if syns:
            if not syns[0].lexname().split('.')[0] == 'noun': 
                keys_pop.append(w)
        else: 
            keys_pop.append(w)

    for i in keys_pop:
        if i != keyword:
            dic.pop(i)

    content = take(8, dic.items())
    content = dict(content)
    return content

def generic_scraper(url, keyword, len_min):

    soup = bs4(url)
    
    content = soup.text

    content = content.replace("\n","")
    content = content.replace("\t","")
    
    processed_text = processing(content)

    sentiment_text = " ".join(processed_text)
    polarity, subjectivity = Processing.text_blob(sentiment_text)

    content_dic = word_count(processed_text, keyword, len_min)
    
    return polarity, subjectivity, content_dic

# SOURCE SCRAP/CALL FUNCTIONS

def techradar(keyword, n, len_min):
    techradar = []
    URL = f"https://www.techradar.com/search?searchTerm={keyword}"
    soup = bs4(URL)
    results = soup.find("div", class_="listingResults")
    results = results.find_all("a", class_="article-link")
    results = results[:n] if len(results) > n else results
    for result in results:
        content = []
        link = result["href"]   
        img = result.figure['data-original']
        title = processing(result.find("h3", class_="article-name").text.strip())
        d = result.find('time', class_="relative-date")['datetime']

        time = re.search("^[^T]*", d).group(0)
        time = datetime.strptime(time, '%Y-%m-%d').strftime('%m-%d-%Y')
        
        soup = bs4(link)
        
        body = soup.find("div", id="article-body")
        ps = body.find_all('p')

        for p in ps:
            raw_text = p.text.strip()
            processed_text = processing(raw_text)

            content += processed_text

        sentiment_text = " ".join(content)
        polarity, subjectivity = Processing.text_blob(sentiment_text)  
        content_dic = word_count(content, keyword, len_min)

        dic = {'title': title,'link': link, 'img': img, 'time': time, 'weighting': 0, 'polarity': polarity, 'subjectivity': subjectivity, 'content': content_dic}
        techradar.append(dic)

    return techradar

def slashdot(keyword, n, len_min):
    slashdot = []
    URL = f"https://slashdot.org/index2.pl?fhfilter={keyword}"
    soup = bs4(URL)
    results = soup.find("div", id="firehose")
    results = results.find_all('span', class_="story-title")

    results = results[:n] if len(results) > n else results

    for result in results:
        link = result.a['href']
        title = processing(result.a.text.strip())
        link = 'https:' + link
        soup = bs4(link)

        d = soup.find('span', class_='story-byline').time['datetime']
        time = datetime.strptime(d, 'on %A %B %d, %Y @%I:%M%p').strftime('%m-%d-%Y')

        weighting = soup.find("span", class_="comment-bubble").text.strip()
        content = soup.find('div', class_='body').text

        content = content.replace("\n","")
        content = content.replace("\t","")
        processed_text = processing(content)

        sentiment_text = " ".join(processed_text)
        polarity, subjectivity = Processing.text_blob(sentiment_text)
        content_dic = word_count(processed_text, keyword, len_min)

        dic = {'title': title,'link': link, 'img': "#", 'time': time, 'weighting': weighting, 'polarity': polarity, 'subjectivity': subjectivity, 'content': content_dic}
        slashdot.append(dic)
        
    return slashdot

def reddit(keyword, n, len_min):
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

    search_list = [keyword]
    sortsub = "relevance"

    subreddit_list = ['technology', 'tech', 'techsupport']

    for subs in subreddit_list:
        for search in search_list:
            startNum = 0
            i = 0
            for submission in reddit.subreddit(subs.strip()).search(search, sort=sortsub):
                i += 1

                if not submission.url in ALL_LINKS:
                    
                    
                    ALL_LINKS.append(submission.url)
                    title = processing(submission.title)

                    # Create a weighting from date/ score/ comments
                    #weighting_comments = submission.comments
                    weighting_score = submission.score

                    comments = submission.num_comments
                    link = submission.url
                    time = datetime.utcfromtimestamp(submission.created).strftime('%m-%d-%Y')
                    polarity, subjectivity, content_dic = generic_scraper(link, keyword, len_min)

                    dic = {'title': title,'link': link, 'img': '#', 'time': time, 'weighting': weighting_score, 'polarity': polarity, 'subjectivity': subjectivity, 'content': content_dic}
                    reddit_list.append(dic)
                    
                if i == n:
                    break

    return reddit_list
 
def thenewsapi(keyword, len_min):
    thenewsapi = []
    API_KEY = os.environ['THENEWSAPI_KEY']

    parameters = {
        "api_token": API_KEY,
        "search": keyword, 
        "language": "en",
        "categories": "tech,science,business"
    }

    response = requests.get("https://api.thenewsapi.com/v1/news/top", params=parameters)
    json = response.json()

    for i in json['data']:

        if not i['url'] in ALL_LINKS:
            ALL_LINKS.append(i['url'])

            title = processing(i['title'])
            link = i['url']
            img = i['image_url']
            d = datetime.fromisoformat(i['published_at'][:-1])
            time = d.strftime('%m-%d-%Y')
            weighting = i['relevance_score']
            
            polarity, subjectivity, content_dic = generic_scraper(i['url'], len_min)

            dic = {'title': title,'link': link, 'img': img, 'time': time, 'weighting': weighting, 'polarity': polarity, 'subjectivity': subjectivity, 'content': content_dic}
            thenewsapi.append(dic)
            
    return thenewsapi

def semrush_scraping(keyword, n, len_min):

    semrush = []
    client_semrush = SemrushClient(key=os.environ['SEMRUSH_API_KEY'])
    database = 'us'

    # ORGANIC RESULTS
    result = client_semrush.phrase_organic(keyword, database, display_limit=n, export_columns=EXPORT_COLUMNS)
    
    # MAYBE ADD PHRASE AND CREATED_AT PARAMETER
    result_to_df_sql(result, 'phrase_organic')
    for i in result:

        title = re.search(r"^[^.]*", i['Domain']).group(0)
        link = i['Url'] 
        weighting = i['Traffic Cost']
        # time is not really relevant - since its not articles - nor is it retrievable (as i see it right now)
        
        # INDEXED PAGES
        result = client_semrush.backlinks_pages(target=link, target_type='root_domain', display_limit=n, export_columns=['source_url','source_title','response_code','backlinks_num','domains_num','last_seen','external_num','internal_num'])
        result_to_df_sql(result, 'backlinks_pages')
        # A PROBLEM I SEE IS THAT THE PAGES THAT ARE LINKED/ PROMOTED VIA KEYWORDS ARE THOSE THAT "LEAD TO CONVERSIONS" NOT THOSE WHERE CONTENT IS ON
        
        polarity = 0
        subjectivity = 0
        content_dic = {}

        for sub_link in result: 
            
            ipolarity, isubjectivity, icontent_dic = generic_scraper(sub_link['source_url'], len_min)

            polarity += ipolarity
            subjectivity += isubjectivity

            for key, value in icontent_dic.items(): 
                if key in content_dic.keys():
                    content_dic[key] += value  
                else: 
                    content_dic[key] = value 

            # do i weigh equally per page - or by e.g. length of string. For now equally
        
        polarity = polarity / len(result)
        subjectivity = subjectivity / len(result)

        dic = dict(sorted(Counter(content_dic).items(), key = lambda item: item[1], reverse = True))
        content_dic = take(8, dic.items())
        content_dic = dict(content_dic)

        today = date.today()
        time = today.strftime('%m-%d-%Y')

        dic = {'title': title,'link': link, 'img': '#', 'time': time, 'weighting': weighting, 'polarity': polarity, 'subjectivity': subjectivity, 'content': content_dic}
        semrush.append(dic)
    return semrush

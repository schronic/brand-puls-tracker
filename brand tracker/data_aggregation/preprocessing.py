import time
from datetime import datetime, date

from gensim.parsing.preprocessing import remove_stopwords
import string
import re
import nltk
#nltk.download('stopwords')
#nltk.download('wordnet')
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet

from textblob import TextBlob
import spacy

class Processing(object):

    def text_blob(text):
        '''
        Takes string returns polarity and subjectivity in according order. 
        '''
        sentiment = TextBlob(text).sentiment
        polarity = sentiment.polarity
        subjectivity = sentiment.subjectivity
        return polarity, subjectivity

        
    def named_entity_recognition(text):
        # Load English tokenizer, tagger, parser and NER
        nlp = spacy.load("en_core_web_sm")

        # Process whole documents
        doc = nlp(text)

        # Find named entities, phrases and concepts
        l = []
        for entity in doc.ents:
            l.append([entity.text, entity.label_])

        return l

    # Text Pre-Processing

    def remove_punctuation(text, characters = None):
        '''
        Removes punctuation as predefined in string.punctuation. Possibility to append string by providing str argument of all character not to include either. Takes string returns string.
        '''
        string.punctuation += '’–'
        if characters: 
            string.punctuation += characters
            string.punctuation = ''.join(set(string.punctuation))

        punctuationfree="".join([i for i in text if i not in string.punctuation])
        return punctuationfree

    def tokenization(text):
        '''
        Splits based on regex W+. Takes string returns list of words.
        '''
        tokens = re.split('W+',text)
        return tokens

    #Stop words present in the library
    
    def remove_stopwords(text):
        stopwords = nltk.corpus.stopwords.words('english')
        '''
        Removes predefined stopwords (nltk corpus). Takes list of words returns list of words.
        '''
        output= [i for i in text if i not in stopwords]
        return output

    
    def lemmatizer(text):
        wordnet_lemmatizer = WordNetLemmatizer()
        '''
        Lemmatize on a word to word bases. Takes list of words, returns list of words.
        '''
        lemm_text = [wordnet_lemmatizer.lemmatize(word) for word in text]
        return lemm_text

    def deEmojify(text):
        '''
        Strip all non-ASCII characters to remove emoji characters
        '''
        text = text.encode('ascii', 'ignore').decode('ascii')
        return text


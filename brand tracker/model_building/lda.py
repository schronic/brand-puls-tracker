import pandas as pd
import os #importing os to set environment variable

""" Import required libraries for topic modeling"""

import gensim
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models.wrappers import LdaMallet

from gensim.models.coherencemodel import CoherenceModel
from gensim import similarities

from data_aggregation.preprocessing import Processing


def LDA (NT, W, data):
                                
    os.environ['MALLET_HOME'] = r'.\mallet-2.0.8'
    mallet_path = r'.\mallet-2.0.8\bin\mallet'


    # data: list of lists containing words (as defined by wordnet and no numeric)
    dictionary = corpora.Dictionary(data)

    # Converting list of documents (corpus) into Document Term Matrix using dictionary prepared above.
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in data]

    number_of_topics = NT
    words = W 

    ldamallet30 = LdaMallet(mallet_path, corpus=doc_term_matrix, num_topics=number_of_topics, id2word=dictionary)


    def format_topics_sentences(ldamodel=None, corpus=doc_term_matrix):
        # Init output
        sent_topics_df = pd.DataFrame()

        # Get main topic in each document
        for i, row in enumerate(ldamodel[corpus]):
            # print(row)
            row = sorted(row, key=lambda x: (x[1]), reverse=True)
            # Get the Dominant topic, Perc Contribution and Keywords for each document
            for j, (topic_num, prop_topic) in enumerate(row):
                if j == 0:  # => dominant topic
                    wp = ldamodel.show_topic(topic_num)
                    topic_keywords = ", ".join([word for word, prop in wp])
                    sent_topics_df = sent_topics_df.append(pd.Series([int(topic_num), round(prop_topic,4), topic_keywords]), ignore_index=True)
                else:
                    break


        return(sent_topics_df)

    df_weight_distribution = format_topics_sentences(ldamodel=ldamallet30, corpus=doc_term_matrix)

    # Format
    df_weight_distribution.columns = ['Dominant_Topic', 'Topic_Perc_Contrib', 'Keywords']

    df_weight_distribution['Topic_Weights'] = ''

    for i in range(len(data)):
        
        dic = {str(weight[0]):weight[1] for weight in ldamallet30[doc_term_matrix[i]]}

        df_weight_distribution.at[i,'Topic_Weights'] = dic

    return df_weight_distribution
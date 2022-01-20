import warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import roc_auc_score
from xgboost import XGBClassifier
from sklearn.model_selection import StratifiedKFold

from sklearn.model_selection import train_test_split
import joblib

import mysql
import mysql.connector

from datetime import date, datetime

import os
import sys

from dotenv import load_dotenv

load_dotenv()


today = date.today()

d1 = today.strftime("%d%m%Y")
mydb = mysql.connector.connect(
    host="eu-cdbr-west-01.cleardb.com",
    user=os.getenv("DB_USER",
    passwd=os.getenv("DB_PWD"),
    database="heroku_1b392502415228b",
    charset = 'utf8',
    auth_plugin='mysql_native_password'
) 

if mydb.is_connected():
    df = pd.read_sql("""
            SELECT * FROM articles
            """, con = mydb)
    mydb.close()



df_clf = df[['source', 'polarity', 'delta_published_at', 
       'subjectivity', 'keyword_count', 'source_weighting', 'user_vote']]


df_clf = pd.get_dummies(df_clf)


X = df_clf.drop(columns=['user_vote'])
y = df_clf['user_vote']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.1, random_state = 42)

# A parameter grid for XGBoost
params = {
        'min_child_weight': [1, 5, 10],
        'gamma': [0.5, 1, 1.5, 2, 5],
        'subsample': [0.6, 0.8, 1.0],
        'colsample_bytree': [0.6, 0.8, 1.0],
        'max_depth': [3, 4, 5]
        }     
       

xgb = XGBClassifier(learning_rate=0.02, n_estimators=600, objective='binary:logistic',
                    silent=True, nthread=1)
folds = 3
param_comb = 5
skf = StratifiedKFold(n_splits=folds, shuffle = True, random_state = 1001)
     

grid = GridSearchCV(estimator=xgb, param_grid=params, scoring='roc_auc', n_jobs=4, cv=skf.split(X_train,y_train), verbose=3 )
grid.fit(X_train, y_train)

results = pd.DataFrame(grid.cv_results_)
results.to_csv(f"xgb-grid-search-results-{d1}.csv", index=False)

joblib.dump(grid.best_estimator_, "latest_xgb.cls")

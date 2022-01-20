# Marketing tracker

The project intents to provide a tool to track the pulse of the time. 
This code constitutes the (backend) foundation of an application, meant to aggregate, transform and load (ETL) as well as analyse publically accessible textual data. 

Querying is conducted on a keyword basis. 
While an integration with semrush's: alike keywords recommender is fully developed and ready for deployment; my inital perception is that that would change the focus of the work from insights into industry-trends to SEO opptimization. 

There are a number of credentials (e.g. API KEYS) needed to run the application. 
Starting script is: node index.js
Localhost port is: 5000

Data is aggregated from news sites (thenewsapi, slashdot, reddit, techradar) and social media platforms (reddit, instagram, twitter).
### On an individual textual instance analysis is conducted, providing: 
- Polarity
- Subjectivity
- Topic 
- Intent
- Named entity recognition (NER)

Further an item-to-item recommender system is integrated, ordering at times huge amounts of content (currently only news sources)

### Next steps include:
- Broadening of data source integration 
- Storage on insights to DB
- Standardization of a number of currently unclean and ineffective processes
- Timeseries analysis (causal impact, and forecasting)



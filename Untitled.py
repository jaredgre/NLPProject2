#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import re
import tweepy
from tweepy import Client
from textblob import TextBlob
import numpy as np
import matplotlib.pyplot as plt
import datetime
import time
import pandas as pd


# In[ ]:


CONSUMER_KEY = ''
CONSUMER_SECRET =''
BEARER_TOKEN ='' #only bearer token needed below
ACCESSS_TOKEN = ''
ACCESS_TOKEN_SECRET= ''


# In[ ]:


#Adapted from https://www.geeksforgeeks.org/twitter-sentiment-analysis-using-python/
class TwitterClient(object):
    '''
    Generic Twitter Class for sentiment analysis.
    '''
    def __init__(self):
        '''
        Class constructor or initialization method.
        '''
        # keys and tokens from the Twitter Dev Console
        consumer_key = CONSUMER_KEY
        consumer_secret = CONSUMER_SECRET
        access_token = ACCESSS_TOKEN
        access_token_secret = ACCESS_TOKEN_SECRET
  
        # attempt authentication
        try:
            self.auth = Client(bearer_token=BEARER_TOKEN)
            # create OAuthHandler object
#             self.auth = OAuthHandler(consumer_key, consumer_secret)
#             # set access token and secret
#             self.auth.set_access_token(access_token, access_token_secret)
#             # create tweepy API object to fetch tweets
            self.api = tweepy.API(self.auth)
        except:
            print("Error: Authentication Failed")
  
    def clean_tweet(self, tweet):
        '''
        Utility function to clean tweet text by removing links, special characters
        using simple regex statements.
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())  
            
    def get_tweet_sentiment(self, tweet):
        '''
        Utility function to classify sentiment of passed tweet
        using textblob's sentiment method
        '''
        # create TextBlob object of passed tweet text
        analysis = TextBlob(self.clean_tweet(tweet))
        # set sentiment
        if analysis.sentiment.polarity > 0:
            return 0#'positive'
        elif analysis.sentiment.polarity == 0:
            return 1#'neutral'
        else:
            return 2#'negative' 
        
    def get_sentiments(self, query,date, parts = 10):
        #parts controls how many samples to take per unit time
        #date must be YYYY-MM-DDTHH:mm:ssZ 
        sentiments = np.zeros(3)
        times = ['T'+str(i*datetime.timedelta(days = 1/parts))+'Z' for i in range(parts)]  
        times.append('T23:59:59Z')
        for i in range(parts):
            try:
                print(date)
                print(date+times[i])
                # call twitter api to fetch tweets
                fetched_tweets = self.auth.search_recent_tweets(query = query,start_time=date+times[i],end_time=date+times[i+1],max_results=100)[0]
                # parsing tweets one by one
                for tweet in fetched_tweets:
                    sentiments[self.get_tweet_sentiment(tweet["text"])] += 1

            except tweepy.TweepyException as e:
                # print error (if any)
                print("Error : " + str(e))
            
            time.sleep(15*60/1000+10) #To not hit rate limits
        return sentiments/sum(sentiments)/parts*100 #returns percents
  


# In[ ]:


start_date = '2022-10-01' #YYYY-MM-DD format
end_date = '2022-10-16'
dates = pd.date_range(start=start_date, end=end_date)
delta = len(dates)
#stores sentiment data by day; In order, Positive, Neutral, and Negative
Fetterman_sentiments = np.zeros((delta,3))
Oz_sentiments = np.zeros((delta,3))
# creating object of TwitterClient Class
api = TwitterClient()
# calling function to get tweets
for date in dates:
    #can only pull 100 tweets at a time
    #pull tweets and score by sentiment
    Fetterman_sentiments[date] = api.get_sentiments(query = "Fetterman",date=date,parts=100)
    Oz_sentiments[date] = api.get_sentiments(query = "Oz",date=date,parts=100)


# In[ ]:


plt.plot(dates,Oz_sentiments,label=["Postive","Negative","Neutral"])
plt.title("Oz Twitter Sentiment over time")
plt.xlabel("Date")
plt.axvline(pd.to_datetime('10-11-2022'),color='black')
plt.axvline(pd.to_datetime('09-30-2022'),color='black')
plt.xticks(rotation=90)
plt.legend(loc="right")
plt.show()


# In[ ]:


plt.plot(dates,Fetterman_sentiments,label=["Postive","Negative","Neutral"])
plt.title("Fetterman Twitter Sentiment over time")
plt.xlabel("Date")
plt.axvline(pd.to_datetime('10-11-2022'),color='black')
plt.axvline(pd.to_datetime('09-30-2022'),color='black')
plt.xticks(rotation=90)
plt.legend(loc="right")
plt.show()


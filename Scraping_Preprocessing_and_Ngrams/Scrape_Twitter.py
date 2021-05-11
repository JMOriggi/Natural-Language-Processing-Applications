from twython import Twython, TwythonError
import json
import re

class Scrape_Twitter():
    def __init__(self): 
        self.__consumerKey = "<your key>"
        self.__consumerSecret = "<your key>"
        
        print("-- Obtaining OAuth 2 token")
        twitter = Twython(self.__consumerKey, self.__consumerSecret, oauth_version=2)
        ACCESS_TOKEN = twitter.obtain_access_token()
        self.twitter = Twython(self.__consumerKey, access_token=ACCESS_TOKEN)
        print("-- Access token granted")
   
    def search_word(self, word, limit):
        """
        :param model: search key word
        :param count: number of result we fetch
        :return result: raw result in dict type (ready for json)
        """
        raw_data = self.twitter.search(q=word, count=limit, lang='en', result_type='recent', tweet_mode='extended')
        index = len(raw_data['statuses'])
        count = limit - index
        max_id = raw_data['statuses'][-1]['id'] -1
        print('-- Tweets fetched: ', index)
        print('-- max_id: ', max_id)
        while index <= count:
            res = self.twitter.search(q=word, count=limit, max_id= max_id, lang='en', result_type='recent', tweet_mode='extended')
            raw_data['statuses'].extend(res['statuses'])
            index = index + len(res['statuses'])
            max_id = raw_data['statuses'][-1]['id'] -1
            print('-- Tweets fetched: ', index)
            print('-- max_id: ', max_id)
        return raw_data
     
    def search_user(self, user, count):
        """
        :param user: twitter user to scrape
        :param count: number of result we fetch
        """
        try:
           user_timeline = self.twitter.get_user_timeline(screen_name=user, count=count)
        except TwythonError as e:
            print(e)
        for tweets in user_timeline:
            print(tweets['text'])
    
    @staticmethod
    def extract_tweet(res):
        """
        :param res: result raw block from previous search
        :return tweet_list: the list with only tweets text: RT or normal tweet
        """
        tweet_list = [el['full_text'] if not el['full_text'].startswith('RT @') else el['retweeted_status']['full_text'] for el in res]
        return tweet_list
    
    @staticmethod
    def extract_country_info(res):
        """
        :param res: result raw block from previous search
        :return lists: the list with only country tweets and list with infos, same ordering
        """
        country_tweet_list = []
        country_code_list = []
        country_name_list = []
        for tweet in res:
            if tweet['place'] != None:
                country_code = tweet['place']['country_code']
                country = tweet['place']['full_name']
                country_tweet_list.append(tweet)
                country_code_list.append(country_code)
                country_name_list.append(country)
        country_tweet_list = Scrape_Twitter.extract_tweet(country_tweet_list)
        return country_tweet_list, country_code_list, country_name_list
    
    @staticmethod
    def clean_tweet(tweet_list):
        """
        :param model: the list with all the tweet
        :return tweet_list: the list with all the tweet cleaned ( other than words it keeps only the period punctuation to be able to sent tokenize)
        """
        for i in range(len(tweet_list)):
            tweet = tweet_list[i]
            #tweet = tweet.encode('utf-8','ignore').decode("utf-8") # remove weird character
            tweet = re.sub('@[^\s]+', '', tweet) # delete username
            tweet = tweet.replace('@', '') # @
            #tweet = tweet.replace('\n', '') 
            #tweet = re.sub(r'#([^\s]+)', ' ', tweet) # delete hashtag 
            tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', '', tweet) # delete web address
            #tweet = re.sub('[^A-Za-z0-9.!?\-\' ]+',' ', tweet) #Remove all characters which are not alphabets, numbers or whitespaces.
            tweet = re.sub("[\s]+"," ",tweet) # delete aditional white spaces
            #tweet = re.sub(r'#([^\s]+)', r' \1', tweet) # replace hashtag with only the word
            #tweet = tweet.lower()
            tweet = tweet.strip()
            tweet_list[i] = tweet
        return tweet_list
    
        

if __name__ == "__main__":
    
    scrape_twitter = Scrape_Twitter()
    
    ## Get raw tweets
    res = scrape_twitter.search_word('covid', 10000)
    
    ## Save raw data
    with open('tweets_raw.json', 'w') as f:
        json.dump(res, f)
    
    '''## Extract and clean tweets
    with open('data/tweets_raw.json') as f:
        data = json.load(f)
    tweet_list = data['statuses'][0:100]
    
    country_tweet_list, country_code_list, country_name_list = scrape_twitter.extract_country_info(tweet_list)
    
    tweet_list = scrape_twitter.extract_tweet(tweet_list)
    tweet_list = scrape_twitter.clean_tweet(tweet_list)
    print(tweet_list)'''
    
          
    
    
    
    
    
    
    
    
    

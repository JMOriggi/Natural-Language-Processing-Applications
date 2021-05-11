import Preprocessing as pre
from Scrape_Twitter import Scrape_Twitter
import Language_Model as lm
from nltk.lm import KneserNeyInterpolated, MLE
import json


## Get twitter raw text
with open('tweets_raw.json') as f:
    tweets_raw = json.load(f)
tweets_raw = tweets_raw['statuses']
tweet_list = Scrape_Twitter.extract_tweet(tweets_raw)
tweet_list = Scrape_Twitter.clean_tweet(tweet_list)


## ------------- Q1
## Preprocess the data: segmenting, tokenizing, lower casing, and padding with begin-of-sentence and end-of-sentence (this last step done after)
## Train preprocessing: a list of sentences (from all the tweets)  containing a list of tokens
tweet_list_train = tweet_list[1000:10000]
train_data = [pre.tokenize_word(tweet) for tweet in tweet_list_train]
train_data = [pre.clean_tokens(tweet) for tweet in train_data ]
train_data = pre.clean_sent(train_data)
train_data = [pre.token_to_text(tweet) for tweet in train_data]

## Test preprocessing: list of tweets that contain a list of sentences with eos containing a list of tokens
tweet_list_test = tweet_list[0:1000]
test_data = [pre.tokenize_word(tweet) for tweet in tweet_list_test]
test_data = [pre.clean_tokens(tweet) for tweet in test_data]
test_data = pre.clean_sent(test_data)
test_data = [pre.token_to_text(tweet) for tweet in test_data]

test_data_uni = lm.pad_eos(1, test_data) 
test_data_bi = lm.pad_eos(2, test_data) 
test_data_tri = lm.pad_eos(3, test_data) 

## Train models: unigram, bigram, trigram
## train a trigram KneserNeyInterpolated language model (based on the 9,000 tweets)
model_uni = lm.train_ngram(KneserNeyInterpolated(1), train_data, ngram=1)
model_bi = lm.train_ngram(KneserNeyInterpolated(2), train_data, ngram=2)
model_tri = lm.train_ngram(KneserNeyInterpolated(3), train_data, ngram=3)

## Test models: plot perplexity
## Important to use Kneser model for the 0 probability smoothing (otherwise perplexity goes to inf)
uni_perplexity = 0
bi_perplexity = 0
tri_perplexity = 0
for uni, bi, tri in zip(test_data_uni, test_data_bi, test_data_tri):
    uni_perplexity += model_uni.perplexity(uni)
    bi_perplexity += model_bi.perplexity(bi)
    tri_perplexity += model_tri.perplexity(tri)
uni_perplexity_avg = uni_perplexity/len(test_data)
bi_perplexity_avg = bi_perplexity/len(test_data)
tri_perplexity_avg = tri_perplexity/len(test_data)
print("Avergae perplexity on test_data model_uni = ", uni_perplexity_avg)
print("Avergae perplexity on test_data model_bi = ", bi_perplexity_avg)
print("Avergae perplexity on test_data model_tri =", tri_perplexity_avg)




## ------------- Q2
## Generate with models: 10 tweets for each model (total 30)
## If too long can use MLE instead of Kneser
print('\n-------Generate sentence')  
model_uni = lm.train_ngram(MLE(1), train_data, ngram=1)
model_bi = lm.train_ngram(MLE(2), train_data, ngram=2)
model_tri = lm.train_ngram(MLE(3), train_data, ngram=3)
max_len = 20
for i in range(1):
    print('Generate round ',i)
    print("Generated from model_uni = ", lm.generate_sent(model_uni, max_len))
    print("Generated from model_bi = ", lm.generate_sent(model_bi, max_len))
    print("Generated from model_tri = ", lm.generate_sent(model_tri, max_len))



'''
## ------------- Q3 
## VADER model: compute the sentiment of each tweet in all your 10,000 tweets
tweet_tok = [pre.tokenize_sent(tweet) for tweet in tweet_list]
tweet_tok = [[str(sent) for sent in tweet] for tweet in tweet_tok] # token spacy type must be casted

average_compound = 0
pos_tweet = []
neg_tweet = []
for tweet in tweet_tok:
    total_pos, total_neg, total_compound = lm.sentiment_tweet(tweet)
    average_compound += total_compound
    ## save positive tweet for later
    if total_pos > abs(total_neg):
        pos_tweet.append(tweet)
    ## save negative tweet for later
    if total_pos < abs(total_neg):
        neg_tweet.append(tweet)
print("Sentiment average score in all tweets =", average_compound/len(tweet_list))




## After removing stopwords, Top 10 words for negative and positive tweets
## Positive tweets
pos_tweet_tok = [pre.tokenize_word(sent) for tweet in pos_tweet for sent in tweet]
pos_tweet_tok = [pre.clean_tokens(sent, with_stop_word=False, with_punct = False, with_numb = False) for sent in pos_tweet_tok]
pos_tweet_tok = [[token.text.lower() for token in sent] for sent in pos_tweet_tok] # remove punct
print(pos_tweet_tok[0])
_, pos_tweet_voc = pre.build_voc(pos_tweet_tok)
res = pre.word_frequency(pos_tweet_voc)
print('\nVocabulary words frequency positive tweets')
print(res)

## Negative tweets
neg_tweet_tok = [pre.tokenize_word(sent) for tweet in neg_tweet for sent in tweet]
neg_tweet_tok = [pre.clean_tokens(sent, with_stop_word=False, with_punct = False, with_numb = False) for sent in neg_tweet_tok]
neg_tweet_tok = [[token.text.lower() for token in sent] for sent in neg_tweet_tok] # remove punct
print(neg_tweet_tok[0])
_, neg_tweet_voc = pre.build_voc(neg_tweet_tok)
res = pre.word_frequency(neg_tweet_voc)
print('\nVocabulary words frequency negative tweets')
print(res)





## Using only tweets that are geo-located with country code US i.e., has non-null child
## object place in its json, extract the state information from the full name child object of place. Report
## Average sentiment compound scores from each of the state you found. 
## Which state in your data has the most positive users, which state has the most negative users
country_tweet_list, country_code_list, country_name_list = Scrape_Twitter.extract_country_info(tweets_raw)
country_tweet_list = Scrape_Twitter.clean_tweet(country_tweet_list)
country_tweet_tok = [pre.tokenize_sent(tweet) for tweet in country_tweet_list]
country_tweet_tok = [[str(sent) for sent in tweet] for tweet in country_tweet_tok]
compound_list = []
for i in range(len(country_tweet_tok)):
    tweet = country_tweet_tok[i]
    total_pos, total_neg, total_compound = lm.sentiment_tweet(tweet)
    compound_list.append(total_compound)

print('\nMost positive countries ranking')
top_index = sorted(range(len(compound_list)), key=lambda i: compound_list[i])
pos = len(top_index)
for i in top_index:
    print('Position: ',pos,' - score:',compound_list[i],' - state: ', country_code_list[i], ' - state info: ', country_name_list[i])
    pos -= 1

print('Top positive: ',compound_list[top_index[-1]])
print('Last negative: ',compound_list[top_index[0]])

'''



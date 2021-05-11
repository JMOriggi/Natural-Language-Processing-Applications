import Preprocessing as pre
from Scrape_Wikipedia import Scrape_Wikipedia
from Scrape_Twitter import Scrape_Twitter
import Language_Model as lm
import nltk
from nltk.lm import KneserNeyInterpolated, MLE
from nltk.util import pad_sequence, everygrams, ngrams, flatten
from nltk.lm.preprocessing import padded_everygram_pipeline, pad_both_ends
import json
import itertools
from functools import partial
        
## Get wikipedia raw text
with open("wikipedia_raw.txt", "r", encoding='utf-8') as f:
    wiki_raw_text = f.read() 
wiki_raw_text = wiki_raw_text

## Get twitter raw text
with open('tweets_raw.json') as f:
    tweets_raw = json.load(f)
tweets_raw = tweets_raw['statuses']
tweet_list = Scrape_Twitter.extract_tweet(tweets_raw)
tweet_list = Scrape_Twitter.clean_tweet(tweet_list)
 

## ------------- Q1
## Sentence split, tokenize, lemmatize, lower case, remove stop words and plot top 20 words
wiki_save = pre.tokenize_sent_word(wiki_raw_text)
wiki_tok = [pre.clean_tokens(sent, with_stop_word=False, with_punct=False, with_numb=False) for sent in wiki_save]
wiki_tok = pre.clean_sent(wiki_tok)
wiki_tok = [pre.lemmatize(s) for s in wiki_tok]

## Generate word cloud and plot frequency top 20
wiki_voc, wiki_voc_dup = pre.build_voc(wiki_tok)
res = pre.word_frequency(wiki_voc_dup)
print('\nVocabulary words frequency Wikipedia')
print(res)
pre.plot_wordcloud(wiki_voc_dup)


## ------------- Q2
## Sentence split, tokenize, lemmatize, lower case, then remove stop words from your 1,000 test tweets
tweet_tok = [pre.tokenize_sent_word(tweet) for tweet in tweet_list[0:1000]]
tweet_tok = [pre.clean_tokens(sent, with_stop_word=False, with_punct=False, with_numb=False) for tweet in tweet_tok for sent in tweet]
tweet_tok = pre.clean_sent(tweet_tok)
tweet_tok = [pre.lemmatize(sent) for sent in tweet_tok]
twitter_test_types, twitter_test_tokens = pre.build_voc(tweet_tok)


## word types in test tweets that are OOV / # word types in test tweets (when vocab is constructed from all your scraped wikipedia)
oov_types_counter = 0
for word in twitter_test_types:
    if word not in wiki_voc:
        oov_types_counter += 1
print('-- OOV for types test twitter word types in wiki vocabulary: ',oov_types_counter/len(twitter_test_types))


## word tokens in test tweets that are OOV/ #word tokens in test tweets (when vocab is constructed from all your scraped wikipedia)
oov_tokens_counter = 0
for token in twitter_test_tokens:
    if token not in wiki_voc:
        oov_tokens_counter += 1
print('-- OOV for test twitter tokens in wiki vocabulary: ',oov_tokens_counter/len(twitter_test_tokens))


## Compute the OOV-rate (tokens not words types) of your tweet test set when using your 9,000 train tweets, to construct your vocabulary/lexicon
tweet_train_tok = [pre.tokenize_sent_word(tweet) for tweet in tweet_list[1000:3000]]
tweet_train_tok = [pre.clean_tokens(sent, with_stop_word=False, with_punct = False, with_numb=False) for tweet in tweet_train_tok for sent in tweet]
tweet_train_tok = pre.clean_sent(tweet_train_tok)
tweet_train_tok = [pre.lemmatize(sent) for sent in tweet_train_tok]
twitter_voc, _ = pre.build_voc(tweet_train_tok)

## word tokens in test tweets that are OOV/ #word tokens in test tweets (when vocab is constructed from train tweets)
oov_tokens_counter = 0
for token in twitter_test_tokens:
    if token not in twitter_voc:
        oov_tokens_counter += 1
print('-- OOV for twitter test tokens in train twitter vocabulary: ',oov_tokens_counter/len(twitter_test_tokens))


## ------------- Q3
## Sentence split, tokenize, and lower case the Wikipedia data you have collected, then get the first 9,000
wiki_tok = [pre.clean_tokens(s) for s in wiki_save]
wiki_tok = pre.clean_sent(wiki_tok)
wiki_tok = [pre.token_to_text(sent) for sent in wiki_tok]
wiki_tok = wiki_tok[0:9000]

## train a trigram KneserNeyInterpolated language model (based on these 9,000 sentences wikipedia)
model_tri = lm.train_ngram(KneserNeyInterpolated(3), wiki_tok, ngram=3)

## Average perplexity of the model on test Twitter sentences (the one that contains 1,000 tweets)
tweet_list_test = tweet_list[0:1000]
test_data = [pre.tokenize_word(tweet) for tweet in tweet_list_test]
test_data = [pre.clean_tokens(tweet) for tweet in test_data]
test_data = pre.clean_sent(test_data)
test_data = [pre.token_to_text(tweet) for tweet in test_data]
test_data = lm.pad_eos(3, test_data) 

tri_perplexity = 0
for tweet in test_data:
    tri_perplexity += model_tri.perplexity(tweet)
tri_perplexity_avg = tri_perplexity/len(tweet_list_test)
print("Perplexity on test_data model_tri =", tri_perplexity_avg)






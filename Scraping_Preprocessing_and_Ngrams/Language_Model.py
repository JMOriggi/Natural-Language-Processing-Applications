import nltk
from nltk.lm import KneserNeyInterpolated
from nltk.util import pad_sequence, everygrams, ngrams, flatten
from nltk.lm.preprocessing import padded_everygram_pipeline, pad_both_ends
from nltk.tokenize.treebank import TreebankWordDetokenizer
detokenize = TreebankWordDetokenizer().detokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
sentiment = SentimentIntensityAnalyzer()


def pad_eos(ngram, data):
    data, _ = padded_everygram_pipeline(ngram, data)
    return data

def train_ngram(model, train_data, ngram):
    """
    :param model: usually KneserNey or MLE
    :param train_data: train data padded 
    :param ngram: ngram to consider
    :return model: the model trained
    """
    ngram_data, padded_sents = padded_everygram_pipeline(ngram, train_data) 
    '''## Decomment to visualize data , but will not run the model as it's a lazy iterator
        for ngramlize_sent in train_data:
        print(list(ngramlize_sent))
    print('#############')
    print(list(padded_sents))'''
    model.fit(ngram_data, padded_sents)
    return model

def sentiment_tweet(sent_list):
    """
    :param sent_list: list of sentences to evaluate
    :return sent_score: global sentiment score for the group of sentences
    """
    total_pos = 0
    total_neg = 0
    total_compound = 0
    for sent in sent_list:
        ss = sentiment.polarity_scores(str(sent))
        total_pos += ss["pos"]
        total_neg -= ss["neg"]
        total_compound += ss["compound"]
    total_pos = round(total_pos,3)
    total_neg = round(total_neg,3)
    total_compound = round(total_compound,3)
    return total_pos, total_neg, total_compound

def generate_sent(model, num_words):
    """
    :param model: An ngram language model from `nltk.lm.model`.
    :param num_words: Max no. of words to generate.
    :return detokenize(content): clean text of the sentence generated
    """
    content = []
    for token in model.generate(num_words):
        if token == '<s>':
            continue
        if token == '</s>':
            break
        content.append(token)
    return detokenize(content)

    
    
    
    
    
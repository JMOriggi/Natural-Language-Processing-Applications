
import matplotlib.pyplot as plt
import Preprocessing as pre
from newspaper import Article
import jsonlines
import glob


## Loading the articles in jsonlines files
abc = []
fox = []
for file in glob.glob('*abc.jsonl'):
    with jsonlines.open(file) as reader:
        for obj in reader:  
            abc.append(obj['url'])
for file in glob.glob('*foxnews.jsonl'):
    with jsonlines.open(file) as reader:
        for obj in reader:
            fox.append(obj['url'])


## Use Article object and Download and get content
abc_urls = [Article(url) for url in abc]
fox_urls = [Article(url) for url in fox]
i = 0
for article in abc_urls:
    i += 1
    print(i,'/',len(abc_urls))
    article.download()
    article.parse()
        
i = 0
for article in fox_urls:
    i += 1
    print(i,'/',len(fox_urls))
    article.download()
    article.parse()

abc_text = '\n'.join([a.text for a in abc_urls])
fox_text = '\n'.join([a.text for a in fox_urls])


## ------------- Q1

## sentence split, tokenize, and remove stop words
abc_tok = pre.tokenize_sent_word(abc_text)
abc_tok = [pre.clean_tokens(sent, with_stop_word=False) for sent in abc_tok]
abc_tok = pre.clean_sent(abc_tok)
abc_tok = [pre.token_to_text(sent) for sent in abc_tok]

fox_tok = pre.tokenize_sent_word(fox_text)
fox_tok = [pre.clean_tokens(sent, with_stop_word=False) for sent in fox_tok]
fox_tok = pre.clean_sent(fox_tok)
fox_tok = [pre.token_to_text(sent) for sent in fox_tok]


## Construct type-token graph of news texts from these two news sites, where x-axis is #token, and y-axisis #type
abc_type = []
abc_token = []
## ABC
abc_voc = []
index = 0
for sent in abc_tok:
    for token in sent:
        index += 1
        if token not in abc_voc:
            abc_voc.append(token)
    abc_token.append(index)
    abc_type.append(len(abc_voc))

plt.plot(abc_token, abc_type) 
plt.xlabel('#token')
plt.ylabel('#type')
plt.show()
  
## Fox
fox_type = []
fox_token = []
fox_voc = []
index = 0
for sent in fox_tok:
    for token in sent:
        index += 1
        if token not in fox_voc:
            fox_voc.append(index)
    fox_token.append(index)
    fox_type.append(len(fox_voc))
    
plt.plot(fox_token, fox_type) 
plt.xlabel('#token')
plt.ylabel('#type')
plt.show()


## ------------- Q2
## Wordcloud
_, abc_text= pre.build_voc(abc_tok)
_, fox_text = pre.build_voc(fox_tok)
pre.plot_wordcloud(abc_text)
pre.plot_wordcloud(fox_text)



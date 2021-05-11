## Libraries
## requests: get an html page
## bs4: go through the page to get information (a parser)
##   select: can use queries
##   findall: must chain different conditions

import requests
from requests.exceptions import HTTPError
from bs4 import BeautifulSoup as bs
import re


class Scrape_Wikipedia():
    def __init__(self, url): 
        self._base = 'https://en.wikipedia.org'
        self.url = url
        self.html = self.get_html(self._base, self.url)
        self.soup = bs(self.html, 'lxml') #  html.parser
        
    @staticmethod    
    def get_html(base, url): 
        """
        :param base: base domain url
        :param url: specific url on base domain
        :return html: raw html from page scraped
        """
        complete_url = base + url
        try:
            r = requests.get(complete_url)
            r.raise_for_status() # detect code status and raise exception for some cases
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}') 
        else:
            print(url + ' -- Success!')
            r.encoding = 'utf-8'
            html = r.text # raw string response
            return html
    
    def get_links(self):
        """
        :return wiki_link_list: all links to other pages in the same domain present in the content of the page
        """
        a_list = self.soup.select("div.mw-parser-output p > a") # with > a is the direct children
        href_list = [el['href'] for el in a_list if el.has_attr('href')] #list comprehension method; take only href attribute value
        wiki_link_list = [el for el in href_list if el.startswith('/wiki/') and '#' not in el and ':' not in el]
        wiki_link_list = list(dict.fromkeys(wiki_link_list)) # remove duplicates
        print('-- Count of links found within the page: '+str(len(wiki_link_list)))
        return wiki_link_list
        
    def get_text(self):
        """
        :return raw_text: raw text of the page text content
        """
        p_list = self.soup.select("div.mw-parser-output p")
        print('-- Count of text element found within the page: '+str(len(p_list)))
        raw_text = '\n'.join([ p.text for p in p_list])
        raw_text = re.sub('\[(.*)\]', '', raw_text) # delete the braket for numering citations
        return raw_text


if __name__ == "__main__":
    
    ## Read main page
    url = '/wiki/COVID-19_pandemic'
    scrape_page = Scrape_Wikipedia(url)
    link_list = scrape_page.get_links()
    raw_text = scrape_page.get_text() 
    
    ## Get all links text from pages
    counter = 0
    for link in link_list:
        print(counter,'/',len(link_list))
        scrape_page_link = Scrape_Wikipedia(link)
        raw_text = raw_text + '\n' + scrape_page_link.get_text()
        del scrape_page_link
        counter += 1
       
    ## Save file
    with open("wikipedia_raw.txt", "wt", encoding='utf-8') as f:
        f.write(raw_text)
    
    
    
    
    
    
    
    
    
    


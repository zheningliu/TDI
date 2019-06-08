import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from requests_futures.sessions import FuturesSession
from urllib.parse import quote
import os
import dill
from retrying import retry

def get_news(ticker, from_date, to_date):
    url = ('https://newsapi.org/v2/everything?'
           'q={}&'
           'from={}&'
           'to={}&'
           'sortBy=popularity&'
           'apiKey=ea4ad2eea1c5495592584f60eee40aac'.format(ticker, from_date, to_date))
    response = requests.get(url)
    return response.json()


def convert_string_to_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d")


def convert_date(date):
    return date.strftime("%Y/%m/%d")


def get_page_args(i, params_str):
    return {"url": "https://www.wsj.com/search/term.html?&" + params_str,
            "params": {"page": i}}


def get_headlines(response):
    soup = BeautifulSoup(response.text, 'lxml')
    news = soup.find_all('h3', attrs={'class': 'headline'})
    result = [(line.select('a')[0]['href'], line.text.strip()) for line in news]
    return result


@retry(wait_fixed=2000, stop_max_attempt_number=7)
def wsj_scrapper(keyword, start_date, end_date):
    cache_dir = 'cache/'
    if not os.path.exists(cache_dir):
        os.mkdir(cache_dir)
    
    # read from cache file if already exist
    file_name = '_'.join(keyword.split()) + '_' + str(end_date.year) + '_' + str(end_date.month) + '.pkd'
    if os.path.exists(cache_dir + file_name):
        news_list = dill.load(open(cache_dir + file_name, 'rb'))
        return news_list
    
    if isinstance(start_date, str):
    	start_date = convert_string_to_date(start_date)
    	end_date = convert_string_to_date(end_date)

    params = {"KEYWORDS":quote(keyword), \
              'min-date':convert_date(start_date), \
              'max-date':convert_date(end_date), \
              'isAdvanced':'true', \
              'andor':'AND', \
              'sort':'date-desc', \
              'source':'wsjarticle,wsjblogs,wsjvideo,interactivemedia,sitesearch,wsjpro'}
    params_str = "&".join("%s=%s" % (k,v) for k,v in params.items())
    
    # process page and return result count
    response = requests.get(**get_page_args(1, params_str))
    # print("Making request to url... {}".format(response.url))
    soup = BeautifulSoup(response.text, 'lxml')
    try:
    	test = soup.find(attrs={'class':'results-menu-wrapper bottom'}).find(attrs={'class':'results-count'})
    except:
    	print("{} cannot be generated".format(file_name))
    	return []
    page_count = int(soup.find(attrs={'class':'results-menu-wrapper bottom'})\
                     .find(attrs={'class':'results-count'}).text.split()[-1])
    news = soup.find_all('h3', attrs={'class':'headline'})
    
    # multithread all available pages
    news_list = []
    session = FuturesSession(max_workers=5)
    futures = [session.get(**get_page_args(i, params_str)) for i in range(1, page_count+1)]
    for future in futures:
        news_list.extend(get_headlines(future.result()))
    
    # cache result
    dill.dump(news_list, open(cache_dir + file_name, 'wb'))

    return news_list


def parse_links(news_list):
	link_list = [news[0] for news in news_list]
	return link_list


def parse_headlines(news_list):
	headline_list = [news[1] for news in news_list]
	return headline_list


def read_scrapper(keyword, start_date, end_date):
	cache_dir = 'cache/'
	file_name = '_'.join(keyword.split()) + '_' + str(end_date.year) + '_' + str(end_date.month) + '.pkd'
	if os.path.exists(cache_dir + file_name):
		news_list = dill.load(open(cache_dir + file_name, 'rb'))
		return news_list
	else:
		return None
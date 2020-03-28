# Parse scrap from el mostrador
import numpy as np
import json
import pandas as pd
from functools import reduce
from datetime import datetime
import re
import math
import requests
from bs4 import BeautifulSoup

def unique(list_x):
    """Gets unique items from a list

    :param list_x: list
    :return: array of unique values
    """
    x = np.array(list_x)
    return np.unique(x)


def parser_elmostrador_each_article(url):
    """ parses each url link

    :param url: string with http url
    :return: text article
    """
    # Get http response
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features="lxml")

    # Get all p tags
    p_tags = soup.find_all('p')
    p_tags_text = [tag.get_text().strip() for tag in p_tags]

    # Filter out sentences that contain newline characters '\n' or don't contain periods, or three dots
    sentence_list = [sentence for sentence in p_tags_text if '\n' not in sentence]
    sentence_list = [sentence for sentence in sentence_list if '.' in sentence]
    sentence_list = [sentence for sentence in sentence_list if '...' not in sentence]

    # Combine list items into string.
    article = ' '.join(sentence_list)

    # remove weird characters
    weird_char = '\xa0'
    article = re.sub(weird_char, ' ', article)

    # replace scaped ''
    article = re.sub("\''", "''", article)

    # if article is empty, it is a video
    if len(article.split()) == 0:
        article = '--VIDEO--'

    return article


def parser_elmostrador(raw_list, on_going=True, input_date=datetime.today().strftime('%Y-%m-%d')):
    """Parses elmostrador raw list of html link tags

    :param raw_list: list of a ref tags from BeautifulSoup
    :param on_going: boolean, whether the
    :param input_date: string date in %Y-%m-%d to find a stored json file
    :return: final pandas DataFrame with 4 columns
        - raw_html_out string (url)
        - section string
        - news_date Date
        - headline text
        - scrap_date Date
    """
    # Hard-coded patterns
    pat_comments_hashtag = "#comentarios"
    url_base = 'https://www.elmostrador.cl'

    # Open stored file (default: today's file) or continue working in memory
    if not on_going:
        with open('output/{0}_elmostrador.json'.format(input_date)) as json_file:
            raw_list = json.load(json_file)

    # filter out '#comentarios'
    out_list = [f for f in raw_list if pat_comments_hashtag not in f]

    # Take only unique values
    out_list = unique(out_list)

    # filter out for each main group
    main_topic_groups = ["dia", "cultura", "noticias", "agenda-pais", "destacado", "braga", "tv", "mercados"]

    # Append all main topic groups
    out_list_filtered = []
    for pattern in main_topic_groups:
        pat = re.compile("/" + pattern + "/")
        out_list_filtered.append([f for f in out_list if pat.search(f)])

    # flatten result
    out_list_filtered = reduce(lambda x, y: x + y, out_list_filtered)

    # Separate 'noticias' and https: entries
    https_entries = [f for f in out_list_filtered if "https://" in f]

    # News have at least the main url with some subsections like /url_base/section/topic
    min_char = math.ceil(np.mean(list(map(len, main_topic_groups)))) * 3 + len(url_base)
    https_entries = [f for f in https_entries if len(f) > min_char]

    # Make a pandas data frame for headlines for https entries, i.e. not so easy news

    df_difficult_news = pd.DataFrame(set(https_entries), columns=["raw_html_out"])

    # Define patterns to extract strings from main html tag
    pat_section = re.compile("{0}/(.*?)/".format(url_base))
    pat_date = re.compile("{0}/.*/(..../../..)/.*".format(url_base))
    pat_headline = re.compile("{0}/.*/(.*)/$".format(url_base))

    # Create columns. Note idx is artificial and continues from last idx from the other data set
    df_difficult_news['section'] = df_difficult_news['raw_html_out'].str.extract(pat=pat_section, expand=True)
    df_difficult_news['news_date'] = df_difficult_news['raw_html_out'].str.extract(pat=pat_date, expand=True)
    df_difficult_news['headline'] = df_difficult_news['raw_html_out'].str.extract(pat=pat_headline, expand=True)

    # Filter out news with no headline
    df_difficult_news = df_difficult_news[df_difficult_news['headline'].notnull()]
    df_difficult_news['scrap_date'] = datetime.today().strftime('%Y-%m-%d')

    # Adjust news date
    df_difficult_news['news_date'] = [re.sub("/", "-", x) for x in df_difficult_news['news_date']]
    return df_difficult_news

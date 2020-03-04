# Parse scrap from el mostrador
import numpy as np
import json
import pandas as pd
from functools import reduce
from datetime import datetime
import re
import math


def unique(list_x):
    """Gets unique items from a list

    :param list_x: list
    :return: array of unique values
    """
    x = np.array(list_x)
    return np.unique(x)


def parser_elmostrador(raw_list, on_going=True, input_date=datetime.today().strftime('%Y-%m-%d')):
    """Parses elmostrador raw list of html link tags

    :param raw_list:
    :param on_going:
    :param input_date:
    :return: final
    """
    # Hard-coded patterns
    el_mostrador_comentarios_pattern = "#comentarios"
    url_base = 'https://www.elmostrador.cl'

    # Open stored file (default: today's file) or continue working in memory
    if not on_going:
        with open('output/{0}_elmostrador.json'.format(input_date)) as json_file:
            raw_list = json.load(json_file)

    out_list = [f for f in raw_list if el_mostrador_comentarios_pattern not in f]
    out_list = unique(out_list)

    # filter out 'comentarios'
    out_list = [f for f in out_list if el_mostrador_comentarios_pattern not in f]
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
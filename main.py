import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime
import logging
from parser_elmostrador import parser_elmostrador
import connect as head_con

'''
# set the urls to scrap from
url_list = ['http://www.emol.com',
            'https://www.elmostrador.cl',
            'https://www.latercera.com']
'''
# Global parameters
url_list = ['https://www.elmostrador.cl']

param_save_json = False
today_date_str = datetime.today().strftime('%Y-%m-%d')


def save_in_json(scrap_out, json_filename):
    """ saves the scrapping output in a json file

    :param scrap_out:
    :param json_filename:
    :return: None
    """
    json_file = open(json_filename, 'w')
    json.dump(scrap_out, json_file)
    json_file.close()


def parser_routine(urls):
    """ parses a list of urls and writes everything into a database

    :param urls: list of urls to scrap
    :return: None
    """
    for url in urls:

        short_url = "".join(re.compile("^http[s]?://www.(.*?)\.([a-z]{1,3})$").search(url).group(1))

        # Set logging config
        logging.basicConfig(filename='{0}_{1}.log'.format(today_date_str, short_url),
                            level=logging.DEBUG,
                            filemode='w',
                            format='%(asctime)s %(levelname)s - %(module)s - %(funcName)s: %(message)s',
                            datefmt='%Y-%m-%d %H:%M:%S')
        # Get logger
        logger = logging.getLogger()
        logger.info("Starting scraping")

        # Initialize list of links
        out_list = []
        logger.info("Scraping {0}".format(url))
        logger.info("")

        # Get http response
        response = requests.get(url)
        logger.info("Response status code {0}".format(response.status_code))

        # Parse the response with beautiful soup
        soup = BeautifulSoup(response.text, "html.parser")

        # Append all divs with links reference a['href']
        for a in soup.find_all('a', href=True):
            logger.info("Found URL with <a href> tag: {0}".format(a['href']))
            out_list.append(a['href'])
        logger.info("Done!")

        # Save output in json file
        if param_save_json:
            logger.info("Saving raw json output...")
            json_filename = 'output/{0}_{1}.json'.format(today_date_str, short_url)
            save_in_json(out_list, json_filename)
            logger.info("{0}... done!".format(json_filename))

        # Parse list
        logger.info('Parsing scrapped html file')
        table_to_db = parser_elmostrador(out_list, on_going=True)

        # Save into db
        logger.info('Saving output in db')
        engine = head_con.create_engine_instance()
        table_to_db.to_sql("headlines_{0}".format(short_url), engine, if_exists='append', index=False)

    logger.info("Done!")


if __name__ == '__main__':
    parser_routine(url_list)

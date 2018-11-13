import requests
from queue import Queue, deque
from bs4 import BeautifulSoup
from time import sleep
import sys
import pandas as pd
import re

class OLXScraper(object):
    def __init__(self, category=18, from_page=1, to_page=5000, links_file=True, data_file=True, no_of_threads=1):
        """
        OLX Scraper needs some initial attributes to work:
        :param category: integer that represents the category(e.g. category 18 are cars)
        :param from_page: integer that shows the starting page that will be scraped
        :param to_page: integer that shows ending page to be scraped (it is inclusive)
        :param links_file: boolean value that creates a file with all links that are scraped, if links_file is True
        :param data_file: boolean value that creates a main file with all the data, if data_file is True
        """

        self.links = Queue(maxsize=0)
        self.main_list = Queue(maxsize=0)
        self.urls = Queue(maxsize=0)

        self.category = category
        self.from_page = from_page
        self.to_page = to_page
        self.links_file = links_file
        self.data_file = data_file

        while from_page < to_page:
            self.urls.put("http://www.olx.ba/pretraga?kategorija=" + str(category) + "&stranica=" + str(from_page))
            from_page += 1

    def scrape_links(self):
        from_page = self.from_page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
        if self.links_file:
            links_file = open("links2.txt", "w")

        print("Number of pages: " + str(self.urls.qsize()))
        while not self.urls.empty():
            try:
                r = requests.get(self.urls.get(), headers=headers)
                r.raise_for_status()
                page_content = r.content.decode()
                soup = BeautifulSoup(page_content, "html.parser")
                articles = soup.find_all(lambda tag: tag.name == 'div' and tag.get('class') == ['naslov'])
                if len(articles) == 0:
                    print("Stopped scraping at page: " + str(from_page))
                    return self.links
                for link in articles:
                    self.links.put(link.a["href"])
                    if self.links_file:
                        links_file.write("%s\n" % link.a["href"])
                        links_file.flush()
                print(self.links.qsize())
            except:
                sleep(3)
                print("Zasp'o sam sekund... kriv je " + str(r.status_code))
            self.urls.task_done()
        return self.links

    def scrape_page(self, links):
        self.links = links
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
        while not self.links.empty():
            attributes = {}
            main_items = {}
            items = {}
            url = self.links.get()
            try:
                r = requests.get(url, headers=headers)
                r.raise_for_status()
            except:
                print("Error: ", sys.exc_info()[0], "  Status code: " + str(r.status_code))
                sleep(3)
                r = requests.get(url, headers=headers)
            page_content = r.content.decode()
            soup = BeautifulSoup(page_content, "html.parser")

            main_attrs = soup.find_all('p', {'class': 'n'})
            main_attrs_keys = []
            main_attrs_values = []
            for attr in main_attrs:
                main_attrs_keys.append(attr.get_text().strip())
            for attr in main_attrs:
                main_attrs_values.append(attr.find_next('p').get_text().strip())
            main_items = dict(zip(main_attrs_keys, main_attrs_values))
            main_items["Latitude"] = self.__get_latitude(soup)
            main_items["Longitude"] = self.__get_longitude(soup)
            main_items["User"] = self.__get_user(soup)
            main_items["ShortDescription"] = self.__get_description(soup)
            #main_items["LongDescription"] = self.__get_long_description(soup)
            main_items["Number_of_photos"] = self.__get_number_of_photos(soup)
            main_items["Number_of_questions"] = self.__get_number_of_questions(soup)

            df1_list = []
            df2_list = []
            df1 = soup.find_all('div', {'class': 'df1'})
            df2 = soup.find_all('div', {'class': 'df2'})
            for df in df1:
                df1_list.append(df.get_text().strip())
            for df in df2:
                df2_list.append('1' if df.get_text().strip() == '' else df.get_text().strip())
            items = dict(zip(df1_list, df2_list))

            attributes = {**main_items, **items}
            self.main_list.put(attributes)
            print(self.main_list.qsize())
            self.links.task_done()

        single_list = list(self.main_list.queue)
        df = pd.DataFrame(single_list)
        if self.data_file:
            df.to_csv("data2.csv", encoding="utf-8", na_rep="NaN", index=False)
        return df

    def __get_latitude(self, soup):
        try:
            return soup.find('script', string=re.compile('LatLng')).get_text().split('LatLng(')[1].split(',')[0]
        except:
            return 'NaN'

    def __get_longitude(self, soup):
        try:
            return soup.find('script', string=re.compile('LatLng')).get_text().split('LatLng(')[1].split(',')[1].split(')')[0]
        except:
            return 'NaN'

    def __get_user(self, soup):
        try:
            return soup.find('div', {'class': 'username'}).findChild('span').get_text()
        except:
            return 'NaN'
    def __get_description(self, soup):
        try:
            return soup.find('div', {'class': 'artikal_detaljniopis_tekst'}).get_text().strip()
        except:
            return 'NaN'

    def __get_long_description(self, soup):
        try:
            return soup.find('div', {'id': 'detaljni-opis'}).get_text().strip()
        except:
            return 'NaN'

    def __get_number_of_photos(self, soup):
        try:
            return soup.find('li', {'class': 'dd disableSelection dugme_galerija hide-mobile'}).find('span').get_text().strip()
        except:
            return 'NaN'

    def __get_number_of_questions(self, soup):
        try:
            return soup.find('a', {'id': 'pitanja_btn'}).find('span').get_text().strip()
        except:
            return 'NaN'


scraper = OLXScraper(category=23, from_page=1)
links = open(r"C:\Users\emir.hodzic\Documents\FAX\OLX-Scraper-master\links2.txt").read().splitlines()#scraper.link_scraper()
q = Queue()
[q.put(i) for i in links]
scraper.scrape_page(q)

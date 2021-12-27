import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

LANCASHIRE_ARCHIVE_WEBSITE = 'https://archivecat.lancashire.gov.uk/calmview/'

class Scraper:
    def __init__(self):
        self.html_dictionary = {}

    def request_html(self, url):
        request = requests.get(url)
        self.content = request.content
        return self.content

    def html_get(self, url):
        self.html_dictionary[url] = BeautifulSoup(self.request_html(url), 'html.parser')
        return self.html_dictionary[url]

    def advanced_search_links(self, url, find_all_param, get_param, search_in_link):
        for link in [link.get(get_param) for link in self.html_get(url).find_all(find_all_param)]:
            if link != None and search_in_link in link:
                return link

    def click_to_next_page(self, url, selection):
        self.driver = webdriver.Firefox()
        self.driver.get(url)
        self.complete_search_bar(self.driver.find_element_by_id(selection))

    def complete_search_bar(self, search_bar):
        search_bar.clear()
        search_bar.send_keys('wcw')
        search_bar.send_keys(Keys.RETURN)
        self.wait_and_return_page_url()

    def wait_and_return_page_url(self):
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.title_contains('Search Results'))
        url = self.driver.current_url
        self.url = url  

    def get_all_page_links(self, url):
        for link in [link.get('onclick') for link in self.html_get(url).find_all('tr')]:
            if link:
                yield self.create_full_url(link.rstrip("'"))

    def create_full_url(self, link):
        if link != None:
            return LANCASHIRE_ARCHIVE_WEBSITE + link.lstrip("document.location='./") 

    def get_page_data(self):
        for url in self.get_all_page_links(self.url):
            data_page_html = self.html_get(url)
            self.get_data_from_table(data_page_html)

    def get_data_from_table(self,data_page_html):
        table_data = data_page_html.find_all('tr')
        for table_row in table_data:
            print(table_row) 
        
if __name__ == '__main__':
    scraper = Scraper()
    link = scraper.advanced_search_links(LANCASHIRE_ARCHIVE_WEBSITE, 'a', 'href', 'advanced')
    url = LANCASHIRE_ARCHIVE_WEBSITE + link
    selection = scraper.advanced_search_links(url, 'input', 'id', 'SearchText_AltRef')
    scraper.click_to_next_page(url, selection)
    scraper.get_page_data()



    
    
    


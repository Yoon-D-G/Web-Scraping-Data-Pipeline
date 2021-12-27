import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas

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
        driver = webdriver.Firefox()
        driver.get(url)
        search_bar = driver.find_element_by_id(selection)
        search_bar.clear()
        search_bar.send_keys('wcw')
        search_bar.send_keys(Keys.RETURN)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.title_contains('Search Results'))
        url = driver.current_url
        return url  

    def get_all_page_links(self, url):
        for link in [link.get('onclick') for link in self.html_get(url).find_all('tr')]:
            if link:
                yield self.create_full_url(link.rstrip("'"))

    def create_full_url(self, link):
        if link != None:
            return LANCASHIRE_ARCHIVE_WEBSITE + link.lstrip("document.location='./")     
        
if __name__ == '__main__':
    scraper = Scraper()
    link = scraper.advanced_search_links(LANCASHIRE_ARCHIVE_WEBSITE, 'a', 'href', 'advanced')
    url = LANCASHIRE_ARCHIVE_WEBSITE + link
    selection = scraper.advanced_search_links(url, 'input', 'id', 'SearchText_AltRef')
    first_page_proper_url = scraper.click_to_next_page(url, selection)
    counter = 0
    data_dictionary = {}
    for url in scraper.get_all_page_links(first_page_proper_url):
        if counter == 2:
            break
        data_page_html = scraper.html_get(url)
        table_data = data_page_html.find_all('tr')
        for table_row in table_data:
            table_column = table_row.find_all('td')
            table_column = [table_entry.text.strip() for table_entry in table_column]
            data_dictionary[]
            data_dictionary[table_column[1]] = table_column[1]
            # data.append([table_entry for table_entry in table_column if table_entry])
        counter += 1
    print(data_dictionary)


    # with open('html_dictionary_first_20', 'w') as file:
    #     file.write(str(scraper.html_dictionary))
    
    
    


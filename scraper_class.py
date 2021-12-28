import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re

LANCASHIRE_ARCHIVE_WEBSITE = 'https://archivecat.lancashire.gov.uk/calmview/'

class Scraper:

    def __init__(self):
        self.html_dictionary = {}
        self.all_data = []
        self.dataframe = pd.DataFrame(columns=[
            'Document Reference',
            'Title', 
            "Testator's name",
            'Occupation/status',
            'Place',
            'Date',
            'Contents'
        ])

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
        self.automatically_enter_search_bar(self.driver.find_element_by_id(selection))

    def automatically_enter_search_bar(self, search_bar):
        search_bar.clear()
        search_bar.send_keys('wcw')
        search_bar.send_keys(Keys.RETURN)
        self.wait_and_set_page_url()

    def wait_and_set_page_url(self):
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
        counter = 0
        for url in self.get_all_page_links(self.url):
            if counter == 20:
                break
            data_page_html = self.html_get(url)
            self.get_table_from_html(data_page_html)
            counter += 1

    def get_table_from_html(self,data_page_html):
        table_data = data_page_html.find_all('tr')
        data = [self.get_data_from_table(table_row) for table_row in table_data]
        self.flattened_data_list(data)

    def flatten_data_list(self, nested_data):
        for data in nested_data:
            if (isinstance(data, list) or isinstance(data, tuple)) and not isinstance(data, str):
                yield from self.flatten_data_list(data)
            else:
                yield data

    def flattened_data_list(self, data):
        flat_list = [i for i in self.flatten_data_list(data)]
        self.create_appendable_data(flat_list)

    def get_data_from_table(self, table_row):
        columns = table_row.find_all('td')
        columns = [element.text.strip() for element in columns]
        if columns[0] != 'Description':
            return columns
        else:
            return self.extract_testator_data(columns[1])

    def extract_testator_data(self, testator_data):
        testator_data_list = []
        testator_tuple = self.extract_testator_data_regex(testator_data, '(.*?)Occupation')
        testator_data_list.append(testator_tuple[1])
        testator_tuple = self.extract_testator_data_regex(testator_tuple[0], '(.*?)Place')
        testator_data_list.append(testator_tuple[1])
        testator_tuple = self.extract_testator_data_regex(testator_tuple[0], '(.*?)Contents')
        testator_data_list.append(testator_tuple)
        return testator_data_list

    def extract_testator_data_regex(self, testator_data, regex_pattern):
        regex = re.compile(regex_pattern)
        output = regex.findall(testator_data)
        if output:
            testator_data = testator_data.lstrip(str(output))
        return testator_data, output

    def create_appendable_data(self, flat_list):
        doc_ref = self.find_data_type_1(flat_list, 'Document reference')
        title = self.find_data_type_1(flat_list, 'Title')
        name = self.find_data_type_2(flat_list, "Testator's name")
        occupation = self.find_data_type_2(flat_list, 'Occupation/status')
        place = self.find_data_type_2(flat_list, 'Place')
        date = self.find_data_type_1(flat_list, 'Date')
        contents = self.find_data_type_2(flat_list, 'Contents')
        self.append_data_to_dataframe(
            doc_ref=doc_ref,
            title=title,
            name=name,
            occupation=occupation,
            place=place,
            date=date,
            contents=contents)

    def find_data_type_1(self, flat_list, data_item):
        try:
            if data_item in flat_list:
                return flat_list[flat_list.index(data_item) + 1]
            else:
                return None
        except (IndexError, AttributeError, TypeError, Exception) as err:
            print(err, data_item)
            return None

    def find_data_type_2(self, flat_list, data_item):
        try:
            for item in flat_list:
                if data_item in item:
                    return item.split(':')[1].strip()
        except (IndexError, AttributeError, TypeError, Exception) as err:
            print(err, data_item)  
            return None     

    def append_data_to_dataframe(
        self, 
        doc_ref='NULL', 
        title='NULL', 
        name='NULL', 
        occupation='NULL', 
        place='NULL', 
        date='NULL', 
        contents='NULL'
    ):
        self.dataframe = self.dataframe.append({
            'Document Reference': doc_ref,
            'Title': title, 
            "Testator's name": name,
            'Occupation/status': occupation,
            'Place': place,
            'Date': date,
            'Contents': contents
        }, ignore_index=True)  

if __name__ == '__main__':
    scraper = Scraper()
    link = scraper.advanced_search_links(LANCASHIRE_ARCHIVE_WEBSITE, 'a', 'href', 'advanced')
    url = LANCASHIRE_ARCHIVE_WEBSITE + link
    selection = scraper.advanced_search_links(url, 'input', 'id', 'SearchText_AltRef')
    scraper.click_to_next_page(url, selection)
    scraper.get_page_data()
    print(scraper.dataframe)



    
    
    


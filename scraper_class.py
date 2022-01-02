import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import pandas as pd
import re
from time import sleep
import pickle

LANCASHIRE_ARCHIVE_WEBSITE = 'https://archivecat.lancashire.gov.uk/calmview/'
MONTH_LIST = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
MONTH_LIBRARY = {
    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 
    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08', 
    'Sep':'09', 'Oct': '10', 'Nov': '11', 'Dec': '12'    
}
ORDINAL_ABBREVIATION_LIST = ['st', 'nd', 'rd', 'th'] 

class Scraper:

    def __init__(self):
        self.all_data = []
        self.dataframe = pd.DataFrame(columns=[
            'Document_reference',
            'Title', 
            "Testators_name",
            'Occupation_status',
            'Place',
            'Date',
            'Contents'
        ]) 
        self.counter = 1

    def request_html(self, url):
        request = requests.get(url)
        self.content = request.content
        return self.content

    def html_get(self, url):
        soup = BeautifulSoup(self.request_html(url), 'html.parser')
        return soup

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
        self.wait_and_get_page_html()

    def wait_and_get_page_html(self):
        page_number = self.counter * 20
        WebDriverWait(self.driver, 10).until(lambda x: x.find_element_by_xpath(
            "//*[contains(text(), 'to {} of')]".format(page_number))) 
        url = self.driver.current_url
        self.html = BeautifulSoup(self.driver.page_source, 'html.parser')
        self.counter += 1 

    def get_all_page_links(self):
        for link in [link.get('onclick') for link in self.html.find_all('tr')]:
            if link:
                yield self.create_full_url(link.rstrip("'"))

    def create_full_url(self, link):
        if link != None:
            return LANCASHIRE_ARCHIVE_WEBSITE + link.lstrip("document.location='./") 

    def get_page_data(self):
        for url in self.get_all_page_links():
            data_page_html = self.html_get(url)
            self.get_table_from_html(data_page_html)

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
        date = self.find_and_standardise_date(flat_list, 'Date')
        if date == 'ERROR':
            return None
        contents = self.find_data_type_2(flat_list, 'Contents')
        self.append_data_to_dataframe(
            doc_ref=doc_ref,
            title=title,
            name=name,
            occupation=occupation,
            place=place,
            date=date,
            contents=contents)

    def find_and_standardise_date(self, flat_list, data_item):
        first_draft_date = str(self.find_data_type_1(flat_list, data_item))
        year = self.find_and_standardise_year(first_draft_date)
        if year == 'ERROR':
            return 'ERROR'
        month = self.find_and_standardise_month(first_draft_date)
        first_draft_date_without_years = first_draft_date.replace(year, '')
        day = self.find_and_standardise_day(first_draft_date_without_years)
        return self.arrange_date_into_ISO_8601(day, month, year)

    def arrange_date_into_ISO_8601(self, day, month, year):
        if year and month and day:
            return year + '-' + month + '-' + day
        elif not month or not day:
            return year + '-01-01'
        elif not year:
            return 'NULL'

    def find_and_standardise_year(self, first_draft_date):
        year_finder = re.compile('\d\d\d\d')
        year_list = re.findall(year_finder, first_draft_date)  
        if len(year_list) > 1 or not year_list:
            return 'ERROR' 
        if year_list:
            return year_list[0]

    def find_and_standardise_month(self, first_draft_date):
        for month in MONTH_LIST:
            if month in first_draft_date:
                return MONTH_LIBRARY[month]
        return None

    def find_and_standardise_day(self, first_draft_date):
        day_finder = re.compile('(\d\d|\d)(\s|[a-zA-Z])')
        days = re.findall(day_finder, first_draft_date)
        if days:
            return ['0' + day[0] if len(day[0]) == 1 else day[0] for day in days][0]
        else:
            return None

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
            'Document_reference': doc_ref,
            'Title': title, 
            "Testators_name": name,
            'Occupation_status': occupation,
            'Place': place,
            'Date': date,
            'Contents': contents
        }, ignore_index=True)  

    def run_full_search(self, skip=False):
        counter = 0
        while True:
            if counter == 2:
                break
            self.driver.find_element_by_link_text('Next').click()
            sleep(10)
            self.wait_and_get_page_html()
            self.get_page_data()
            counter += 1

    def persist_dataframe(self):
        self.dataframe.to_pickle('pickled_dataframe.pkl')

        # with open('dataframe', 'a') as file:
        #     dataframe_as_string = self.dataframe.to_string(header=False, index=False)
        #     file.write(dataframe_as_string)
        
if __name__ == '__main__':
    scraper = Scraper()
    link = scraper.advanced_search_links(LANCASHIRE_ARCHIVE_WEBSITE, 'a', 'href', 'advanced')
    url = LANCASHIRE_ARCHIVE_WEBSITE + link
    selection = scraper.advanced_search_links(url, 'input', 'id', 'SearchText_AltRef')
    scraper.click_to_next_page(url, selection)
    scraper.get_page_data()
    scraper.run_full_search()
    print(scraper.dataframe)
    scraper.persist_dataframe()


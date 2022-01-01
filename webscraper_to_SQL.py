from scraper_class import Scraper, LANCASHIRE_ARCHIVE_WEBSITE
import pymysql.cursors

scraper = Scraper()
link = scraper.advanced_search_links(LANCASHIRE_ARCHIVE_WEBSITE, 'a', 'href', 'advanced')
url = LANCASHIRE_ARCHIVE_WEBSITE + link
selection = scraper.advanced_search_links(url, 'input', 'id', 'SearchText_AltRef')
scraper.click_to_next_page(url, selection)
scraper.get_page_data()
scraper.run_full_search()
scraper.persist_dataframe()


connection = pymysql.connect(host='192.168.1.50',
                            port=3306,
                            user='ewen_remote',
                            password='ABCeasyas123!',
                            db='Webscraper',
                            charset='utf8mb4',
                            cursorclass=pymysql.cursors.DictCursor)

print(connection)

from scraper_class import Scraper, LANCASHIRE_ARCHIVE_WEBSITE
from webscraper_to_SQL import Transfer_dataframe_to_mysql

# Initialise Scraper class and call all functions to create complete dataframe.
scraper = Scraper()
link = scraper.advanced_search_links(LANCASHIRE_ARCHIVE_WEBSITE, 'a', 'href', 'advanced')
url = LANCASHIRE_ARCHIVE_WEBSITE + link
selection = scraper.advanced_search_links(url, 'input', 'id', 'SearchText_AltRef')
scraper.click_to_next_page(url, selection)
scraper.get_page_data()
scraper.run_full_search()
scraper.persist_dataframe()

# Create connection to remote database, input data from dataframe and close connection.
tdf = Transfer_dataframe_to_mysql()
tdf.unpickle_dataframe()
tdf.create_db_engine()
tdf.create_connection_to_db()
tdf.create_cursor()
tdf.create_table()
tdf.upload_dataframe()
tdf.close_connection()
from scraper_class import Scraper, LANCASHIRE_ARCHIVE_WEBSITE
import pymysql
import pandas as pd
from sqlalchemy import create_engine

class Transfer_dataframe_to_mysql:

    def unpickle_dataframe(self):
        with open('pickled_dataframe.pkl', 'rb') as file:
            self.dataframe = pd.read_pickle(file)

    def create_db_engine(self):
        db_data = "mysql+pymysql://ewen:ABCeasyas123!@HOST:3306/Webscraper?charset=utf8mb4"
        self.engine = create_engine(db_data)

    def create_connection_to_db(self):
        try:
            self.connection = pymysql.connect(host='192.168.1.50',
                                            port=3306,
                                            user='ewen_remote',
                                            password='ABCeasyas123!',
                                            charset='utf8mb4',
                                            database='Webscraper')
        except (pymysql.err.OperationalError, Exception) as err:
            print('Problem creating connection error:',err)
        
    def create_cursor(self):
        self.dbcursor = self.connection.cursor()
        
    def create_table(self):
        self.dbcursor.execute(
            """ CREATE TABLE IF NOT EXISTS all_testators (
                Document_reference varchar(100), 
                Title varchar(255),
                Testators_name varchar(255), 
                Occupation_status varchar(255),
                Place varchar(100),
                Date DATE,
                Contents varchar(255),
                Primary Key(Document_reference)
            );""" 
        )

    def show_table(self):
        self.dbcursor.execute(
            """
            SELECT *
            FROM all_testators;
            """
        )
        return self.dbcursor.fetchall()

    def close_connection(self):
        if self.connection.open:
            self.connection.close()
            self.dbcursor.close()
            print("MySQL connection is closed")

if __name__ == '__main__':
    tdf = Transfer_dataframe_to_mysql()
    tdf.unpickle_dataframe()
    tdf.create_db_engine()
    tdf.create_connection_to_db()
    tdf.create_cursor()
    tdf.create_table()
    print(tdf.show_table())
    tdf.close_connection()





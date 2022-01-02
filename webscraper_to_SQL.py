import pymysql
import pandas as pd
from sqlalchemy import create_engine

class Transfer_dataframe_to_mysql:

    def unpickle_dataframe(self):
        with open('pickled_dataframe.pkl', 'rb') as file:
            self.dataframe = pd.read_pickle(file)

    def create_db_engine(self):
        db_data = "mysql+pymysql://ewen_remote:ABCeasyas123!@192.168.1.50:3306/Webscraper?charset=utf8mb4"
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

    def create_3nf_title_table(self, table_name):
        self.dbcursor.execute(
            """
            CREATE TABLE {tn}_table (
                {tn}_id INT NOT NULL AUTO_INCREMENT, 
                {tn} varchar (255), 
                PRIMARY KEY ({tn}_id)
            );
            """.format(tn=table_name)
        )

    def create_3nf_main_table(self):
        self.dbcursor.execute(
            """
            CREATE TABLE main_testator_table(
            Document_reference varchar(100),
            Testators_name varchar(100),
            Date DATE,
            Place_id INT,
            Title_id INT,
            Contents_id INT,
            Occupation_id INT,
            PRIMARY KEY (Document_reference),
            CONSTRAINT Title_fk 
            FOREIGN KEY (Title_id)
                REFERENCES Title_table(Title_id)
                ON DELETE SET NULL
                ON UPDATE CASCADE,
            CONSTRAINT Place_fk
            FOREIGN KEY (Place_id)
                REFERENCES Place_table(Place_id)
                ON DELETE SET NULL
                ON UPDATE CASCADE,
            CONSTRAINT Contents_fk
            FOREIGN KEY (Contents_id)
                REFERENCES Contents_table(Contents_id)
                ON DELETE SET NULL
                ON UPDATE CASCADE,
            CONSTRAINT Occupation_fk
            FOREIGN KEY (Occupation_id)
                REFERENCES Occupation_table(Occupation_id)
                ON DELETE SET NULL
                ON UPDATE CASCADE
            )ENGINE=INNODB;
            """
        )

    def upload_dataframe(self):
        self.dataframe.to_sql('all_testators', self.engine, if_exists='append', index=False)

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
    for table_name in ['Title', 'Contents', 'Place', 'Occupation']:
        tdf.create_3nf_title_table(table_name)
    tdf.create_3nf_main_table()
    tdf.close_connection()





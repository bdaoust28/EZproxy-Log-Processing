# Written by Beau Daoust (2021)
import mysql.connector, json, json2, sys, time
from mysql.connector import errorcode
from logwriter import login_log_action as log_action
from datetime import date

class Execution():
    def __init__(self):
        try:
            self.settings = json2.load_file(f'{sys.path[0]}/ezproxy/ezproxy/dir_settings.json')  # load dir settings
            creds = json2.load_file(f'{sys.path[0]}/ezproxy/ezproxy/creds.json') # load login creds
            self.cnx = mysql.connector.connect(user=creds['ms_user'], password=creds['ms_pass'], host=creds['host_ip'], database=creds['host_db'], allow_local_infile=True)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("The submitted user name or password is incorrect. Login credentials have likely been changed.")
                self.login_fail()
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist.")
            else:
                print(err)
        else:
            print('MySQL login success!')
            # self.login_success()

    def close(self):
        self.cnx.close()

    def login_fail(self):
        log_action('ms_login')

    def select_all(self, table):
        cursor = self.cnx.cursor()
        query = f'SELECT * FROM ezproxy.{table} ' \
                'LIMIT 100;'
        cursor.execute(query)

        myresult = cursor.fetchall()
        for x in myresult:
            print(x)
        cursor.close()

    def manual_import(self, table, file):
        statement = None
        if table == 'login':
            statement = f"load data local infile '{self.settings['dest_dir']}/{file}' " \
                        "into table test.log " \
                        "fields terminated by '\t'" \
                        "enclosed by ''" \
                        "lines terminated by '\n'" \
                        "(Date,Time,Event,IP,User,Session,Other);"
            cursor = self.cnx.cursor()
            cursor.execute(statement)
            self.cnx.commit()
        elif table == 'domain':
            statement = f"load data local infile '{self.settings['dest_dir']}/{file}' " \
                        "into table test.domain " \
                        "fields terminated by '\t' " \
                        "enclosed by '' "\
                        "lines terminated by '\n' " \
                        "(Date,Time,IP,Session,Domain,FullSite);"
            cursor = self.cnx.cursor()
            cursor.execute(statement)
            self.cnx.commit()
        elif table == 'both':
            domain_statement = f"load data local infile '{self.settings['dest_dir']}/{file[0]}' " \
                        "into table test.domain " \
                        "fields terminated by '\t' " \
                        "enclosed by '' " \
                        "lines terminated by '\n' " \
                        "(Date,Time,IP,Session,Domain,FullSite);"
            login_statement = f"load data local infile '{self.settings['dest_dir']}/{file[1]}' " \
                        "into table test.log " \
                        "fields terminated by '\t'" \
                        "enclosed by ''" \
                        "lines terminated by '\n'" \
                        "(Date,Time,Event,IP,User,Session,Other);"
            cursor = self.cnx.cursor()
            cursor.execute(login_statement)
            # self.cnx.commit()
            cursor.execute(domain_statement)
            self.cnx.commit()
        else:
            print('ERROR: Invalid table name, which means the script has been tampered with.')
        cursor.close()

    def auto_import_data(self, table, file):
        statement = None
        if table == 'log':
            statement = f"load data local infile '{file}' " \
                        "into table ezproxy.log " \
                        "fields terminated by '\t' " \
                        "enclosed by '' " \
                        "lines terminated by '\n' " \
                        "(Date,Time,Event,IP,User,Session,Other);"
        elif table == 'domain':
            statement = f"load data local infile '{file}' " \
                        "into table ezproxy.domain " \
                        "fields terminated by '\t' " \
                        "enclosed by '' "\
                        "lines terminated by '\n' " \
                        "(Date,Time,IP,Session,Domain,FullSite);"
        else:
            print('ERROR: Invalid table name, which means the script has been tampered with.')
        cursor = self.cnx.cursor()
        cursor.execute(statement)
        self.cnx.commit()
        cursor.close()

if __name__ == "__main__":
    e = Execution()
    print('\nLOGIN: ')
    e.select_all('log')
    print('\nDOMAIN: ')
    e.select_all('domain')
    '''print('[1] select all from login\n'
          '[2] select all from domain\n'
          '[3] import data into login\n'
          '[4] import data into domain')
    choice = int(input('choose option: '))
    if choice == 1:
        e.select_all('log')
    elif choice == 2:
        e.select_all('domain')
    elif choice == 3:
        e.import_data('log')
    elif choice == 4:
        e.import_data('domain')'''
    e.close()
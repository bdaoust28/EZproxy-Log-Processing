# Written by Beau Daoust (2021)
from ezproxy.script import SpiderScript
from logwriter import auto_log_action as log_action
from datetime import date, timedelta, datetime
import reader, time, json, json2, sys
import mysql_connection as sql

def main():
    log_action('startup')

    # 1. import log files
    spider = SpiderScript()
    spider.run()

    action_log = open(f'{sys.path[0]}/history.log', 'r')
    lines = action_log.readlines()
    if 'failed' in lines[-1]:
        log_action('close')
        return
    log_action('log_dl')
    action_log.close()

    # 2. process yesterday's logs
    settings = json2.load_file(f'{sys.path[0]}/ezproxy/ezproxy/dir_settings.json')  # load dir settings
    yest = date.today() - timedelta(days=1)
    yest = yest.strftime('%Y%m%d')
    files = reader.auto_read(settings['source_dir'], settings['dest_dir'], yest)
    domain_file = files[0].split('/')[-1]
    login_file = files[1].split('/')[-1]
    log_action('process_logs', domain_file, login_file)

    # 3. upload to 'log' and 'domain' tables
    cnx = sql.Execution()

    action_log = open(f'{sys.path[0]}/history.log', 'r')
    lines = action_log.readlines()
    if 'failed' in lines[-1]:
        log_action('close')
        return
    action_log.close()

    cnx.auto_import_data('domain', files[0])
    log_action('mysql_domain', domain_file)
    cnx.auto_import_data('log', files[1])
    log_action('mysql_login', login_file)

    # 4. close script and files
    cnx.close()
    log_action('close')
    return

if __name__ == "__main__":
    main()
# Written by Beau Daoust (2021)
import time, sys
from datetime import date

def log_action_base(action, dts, log, info, info2):
    if action == 'mysql_domain':
        log.write(f"{dts}'{info}' uploaded to ezproxy.domain\n")
    elif action == 'mysql_login':
        log.write(f"{dts}'{info}' uploaded to ezproxy.log\n")
    elif action == 'process_logs':
        log.write(f"{dts}'{info}' and '{info2}' files created\n")
    elif action == 'log_dl':
        log.write(f"{dts}EZProxy logs downloaded\n")
    elif action == 'sdir_change':
        log.write(f"{dts}Input directory changed from '{info}' to '{info2}'\n")
    elif action == 'ddir_change':
        log.write(f"{dts}Output directory changed from '{info}' to '{info2}'\n")
    elif action == 'restore':
        log.write(f"{dts}Backup directory settings restored\n")
    elif action == 'backup':
        log.write(f"{dts}Directory settings backed up\n")
    elif action == 'mysql_creds':
        log.write(f"{dts}Login credentials changed for MySQL\n")
    elif action == 'ezp_creds':
        log.write(f"{dts}Login credentials changed for EZProxy\n")
    elif action == 'su_pass':
        log.write(f"{dts}Super user password changed\n")
    elif action == 'su_login':
        log.write(f"{dts}Super user activated\n")
    else:
        print('DEBUGGING:')
        print(f'Invalid action: {action}')
        print(f'Primary description: {info}')
        print(f'Secondary description: {info2}')

def auto_log_action(action, info = None, info2 = None):
    # combine into day/time/source
    dts = date.today().strftime('%Y-%m-%d') + '\t' + time.strftime('%H:%M:%S') + '\t' + 'auto' + '\t'
    log = open(f'{sys.path[0]}/history.log', 'a+')
    if action == 'startup':
        log.write(f"{dts}'automation.py' started\n")
    elif action == 'close':
        log.write(f"{dts}'automation.py' closed\n")
    else:
        log_action_base(action, dts, log, info, info2)
    log.close()

def manual_log_action(action, info = None, info2 = None):
    # combine into day/time/source
    dts = date.today().strftime('%Y-%m-%d') + '\t' + time.strftime('%H:%M:%S') + '\t' + 'manual' + '\t'
    log = open(f'{sys.path[0]}/history.log', 'a+')
    if action == 'startup':
        log.write(f"{dts}'frontend.py' started\n")
    elif action == 'close':
        log.write(f"{dts}'frontend.py' closed\n")
    else:
        log_action_base(action, dts, log, info, info2)
    log.close()

def login_log_action(action):
    # combine into day/time/source
    dts = date.today().strftime('%Y-%m-%d') + '\t' + time.strftime('%H:%M:%S') + '\t' + 'login' + '\t'
    log = open(f'{sys.path[0]}/history.log', 'a+')
    if action == 'ezp_login':
        log.write(f"{dts}EZProxy Admin Access login failed. Please change username and/or password.\n")
    elif action == 'ms_login':
        log.write(f"{dts}MySQL user login failed. Please change username and/or password.\n")
    else:
        log_action_base(action, dts, log)
    log.close()

if __name__ == "__main__":
    print("Please run 'frontend.py' instead.")
# Written by Beau Daoust (2021)

from ezproxy.script import SpiderScript
from logwriter import manual_log_action as log_action
from datetime import date, timedelta, datetime
import reader, time, json, json2, sys, os
import mysql_connection as sql

class Options():
    def __init__(self):
        log_action('startup')
        self.settings = json2.load_file(f'{sys.path[0]}/ezproxy/ezproxy/dir_settings.json') # load dir settings
        self.yesterday = date.today() - timedelta(days = 1) # today minus 1 day
        self.choice_num = 8

    def ch_source_dir(self, new_source_dir):
        log_action('sdir_change', self.settings['source_dir'], new_source_dir)
        self.settings['source_dir'] = new_source_dir
        json2.dump_file(f'{sys.path[0]}/ezproxy/ezproxy/dir_settings.json', self.settings)

    def ch_dest_dir(self, new_dest_dir):
        log_action('ddir_change', self.settings['dest_dir'], new_dest_dir)
        self.settings['dest_dir'] = new_dest_dir
        json2.dump_file(f'{sys.path[0]}/ezproxy/ezproxy/dir_settings.json', self.settings)

    def dir_entry(self, dir):
        print("WARNING: Only change directories if absolutely necessary.\n"
              "There are few checks in place to account for incorrect entries. Backslashes are accepted.\n"
              "If you'd like to escape this process prematurely, enter this escape key at any time: *\n")
        new_dir = None
        while True:
            try:
                if dir == 'in':
                    new_dir = str(input("Please enter the full directory path you'd like to save downloaded logs to: "))
                elif dir == 'out':
                    new_dir = str(input("Please enter the full directory path you'd like to save processed logs to: "))
                # if escape key is entered
                if '*' in new_dir:
                    new_dir = None
                    print('Escape key detected.')
                    break
                new_dir = new_dir.replace('\\', '/')  # replace all backslashes with forwardslashes
                new_dir = new_dir.strip()  # strip whitespace from front and end of string
                numtest = int(new_dir[0])  # test if first index is number, resets if true
                new_dir = None
            except ValueError:
                # if entry is missing slashes
                if '/' not in new_dir and '\\' not in new_dir:
                    continue
                # if the second index of the list is not ':'
                if ':' not in new_dir[1]:
                    print("Full path required, therefore must include 'C:', 'D:', etc.")
                    continue
                # add a slash to the end if there is none
                if new_dir[-1] != '/':
                    new_dir = new_dir + '/'
                # check if entered dir is the same as old dir
                if new_dir == self.settings['source_dir']:
                    print('The directory you submitted is already in use as: the download directory.')
                    new_dir = None
                elif new_dir == self.settings['dest_dir']:
                    print('The directory you submitted is already in use as: the parse directory.')
                    new_dir = None
                else:
                    break
        return new_dir

    def create_backup(self):
        try:
            backup = json2.load_file(f'{sys.path[0]}/ezproxy/ezproxy/dir_backup.json')  # load backup dir settings
        except FileNotFoundError as notfound:
            notfound = str(notfound)
            print(notfound[10:])
            print(f"Please create a text file named 'dir_backup.json' at this path: {sys.path[0]}/ezproxy/ezproxy/")
        else:
            print('Are you sure you want to backup the following directory settings? (This action cannot be undone)')
            print(f"Input:\t{self.settings['source_dir']}")
            print(f"Output:\t{self.settings['dest_dir']}")
            if ynchoice():
                backup['source_dir'] = self.settings['source_dir']
                backup['dest_dir'] = self.settings['dest_dir']
                json2.dump_file(f'{sys.path[0]}/ezproxy/ezproxy/dir_backup.json', backup)
                print('Directory settings backed up.')
                log_action('backup')
            else:
                print('Directory settings not backed up.')

    def restore_backup(self):
        try:
            backup = json2.load_file(f'{sys.path[0]}/ezproxy/ezproxy/dir_backup.json')  # load backup dir settings
        except FileNotFoundError as notfound:
            notfound = str(notfound)
            print(notfound[10:])
            print(f"Please create a text file named 'dir_backup.json' at this path: {sys.path[0]}/ezproxy/ezproxy/")
        else:
            print('Are you sure you want to restore directory settings to the following? (This action cannot be undone)')
            print(f"Input:\t{backup['source_dir']}")
            print(f"Output:\t{backup['dest_dir']}")
            if ynchoice():
                self.settings['source_dir'] = backup['source_dir']
                self.settings['dest_dir'] = backup['dest_dir']
                json2.dump_file(f'{sys.path[0]}/ezproxy/ezproxy/dir_settings.json', self.settings)
                print('Backup settings restored.')
                log_action('restore')
            else:
                print('Backup settings not restored.')

    def parse(self, ym, ymd, yest):
        try:
            files = reader.manual_read(self.settings['source_dir'], self.settings['dest_dir'], ym, ymd, yest)
        except FileNotFoundError as notfound: # if file does not exist
            notfound = str(notfound)
            print(notfound[10:])
            print("Possible solution: make sure that all logs are downloaded first. Restart and choose option 1.")
            if ym:
                print("Likely explanation: the month you selected may be incomplete. This happens if your selected month is the current month.")
                print('NOTE: Generated files will contain data up to missing day.')
            return False
        else:
            domain_file = files[0].split('/')[-1]
            login_file = files[1].split('/')[-1]
            if ym:
                log_action('process_logs', domain_file, login_file)
            elif ymd:
                log_action('process_logs', domain_file, login_file)
            else:
                log_action('process_logs', domain_file, login_file)
            return True

class SuperOptions():
    def __init__(self):
        self.check = False
        self.creds = json2.load_file(f'{sys.path[0]}/ezproxy/ezproxy/creds.json') # load creds

    def login(self):
        while True:
            passtest = str(input("Enter password: "))
            passtest = passtest.strip()
            if passtest != self.creds['su_pass']:
                print('Incorrect password. Try again?')
                if not ynchoice():
                    return False
            else:
                # print('Access granted!\n')
                log_action('su_login')
                return True

    def ch_creds(self, choice):
        # change login credentials
        if choice == 1: # MySQL
            print('\n-----Change credentials for: MySQL-----')
            while True:
                usr = str(input('Enter new username: '))
                pwd = str(input('Enter new password: '))
                usr, pwd = usr.strip(), pwd.strip()
                if usr == self.creds['ms_user'] or pwd == self.creds['ms_pass']:
                    print('Username and/or password already exists.')
                    continue
                break
            print('\nAre you sure you want to change the login credentials for MySQL?')
            if ynchoice():
                self.creds['ms_user'] = usr
                self.creds['ms_pass'] = pwd
                json2.dump_file(f'{sys.path[0]}/ezproxy/ezproxy/creds.json', self.creds)
                print('MySQL login credentials changed.')
                log_action('mysql_creds')
            else:
                print('MySQL login credentials not changed.')

        if choice == 2: # EZProxy
            print('\n-----Change credentials for: EZProxy-----')
            while True:
                usr = str(input('Enter new username: '))
                pwd = str(input('Enter new password: '))
                usr, pwd = usr.strip(), pwd.strip()
                if usr == self.creds['ezp_user'] or pwd == self.creds['ezp_pass']:
                    print('Username and/or password already exists.')
                    continue
                break
            print('\nAre you sure you want to change the login credentials for EZProxy?')
            if ynchoice():
                self.creds['ezp_user'] = usr
                self.creds['ezp_pass'] = pwd
                json2.dump_file(f'{sys.path[0]}/ezproxy/ezproxy/creds.json', self.creds)
                print('EZProxy login credentials changed.')
                log_action('ezp_creds')
            else:
                print('EZProxy login credentials not changed.')

        if choice == 3: # Super User
            print('\n-----Change password for: Super User-----')
            while True:
                pwd = str(input('Enter new password: '))
                pwd = pwd.strip()
                if pwd == self.creds['su_pass']:
                    print('Password already exists.')
                    continue
                break
            print('\nAre you sure you want to change the password for Super User?')
            if ynchoice():
                self.creds['su_pass'] = pwd
                json2.dump_file(f'{sys.path[0]}/ezproxy/ezproxy/creds.json', self.creds)
                print('Super User password changed.')
                log_action('su_pass')
            else:
                print('Super User password not changed.')

    def file_search(self, o):
        # choose a file
        files = os.listdir(o.settings['dest_dir'])
        today = date.today().strftime('%Y-%m-%d')
        today_nd = date.today().strftime('%Y%m%d') # no dash
        foi = []  # files of interest
        while True:
            while True:
                try:
                    ymd = str(input("Please specify when log data was processed as YYYYMMDD (or type 'today'): "))
                    if ymd == 'today':
                        ymd = today
                        break
                    test = int(ymd)
                    if len(ymd) != 8:  # ensures length of input is valid
                        continue
                    # if entered ymd is in the future, reset
                    if ymd > today_nd:
                        ymd = None
                        continue
                    ymd = datetime.strptime(ymd, '%Y%m%d').strftime('%Y-%m-%d')
                    break
                except ValueError:
                    ymd = None

            for file in files:
                if ymd in file:
                    foi.append(file)

            # test if files found
            if foi:
                print(f'{len(foi)} files match your query.')
            else:
                print('No files were generated on the given day. Please choose another day or process logs manually.')
                break

            # ask if month or day
            print('\nDo your desired file(s) contain a month of data?')
            copy = foi.copy() # copies list without reference to same location in memory
            if ynchoice(): # months only
                for file in foi:
                    info = file.split('_')
                    if len(info[2]) == 8:
                        copy.remove(file)
            else: # days only
                for file in foi:
                    info = file.split('_')
                    if len(info[2]) == 6:
                        copy.remove(file)
            foi = copy.copy()
            print(f'{len(foi)} files match your query.')
            if not foi:
                break

            # ask for type
            print('\nWould you like to upload...\n'
                  '[1] Login (ezproxy.log)?\n'
                  '[2] Domain (ezproxy.domain)?\n'
                  '[3] Both types (ezproxy.log & ezproxy.domain)?')
            type_choice = multichoice(3)
            copy = foi.copy()
            if type_choice == 1:
                copy = foi.copy()
                for file in foi:
                    if 'domain' in file:
                        copy.remove(file)
                foi = copy.copy()
            elif type_choice == 2:
                copy = foi.copy()
                for file in foi:
                    if 'login' in file:
                        copy.remove(file)
                foi = copy.copy()
            print(f'{len(foi)} files match your query.')
            if not foi:
                break

            # display options
            if type_choice == 3:
                pairs = len(foi) // 2
                print(f'\nThere are {pairs} pairs of files. Please choose one:')
                for counter in range(pairs):
                    index = counter * 2
                    info = foi[index].split('_')
                    info[1] = info[1].replace('-', ':')
                    if len(info[2]) == 6:
                        content = datetime.strptime(info[2], '%Y%m').strftime('%Y-%m')
                    elif len(info[2]) == 8:
                        content = datetime.strptime(info[2], '%Y%m%d').strftime('%Y-%m-%d')
                    print(f'[{counter + 1}]\t\tCreated on: {info[0]} {info[1]}\n'
                          f'\t\tContains log data from: {content}\n'
                          f'\t\tLog data types: login & domain\n')
                file_num = multichoice(pairs) - 1
                file_name = [foi[file_num * 2], foi[(file_num * 2) + 1]]
                file_type = 'both'
                print(f"\nYou have chosen '{file_name[0]}' and '{file_name[1]}' to upload to the database.\n"
                      f"Is this correct?")
            else:
                print(f'\nThere are {len(foi)} total files. Please choose one:')
                counter = 1
                for file in foi:
                    info = file.split('_')
                    info[1] = info[1].replace('-', ':')
                    if len(info[2]) == 6:
                        content = datetime.strptime(info[2], '%Y%m').strftime('%Y-%m')
                    elif len(info[2]) == 8:
                        content = datetime.strptime(info[2], '%Y%m%d').strftime('%Y-%m-%d')
                    if 'domain' in info[3]:
                        file_type = 'domain'
                    elif 'login' in info[3]:
                        file_type = 'login'
                    print(f'[{counter}]\t\tCreated on: {info[0]} {info[1]}\n'
                          f'\t\tContains log data from: {content}\n'
                          f'\t\tLog data type: {file_type}\n')
                    counter += 1
                file_num = multichoice(len(foi))
                file_name = foi[file_num - 1]
                print(f"\nYou have chosen '{file_name}' to upload to the database.\n"
                      f"Is this correct?")
            break
        if ynchoice():
            self.upload(file_name, file_type)
        else:
            print("Operation aborted. Please try choose another file if you'd like.")

    def upload(self, file, type):
        # perform a manual upload to MySQL database
        print("\nIt is strongly suggested that you check 'history.log' before doing a manual upload.")
        print("Are you sure you want to do a manual upload? (This cannot be undone.)")
        if ynchoice():
            cnx = sql.Execution()

            # verify login success
            action_log = open(f'{sys.path[0]}/history.log', 'r')
            lines = action_log.readlines()
            if 'failed' not in lines[-1]:
                cnx.manual_import(type, file)
                if type == 'domain':
                    log_action('mysql_domain', file)
                elif type == 'login':
                    log_action('mysql_login', file)
                elif type == 'both':
                    log_action('mysql_domain', file[0])
                    log_action('mysql_login', file[1])
        else:
            print('Manual upload cancelled.')

def main():
    o = Options()  # create instance of Options class -- basic options
    su = SuperOptions() # create instance of SuperOptions class -- reserved for the super user
    menu(o, su)

def menu(o, su):
    # begin interactable UI
    # os.system('cls')
    if not su.check:
        print("----EZProxy Log Processing----\n"
              "---Copyright(C) Beau Daoust---\n\n"
             f"[1]  DOWNLOAD new logs (up to {o.yesterday})\n"
              "[2]  PROCESS logs\n"
              "{3}  UNLOCK super user mode to perform sensitive actions\n"
              "[4]  CHANGE input directory (where downloaded logs are saved)\n"
              "[5]  CHANGE output directory (where processed logs are saved)\n"
              "[6]  BACKUP directory settings\n"
              "[7]  RESTORE directory settings\n"
              "[8]  CLOSE the program\n")
    else:
        o.choice_num = 10
        print("----EZProxy Log Processing----\n"
              "---Copyright(C) Beau Daoust---\n"
              "~~~~~~~~~~Super User~~~~~~~~~~\n\n"
             f"[1]  DOWNLOAD new logs (up to {o.yesterday})\n"
              "[2]  PROCESS logs\n"
              "{3}  UPLOAD to MySQL database\n"
              "{4}  CHANGE login credentials\n"
              "{5}  EXIT super user mode\n"
              "[6]  CHANGE input directory (where downloaded logs are saved)\n"
              "[7]  CHANGE output directory (where processed logs are saved)\n"
              "[8]  BACKUP directory settings\n"
              "[9]  RESTORE directory settings\n"
              "[10] CLOSE the program\n")
    yest_str = o.yesterday.strftime('%Y%m%d')
    choice = multichoice(o.choice_num)

    # option 1 -------------------------------------------------------------------------------
    if choice == 1:
        # run web crawler
        run_spider()

    # option 2 -------------------------------------------------------------------------------
    elif choice == 2:
        # run log readers
        print("[1] Process yesterday's logs\n"
              "[2] Process specified day of logs\n" # ymd
              "[3] Process specified month of logs\n") # ym
        process_choice = multichoice(3)
        ym = None
        ymd = None
        if process_choice == 1:
            pass
        elif process_choice == 2:
            while True:
                try:
                    ymd = int(input("Please specify year, month, and day as YYYYMMDD: "))
                    ymd = str(ymd)
                    if len(ymd) != 8: # ensures length of input is valid
                        continue
                    # if entered ymd is in the future, reset
                    if ymd > yest_str:
                        ymd = None
                        continue
                    break
                except ValueError:
                    ymd = None
        elif process_choice == 3:
            while True:
                try:
                    ym = int(input("Please specify year and month as YYYYMM: "))
                    ym = str(ym)
                    if len(ym) != 6: # ensures length of input is valid
                        continue
                    # if entered ym is in the future, reset
                    if ym > yest_str[:6]:
                        ym = None
                        continue
                    break
                except ValueError:
                    ym = None
            if ym[4:] == o.yesterday.month:
                print("Current month selected. Logs from start of month to yesterday will be processed and grouped.")
        if o.parse(ym, ymd, yest_str):
            print('Logs processed successfully!')

    # BASIC USER ONLY: option 3 --------------------------------------------------------------
    elif choice == 3 and not su.check:
        # attempt super user mode
        if su.login():
            su.check = True
            return menu(o, su)

    # SUPER USER ONLY: option 3 --------------------------------------------------------------
    elif choice == 3 and su.check:
        # before MySQL upload, first search for desired CSV file(s)
        su.file_search(o)

    # SUPER USER ONLY: option 4 --------------------------------------------------------------
    elif choice == 4 and su.check:
        # change login credentials
        print("Change login credentials for...\n"
              "[1] MySQL\n"
              "[2] EZProxy Admin Access\n"
              "[3] Super User\n")
        su.ch_creds(multichoice(3))

    # option 4 (6 if SU) ---------------------------------------------------------------------
    elif choice == 4 and not su.check:
        # change cwd for downloaded logs
        print(f"\nCurrent input dir: {o.settings['source_dir']}")
        new_dir = o.dir_entry('in')
        if new_dir:
            print("\nAre you sure you want to change the cwd from...\n"
                  f"{o.settings['source_dir']}\n"
                  "to...\n"
                  f"{new_dir} ?")
            if ynchoice():
                o.ch_source_dir(new_dir)
                print(f'Input directory changed to {new_dir}')
            else:
                print('Input directory not changed.')

    # SUPER USER ONLY: option 5 --------------------------------------------------------------
    elif choice == 5 and su.check:
        # exit super user mode
        print('Exiting super user mode...')
        su.check = False
        o.choice_num = 8
        print()
        return menu(o, su)

    # option 5 (7 if SU) ---------------------------------------------------------------------
    elif choice == o.choice_num - 3:
        # change cwd for processed logs
        print(f"\nCurrent output dir: {o.settings['dest_dir']}")
        new_dir = o.dir_entry('out')
        if new_dir:
            print("\nAre you sure you want to change the cwd from...\n"
                  f"{o.settings['dest_dir']}\n"
                  "to...\n"
                  f"{new_dir} ?")
            if ynchoice():
                o.ch_dest_dir(new_dir)
                print(f'Output directory changed to {new_dir}')
            else:
                print('Output directory not changed.')

    # option 6 (8 if SU) ---------------------------------------------------------------------
    elif choice == o.choice_num - 2:
        # create backup of directory settings
        o.create_backup()

    # option 7 (9 if SU) ---------------------------------------------------------------------
    elif choice == o.choice_num - 1:
        # restore backup directory settings
        o.restore_backup()

    # option 8 (10 if SU) ---------------------------------------------------------------------
    elif choice == o.choice_num:
        # exit program
        print('\nThanks for using the program!\nWritten by Beau Daoust (2021)')
        log_action('close')
        print('\nThis window will close in 5 seconds...')
        time.sleep(5)
        return
    else:
        print('ERROR: Input so invalid that the program does not recognize it.')

    restart_query(o, su) # prompt to continue program

def restart_query(options, super):
    print('---\nWould you like to continue using the program?')
    if ynchoice():
        print()
        menu(options, super)
    else:
        print('\nThanks for using the program!\nWritten by Beau Daoust (2021)')
        log_action('close')
        print('\nThis window will close in 5 seconds...')
        time.sleep(5)
        return

def run_spider():
    print('Retrieving logs...')
    spider = SpiderScript()
    spider.run()

    action_log = open(f'{sys.path[0]}/history.log', 'r')
    lines = action_log.readlines()
    if 'failed' not in lines[-1]:
        log_action('log_dl')
        print('Logs retrieved!')
    action_log.close()

def multichoice(range_num):
    while True:
        try:
            choice = int(input(f"Enter your option [1-{range_num}]: "))
            if not 1 <= choice <= range_num:
                choice = None
                continue
            break
        except ValueError:
            choice = None
    return choice

def ynchoice():
    choice = None
    while True:
        try:
            choice = str(input("Enter your option [Y/N]: "))
            numtest = int(choice)
            choice = None
        except ValueError:
            choice = choice.lower()
            if choice == '':
                continue
            elif choice[0] == 'y':
                result = True
                break
            elif choice[0] == 'n':
                result = False
                break
            else:
                choice = None
    if len(choice) > 1:
        print('Multiple characters detected. First character selected.')
    return result
if __name__ == "__main__":
    main()
# Written by Beau Daoust (2021)
import csv, datetime
import time as tm
from calendar import monthrange

def manual_read(source, dest, ym, ymd, yest):
    logToday = datetime.date.today().strftime('%Y-%m-%d')
    logTime = tm.strftime('%H-%M-%S')
    file_front = dest + logToday + "_" + logTime + "_" # ex: "C:.../LogProcessing/venv/Logs/Processed/2020-12-31_23-59-59_"
    print('Generating...')
    if ym:
        domain_file = file_front + ym + "_domain.csv"
        login_file = file_front + ym + "_login.csv"
        dayMax = monthrange(int(ym[:4]), int(ym[4:])) # finds num of days in specified month + year
        for day in range(1, dayMax[1] + 1): # right bound = num of days in month + 1
            day = f'{day:02}'
            fullDate = str(ym) + str(day)
            domain(source, dest, fullDate, domain_file)
            login(source, dest, fullDate, login_file)
    elif ymd:
        domain_file = file_front + ymd + "_domain.csv"
        login_file = file_front + ymd + "_login.csv"
        domain(source, dest, ymd, domain_file)
        login(source, dest, ymd, login_file)
    else:
        domain_file = file_front + yest + "_domain.csv"
        login_file = file_front + yest + "_login.csv"
        domain(source, dest, yest, domain_file)
        login(source, dest, yest, login_file)

    print(f"---\nDomain data stored in file: '{domain_file}'")
    print(f"Login data stored in file:  '{login_file}'\n---")
    files = [domain_file, login_file]
    return files

def auto_read(source, dest, yest):
    logToday = datetime.date.today().strftime('%Y-%m-%d')
    logTime = tm.strftime('%H-%M-%S')
    domain_file = dest + logToday + "_" + logTime + "_" + yest + "_domain.csv"
    login_file = dest + logToday + "_" + logTime + "_" + yest + "_login.csv"

    domain(source, dest, yest, domain_file)
    login(source, dest, yest, login_file)

    files = [domain_file, login_file]
    return files

def domain(source, dest, logDate, csvFile):
    fileName = source + 'spu' + str(logDate) + '.log'
    logFile = open(fileName, 'r')
    logData = []
    date = []
    time = []
    ip = []
    encText = []
    p_check = []
    domain = []
    fullSite = []
    logFile = logFile.read()
    counter = 0
    split = 10
    for info in logFile:
        logData.append(info)
        if (info == '\t' or info == '\n'):
            data = ''.join(logData[:-1])
            if (counter == 0):
                # split datetime at first instance of ':'
                for i in range(len(data)):
                    if data[i] == ':':
                        split = i
                        break
                tempDate = data[:split]
                try:
                    dateTest = datetime.datetime.strptime(tempDate, '%Y/%m/%d') # read as YYYY/MM/DD format
                except ValueError:
                    print('ERROR: Incorrect date format detected\n'
                          'Date attempted: {14}\n'
                          'Time attempted: {15}\n'
                          'Previous two log entries:\n'
                          '{0:12} {1:10} {2:20} {3:20} {4:10} {5:30} {6:100}\n'
                          '{7:12} {8:10} {9:20} {10:20} {11:10} {12:30} {13:100}\n'.format(date[-1], time[-1], ip[-1], encText[-1], p_check[-1], domain[-1], fullSite[-1],
                                                                                           date[-2], time[-2], ip[-2], encText[-2], p_check[-2], domain[-2], fullSite[-2],
                                                                                           tempDate, data[split + 1:]))
                    return
                date.append(tempDate)
                time.append(data[split + 1:])
            elif (counter == 1):
                ip.append(data)
            elif (counter == 2):
                encText.append(data)
            elif (counter == 3):
                p_check.append(data)
            elif (counter == 4):
                domain.append(data)
            elif (counter == 5):
                fullSite.append(data)
                counter = -1
            counter = counter + 1
            logData = []
    fullSite.append(data)
    # to display processed data for testing, uncomment the next 4 lines
    '''i = 0
    for loop in date:
        print("{0:12} {1:10} {2:20} {3:20} {4:10} {5:30} {6:100}".format(date[i], time[i], ip[i], encText[i], p_check[i], domain[i], fullSite[i]))
        i = i+1'''
    with open(csvFile, 'a+') as file:
        write = csv.writer(file, delimiter='\t')
        for i in range(len(date)):
            write.writerow([date[i], time[i], ip[i], encText[i], domain[i], fullSite[i]])

def login(source, dest, logDate, csvFile):
    fileName = source + str(logDate) + '.txt'
    logFile = open(fileName, 'r')
    logData = []
    date = []
    time = []
    event = []
    ip = []
    user = []
    session = []
    other = []
    skip = True
    logFile = logFile.read()
    counter = 0
    for info in logFile:
        # skip first line
        if skip:
            if info == '\n':
                skip = False
        else:
            logData.append(info)
            if info == '\t' or info == '\n':
                data = ''.join(logData[:-1])
                if data == '':
                    data = None
                if counter == 0:
                    dtSplit = data.split(' ') # split by space
                    finalDate = datetime.datetime.strptime(dtSplit[0], '%Y-%m-%d') # read as YY-MM-DD format
                    finalDate = finalDate.strftime('%Y/%m/%d') # convert to YYYY/MM/DD format
                    date.append(finalDate)
                    time.append(dtSplit[1])
                    counter += 1
                elif counter == 2:
                    event.append(data)
                elif counter == 3:
                    ip.append(data)
                elif counter == 4:
                    user.append(data)
                    if logData[-1] == '\n':
                        session.append(None)
                        other.append(None)
                        counter = -1
                elif counter == 5:
                    session.append(data)
                elif counter == 6:
                    if logData[-1] == '\n': # usual case
                        other.append(data)
                        counter = -1
                    elif logData[-1] == '\t': # happens if entry is missing OTHER
                        other.append(None)
                        dtSplit = data.split(' ')
                        finalDate = datetime.datetime.strptime(dtSplit[0], '%Y-%m-%d')
                        finalDate = finalDate.strftime('%Y/%m/%d')
                        date.append(finalDate)
                        time.append(dtSplit[1])
                        counter = 1
                logData = []
                counter += 1
    # to display processed data for testing, place quotes around all instances of None and uncomment the next 4 lines
    '''i = 0
    for loop in date:
        print("{0:10} {1:8} {2:25} {3:20} {4:30} {5:17} {6:100}".format(date[i], time[i], event[i], ip[i], user[i], session[i], other[i]))
        i = i+1'''
    with open(csvFile, 'a+') as file:
        write = csv.writer(file, delimiter='\t')
        for i in range(len(date)):
            write.writerow([date[i], time[i], event[i], ip[i], user[i], session[i], other[i]])

if __name__ == "__main__":
    source = "C:/Users/beaud/Documents/Pycharm Projects/LogProcessing/venv/Logs/Downloaded/"
    dest = "C:/Users/beaud/Documents/Pycharm Projects/LogProcessing/venv/Logs/Processed/"
    yearmonth = '202012'  # YYYYMM format
    ymd = None
    yest = None
    manual_read(source, dest, yearmonth, ymd, yest)
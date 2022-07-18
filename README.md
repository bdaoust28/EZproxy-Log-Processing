# EZproxy Log Processor
###### by Beau Daoust (2021)
This project is an ETL pipeline that automatically crawls for, processes, and uploads EZproxy logs to a MySQL database. 

*DISCLAIMER: the user must store their own JSON files in **/ezproxy/ezproxy** for this project to function.*

**Project dependencies:**
   - scrapy
   - mysql-connector-python
   - json2

This project can be ran automatically by calling **automation.py** using Task Scheduler (Windows) or Cron (Linux).

*The following information is a modified version of the internal README, provided with permission:*
## Using this project
### Instructions on how to open and run the frontend:

1. Double click 'frontend.py'. If this method does not work, continue to step 2. If a small menu opens with the title "EZproxy Log Processing", you can move on to the next section.
2. Right-click 'frontend.py', click 'Edit with IDLE', then click 'Edit with IDLE 3.7/3.9 (64-bit)'*. A new window will open.
3. Try pressing F5 on your keyboard. If a new window opened, go to step 5.
4. If the previous step did not work, click 'Run' at the top of the window, then 'Run Module'. A new window will open.
5. Wait a few seconds until you see a small menu open with the title "EZproxy Log Processing". You are now interacting with the frontend, and you can move on to the next section.

* It is possible there will be different IDLE versions listed. The project's required modules are already installed to work with both IDLE 3.7 and 3.9.
	* If neither is listed, then the script will likely not run (and likely has not been running), and you should scroll down to the last section of this document titled 'What to do if the project is not working'

### Instructions on how to use the frontend:

Once opened, the frontend will present a list of options. Simply type a number between 1-8 and press Enter.
1. Download new logs
	* This will retrieve all available logs from EZproxy up until yesterday. This is because today's logs are still incomplete.
2. Process logs
	* Here you will be presented with three more options:
        1) Process yesterday's logs
        2) Process specified day of logs
        3) Process specified month of logs
	* After entering your choice, two CSV files will be created containing the processed data from two logs.
3. Unlock super user mode
	* Enabling this mode will allow the ability to perform sensitive actions.
	* This mode is detailed in the next section.
4. Change input directory (where downloaded logs are saved)
	* This option lets you submit a new directory where logs downloaded from EZproxy will go.
	* Please only do this when absolutely necessary.
5. Change output directory (where processed logs are saved)
	* This option lets you submit a new directory where the CSV files will be saved.
	* Please only do this when absolutely necessary.
6. Backup directory settings
    * This option lets you back up current directory settings to be restored at another time.
7. Restore directory settings
	* This option lets you restore backup directory settings in case of incorrect directory changes made using options 4 and 5.
8. Close the program
	* This option will close the program.

#### Super user mode:
Unlocking super user mode allows the ability to perform sensitive actions, such as:
1. Upload to MySQL database
    * This option allows you to choose CSV files to manually upload to the database.
    * Please use caution when using this feature, as this could result in data redundancy.
2. Change login credentials
    * This option allows you to change the usernames and/or passwords for the MySQL database user, EZproxy admin website, and super user.
    * This option should only be used when absolutely necessary as it could prevent the project from working properly.

### Instructions on how to migrate the entire project to a new directory (Windows):

This is a somewhat tedious process, so hopefully these instructions will be concise enough.
These instructions are written with the assumption that you are using Windows and PyCharm is installed on your system.
If it is not already installed, you can [download it for free](https://www.jetbrains.com/pycharm/download/).
1. Open PyCharm and start a new project.
2. After all loading is done, open terminal by clicking the button on the bottom left of PyCharm, and install the project dependencies in terminal by typing 'pip install scrapy mysql-connector-python json2'.
3. Navigate to .../LogProcessing/venv/ in terminal using 'cd' command.
4. Type in terminal: 'scrapy startproject ezproxy'. Once the project is created, there will be a new folder in /venv/ named 'ezproxy', with another folder of the same name within it.
5. Copy all files and folders from the old project and paste them into this project. When prompted, click 'replace all files'.
6. Run 'frontend.py' and choose options 4 and 5 to change the input and output directories to what you want them to be.
	It is likely that there is now a /venv/Logs folder that contains two folders named /Downloaded/ and /Processed/. It would be best if you entered those directories into the script.
7. Once the directories have been changed, stop and rerun 'frontend.py', and choose option 2 ('PROCESS logs').
8. Try processing some data to test if your directory changes were correct. If not, change the directories to how they should be.
9. If all works correctly, then you can navigate to /venv/ezproxy/ezproxy/ and copy the contents of 'dir_settings.json' to 'dir_backup.json'.
	This will allow you to restore the correct directory settings via the frontend if accidentally tampered with in the future.
	DO NOT change the names of these files, or the script will break.
10. Open Task Scheduler (which can be found by typing it in the search bar). 
11. Click "Create Basic Task..." on the right side of the window.
12. Type "EZproxy_Log_Processing_Automation" in the Name field, and write any description. Click Next.
13. Make sure "Daily" is selected and click Next.
14. Edit "Start" to be tomorrow's date and 3:00:00 AM (no need to sync time zones), and make sure it recurs every 1 day. Click Next.
15. Make sure "Start a program" is selected and click Next.
16. Click "Browse..." and navigate to the .../LogProcessing/ folder, and select "run_automation.bat". Click Next.
17. Make sure all info is correct, and click Finish.

Congratulations! This project should now be properly migrated to its new location.

## Notable Project Files
### reader.py
* This script processes the EZproxy log files and generates CSV files with normalized data.

### ezproxy_spider.py
* This script contains the EZproxySpider class that performs the automated web crawling and log downloading process.

### pipelines.py
* This script overrides the standard Scrapy FilesPipeline by inheriting and overriding its file_path() method.
* This ensures that downloaded log files are named appropriately, rather than encrypted (which was Scrapy’s standard).

### dir_settings.json
* This JSON file contains the input/source and output/destination directories used by the project to store EZproxy log files and to store generated CSV files, respectively.

### dir_backup.json
* This JSON file contains a backup of the directories stored in dir_settings.json, allowing the user to restore previous directory settings at any time.

### creds.json
* This JSON file contains the login credentials for the EZproxy admin site, MySQL database, and super user.

### mysql_connection.py
* This script inherits the mysql-connector-python module to initialize a connection with the MySQL database and submit queries.

### automation.py
* This script downloads, processes, and uploads yesterday’s EZproxy logs to the MySQL database.
* Automatically running this script on a daily basis will ensure the MySQL database is up to date.
* All actions done by 'automation.py' are logged to 'history.log'.

### frontend.py
* This script contains the project’s front-end, which is interactable by the user when ran.
* It allows the user to manually download EZproxy logs, process any single or group of logs, change the input or output directories, back-up and restore directory settings, and perform manual database uploads.
* All actions done by 'frontend.py' are logged to 'history.log'.

### settings.py & script_settings.py
* These scripts are the settings files for the main Scrapy configuration and for the scripted version, respectively.

### script.py
* This script calls the EZproxySpider class from ezproxy_spider.py and initializes a scripted instance of the spider, replacing the need to run the spider in the terminal.

### logwriter.py
* This script writes to 'history.log' whenever an action is taken by the project, manual or automatic.

### history.log
* All actions taken within this project are recorded into 'history.log'.
* The information within this file is essential for system administrators and/or other IT professionals to identify issues related to this project.
* There are four columns: Date, Time, Source, Event.

    * Date and Time tell exactly when the action was taken.
    * Source identifies whether the action was taken manually (using 'frontend.py') or automatically (using 'automation.py'). It could also identify whether there has been a login failure.
    * Event describes the action taken.

## What to do if the project is not working

This is where you should be if you suspect that this project has not been running properly (perhaps when discovering that no EZproxy log data has been uploaded lately), or you noticed that IDLE versions 3.7 and 3.9 do not exist.

There are many things to keep in mind if this is the case; the most important of which being that no log data has been uploaded to the MySQL database in a certain amount of time.
	The easiest way to find out how long this project has not been running is by looking at 'history.log' and finding the last time an instance of 'auto' has run.
	The second way might have been the one that brought you here, which is that the 'domain' and 'login' data is not up-to-date in their respective tables in the MySQL database.

If your suspicions have been confirmed, then follow these next steps:
1. Ensure that all files are accounted for.
2. You should install the following modules on the new Python version via command prompt using the command 'py -m pip install'...
    - scrapy
    - mysql-connector-python
    - json2
	
	If you don't see any messages that say 'Requirement already satisfied', then you're on the right track.
    If you do, this means that all of the modules are already installed and step 3 may instead be the solution.
3. Navigate to ./LogProcessing/ and you will see a file called 'run_automation' or 'run_automation.bat'. Right-click on it and select 'Edit' (note: do NOT select 'Open', as this will run the file).
	Once opened for editing via Notepad (or any other text editor), delete '-3.9'. This removes the requirement to make 'automation.py' run using the Python 3.9 interpreter, and will instead run the newest version.

#### If any of the above steps fixed the project, you will now need to upload all missing log data up to yesterday (the day prior to the day you are reading this).
This can be done by running 'frontend.py', unlocking super user mode, selecting the "UPLOAD to MySQL database" option after generating the necessary data you need to upload.

If the manual upload feature is somehow not functioning properly, contact a database administrator, or at least someone you know with DBMS experience.

## Thank you for taking the time to read this document!

As of June 28th 2021, this project was developed entirely by Beau Daoust, a ULV alum with a B.S. in Computer Science, Software.

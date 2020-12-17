"""The workflow execution:
1) Get all the EQUITY_* data of the week and collect it into one CSV file WEEKLY_*
2) Create a back of all the EQUITY_* files in a back_up location.
3) Remove the daily logs of the week and the EQUITY_* files.
4) Convert WEEKLY_* files in JSON.
5) Insert it inES index as docs. If it fails retain the WEEKLY_JSON_TMP"""

from datetime import datetime
import glob
import shutil
import os
import pandas as pd
from elasticsearch.exceptions import ConnectionTimeout, ConflictError
from LoggerApi.Logger import Logger
from Harvester import Utils


LOGGER = Logger(__file__, "WEEKLY_GATHERING")
DESTINATION_FOLDER = "/backup_stock_data/"
DAILY_DATA_FILES = [daily_data for daily_data in
                    glob.glob(".\\resources\\*.csv") if "EQUITY" in daily_data]
LOG_FILES = [logs for logs in
             glob.glob(os.path.dirname(os.path.dirname(__file__)) + "\\*LOG*") if "LOG" in logs]
FIRST_FILE_INDICATOR = True

for file in DAILY_DATA_FILES:
    date = file.split("\\")[2].split(".")[0].split("_")[-1:][0]
    daily_df = pd.read_csv(file)
    daily_df['processingDate'] = date
    if FIRST_FILE_INDICATOR:
        FIRST_FILE_INDICATOR = False
        column_names = daily_df.columns
        FINAL_DATA = daily_df.copy()
        LOGGER.add("INFO", "First files parsed."
                           " Date:{}".format(date[:2] + "/" + date[2:4] + "/" + date[4:]))
        continue
    FINAL_DATA = pd.concat([FINAL_DATA, daily_df], axis=0)
    LOGGER.add("INFO",
               "Data added for Date:{} ".format(date[:2] + "/" + date[2:4] + "/" + date[4:]))

try:
    FINAL_DATA.to_csv(".\\resources\\WEEKLY_{}.csv".format(datetime.now().strftime('%d%m%Y')),
                      index=False)
    LOGGER.add("INFO", "COMPLETED")
    LOGGER.add("INFO", "Moving the daily data of the week to the back-up folder.")
    for file in DAILY_DATA_FILES:  # move the daily collected files to backup folder
        try:
            shutil.move(file, DESTINATION_FOLDER)
        except shutil.Error:
            LOGGER.add("ERROR", "The file already exists in back-up")
            os.remove(file)
            LOGGER.add("INFO", "The duplicates removed from cwd")
    for file in LOG_FILES:  # removing the logs for the week
        os.remove(file)

    Utils.weekly_report_to_json()  # Converting all the csv weekly report to JSON file
    LOGGER.add("INFO", "Converted to JSON successfully.")

    try:
        Utils.insert_to_es_index(LOGGER)  # Insert the file to ES
        LOGGER.add("INFO", "Insertion into ES was successful")
        for file in [weekly_json for weekly_json in glob.glob(".\\resources\\*JSON*")]:
            try:
                shutil.move(file, DESTINATION_FOLDER)
            except shutil.Error:
                LOGGER.add("ERROR", "File already exists")
                os.remove(file)
    except ConnectionTimeout:
        LOGGER.add("ERROR", "Connection Timed out while inserting")
    except ConflictError:
        LOGGER.add("ERROR", "Error while establishing connection. Please check ES host is up.")

    for file in [daily_data for daily_data in glob.glob(".\\resources\\*.csv") if
                 "WEEKLY" in daily_data]:  # Removing the temporary WEEKLY* csv files
        os.remove(file)
    LOGGER.add("INFO", "Weekly temp csv files removed.")
except NameError:
    LOGGER.add("ERROR", "There is not data present in the resource folder.")

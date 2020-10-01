from datetime import datetime
import pandas as pd
import glob
from LoggerApi.Logger import Logger
import shutil
from Harvester import Utils
import os
from elasticsearch.exceptions import ConnectionTimeout, ConflictError

"""The workflow execution:
1) Get all the EQUITY_* data of the week and collect it into one CSV file WEEKLY_*
2) Create a back of all the EQUITY_* files in a back_up location.
3) Remove the daily logs of the week and the EQUITY_* files.
4) Convert WEEKLY_* files in JSON.
5) Insert it inES index as docs. If it fails retain the WEEKLY_JSON_TMP"""


logger = Logger(__file__, "WEEKLY_GATHERING")
DESTINATION_FOLDER = "/backup_stock_data/"
DAILY_DATA_FILES = [daily_data for daily_data in glob.glob(".\\resources\\*.csv") if "EQUITY" in daily_data]
LOG_FILES = [logs for logs in glob.glob(os.path.dirname(os.path.dirname(__file__)) + "\\*LOG*") if "LOG" in logs]
first_file_indicator = True
for file in DAILY_DATA_FILES:
    date = file.split("\\")[2].split(".")[0].split("_")[-1:][0]
    daily_df = pd.read_csv(file)
    daily_df['processingDate'] = date
    if first_file_indicator:
        first_file_indicator = False
        column_names = daily_df.columns
        FINAL_DATA = daily_df.copy()
        logger.add("INFO", "First files parsed. Date:{}".format(date[:2] + "/" + date[2:4] + "/" + date[4:]))
        continue
    FINAL_DATA = pd.concat([FINAL_DATA, daily_df], axis=0)
    logger.add("INFO", "Data added for Date:{} ".format(date[:2] + "/" + date[2:4] + "/" + date[4:]))


try:
    FINAL_DATA.to_csv(".\\resources\\WEEKLY_{}.csv".format(datetime.now().strftime('%d%m%Y')), index=False)
    logger.add("INFO", "COMPLETED")
    logger.add("INFO", "Moving the daily data of the week to the back-up folder.")
    for file in DAILY_DATA_FILES:  # move the daily collected files to backup folder
        shutil.move(file, DESTINATION_FOLDER)
    for file in LOG_FILES:  # removing the logs for the week
        os.remove(file)

    Utils.weekly_report_to_json()  # Converting all the csv weekly report to JSON file
    logger.add("INFO", "Converted to JSON successfully.")

    try:
        Utils.insert_to_es_index()  # Insert the file to ES
        logger.add("INFO", "Insertion into ES was successful")
        for file in [weekly_json for weekly_json in glob.glob(".\\resources\\*JSON*")]:
            shutil.move(file, DESTINATION_FOLDER)
    except ConnectionTimeout:
        logger.add("ERROR", "Connection Timed out while inserting")
    except ConflictError:
        logger.add("ERROR", "Error while establishing connection. Please check ES host is up.")

    # Uncomment once ES becomes a reliable source of data storage.
    # for file in [daily_data for daily_data in glob.glob(".\\resources\\*.csv") if
    #              "WEEK" in daily_data]:  # Removing the temporary csv files
    #     os.remove(file)
    # logger.add("INFO", "Weeks log files removed.")
except NameError:
    logger.add("ERROR", "There is not data present in the resource folder.")
except shutil.Error:
    logger.add("ERROR", "The file already exists in back-up")
    for file in DAILY_DATA_FILES:
        os.remove(file)
    logger.add("INFO", "The duplicates removed from cwd")

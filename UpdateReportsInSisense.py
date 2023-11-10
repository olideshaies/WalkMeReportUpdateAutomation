# main.py
#!/usr/bin/env python3
import logging
from logging.handlers import TimedRotatingFileHandler
from WalkMeReportUpdateFile import *
from EmailFetching.WalkMeReportFetchGmailCSV import fetch_csvs_from_today
import shutil
import os

# Setting up the logging
log_file = "logs/script.log"
log_handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, encoding='utf-8')
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
log_handler.suffix = "%Y-%m-%d"

logging.basicConfig(level=logging.INFO,
                    handlers=[log_handler, logging.StreamHandler()])

logger = logging.getLogger()


REPORT_CLASSES = {
    #ONBOARDING FILES#
     "OnboardingSurveyComment": (UpdateOnBoardingSurveyComment, "OnboardingSurvey"),
     "OnboardingSurvey": (UpdateOnBoardingSurvey, "OnboardingSurvey"),
     "OnboardingSurveyViews": (UpdateOnBoardingSurveyViews, "OnboardingSurvey"),
    #CONTINUOUS SATISFACTION SCORE FILES#
     "dbo.ContinuousSatisfactionScore": (UpdateContinuousSatisfactionScore, "ContinuousSatisfactionScore"),
    #NPS FILES#
    # NOT FOR NOW IF REACTIVATING need to change "the name of the survey segmentation"
    #(UNCOMMENT HERE)"dbo.NpsCampaign": (UpdateNPS, "NPS")
}

if __name__ == "__main__":
    # Strip the ".csv" from the subject before processing
    subjects_and_paths = [(subject.replace('.csv', ''), path) for subject, path in fetch_csvs_from_today()]

    for subject, csv_path in subjects_and_paths:
        logger.info(f"Email Subject: {subject}")
        logger.info(f"CSV File Path: {csv_path}")

        # Dynamically find and instantiate the matching class
        matched_class = None
        directory_group = None
        
        # Use word-matching logic to find the corresponding class
        subject_words = set(subject.split())
        for key, (value, dir_group) in REPORT_CLASSES.items():
            key_words = set(key.split())
            if key_words.issubset(subject_words):
                matched_class = value
                directory_group = dir_group
                break

        if matched_class:
            report = matched_class(directory_group, subject, csv_path)
            report.process()
        else:
            logger.warning(f"No matching class found for subject: {subject}")

    # Empty temp_csv_folder
    shutil.rmtree(r'C:\Users\olivier.deshaies\Desktop\GIT\WalkMeReportUpdateAutomation\temp_csv_files')
    os.mkdir(r'C:\Users\olivier.deshaies\Desktop\GIT\WalkMeReportUpdateAutomation\temp_csv_files')
    logger.info("Temp_csv_files folder emptied")
    logger.info("All files processed")
    print("Temp_csv_files folder emptied")
    print("All files processed")
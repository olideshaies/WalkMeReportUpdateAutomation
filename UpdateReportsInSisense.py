# main.py
from WalkMeReportUpdateFile import *
from EmailFetching.WalkMeReportFetchGmailCSV import fetch_csvs_from_today
import shutil
import os

REPORT_CLASSES = {
    #ONBOARDING FILES#
    # "OnboardingSurveyComment": (UpdateOnBoardingSurveyComment, "OnboardingSurvey"),
    # "OnboardingSurvey": (UpdateOnBoardingSurvey, "OnboardingSurvey"),
    # "OnboardingSurveyViews": (UpdateOnBoardingSurveyViews, "OnboardingSurvey"),
    #CONTINUOUS SATISFACTION SCORE FILES#
    "dbo.ContinuousSatisfactionScore": (UpdateContinuousSatisfactionScore, "ContinuousSatisfactionScore"),
    #NPS FILES#
    # NOT FOR NOW IF REACTIVATING need to change "the name of the survey segmentation"
    #(UNCOMMENT HERE)"dbo.NpsCampaign": (UpdateNPS, "NPS")
}

if __name__ == "__main__":
    subjects_and_paths = fetch_csvs_from_today()

    for subject, csv_path in subjects_and_paths:
        print(f"Email Subject: {subject}")
        print(f"CSV File Path: {csv_path}")

        # Dynamically find and instantiate the matching class
        matched_class = None
        directory_group = None
        for key, (value, dir_group) in REPORT_CLASSES.items():
            if key in subject:
                matched_class = value
                directory_group = dir_group
                break

        if matched_class:
            report = matched_class(directory_group, subject, csv_path)
            report.process()
        else:
            print(f"No matching class found for subject: {subject}")

    # Empty temp_csv_folder
    shutil.rmtree(r'C:\Users\olivier.deshaies\Desktop\GIT\WalkMeReportUpdateAutomation\temp_csv_files')
    os.mkdir(r'C:\Users\olivier.deshaies\Desktop\GIT\WalkMeReportUpdateAutomation\temp_csv_files')
    print("Temp_csv_files folder emptied")
    print("All files processed")

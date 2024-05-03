import os
import shutil
import pandas as pd
import datetime
from  EmailFetching.WalkMeReportFetchGmailCSV import fetch_csvs_from_today

class WalkMeReportUpdateFile:
    def __init__(self, directory_group, subject, csv_path):
        self.directory_group = directory_group
        self.subject = subject
        #add general csv path and single survey csv path (modify the self.csv_path under to get repeated string in the csv path)
        self.csv_path = csv_path
        self.file_name = os.path.basename(csv_path)
        self.backup_path = r'\\vmsisense1\Sisense\ExternalDataFile'+ '\\' + directory_group 
    
    def get_backup_path(self):
        # Check if the backup_path directory exists
        if not os.path.exists(self.backup_path):
            raise ValueError(f"The directory {self.backup_path} does not exist!")
        
        # Get all directories inside the self.backup_path directory
        all_dirs = [d for d in os.listdir(self.backup_path) if os.path.isdir(os.path.join(self.backup_path, d))]
        
        # Find the first directory that contains the word 'backup' (case-insensitive)
        backup_folder = next((d for d in all_dirs if 'backup' in d.lower()), None)

        # If no such directory exists, create a default 'backup' directory inside self.backup_path
        if not backup_folder:
            backup_folder = self.subject + "_backup"
            os.mkdir(os.path.join(self.backup_path, backup_folder))

        final_backup_path = os.path.join(self.backup_path, backup_folder, self.file_name)
        return final_backup_path

    def save_actual_file(self):
        # First backup the existing file with the same name as the fetched CSV in the backup_path
        existing_file_path = os.path.join(self.backup_path, self.file_name)
        if os.path.exists(existing_file_path):
            backup_target = self.get_backup_path()
            yesterday_date = datetime.datetime.now() - datetime.timedelta(days=1)
            yesterday_date_str = yesterday_date.strftime("%Y-%m-%d")
            backup_file_name = f"{os.path.splitext(self.file_name)[0]}_{yesterday_date_str}{os.path.splitext(self.file_name)[1]}"
            backup_target = os.path.join(os.path.dirname(backup_target), backup_file_name)
            
            shutil.copy(existing_file_path, backup_target)
            print(f"Existing file backed up to: {backup_target}")
        else:
            print(f"No existing file named {self.file_name} found in {self.backup_path} to backup.")
    
    # Just need to add another function to merge csv files with similar name then output one csv file with the merged data to be use after
    # 1. fetch all emails from today

    def clean_data(self):
        # You can modify this method based on your cleaning requirements
        df = pd.read_csv(self.csv_path)

        print(f"Data cleaned for {self.csv_path}")
        return df
    
    def append_new_data(self):
        # Get actual file in Directory
        actual_file_path = os.path.join(self.backup_path, self.file_name)
        df = pd.read_csv(actual_file_path)
        # add new data to the end of the file
        new_data = self.clean_data()
        df= pd.concat([df, new_data], ignore_index=True)
        return actual_file_path, df

    def update_actual_file(self):
        # Save the file to the actual file path
        actual_file_path, updated_df = self.append_new_data()
        updated_df.to_csv(actual_file_path, index=False)

    def log(self, message):
        # You can log to a file or just print out. Here's a simple print-based log.
        print(f"[{self.subject}]: {message}")
    
    def process(self):
        self.save_actual_file()
        #self.merge_files()
        self.update_actual_file()
        self.log("Processing Complete")

# Define sub classes of WalkMeReportUpdateFile for each type of report you want to process

######################
## ONBOARDING FILES ##
######################

class UpdateOnBoardingSurvey(WalkMeReportUpdateFile):
    def clean_data(self):
        # You can modify this method based on your cleaning requirements
        df = pd.read_csv(self.csv_path)        
        # 1 drop columns Number of Survey Submittals & Number of Survey Plays \\
        # 2 add QuestionDate&Time(Eastern) next to QuestionDate&Time(UTC) just copy same value -4 hours \\ 
        # 3 move Quesstion to the last column
        df = df.drop(columns='Number of Survey Submittals') 
        df = df.drop(columns='Number of Survey Plays')
        # copy QuestionDate&Time(UTC) to QuestionDate&Time(Eastern) - 4H
        df['Question Date & Time (UTC)'] = pd.to_datetime(df['Question Date & Time (UTC)'])
        df['QuestionDate&Time(Eastern)'] = df['Question Date & Time (UTC)'] - pd.Timedelta(hours=4)
        # Move QuestionDate&Time(Eastern) to the second column
        colEsternDate = df.pop('QuestionDate&Time(Eastern)')
        df.insert(4, colEsternDate.name, colEsternDate)
        # Move Question to the last column
        colQuestion = df.pop('Question')
        df.insert(len(df.columns), colQuestion.name, colQuestion)
        # Order by QuestionDate&Time(UTC)
        df = df.sort_values(by=['Question Date & Time (UTC)'])
        #Remove the empty spaces in the column names
        df.columns = df.columns.str.replace(' ', '')
        print(f"Data cleaned for {self.csv_path}")
        return df

    def append_new_data(self):
        # Get actual file in Directory
        actual_file_path = os.path.join(self.backup_path, self.file_name)
        df = pd.read_csv(actual_file_path)
        # add new data to the end of the file
        new_data = self.clean_data()
        starting_id = df['Id'].max()
        # add the id column to the new data continue the numbering
        new_data['Id'] = [starting_id + i for i in range(1, len(new_data) + 1)]
        df= pd.concat([df, new_data], ignore_index=True)
        return actual_file_path, df
        #NEED TO ADD THE ID NUMBER FOLLOWING THE ORIGINAL FILE (CONTINUE THE NUMBERING)

class UpdateOnBoardingSurveyViews(WalkMeReportUpdateFile):
    def clean_data(self):
        df = pd.read_csv(self.csv_path)
        #Drop empty account name rows
        df = df.dropna(subset=['Account Name'])
        # Drop all rows where both 'Users Viewed Surveys' and 'Users Submitted Surveys' are 1
        df = df[~((df['Users Viewed Surveys'] == 1) & (df['Users Submitted Surveys'] == 1))]
        # Get the viewers only
        viewers_only = df[df['Users Submitted Surveys'] == 0]
        # Drop the viewers only from the df
        df = df[~(df['Users Submitted Surveys'] == 0)].reset_index(drop=True)
        #Drop empty Question rows
        df = df.dropna(subset=['Question'])
        # Get the list of questions asked grouped by survey
        question_by_survey = df.groupby('Survey ID')['Question'].apply(list).to_dict()
        
        # Initialize an empty list to collect new rows
        new_rows = []
        # Iterate over viewers_only DataFrame
        for _, viewer_row in viewers_only.iterrows():
            survey_id = viewer_row['Survey ID']
            # Get the list of unique questions for the survey ID
            questions = list(set(question_by_survey.get(survey_id, [])))
            # Create a new row for each unique question
            for question in questions:
                if question:  # Ensure the question is not empty
                    new_row = viewer_row.copy()
                    new_row['Question'] = question
                    new_rows.append(new_row)

        # Convert the list of new rows into a DataFrame
        viewers_only_with_question = pd.DataFrame(new_rows)
        # Append the new 'viewers only with question' rows to the df
        df = pd.concat([df, viewers_only_with_question], ignore_index=True)
        return df

    def append_new_data(self):
        # Get actual file in Directory
        actual_file_path = os.path.join(self.backup_path, self.file_name)
        df = pd.read_csv(actual_file_path)
        # add new data to the end of the file
        new_data = self.clean_data()
        #Remove the empty spaces in the column names
        new_data.columns = new_data.columns.str.replace(' ', '')
        df= pd.concat([df, new_data], ignore_index=True)
        return actual_file_path, df

class UpdateOnBoardingSurveyComment(WalkMeReportUpdateFile):
    def clean_data(self):
        # You can modify this method based on your cleaning requirements
        df = pd.read_csv(self.csv_path)
        #Remove the empty spaces in the column names
        df.columns = df.columns.str.replace(' ', '')
        print(f"Data cleaned for {self.csv_path}")
        return df
    
class UpdateOnBoardingSurveyNPS(WalkMeReportUpdateFile):
    def clean_data(self):
        # You can modify this method based on your cleaning requirements
        df = pd.read_csv(self.csv_path)        
        # 1 drop columns Number of Survey Submittals & Number of Survey Plays \\
        # 2 add QuestionDate&Time(Eastern) next to QuestionDate&Time(UTC) just copy same value -4 hours \\ 
        # 3 move Quesstion to the last column
        df = df.drop(columns='Number of Survey Submittals') 
        df = df.drop(columns='Number of Survey Plays')
        # copy QuestionDate&Time(UTC) to QuestionDate&Time(Eastern) - 4H
        df['Question Date & Time (UTC)'] = pd.to_datetime(df['Question Date & Time (UTC)'])
        df['QuestionDate&Time(Eastern)'] = df['Question Date & Time (UTC)'] - pd.Timedelta(hours=4)
        # Move QuestionDate&Time(Eastern) to the second column
        colEsternDate = df.pop('QuestionDate&Time(Eastern)')
        df.insert(4, colEsternDate.name, colEsternDate)
        # Move Question to the last column
        colQuestion = df.pop('Question')
        df.insert(len(df.columns), colQuestion.name, colQuestion)
        # Order by QuestionDate&Time(UTC)
        df = df.sort_values(by=['Question Date & Time (UTC)'])
        #Remove the empty spaces in the column names
        df.columns = df.columns.str.replace(' ', '')
        print(f"Data cleaned for {self.csv_path}")
        return df

    def append_new_data(self):
        # Get actual file in Directory
        actual_file_path = os.path.join(self.backup_path, self.file_name)
        df = pd.read_csv(actual_file_path)
        # add new data to the end of the file
        new_data = self.clean_data()
        starting_id = df['Id'].max()
        # add the id column to the new data continue the numbering
        new_data['Id'] = [starting_id + i for i in range(1, len(new_data) + 1)]
        df= pd.concat([df, new_data], ignore_index=True)
        return actual_file_path, df
        #NEED TO ADD THE ID NUMBER FOLLOWING THE ORIGINAL FILE (CONTINUE THE NUMBERING)


#########################################
## TEACHME FILES ##
#########################################
class UpdateTeachMeCoursesReport(WalkMeReportUpdateFile):
    def clean_data(self):
        df = pd.read_csv(self.csv_path)
        #Remove the empty spaces in the column names
        df.columns = df.columns.str.replace(' ', '')
        print(f"Data cleaned for {self.csv_path}")
        return df
    
class UpdateTeachMeQuizAnswers(WalkMeReportUpdateFile):
    def clean_data(self):
        df = pd.read_csv(self.csv_path)
        #Remove the empty spaces in the column names
        df.columns = df.columns.str.replace(' ', '')
        print(f"Data cleaned for {self.csv_path}")
        return df

#########################################
## CONTINUOUS SATISFACTION SCORE FILES ##
#########################################

class UpdateContinuousSatisfactionScore(WalkMeReportUpdateFile):
    def clean_data(self):
                # You can modify this method based on your cleaning requirements
        df = pd.read_csv(self.csv_path)
        
        # 1 add QuestionDate&Time(Eastern) next to QuestionDate&Time(UTC) just copy same value -4 hours \\ 
        # copy QuestionDate&Time(UTC) to QuestionDate&Time(Eastern) - 4H
        df['Question Date & Time (UTC)'] = pd.to_datetime(df['Question Date & Time (UTC)'])
        df['QuestionDate&Time(Eastern)'] = df['Question Date & Time (UTC)'] - pd.Timedelta(hours=4)
        # Move QuestionDate&Time(Eastern) to the second column
        colEsternDate = df.pop('QuestionDate&Time(Eastern)')
        df.insert(4, colEsternDate.name, colEsternDate)
        # Order by QuestionDate&Time(UTC)
        df = df.sort_values(by=['Question Date & Time (UTC)'])
        print(f"Data cleaned for {self.csv_path}")
        return df
    



###############
## NPS FILES ##   
###############

class UpdateNPS(WalkMeReportUpdateFile):
    
    def clean_data(self):
        # You can modify this method based on your cleaning requirements
        df = pd.read_csv(self.csv_path)

        """ TO ADD NEW NPS SCORE --> Need to define the name of the SurveySegmentation & drop the Number of Survey Plays"""
        # Drop the Number of Survey Plays
        df = df.drop(columns=['Number of Survey Plays'])
        # Add the SurveySegmentation column & define the new name to add
        df['SurveySegmentation'] = '4_March_2024'

        print("\nData cleaned\n", df.head())
        print(f"Data cleaned for {self.csv_path}")
        return df

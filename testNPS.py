import pandas as pd

def clean_data(csv_path):
        # You can modify this method based on your cleaning requirements
        df = pd.read_csv(csv_path)        
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
        print(f"Data cleaned for {csv_path}")
        return df

def append_new_data():
        # Get actual file in Directory
        
        df = pd.read_csv('OnboardingSurveyNPS.csv')
        # add new data to the end of the file
        new_data = clean_data('FullNPS.csv')
        starting_id = df['Id'].max()
        # add the id column to the new data continue the numbering
        new_data['Id'] = [starting_id + i for i in range(1, len(new_data) + 1)]
        df= pd.concat([df, new_data], ignore_index=True)
        return  df
        #NEED TO ADD THE ID NUMBER FOLLOWING THE ORIGINAL FILE (CONTINUE THE NUMBERING)

df = append_new_data()
df.to_csv('OnboardingSurveyNPSNew.csv', index=False)
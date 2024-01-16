import pandas as pd    



def clean_data(csv_path):
    
        df = pd.read_csv(csv_path)
        # Drop all rows where both 'Users Viewed Surveys' and 'Users Submitted Surveys' are 1
        df = df[~((df['Users Viewed Surveys'] == 1) & (df['Users Submitted Surveys'] == 1))]
        # Get the viewers only
        viewers_only = df[df['Users Submitted Surveys'] == 0]
        # Drop the viewers only from the df
        df = df[~(df['Users Submitted Surveys'] == 0)].reset_index(drop=True)
        # Get the list of questions asked grouped by survey
        question_by_survey = df.groupby('Survey ID')['Question'].apply(list).to_dict()
        # Adding the Survey Id and Question from NPS to the viewers only

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

def append_new_data():
        # Get actual file in Directory
        
        df = pd.read_csv(r'C:\Users\olivier.deshaies\Desktop\GIT\WalkMeReportUpdateAutomation\OnboardingSurveyViews.csv')
        # add new data to the end of the file
        new_data = clean_data(r'C:\Users\olivier.deshaies\Desktop\GIT\WalkMeReportUpdateAutomation\Onb. Surveys.csv')

        #Remove the empty spaces in the column names
        new_data.columns = new_data.columns.str.replace(' ', '')
        df= pd.concat([df, new_data], ignore_index=True)
        return df


df = append_new_data()
#df = clean_data('Onb. Surveys.csv')
#df.columns = df.columns.str.replace(' ', '')
df.to_csv('Real_OnboardingSurveyViews', index=False)




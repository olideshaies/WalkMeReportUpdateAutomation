import pandas as pd
import os

class OnboardingSurveyViews:
    def __init__(self):
        self.existing_data = None
        self.new_data = None
    
    def clean_data(self):
        df = self.new_data
        #Drop empty account name rows
        df = df.dropna(subset=['Account Name'])
        # Convert 'Date' column to datetime format (if not already)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  # 'coerce' turns invalid parsing into NaT
        # Drop all rows where both 'Users Viewed Surveys' and 'Users Submitted Surveys' are 1
        df = df[~((df['Users Viewed Surveys'] == 1) & (df['Users Submitted Surveys'] == 1))]
        # Get the viewers only
        viewers_only = df[df['Users Submitted Surveys'] == 0]
        print(viewers_only)
        # Drop the viewers only from the df
        df = df[~(df['Users Submitted Surveys'] == 0)].reset_index(drop=True)
        #drop empty question
        df = df.dropna(subset=['Question'])
        print(df)
        # Get the list of questions asked grouped by survey
        question_by_survey = df.groupby('Survey ID')['Question'].apply(list).to_dict()
        print(question_by_survey)
        
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

        df = self.existing_data
        # add new data to the end of the file
        new_data = self.clean_data()
        #Remove the empty spaces in the column names
        new_data.columns = new_data.columns.str.replace(' ', '')
        df= pd.concat([df, new_data], ignore_index=True)
        return df
    
    def load_data(self, file_path):
        # Load data from a validated file path
        data = pd.read_csv(file_path)
        return data
    
    def fun_message(self):
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║                                                                      ║")
        print("║        ██████╗  ██████╗     ██████╗  ██████╗     ██████╗  ██████╗    ║")
        print("║       ██╔════╝ ██╔═══██╗   ██╔════╝ ██╔═══██╗   ██╔════╝ ██╔═══██╗   ║")
        print("║       ██║  ███╗██║   ██║   ██║  ███╗██║   ██║   ██║  ███╗██║   ██║   ║")
        print("║       ██║   ██║██║   ██║   ██║   ██║██║   ██║   ██║   ██║██║   ██║   ║")
        print("║       ╚██████╔╝╚██████╔╝   ╚██████╔╝╚██████╔╝   ╚██████╔╝╚██████╔╝   ║")
        print("║        ╚═════╝  ╚═════╝     ╚═════╝  ╚═════╝     ╚═════╝  ╚═════╝    ║")
        print("║                                                                      ║")
        print("║    Welcome to the Onboarding Comment!                                ║")
        print("║    Let's make data cleaning fun... or at least as fun as it can be!  ║")
        print("║                                                                      ║")
        print("╚══════════════════════════════════════════════════════════════════════╝")

    def get_valid_file_path(self, file_description):
        while True:
            try:
                file_name = input(f"\n📂 Enter the path to the {file_description} data file: ")
                file_path = os.path.join('ManualExtraction', 'Onboarding', 'VIEWS', file_name)
                pd.read_csv(file_path)  # Try to load the file to check if it exists
                return file_path
            except FileNotFoundError:
                print(f"Error: The file '{file_name}' was not found.")
                decision = input("\nPlease check the file name and path pressing ENTER KEY or if you want to EXIT type in EXIT :")
                if decision.upper() == "EXIT":
                    exit()
                else:
                    continue

    def run(self):
        self.fun_message()
        existing_file_path = self.get_valid_file_path("existing")
        self.existing_data = self.load_data(existing_file_path)

        new_file_path = self.get_valid_file_path("new")
        self.new_data = self.load_data(new_file_path)

        updated_data = self.append_new_data()
        updated_data.to_csv('OnboardingSurveyViews.csv', index=False)
        print("Data successfully updated and saved! 🎉")

# Running the OnboardingSurvey
survey = OnboardingSurveyViews()
survey.run()

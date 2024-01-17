import pandas as pd
import os


class ContinuousSentiment:
    def clean_data(self, new_data):
        df = new_data
        df['Question Date & Time (UTC)'] = pd.to_datetime(df['Question Date & Time (UTC)'])
        df['QuestionDate&Time(Eastern)'] = df['Question Date & Time (UTC)'] - pd.Timedelta(hours=4)
        colEsternDate = df.pop('QuestionDate&Time(Eastern)')
        df.insert(4, colEsternDate.name, colEsternDate)
        df = df.sort_values(by=['Question Date & Time (UTC)'])
        print(f"Data cleaned for {new_data}")
        return df

    def append_new_data(self, new_data, existing_data):
        df = existing_data
        new_clean_data = self.clean_data(new_data)
        df = pd.concat([df, new_clean_data], ignore_index=True)
        return df

    def run(self, new_data, existing_data):
        new_data = self.clean_data(new_data)
        df = self.append_new_data(new_data, existing_data)
        df.to_csv('dbo.ContinuousSatisfactionScore.csv', index=False)
        print("Data saved !!! 🎉🌟")

# Elaborate Welcome Message
print("╔══════════════════════════════════════════════════════════════════════╗")
print("║                                                                      ║")
print("║       █████╗ ██╗     ██╗        ██████╗  ██████╗  ██████╗ ██████╗    ║")
print("║      ██╔══██╗██║     ██║       ██╔════╝ ██╔═══██╗██╔═══██╗██╔══██╗   ║")
print("║      ███████║██║     ██║       ██║  ███╗██║   ██║██║   ██║██║  ██║   ║")
print("║      ██╔══██║██║     ██║       ██║   ██║██║   ██║██║   ██║██║  ██║   ║")
print("║      ██║  ██║███████╗███████╗  ╚██████╔╝╚██████╔╝╚██████╔╝██████╔╝   ║")
print("║      ╚═╝  ╚═╝╚══════╝╚══════╝   ╚═════╝  ╚═════╝  ╚═════╝ ╚═════╝    ║")
print("║                                                                      ║")
print("║    Welcome to the Continuous Sentiment Analyzer!                     ║")
print("║    Let's make data cleaning fun... or at least as fun as it can be!  ║")
print("║                                                                      ║")
print("╚══════════════════════════════════════════════════════════════════════╝")



# Get file names from user
existing_file = input("\n📂 Enter the name of the existing data file (e.g., 'existing_data.csv'): ")
 
while True:
    try:
        existing_file_path = os.path.join('ManualExtraction', 'ContinuousSentiment', existing_file) 
        existing_data = pd.read_csv(existing_file_path)
        break
    except FileNotFoundError:
        print(f"Error: The file '{existing_file}' was not found. Please check the file name and path.")
        what_do_you_want = input('\nTo try again tap the ENTER key or exit by typing "EXIT"')
        if (what_do_you_want).upper == "EXIT":
            exit()
        else:
            existing_file = input ("\nEnter the name of the Existing File again : ")
new_file = input("\n📂 Enter the name of the new data file (e.g., 'new_data.csv'): ")
while True:     
    try:
        new_file_path = os.path.join( 'ManualExtraction', 'ContinuousSentiment', new_file)
        new_data = pd.read_csv(new_file_path)
        break
    except FileNotFoundError:
        print(f"Error: The file '{new_file}' was not found. Please check the file name and path.")
        what_do_you_want = input('\nTo try again tap the ENTER key or exit by typing "EXIT"')
        if (what_do_you_want).upper == "EXIT":
            exit()
        else:
            new_file = input ("\nEnter the name of the File with the New Data again : ")

cs = ContinuousSentiment()
cs.run(new_data, existing_data)

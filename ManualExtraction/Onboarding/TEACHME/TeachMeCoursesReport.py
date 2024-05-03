import pandas as pd
import os

class TeachMeCoursesReport:
    def __init__(self):
        self.existing_data = None
        self.new_data = None

    def clean_data(self):
        df = pd.read_csv(self.csv_path)
        #Remove the empty spaces in the column names
        df.columns = df.columns.str.replace(' ', '')
        print(f"Data cleaned for {self.csv_path}")
        return df
    
    def append_new_data(self):
            new_clean_data = self.clean_data()
            updated_data = pd.concat([self.existing_data, new_clean_data], ignore_index=True)
            return updated_data

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
        print("║    Welcome to the Onboarding TeachMe Course!                         ║")
        print("║    Let's make data cleaning fun... or at least as fun as it can be!  ║")
        print("║                                                                      ║")
        print("╚══════════════════════════════════════════════════════════════════════╝")

    def get_valid_file_path(self, file_description):
        while True:
            try:
                file_name = input(f"\n📂 Enter the path to the {file_description} data file: ")
                file_path = os.path.join('ManualExtraction', 'Onboarding', 'TEACHME', file_name)
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
        updated_data.to_csv('TeachMeCoursesReport.csv', index=False)
        print("Data successfully updated and saved! 🎉")

# Running the OnboardingSurvey
survey = TeachMeCoursesReport()
survey.run()

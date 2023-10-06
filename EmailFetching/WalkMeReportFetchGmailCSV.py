import os
import re
import datetime
import imaplib
import requests
from email import policy
from email.parser import BytesParser

EMAIL = 'getreportfromwalkme@gmail.com'
PASSWORD = 'gczx yepd mbpt dbce'
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993
FOLDER = 'inbox'
SEARCH_SENDER = 'do-not-reply@Walkme.com'

def fetch_csvs_from_today():
    mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
    mail.login(EMAIL, PASSWORD)
    mail.select(FOLDER)
    
    today_date = datetime.date.today().strftime("%d-%b-%Y")

    # Search for today's emails from the specified sender
    result, data = mail.search(None, '(FROM "{}") SINCE {}'.format(SEARCH_SENDER, today_date))
    email_ids = data[0].split()

    subjects_and_paths = []
    
    # Create a temporary directory for the CSV files
    temp_dir = 'temp_csv_files'
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)

    for email_id in email_ids:
        result, email_data = mail.fetch(email_id, '(RFC822)')
        
        email_msg = BytesParser(policy=policy.default).parsebytes(email_data[0][1])
        email_subject = email_msg['subject']
        
        csv_url_pattern = r'https://insights-reports\.walkme\.com/g_reports/[a-f0-9\-]+\.csv\?.+'
        match = re.search(csv_url_pattern, str(email_msg))
        
        if match:
            csv_url = match.group(0)
            response = requests.get(csv_url)
            
            if response.status_code == 200:
                csv_file_path = os.path.join(temp_dir, email_subject.replace(" ", "_") + ".csv")
                with open(csv_file_path, 'wb') as f:
                    f.write(response.content)
                subjects_and_paths.append((email_subject, csv_file_path))
            else:
                print(f"Error downloading the CSV for subject: {email_subject}")

    mail.logout()
    return subjects_and_paths

if __name__ == "__main__":
    subjects_and_paths = fetch_csvs_from_today()
    
    for subject, csv_path in subjects_and_paths:
        print(f"Email Subject: {subject}")
        print(f"CSV File Path: {csv_path}")
        

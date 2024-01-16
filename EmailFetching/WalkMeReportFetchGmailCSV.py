import os
import re
import datetime
from datetime import timedelta
import imaplib
import requests
import logging
from email import policy
from email.parser import BytesParser
import html


EMAIL = 'getreportfromwalkme@gmail.com'
PASSWORD = 'ihju piba chcp paob'
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993
FOLDER = 'inbox'
SEARCH_SENDER = 'do-not-reply@Walkme.com'

def fetch_csvs_from_today():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL, PASSWORD)
        mail.select(FOLDER)
    except Exception as e:
        print(f"Error connecting to IMAP server: {e}")
        return []
    # Specific date you want to load emails from
    specific_date_str = "01-06-2024"
    specific_date_obj = datetime.datetime.strptime(specific_date_str, "%d-%b-%Y")
    # Format for IMAP
    formatted_date_since = specific_date_obj.strftime("%d-%b-%Y")
    formatted_date_before = (specific_date_obj + timedelta(days=1)).strftime("%d-%b-%Y")

    today_date = datetime.date.today().strftime("%d-%b-%Y")
    result, data = mail.search(None, '(FROM "{}") SINCE {}'.format(SEARCH_SENDER, today_date))
    # Search for emails on the specific date
    #query = '(FROM "{}" SINCE {} BEFORE {})'.format(SEARCH_SENDER, formatted_date_since, formatted_date_before)
    #result, data = mail.search(None, query)
    email_ids = data[0].split()

    subjects_and_paths = []
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
            # Unescape HTML entities in the URL
            csv_url = html.unescape(csv_url)


            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36 Brave/91'}
                response = requests.get(csv_url, headers=headers)
                if response.status_code == 200:
                    csv_file_path = os.path.join(temp_dir, email_subject.replace(" ", "_") + ".csv")
                    with open(csv_file_path, 'wb') as f:
                        f.write(response.content)
                    subjects_and_paths.append((email_subject, csv_file_path))

            except Exception as e:
                print(f"Error downloading CSV for subject {email_subject}: {e}")


    mail.logout()
    return subjects_and_paths

if __name__ == "__main__":
    subjects_and_paths = fetch_csvs_from_today()

    for subject, csv_path in subjects_and_paths:
        print(f"Email Subject: {subject}")
        print(f"CSV File Path: {csv_path}")

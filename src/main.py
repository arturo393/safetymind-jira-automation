import os
import argparse
from dotenv import load_dotenv
from jira_client import JiraClient

def main():
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Jira Automated Reporting")
    parser.add_argument("--project", help="Jira Project Key")
    parser.add_argument("--test-connection", action="store_true", help="Test Jira Connection")
    
    args = parser.parse_args()

    jira_url = os.getenv("JIRA_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_token = os.getenv("JIRA_API_TOKEN")

    if not all([jira_url, jira_email, jira_token]):
        print("Error: Missing Jira credentials in .env file.")
        return

    client = JiraClient(jira_url, jira_email, jira_token)

    if args.test_connection:
        if client.connect():
            print("Successfully connected to Jira!")
        else:
            print("Failed to connect to Jira.")
        return

    print("Jira Automation Tool Initialized.")

if __name__ == "__main__":
    main()

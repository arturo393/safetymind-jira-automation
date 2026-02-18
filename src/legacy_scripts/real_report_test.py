import os
from dotenv import load_dotenv
from jira_client import JiraClient
from report_generator import ReportGenerator

def run_real_report():
    # Load credentials from the current directory .env
    # We will copy it first in the terminal step
    load_dotenv()
    
    jira_url = os.getenv("JIRA_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_token = os.getenv("JIRA_API_TOKEN")
    project_key = os.getenv("JIRA_PROJECT_KEY", "IM")

    print(f"Connecting to Jira at {jira_url}...")
    client = JiraClient(jira_url, jira_email, jira_token)
    
    if not client.connect():
        print("Failed to connect to Jira.")
        return

    print(f"Fetching issues for project: {project_key}...")
    # Fetch some issues (limited to 50 for the test)
    query = f'project = "{project_key}" ORDER BY created DESC'
    issues = client.jira.search_issues(query, maxResults=50)
    
    if not issues:
        print(f"No issues found for project {project_key}.")
        return

    print(f"Found {len(issues)} issues. Generating report...")
    generator = ReportGenerator(issues)
    
    # Generate MD and PDF
    generator.save_markdown("real_test_report.md")
    generator.generate_pdf("real_test_report.pdf")
    
    print("Done! 'real_test_report.pdf' generated with real Jira data.")

if __name__ == "__main__":
    run_real_report()

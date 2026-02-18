import os
from dotenv import load_dotenv
from jira_client import JiraClient

def explore_epics():
    load_dotenv()
    
    jira_url = os.getenv("JIRA_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_token = os.getenv("JIRA_API_TOKEN")
    project_key = os.getenv("JIRA_PROJECT_KEY", "IM")
    start_date_field = os.getenv("JIRA_START_DATE_FIELD", "customfield_10015")

    client = JiraClient(jira_url, jira_email, jira_token)
    if not client.connect():
        return

    print(f"Exploring Epics for project: {project_key}...")
    query = f'project = "{project_key}" AND issuetype = Epic ORDER BY created ASC'
    epics = client.jira.search_issues(query)
    
    for epic in epics:
        start_date = getattr(epic.fields, start_date_field, "N/A")
        due_date = getattr(epic.fields, "duedate", "N/A")
        # In Jira Cloud, Epic Name is often in a custom field or just 'summary'
        epic_name = epic.fields.summary
        
        # Get progress (issues within epic)
        issues_in_epic = client.jira.search_issues(f'"Epic Link" = {epic.key}')
        total = len(issues_in_epic)
        done = len([i for i in issues_in_epic if i.fields.status.name.lower() in ['done', 'completado', 'cerrado', 'finalizado']])
        progress = (done / total * 100) if total > 0 else 0
        
        print(f"Epic: {epic.key} | Name: {epic_name}")
        print(f"  Start: {start_date} | Due: {due_date}")
        print(f"  Progress: {progress:.1f}% ({done}/{total} issues)")
        print("-" * 20)

if __name__ == "__main__":
    explore_epics()

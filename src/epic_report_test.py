import os
from dotenv import load_dotenv
from jira_client import JiraClient
from report_generator import ReportGenerator

def generate_epic_report():
    load_dotenv()
    
    jira_url = os.getenv("JIRA_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_token = os.getenv("JIRA_API_TOKEN")
    project_key = os.getenv("JIRA_PROJECT_KEY", "IM")
    start_date_field = os.getenv("JIRA_START_DATE_FIELD", "customfield_10015")

    client = JiraClient(jira_url, jira_email, jira_token)
    if not client.connect():
        return

    print(f"Fetching Epics for project: {project_key}...")
    query = f'project = "{project_key}" AND issuetype = Epic ORDER BY created ASC'
    epics = client.jira.search_issues(query)
    
    epics_data = []
    for epic in epics:
        # Get basic info
        epic_name = epic.fields.summary
        start_date = getattr(epic.fields, start_date_field, None)
        due_date = getattr(epic.fields, "duedate", None)
        status = epic.fields.status.name
        
        # Calculate progress
        issues_in_epic = client.jira.search_issues(f'"Epic Link" = {epic.key}')
        total = len(issues_in_epic)
        done = len([i for i in issues_in_epic if i.fields.status.name.lower() in ['done', 'completado', 'cerrado', 'finalizado']])
        progress = (done / total * 100) if total > 0 else 0
        
        epics_data.append({
            'key': epic.key,
            'name': epic_name,
            'start': start_date,
            'due': due_date,
            'progress': progress,
            'status': status
        })

    if not epics_data:
        print("No se encontraron Épicas para reportar.")
        return

    print(f"Generating Epic Report for {len(epics_data)} epics...")
    generator = ReportGenerator(None) # Data not used in epic flow
    generator.generate_epic_pdf(epics_data, "epic_progress_report.pdf")
    print("Reporte de Épicas con Gantt generado con éxito.")

if __name__ == "__main__":
    generate_epic_report()

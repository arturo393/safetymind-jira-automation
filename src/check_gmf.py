from dotenv import load_dotenv
import os
from jira_client import JiraClient

load_dotenv()
jira_url = os.getenv("JIRA_URL")
jira_email = os.getenv("JIRA_EMAIL")
jira_token = os.getenv("JIRA_API_TOKEN")

client = JiraClient(jira_url, jira_email, jira_token)
client.connect()

print("Buscando proyecto GMF...")
issues = client.jira.search_issues('project = "GMF" ORDER BY created DESC', maxResults=5)
if issues:
    print(f"Encontrados {len(issues)} issues en GMF.")
    for i in issues:
        print(f"{i.key}: {i.fields.summary}")
else:
    print("No se encontraron issues en GMF. Verificando proyectos accesibles...")
    projects = client.jira.projects()
    for p in projects:
        print(f"{p.key}: {p.name}")

import os
import argparse
import yaml
from datetime import datetime
from dotenv import load_dotenv
from clients.jira_client import JiraClient
from reporting.report_context import ReportContext 
from jinja2 import Environment, FileSystemLoader

# Load Env
load_dotenv()

def load_config(config_path="config/projects.yaml"):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def get_jira_client():
    jira_url = os.getenv("JIRA_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_token = os.getenv("JIRA_API_TOKEN")
    client = JiraClient(jira_url, jira_email, jira_token)
    if not client.connect():
        raise Exception("Failed to connect to Jira")
    return client

def render_template(template_name, context, output_path):
    # Templates are now relative to project root
    template_dir = os.path.join(os.getcwd(), 'templates')
    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_name)
    html_content = template.render(context)
    
    from weasyprint import HTML
    HTML(string=html_content).write_pdf(output_path)
    print(f"Report generated: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="SafetyMind Report Automation CLI")
    parser.add_argument("--project", required=True, help="Project Key (e.g., GMF, IM)")
    parser.add_argument("--type", required=True, choices=['kickoff', 'progress', 'final'], help="Type of report to generate")
    
    args = parser.parse_args()
    
    # 1. Load Config
    config = load_config()
    if args.project not in config['projects']:
        print(f"Project {args.project} not found in config/projects.yaml")
        return
        
    project_config = config['projects'][args.project]
    
    # 2. Connect to Jira
    jira = get_jira_client()
    
    # 3. Build Context (Data Model)
    context_builder = ReportContext(jira, project_config)
    context = context_builder.build(args.type)
    
    # 4. Render Template (View)
    output_filename = f"{args.project}_{args.type}_{datetime.now().strftime('%Y%m%d')}.pdf"
    render_template(f"{args.type}.html", context, output_filename)

if __name__ == "__main__":
    main()

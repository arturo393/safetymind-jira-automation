import os
from dotenv import load_dotenv
from jira_client import JiraClient
from report_generator import ReportGenerator

def run():
    load_dotenv()
    jira_url = os.getenv("JIRA_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_token = os.getenv("JIRA_API_TOKEN")
    project_key = os.getenv("JIRA_PROJECT_KEY", "IM")

    client = JiraClient(jira_url, jira_email, jira_token)
    if not client.connect():
        return

    generator = ReportGenerator(None)

    # 1. GENERATE KICKOFF REPORT
    print("Generating Kickoff Report...")
    project_info = {
        "name": os.getenv("PROJECT_NAME", "SafetyMind Implementation"),
        "description": "Despliegue de analítica de video inteligente para auditoría visual en tiempo real.",
        "architecture_desc": "Cámaras IP con protocolo RTSP conectadas a Gateway Local (Apptainer) -> Procesamiento de IA -> Alertas vía Telegram y Dashboard Cloud."
    }
    # Get all issues for the plan
    query_all = f'project = "{project_key}" ORDER BY created ASC'
    all_issues = client.jira.search_issues(query_all, maxResults=20)
    generator.generate_kickoff_report(project_info, all_issues, "1_Kickoff_Report.pdf")

    # 2. GENERATE PROGRESS REPORT
    print("Generating Progress Report...")
    # Calculate real progress
    query_done = f'project = "{project_key}" AND status IN ("Done", "Completado", "Cerrado")'
    done_issues = client.jira.search_issues(query_done)
    total_issues = client.jira.search_issues(f'project = "{project_key}"')
    
    percentage = (len(done_issues) / len(total_issues) * 100) if len(total_issues) > 0 else 0
    progress_data = {"percentage": round(percentage, 1)}
    
    # Simple blocker text (this could come from a custom field or manual)
    blockers = "Retraso en la entrega de accesos VPN por parte del cliente. Se requiere validación de puertos 8080 y 443."
    
    generator.generate_progress_status_report(progress_data, done_issues[:5], blockers, "2_Avance_Status_Report.pdf")

    # 3. GENERATE FINAL REPORT
    print("Generating Final Report...")
    implementation_details = {
        "cameras": [
            {"name": "Acceso Principal", "ip": "192.168.1.50", "telegram_group": "@SafetyMind_Alerts_A", "status": "Online"},
            {"name": "Bodega Norte", "ip": "192.168.1.51", "telegram_group": "@SafetyMind_Alerts_A", "status": "Online"},
            {"name": "Línea de Producción 1", "ip": "192.168.1.55", "telegram_group": "@SafetyMind_Alerts_B", "status": "Offline (Mantenimiento)"},
        ]
    }
    deviations = "Se cambió el Gateway local de Docker a Apptainer para cumplir con los requisitos de seguridad del servidor del cliente. Se añadió un grupo secundario de Telegram para el área de producción."
    
    generator.generate_final_report(implementation_details, deviations, "3_Informe_Final_Implementacion.pdf")

    print("\n¡Todos los informes han sido generados exitosamente!")

if __name__ == "__main__":
    run()

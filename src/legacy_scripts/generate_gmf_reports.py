import os
from dotenv import load_dotenv
from jira_client import JiraClient
from report_generator import ReportGenerator

def run():
    load_dotenv()
    jira_url = os.getenv("JIRA_URL")
    jira_email = os.getenv("JIRA_EMAIL")
    jira_token = os.getenv("JIRA_API_TOKEN")
    project_key = "GMF" # Explicitly using GMF as requested

    client = JiraClient(jira_url, jira_email, jira_token)
    if not client.connect():
        return

    generator = ReportGenerator(None)

    # 1. GENERATE KICKOFF REPORT
    print("Generating Kickoff Report (with Gantt)...")
    project_info = {
        "name": "SafetyMind GMF Implementation",
        "description": "Implementación de sistema de monitoreo AI para GMF. Alcance: Detección de EPP y comportamientos inseguros en zonas de carga.",
        "architecture_desc": "4 Cámaras Hikvision 4K -> Switch PoE -> Servidor On-Premise (Ubuntu Server + Apptainer) -> VPN WireGuard -> SafetyMind Cloud Dashboard."
    }
    # Get all planned issues
    query_all = f'project = "{project_key}" ORDER BY created ASC'
    all_issues = client.jira.search_issues(query_all)
    generator.generate_kickoff_report(project_info, all_issues, "1_Kickoff_Report_GMF.pdf")

    # 2. GENERATE PROGRESS REPORT
    print("Generating Progress Report (with Critical Path)...")
    
    # Calculate real progress
    query_done = f'project = "{project_key}" AND status IN ("Done", "Completado", "Cerrado")'
    done_issues = client.jira.search_issues(query_done)
    
    # Active issues for critical path analysis
    query_active = f'project = "{project_key}" AND status NOT IN ("Done", "Completado", "Cerrado")'
    active_issues = client.jira.search_issues(query_active)
    
    total_count = len(done_issues) + len(active_issues)
    percentage = (len(done_issues) / total_count * 100) if total_count > 0 else 0
    progress_data = {"percentage": round(percentage, 1)}
    
    blockers = "Retraso en la habilitación eléctrica del rack de comunicaciones. Se está utilizando extensión temporal."
    
    generator.generate_progress_status_report(progress_data, done_issues[:10], blockers, active_issues, "2_Avance_Status_Report_GMF.pdf")

    # 3. GENERATE FINAL REPORT
    print("Generating Final Report...")
    implementation_details = {
        "cameras": [
            {"name": "Cam 1 - Acceso Norte", "ip": "10.0.10.21", "telegram_group": "@SafetyMind_GMF_Alerts", "status": "Online"},
            {"name": "Cam 2 - Zona Carga", "ip": "10.0.10.22", "telegram_group": "@SafetyMind_GMF_Alerts", "status": "Online"},
            {"name": "Cam 3 - Pasillo EPP", "ip": "10.0.10.23", "telegram_group": "@SafetyMind_GMF_Alerts_Criticos", "status": "Online"},
            {"name": "Cam 4 - Bodega", "ip": "10.0.10.24", "telegram_group": "@SafetyMind_GMF_Alerts", "status": "Online"},
        ]
    }
    deviations = "Se modificó la ubicación de la Cámara 3 debido a obstrucción visual por nuevas estanterías. Se requirió recableado de 15 metros adicionales."
    
    generator.generate_final_report(implementation_details, deviations, "3_Informe_Final_GMF.pdf")

    print("\n¡Todos los informes GMF han sido generados exitosamente!")

if __name__ == "__main__":
    run()

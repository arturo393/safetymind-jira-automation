import base64
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io

class ReportContext:
    def __init__(self, jira_client, project_config):
        self.jira = jira_client
        self.config = project_config
        self.project_key = project_config['jira_key']

    def build(self, report_type):
        """Constructs the context dictionary for the template."""
        if report_type == 'kickoff':
            return self._build_kickoff_context()
        elif report_type == 'progress':
            return self._build_progress_context()
        elif report_type == 'final':
            return self._build_final_context()
        else:
            raise ValueError(f"Unknown report type: {report_type}")

    def _get_base_context(self, report_title):
        return {
            "title": f"SafetyMind - {report_title}",
            "project_name": self.config['name'],
            "year": datetime.now().year,
            "report_date": datetime.now().strftime("%Y-%m-%d"),
            "report_type": report_title
        }

    def _build_kickoff_context(self):
        ctx = self._get_base_context("Informe de Kickoff")
        ctx.update({
            "description": self.config['description'],
            "architecture_desc": self.config['architecture_desc'],
            "activities": self._get_jira_activities()
        })
        
        # Add Gantt Chart
        ctx['gantt_image'] = self._generate_gantt_chart(ctx['activities'])
        return ctx

    def _build_progress_context(self):
        ctx = self._get_base_context("Informe de Avance")
        
        # Fetch active and closed issues
        active_issues = self.jira.jira.search_issues(f'project = "{self.project_key}" AND status NOT IN ("Done", "Completado", "Cerrado")')
        closed_issues = self.jira.jira.search_issues(f'project = "{self.project_key}" AND status IN ("Done", "Completado", "Cerrado") ORDER BY updated DESC', maxResults=10)
        
        total = len(active_issues) + len(closed_issues)
        percentage = int((len(closed_issues) / total * 100)) if total > 0 else 0
        
        # Calculate Critical Path (High Priority + Overdue)
        critical_path = []
        today = datetime.now()
        for i in active_issues:
            priority = getattr(i.fields.priority, 'name', 'Medium')
            due_str = getattr(i.fields, 'duedate', None)
            reason = ""
            
            if priority in ['High', 'Highest', 'Critical']:
                reason = f"Prioridad: {priority}"
            
            if due_str:
                due = datetime.strptime(due_str, "%Y-%m-%d")
                if due < today:
                    reason += f" | Vencida: {due_str}"
            
            if reason:
                critical_path.append({"key": i.key, "summary": i.fields.summary, "reason": reason})

        ctx.update({
            "percentage": percentage,
            "blockers": self.config.get('blockers_default', 'Sin bloqueos mayores.'),
            "critical_path": critical_path,
            "completed_tasks": [{"key": i.key, "summary": i.fields.summary, "updated": i.fields.updated[:10]} for i in closed_issues],
            "pending_tasks": [{"key": i.key, "summary": i.fields.summary, "priority": getattr(i.fields.priority, 'name', 'Normal')} for i in active_issues]
        })
        return ctx

    def _build_final_context(self):
        ctx = self._get_base_context("Informe Final de Cierre")
        ctx.update({
            "description": self.config['description'],
            "cameras": self.config.get('cameras', []),
            "deviations": self.config.get('deviations', []),
            "lessons_learned": self.config.get('lessons_learned', []) # Future enhancement: Add to YAML
        })
        return ctx

    def _get_jira_activities(self):
        issues = self.jira.jira.search_issues(f'project = "{self.project_key}" ORDER BY created ASC')
        return [{
            "key": i.key, 
            "summary": i.fields.summary, 
            "status": i.fields.status.name,
            "start": getattr(i.fields, 'customfield_10015', None), # Start Date
            "due": getattr(i.fields, 'duedate', None)
        } for i in issues]

    def _generate_gantt_chart(self, activities):
        """Generates a Gantt chart and returns base64 string."""
        data = []
        for a in activities:
            s_str = a.get('start')
            d_str = a.get('due')
            
            # Simple fallback logic for demonstration
            if s_str:
                s_dt = datetime.strptime(s_str, "%Y-%m-%d")
            else:
                s_dt = datetime.now()
                
            if d_str:
                d_dt = datetime.strptime(d_str, "%Y-%m-%d")
            else:
                d_dt = s_dt + timedelta(days=7)
                
            data.append((a['key'], s_dt, d_dt))

        if not data:
            return ""

        fig, ax = plt.subplots(figsize=(10, 6))
        names = [x[0] for x in data]
        starts = [x[1] for x in data]
        durations = [(x[2] - x[1]).days for x in data]
        
        ax.barh(names, durations, left=starts, color='#ffed01')
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.tight_layout()
        
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')

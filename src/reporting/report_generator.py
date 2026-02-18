import markdown
from weasyprint import HTML
from gdocs_client import GoogleDocsClient

class ReportGenerator:
    def __init__(self, data):
        self.data = data
        self.gdocs = GoogleDocsClient()

    def generate_markdown(self):
        """Generates a Markdown string from the data."""
        # This is a sample template. In reality, you'd iterate over self.data
        md_content = f"""
# Jira Report

## Summary
Total Issues: {len(self.data) if self.data else 0}

## Details
"""
        if self.data:
            for issue in self.data:
                md_content += f"- **{issue.key}**: {issue.fields.summary}\n"
        else:
            md_content += "No issues found."
            
        return md_content

    def save_markdown(self, filename="report.md"):
        content = self.generate_markdown()
        with open(filename, "w") as f:
            f.write(content)
        return filename

    def generate_pdf(self, filename="report.pdf"):
        md_content = self.generate_markdown()
        html_content = markdown.markdown(md_content)
        # Create a CSS that matches SafetyMind's branding (from infrastructure_monitoring/configs/branding/custom.css)
        full_html = f"""
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
                
                :root {{
                    --safetymind-primary: #ffed01;
                    --safetymind-black: #000000;
                    --safetymind-white: #ffffff;
                    --safetymind-gray: #adadad;
                }}

                body {{
                    font-family: 'Montserrat', sans-serif;
                    color: var(--safetymind-black);
                    margin: 20px;
                    font-size: 14px;
                }}

                h1 {{
                    color: var(--safetymind-black);
                    border-bottom: 3px solid var(--safetymind-primary);
                    padding-bottom: 5px;
                    text-transform: uppercase;
                    font-size: 24px;
                    margin-top: 0;
                }}

                h2 {{
                    color: var(--safetymind-black);
                    background-color: var(--safetymind-primary);
                    padding: 4px 8px;
                    display: block;
                    width: 100%;
                    border-radius: 4px;
                    margin-top: 15px;
                    margin-bottom: 10px;
                    font-size: 16px;
                }}

                ul {{
                    list-style-type: none;
                    padding: 0;
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                }}

                li {{
                    margin-bottom: 0px;
                    padding: 8px;
                    border-left: 4px solid var(--safetymind-primary);
                    background-color: #f4f4f4;
                    border-radius: 0 4px 4px 0;
                    page-break-inside: avoid;
                }}

                strong {{
                    color: #d35400; /* Fallback accent */
                }}
            </style>
        </head>
        <body>
            <div style="text-align: right; margin-bottom: 20px;">
                <span style="font-weight: bold; font-size: 24px;">SAFETY<span style="color: var(--safetymind-primary);">MIND</span></span>
                <br>
                <span style="font-size: 10px; color: var(--safetymind-gray); letter-spacing: 2px;">PREVIENE Y PROTEGE</span>
            </div>
            {html_content}
            <div style="margin-top: 50px; text-align: center; font-size: 10px; color: var(--safetymind-gray); border-top: 1px solid var(--safetymind-primary); padding-top: 10px;">
                SafetyMind Automated Report
            </div>
        </body>
        </html>
        """
        HTML(string=full_html).write_pdf(filename)
        print(f"PDF generated: {filename}")

    def generate_google_doc(self, title="Jira Report"):
        """Generates a Google Doc from the Markdown content."""
        try:
            doc_id = self.gdocs.create_document(title)
            md_content = self.generate_markdown()
            # Note: A real converter would parse MD structure to GDocs structure.
            # Simplified: just appending raw text for now.
            self.gdocs.append_text(doc_id, md_content)
            return doc_id
        except Exception as e:
            print(f"Failed to generate Google Doc: {e}")
            return None

    def generate_epic_markdown(self, epics_data):
        """Generates a Markdown string for Epic-level progress."""
        md_content = f"""
# Reporte de Avance por Épicas

## Resumen del Proyecto
Este informe muestra el progreso de las iniciativas de alto nivel (Épicas) en Jira.

## Estado de las Épicas
"""
        for epic in epics_data:
            md_content += f"### {epic['key']}: {epic['name']}\n"
            md_content += f"- **Progreso**: {epic['progress']:.1f}%\n"
            md_content += f"- **Fechas**: {epic['start']} a {epic['due']}\n"
            md_content += f"- **Estado**: {epic['status']}\n\n"
            
        return md_content

    def generate_gantt_chart(self, epics_data, output_path="gantt.png"):
        """Generates a Gantt chart using matplotlib and saves it as an image."""
        import matplotlib.pyplot as plt
        import matplotlib.dates as mdates
        from datetime import datetime, timedelta

        plt.figure(figsize=(10, 6))
        
        # Filter epics that have at least one valid date or handle fallbacks better
        processed_epics = []
        for e in epics_data:
            s_str = e['start'] if e['start'] != "None" and e['start'] else None
            d_str = e['due'] if e['due'] != "None" and e['due'] else None
            
            if not s_str and not d_str:
                # If no dates, we can't really draw a Gantt bar easily, 
                # but we'll use "now" as a dummy reference for the plot
                s_dt = datetime.now()
                d_dt = s_dt + timedelta(days=14)
            elif not d_str:
                s_dt = datetime.strptime(s_str, "%Y-%m-%d")
                d_dt = s_dt + timedelta(days=14)
            elif not s_str:
                d_dt = datetime.strptime(d_str, "%Y-%m-%d")
                s_dt = d_dt - timedelta(days=14)
            else:
                s_dt = datetime.strptime(s_str, "%Y-%m-%d")
                d_dt = datetime.strptime(d_str, "%Y-%m-%d")
            
            processed_epics.append({
                'name': e['name'],
                'start': s_dt,
                'end': d_dt,
                'progress': e['progress']
            })

        epic_names = [e['name'] for e in processed_epics]
        start_dates = [e['start'] for e in processed_epics]
        durations = [(e['end'] - e['start']).days if (e['end'] - e['start']).days > 0 else 1 for e in processed_epics]
        progresses = [e['progress'] for e in processed_epics]

        y_pos = range(len(epic_names))
        
        # Draw base bars (total duration)
        plt.barh(y_pos, durations, left=start_dates, color='#adadad', alpha=0.3, label='Planificado')
        
        # Draw progress bars
        progress_durations = [d * (p/100) for d, p in zip(durations, progresses)]
        plt.barh(y_pos, progress_durations, left=start_dates, color='#ffed01', label='Progreso Real')

        plt.yticks(y_pos, epic_names)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator())
        plt.gcf().autofmt_xdate()
        
        plt.title('Diagrama de Gantt - Avance de Épicas (SafetyMind)', pad=20)
        plt.xlabel('Línea de Tiempo')
        plt.grid(axis='x', linestyle='--', alpha=0.5)
        plt.legend()
        plt.tight_layout()
        
        plt.savefig(output_path)
        plt.close()
        return output_path

    def generate_epic_pdf(self, epics_data, filename="epic_progress_report.pdf"):
        """Generates a PDF report for Epics with an embedded Gantt chart."""
        import base64
        from datetime import datetime
        
        md_content = self.generate_epic_markdown(epics_data)
        html_content = markdown.markdown(md_content)
        
        # Generate chart
        gantt_path = self.generate_gantt_chart(epics_data)
        with open(gantt_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode()

        # Prepare HTML body content
        processed_html = html_content.replace('<h3>', '<div class="epic-card"><h3>')
        processed_html = processed_html.replace('</h3>', '</h3>')
        processed_html = processed_html.replace('</h3>\n', '</h3>\n</div>')
        
        current_year = datetime.now().year

        full_html = f"""
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
                :root {{
                    --safetymind-primary: #ffed01;
                    --safetymind-black: #000000;
                    --safetymind-white: #ffffff;
                    --safetymind-gray: #adadad;
                }}
                body {{ font-family: 'Montserrat', sans-serif; color: var(--safetymind-black); margin: 30px; font-size: 14px; }}
                h1 {{ border-bottom: 3px solid var(--safetymind-primary); padding-bottom: 10px; text-transform: uppercase; }}
                h2, h3 {{ color: var(--safetymind-black); }}
                .gantt-container {{ width: 100%; text-align: center; margin: 30px 0; }}
                .gantt-container img {{ width: 100%; border: 1px solid var(--safetymind-gray); border-radius: 8px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
                .epic-card {{ border-left: 5px solid var(--safetymind-primary); background: #f9f9f9; padding: 15px; margin-bottom: 15px; border-radius: 0 5px 5px 0; }}
            </style>
        </head>
        <body>
            <div style="text-align: right;">
                <span style="font-weight: bold; font-size: 24px;">SAFETY<span style="color: var(--safetymind-primary);">MIND</span></span>
            </div>
            
            <h1>Reporte de Avance - Iniciativas Estratégicas</h1>
            
            <div class="gantt-container">
                <h3>Cronograma y Progreso de Épicas</h3>
                <img src="data:image/png;base64,{img_base64}">
            </div>

            {processed_html}
            
            <div style="margin-top: 30px; text-align: center; font-size: 10px; color: var(--safetymind-gray); border-top: 1px solid var(--safetymind-primary); padding-top: 10px;">
                © {current_year} SafetyMind - Informe Generado Automáticamente mediante Jira API
            </div>
        </body>
        </html>
        """
        HTML(string=full_html).write_pdf(filename)
        print(f"PDF de Épicas generado: {filename}")

    def _generate_critical_path_html(self, issues):
        """Generates HTML for the Critical Path section based on high priority or overdue issues."""
        critical_items = []
        from datetime import datetime
        today = datetime.now()

        for issue in issues:
            # Check for critical criteria: High/Highest Priority OR Overdue
            priority = getattr(issue.fields.priority, 'name', 'Medium')
            due_date_str = getattr(issue.fields, 'duedate', None)
            
            is_critical = False
            reason = ""
            
            if priority in ['High', 'Highest', 'Critical']:
                is_critical = True
                reason = f"Prioridad: {priority}"
            
            if due_date_str:
                due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                if due_date < today and issue.fields.status.name not in ['Done', 'Completado', 'Cerrado']:
                    is_critical = True
                    reason += f" | Vencida: {due_date_str}"

            if is_critical:
                critical_items.append(f"<li><strong>{issue.key}: {issue.fields.summary}</strong><br><span style='color:red; font-size:12px;'>{reason}</span></li>")
        
        if not critical_items:
            return "<p>No se detectaron elementos críticos activos.</p>"
        
        return "<ul>" + "".join(critical_items) + "</ul>"

    def generate_kickoff_report(self, project_info, activities, filename="kickoff_report.pdf"):
        """Generates a Kickoff report with architecture, activity plan and Gantt chart."""
        from datetime import datetime
        import base64
        
        # Format activities for Gantt chart generation
        # Assuming 'activities' are Jira Issue objects
        gantt_data = []
        for a in activities:
             # simple mapping for Gantt
             start = getattr(a.fields, 'customfield_10015', None) # Start Date
             due = getattr(a.fields, 'duedate', None)
             gantt_data.append({
                 'name': a.key, # Use key for brevity in chart
                 'start': start,
                 'due': due,
                 'progress': 0 if a.fields.status.name not in ['Done', 'Completado'] else 100
             })

        # Generate Gantt Chart
        gantt_path = self.generate_gantt_chart(gantt_data, "kickoff_gantt.png")
        with open(gantt_path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode()

        full_html = f"""
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
                :root {{
                    --safetymind-primary: #ffed01;
                    --safetymind-black: #000000;
                    --safetymind-gray: #666666;
                    --safetymind-light-gray: #f4f4f4;
                }}
                body {{ 
                    font-family: 'Roboto', sans-serif; 
                    color: #333; 
                    margin: 40px; 
                    line-height: 1.5; 
                    font-size: 11pt; /* Professional document standard */
                }}
                header {{ 
                    border-bottom: 2px solid var(--safetymind-primary); 
                    padding-bottom: 20px; 
                    margin-bottom: 30px; 
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }}
                .logo {{ font-weight: 700; font-size: 18pt; color: var(--safetymind-black); }}
                .accent {{ color: var(--safetymind-primary); }}
                h1 {{ 
                    font-size: 24pt; 
                    margin: 0; 
                    color: var(--safetymind-black); 
                    text-transform: uppercase; 
                    letter-spacing: 1px;
                }}
                h2 {{ 
                    font-size: 14pt; 
                    color: var(--safetymind-black); 
                    border-left: 5px solid var(--safetymind-primary); 
                    padding-left: 10px; 
                    margin-top: 30px; 
                    margin-bottom: 15px;
                }}
                p {{ margin-bottom: 15px; text-align: justify; }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin-top: 15px; 
                    font-size: 10pt;
                }}
                th, td {{ 
                    border: 1px solid #ddd; 
                    padding: 8px 12px; 
                    text-align: left; 
                }}
                th {{ 
                    background-color: var(--safetymind-light-gray); 
                    color: var(--safetymind-black); 
                    font-weight: 700;
                }}
                .gantt-container {{ 
                    text-align: center; 
                    margin: 30px 0; 
                    border: 1px solid #ddd; 
                    padding: 10px;
                }}
                .gantt-container img {{ max-width: 100%; height: auto; }}
                footer {{
                    position: fixed; 
                    bottom: 20px; 
                    width: 100%; 
                    text-align: center; 
                    font-size: 8pt; 
                    color: var(--safetymind-gray);
                }}
            </style>
        </head>
        <body>
            <header>
                <div>
                    <h1>Informe de Kickoff</h1>
                    <span style="font-size: 12pt; color: var(--safetymind-gray);">Proyecto: {project_info.get('name', 'N/A')}</span>
                </div>
                <div class="logo">SAFETY<span class="accent">MIND</span></div>
            </header>

            <h2>1. Objetivos del Proyecto</h2>
            <p>{project_info.get('description', 'Definición de bases y alcance del proyecto de monitoreo.')}</p>

            <h2>2. Arquitectura del Sistema</h2>
            <div style="border: 1px solid #ddd; padding: 15px; background: #f9f9f9;">
                <p><strong>Descripción de Componentes:</strong></p>
                <p>{project_info.get('architecture_desc', 'Conexión de cámaras IP -> Servidor Local -> Nube SafetyMind')}</p>
            </div>

            <h2>3. Cronograma del Proyecto (Ganta)</h2>
            <div class="gantt-container">
                <img src="data:image/png;base64,{img_base64}">
            </div>

            <h2>4. Plan de Actividades (Jira)</h2>
            <table>
                <thead>
                    <tr><th style="width: 15%;">Calculated ID</th><th>Actividad</th><th style="width: 15%;">Estado</th></tr>
                </thead>
                <tbody>
                    {"".join([f"<tr><td>{a.key}</td><td>{a.fields.summary}</td><td>{a.fields.status.name}</td></tr>" for a in activities])}
                </tbody>
            </table>

            <footer>
                © {datetime.now().year} SafetyMind - Documento Confidencial generado automáticamente.
            </footer>
        </body>
        </html>
        """
        HTML(string=full_html).write_pdf(filename)
        print(f"Kickoff Report generado: {filename}")

    def generate_progress_status_report(self, progress_data, increments, blockers, all_active_issues=[], filename="avance_report.pdf"):
        """Generates a progress report with critical path analysis."""
        from datetime import datetime
        
        critical_path_html = self._generate_critical_path_html(all_active_issues)

        full_html = f"""
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
                :root {{
                    --safetymind-primary: #ffed01;
                    --safetymind-black: #000000;
                    --safetymind-alert: #d32f2f;
                }}
                body {{ 
                    font-family: 'Roboto', sans-serif; 
                    margin: 40px; 
                    font-size: 11pt;
                    color: #333;
                }}
                header {{ 
                    border-bottom: 2px solid var(--safetymind-primary); 
                    padding-bottom: 20px; 
                    margin-bottom: 30px; 
                    display: flex;
                    justify-content: space-between;
                }}
                .header-title h1 {{ margin: 0; font-size: 22pt; text-transform: uppercase; }}
                .logo {{ font-size: 18pt; font-weight: bold; }}
                
                h2 {{ 
                    font-size: 14pt; 
                    color: var(--safetymind-black); 
                    border-bottom: 1px solid #ddd; 
                    padding-bottom: 5px; 
                    margin-top: 30px;
                }}

                .progress-section {{ 
                    background: #f4f4f4; 
                    padding: 20px; 
                    border-radius: 4px; 
                    margin-bottom: 20px;
                }}
                .progress-bar-bg {{ background: #ddd; height: 10px; border-radius: 5px; width: 100%; }}
                .progress-bar-fill {{ background: var(--safetymind-primary); height: 10px; border-radius: 5px; }}
                .percentage {{ font-size: 24pt; font-weight: bold; color: var(--safetymind-black); }}

                .critical-path {{ 
                    border: 1px solid var(--safetymind-alert); 
                    background-color: #fdecea; 
                    padding: 15px; 
                    border-radius: 4px;
                }}
                .critical-path li {{ margin-bottom: 10px; list-style-type: none; }}
                
                ul {{ padding-left: 20px; }}
                li {{ margin-bottom: 5px; }}
            </style>
        </head>
        <body>
            <header>
                <div class="header-title">
                    <h1>Estado de Avance</h1>
                    <span style="color: #666; font-size: 10pt;">Reporte Ejecutivo de Proyecto</span>
                </div>
                <div class="logo">SAFETY<span style="color: var(--safetymind-primary);">MIND</span></div>
            </header>
            
            <div class="progress-section">
                <strong>Progreso General del Proyecto</strong>
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span class="percentage">{progress_data.get('percentage', 0)}%</span>
                    <div style="width: 80%;">
                        <div class="progress-bar-bg">
                            <div class="progress-bar-fill" style="width: {progress_data.get('percentage', 0)}%;"></div>
                        </div>
                    </div>
                </div>
            </div>

            <h2>Ruta Crítica y Riesgos</h2>
            <div class="critical-path">
                <p><strong>Atención Requerida (Prioridad Alta / Vencidos):</strong></p>
                {critical_path_html}
            </div>

            <h2>Actividades Recientes Completadas</h2>
            <ul>
                {"".join([f"<li><strong>{i.key}</strong>: {i.fields.summary}</li>" for i in increments])}
            </ul>

            <h2>Inconvenientes y Bloqueos Reportados</h2>
            <div style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffecb5;">
                {f"<p>{blockers}</p>" if blockers else "<p>No se reportan bloqueos mayores.</p>"}
            </div>

            <footer style="position: fixed; bottom: 20px; width: 100%; text-align: center; font-size: 8pt; color: #999;">
                Generado el {datetime.now().strftime('%Y-%m-%d')} | SafetyMind Monitoring
            </footer>
        </body>
        </html>
        """
        HTML(string=full_html).write_pdf(filename)
        print(f"Progress Report generado: {filename}")

    def generate_final_report(self, implementation_details, deviations, filename="informe_final.pdf"):
        """Generates a final delivery report with technical details."""
        from datetime import datetime
        
        cameras_html = "".join([f"<tr><td>{c['name']}</td><td>{c['ip']}</td><td>{c['telegram_group']}</td><td>{c['status']}</td></tr>" for c in implementation_details.get('cameras', [])])

        full_html = f"""
        <html>
        <head>
             <style>
                @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
                :root {{ --safetymind-primary: #ffed01; --safetymind-black: #000000; }}
                body {{ 
                    font-family: 'Roboto', sans-serif; 
                    margin: 40px; 
                    font-size: 11pt; 
                    color: #333;
                }}
                header {{ 
                    text-align: center; 
                    border-bottom: 4px solid var(--safetymind-primary); 
                    padding-bottom: 20px; 
                    margin-bottom: 30px;
                }}
                h1 {{ font-size: 20pt; text-transform: uppercase; margin: 0; }}
                h2 {{ font-size: 14pt; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-top: 30px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 15px; font-size: 10pt; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                th {{ background: #333; color: white; text-align: left; }}
                .deviation-box {{ background: #f9f9f9; padding: 15px; border-left: 5px solid var(--safetymind-primary); }}
            </style>
        </head>
        <body>
            <header>
                <h1>Informe Final de Implementación</h1>
                <p>SafetyMind AI Visual Auditing</p>
            </header>

            <h2>1. Detalle Técnico de Instalación</h2>
            <p>Se listan a continuación los dispositivos configurados y operativos:</p>
            <table>
                <thead>
                    <tr><th>Cámara</th><th>Dirección IP</th><th>Grupo Telegram</th><th>Estado</th></tr>
                </thead>
                <tbody>
                    {cameras_html}
                </tbody>
            </table>

            <h2>2. Modificaciones al Plan Original</h2>
            <div class="deviation-box">
                <p>{deviations if deviations else "Implementación realizada sin desviaciones significativas."}</p>
            </div>

            <h2>3. Conclusiones y Cierre</h2>
            <p>El sistema se encuentra operativo, transmitiendo alertas y visualización en tiempo real. Se ha completado la capacitación a los usuarios finales.</p>
            
            <br><br>
            <div style="text-align: center; margin-top: 50px;">
                <p>__________________________</p>
                <p>Firma de Conformidad</p>
            </div>
        </body>
        </html>
        """
        HTML(string=full_html).write_pdf(filename)
        print(f"Final Report generado: {filename}")

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

    def generate_kickoff_report(self, project_info, activities, filename="kickoff_report.pdf"):
        """Generates a Kickoff report with architecture and activity plan."""
        from datetime import datetime
        
        full_html = f"""
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
                :root {{
                    --safetymind-primary: #ffed01;
                    --safetymind-black: #000000;
                    --safetymind-gray: #adadad;
                }}
                body {{ font-family: 'Montserrat', sans-serif; color: var(--safetymind-black); margin: 30px; line-height: 1.6; }}
                header {{ border-bottom: 4px solid var(--safetymind-primary); padding-bottom: 10px; margin-bottom: 20px; }}
                .section {{ margin-bottom: 30px; }}
                h1 {{ text-transform: uppercase; margin: 0; }}
                h2 {{ background: var(--safetymind-primary); padding: 5px 10px; display: inline-block; border-radius: 4px; }}
                .arch-box {{ border: 2px dashed var(--safetymind-gray); padding: 20px; text-align: center; background: #fefefe; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
                th {{ background-color: #f2f2f2; color: var(--safetymind-black); }}
            </style>
        </head>
        <body>
            <header>
                <div style="float: right; font-weight: bold; font-size: 20px;">SAFETY<span style="color: var(--safetymind-primary);">MIND</span></div>
                <h1>Informe de Kickoff</h1>
                <p>Proyecto: {project_info.get('name', 'N/A')}</p>
            </header>

            <div class="section">
                <h2>1. Objetivos del Proyecto</h2>
                <p>{project_info.get('description', 'Definición de bases y alcance del proyecto de monitoreo.')}</p>
            </div>

            <div class="section">
                <h2>2. Arquitectura del Sistema</h2>
                <div class="arch-box">
                    <p><strong>Diagrama de Componentes:</strong></p>
                    <p>{project_info.get('architecture_desc', 'Conexión de cámaras IP -> Servidor Local -> Nube SafetyMind')}</p>
                </div>
            </div>

            <div class="section">
                <h2>3. Plan de Actividades (Jira)</h2>
                <table>
                    <thead>
                        <tr><th>ID</th><th>Actividad</th><th>Estado</th></tr>
                    </thead>
                    <tbody>
                        {"".join([f"<tr><td>{a.key}</td><td>{a.fields.summary}</td><td>{a.fields.status.name}</td></tr>" for a in activities])}
                    </tbody>
                </table>
            </div>

            <div style="margin-top: 50px; text-align: center; font-size: 10px; color: var(--safetymind-gray);">
                © {datetime.now().year} SafetyMind - Confidencial
            </div>
        </body>
        </html>
        """
        HTML(string=full_html).write_pdf(filename)
        print(f"Kickoff Report generado: {filename}")

    def generate_progress_status_report(self, progress_data, increments, blockers, filename="avance_report.pdf"):
        """Generates a progress report with milestones, percentage and blockers."""
        from datetime import datetime
        
        full_html = f"""
        <html>
        <head>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
                :root {{
                    --safetymind-primary: #ffed01;
                    --safetymind-black: #000000;
                    --safetymind-gray: #adadad;
                }}
                body {{ font-family: 'Montserrat', sans-serif; margin: 30px; font-size: 14px; }}
                .progress-container {{ background: #eee; border-radius: 10px; height: 25px; width: 100%; margin: 20px 0; }}
                .progress-fill {{ background: var(--safetymind-primary); height: 100%; border-radius: 10px; text-align: right; padding-right: 10px; line-height: 25px; font-weight: bold; }}
                .blocker-box {{ background: #fff5f5; border-left: 5px solid #ff4d4d; padding: 15px; margin-top: 20px; }}
                h1 {{ border-bottom: 3px solid var(--safetymind-primary); }}
            </style>
        </head>
        <body>
            <div style="text-align: right; font-weight: bold; font-size: 20px;">SAFETY<span style="color: var(--safetymind-primary);">MIND</span></div>
            <h1>Estado de Avance del Proyecto</h1>
            
            <h3>Progreso General</h3>
            <div class="progress-container">
                <div class="progress-fill" style="width: {progress_data.get('percentage', 0)}%">{progress_data.get('percentage', 0)}%</div>
            </div>

            <h3>Actividades Realizadas</h3>
            <ul>
                {"".join([f"<li><strong>{i.key}</strong>: {i.fields.summary} - <span style='color:green'>Completado</span></li>" for i in increments])}
            </ul>

            <h3>Inconvenientes y Bloqueos</h3>
            <div class="blocker-box">
                {f"<p>{blockers}</p>" if blockers else "<p>No se reportan bloqueos hasta la fecha.</p>"}
            </div>
        </body>
        </html>
        """
        HTML(string=full_html).write_pdf(filename)
        print(f"Progress Report generado: {filename}")

    def generate_final_report(self, implementation_details, deviations, filename="informe_final.pdf"):
        """Generates a final delivery report with technical details of cameras, IPs, etc."""
        from datetime import datetime
        
        cameras_html = "".join([f"<tr><td>{c['name']}</td><td>{c['ip']}</td><td>{c['telegram_group']}</td><td>{c['status']}</td></tr>" for c in implementation_details.get('cameras', [])])

        full_html = f"""
        <html>
        <head>
             <style>
                @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
                :root {{ --safetymind-primary: #ffed01; --safetymind-black: #000000; }}
                body {{ font-family: 'Montserrat', sans-serif; margin: 30px; }}
                header {{ background: var(--safetymind-black); color: white; padding: 20px; text-align: center; border-bottom: 5px solid var(--safetymind-primary); }}
                .tech-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                .tech-table th, .tech-table td {{ border: 1px solid #ddd; padding: 10px; }}
                .tech-table th {{ background: #333; color: white; }}
                .deviation-box {{ background: #f9f9f9; padding: 15px; border-left: 5px solid var(--safetymind-primary); margin-top: 20px; }}
            </style>
        </head>
        <body>
            <header>
                <h1>INFORME FINAL DE IMPLEMENTACIÓN</h1>
                <p>SafetyMind AI Visual Auditing</p>
            </header>

            <h3>1. Detalle Técnico de Instalación (Cámaras)</h3>
            <table class="tech-table">
                <thead>
                    <tr><th>Cámara</th><th>Dirección IP</th><th>Grupo Telegram</th><th>Estado</th></tr>
                </thead>
                <tbody>
                    {cameras_html}
                </tbody>
            </table>

            <h3>2. Modificaciones al Plan Original</h3>
            <div class="deviation-box">
                <p>{deviations if deviations else "Implementación realizada según plan original sin desviaciones."}</p>
            </div>

            <h3>3. Conclusiones</h3>
            <p>El sistema se encuentra operativo y transmitiendo alertas en tiempo real.</p>
        </body>
        </html>
        """
        HTML(string=full_html).write_pdf(filename)
        print(f"Final Report generado: {filename}")

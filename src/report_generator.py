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

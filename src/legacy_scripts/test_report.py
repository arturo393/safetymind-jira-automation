from report_generator import ReportGenerator

# Mock Jira Issue Object
class MockIssue:
    def __init__(self, key, summary):
        self.key = key
        self.fields = type('obj', (object,), {'summary': summary})

if __name__ == "__main__":
    # Simulate Jira data
    issues = [
        MockIssue("SM-101", "Implement AHP Algorithm for Risk Analysis"),
        MockIssue("SM-102", "Design new Warning Dashboard"),
        MockIssue("SM-103", "Fix bug in Icinga branding CSS"),
    ]

    generator = ReportGenerator(issues)
    
    # Generate MD (for inspection if needed)
    generator.save_markdown("sample_report.md")
    
    # Generate PDF (the main deliverable)
    try:
        generator.generate_pdf("sample_report.pdf")
        print("Success! 'sample_report.pdf' has been created.")
    except Exception as e:
        print(f"Error generating PDF: {e}")

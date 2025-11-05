import json
from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Findings Report', 0, 1, 'C')

    def chapter_title(self, findings_title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, findings_title, 0, 1, 'L')
        self.ln(5)
    
    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

def generate_report(findings_json):
    pdf = PDF()
    pdf.add_page()
    
    findings = json.loads(findings_json)
    
    for finding in findings:
        title = finding.get('title', 'No Title')
        description = finding.get('description', 'No Description')
        pdf.chapter_title(title)
        pdf.chapter_body(description)
    
    pdf_file_name = 'findings_report.pdf'
    pdf.output(pdf_file_name)

if __name__ == "__main__":
    # Example of how to use the function
    with open('findings.json') as f:
        findings_json = f.read()
    
    generate_report(findings_json)
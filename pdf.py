from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.platypus import Spacer

document_content = {
    "content": [
        {
            "title": "Artificial Intelligence",
            "body": "Artificial Intelligence (AI) is the simulation of human intelligence in machines that are programmed to think like humans and mimic their actions. The term may also be applied to any machine that exhibits traits associated with a human mind such as learning and problem-solving."
        },
        {
            "title": "Python Programming Language",
            "body": "Python was developed by Guido van Rossum and first released in 1991. Python is known for its readability and simplicity, making it a popular choice for beginners and experts alike."
        },
        {
            "title": "Capital of France",
            "body": "The capital of France is Paris, a global center for art, fashion, gastronomy, and culture."
        },
        {
            "title": "Additional Information",
            "body": "This section contains additional information that may require more space. If the content here exceeds the current page, it will automatically flow to the next page."
        },
        {
            "title": "Conclusion",
            "body": "In conclusion, this document provides insights into various topics, demonstrating how multipage PDF generation works with ReportLab."
        }
    ]
}

def create_pdf(filename, content):
    pdf = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    for section in content['content']:
        title = Paragraph(section['title'], styles['Title'])
        elements.append(title)
        body = Paragraph(section['body'], styles['BodyText'])
        elements.append(body)
        elements.append(Spacer(1, 12))

        if section['title'] == "Capital of France":
            elements.append(PageBreak()) 
    
    pdf.build(elements)

create_pdf("output.pdf", document_content)

print("PDF created successfully!")

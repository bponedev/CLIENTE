"""
Geração de PDFs usando reportlab.
"""

from reportlab.pdfgen import canvas

def generate_pdf(path, title):
    c = canvas.Canvas(path)
    c.drawString(100, 750, title)
    c.save()

"""
pdfgen.py
---------
Geração de PDFs usando reportlab.
"""

from flask import send_file
from reportlab.pdfgen import canvas
import io


def generate_pdf(registro):
    """
    Recebe um dict com os dados do registro e devolve um arquivo PDF.
    """

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(30, 800, "Relatório — Registro")

    pdf.setFont("Helvetica", 12)

    y = 760
    for k, v in registro.items():
        pdf.drawString(30, y, f"{k}: {v}")
        y -= 20

    pdf.save()
    buffer.seek(0)

    return buffer

"""
Geração de PDFs com reportlab.
Utilizado para exportar registros.
"""

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def gerar_pdf(filepath, dados):
    doc = SimpleDocTemplate(filepath)
    styles = getSampleStyleSheet()
    conteudo = []

    for linha in dados:
        txt = " | ".join(str(v) for v in linha.values())
        conteudo.append(Paragraph(txt, styles["Normal"]))

    doc.build(conteudo)

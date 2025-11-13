from typing import Optional, List
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime

def generate_report(path: str, title: str, grammar_text: str, classification: int, steps: List[str], diagram_path: Optional[str] = None):
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    c.setTitle(title)
    y = height - 50
    c.setFont("Helvetica-Bold", 14); c.drawString(40, y, title); y -= 20
    c.setFont("Helvetica", 10); c.drawString(40, y, f"Fecha: {datetime.now()}"); y -= 20
    c.setFont("Helvetica-Bold", 12); c.drawString(40, y, "Gramática:"); y -= 14
    c.setFont("Courier", 9)
    for line in grammar_text.splitlines():
        c.drawString(40, y, line[:100]); y -= 12
        if y < 100: c.showPage(); y = height - 50
    c.setFont("Helvetica-Bold", 12); c.drawString(40, y, f"Clasificación: Tipo {classification}"); y -= 16
    c.setFont("Helvetica-Bold", 12); c.drawString(40, y, "Justificación:"); y -= 14
    c.setFont("Helvetica", 10)
    for s in steps:
        for chunk in [s[i:i+90] for i in range(0, len(s), 90)]:
            c.drawString(50, y, u"• " + chunk); y -= 12
            if y < 120: c.showPage(); y = height - 50
    if diagram_path:
        try:
            c.showPage()
            c.setFont("Helvetica-Bold", 12); c.drawString(40, height - 40, "Diagrama")
            img = ImageReader(diagram_path)
            iw, ih = img.getSize()
            scale = min((width-80)/iw, (height-120)/ih)
            c.drawImage(img, 40, 80, iw*scale, ih*scale, preserveAspectRatio=True, mask='auto')
        except Exception as e:
            c.showPage(); c.drawString(40, height - 40, f"No se pudo insertar imagen: {e}")
    c.save(); return path

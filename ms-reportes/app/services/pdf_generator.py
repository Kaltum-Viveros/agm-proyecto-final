from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_calificaciones_pdf(materia_data: dict, alumnos: list, concentrado_alumnos: list) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    styles = getSampleStyleSheet()
    
    # Title
    elements.append(Paragraph("Reporte de Calificaciones", styles['Title']))
    elements.append(Spacer(1, 12))
    
    # Materia Info
    info_text = f"<b>Materia:</b> {materia_data.get('nombre', 'N/A')} <br/>"
    info_text += f"<b>NRC:</b> {materia_data.get('nrc', 'N/A')} <br/>"
    info_text += f"<b>Sección:</b> {materia_data.get('seccion', 'N/A')} <br/>"
    if materia_data.get('docente_nombre'):
        info_text += f"<b>Docente:</b> {materia_data.get('docente_nombre')} <br/>"
    if materia_data.get('periodo'):
        info_text += f"<b>Periodo:</b> {materia_data['periodo'].get('nombre', 'N/A')} <br/>"
        
    elements.append(Paragraph(info_text, styles['Normal']))
    elements.append(Spacer(1, 24))
    
    # Create Table Data
    data = [["Matrícula", "Nombre Alumno", "Prom. Real", "Prom. Final", "Estado"]]
    
    # Build a lookup for concentrated data by alumno_id
    concentrado_dict = {}
    for a in concentrado_alumnos:
        concentrado_dict[a.alumno_id] = {
            'real': a.promedio_real,
            'redondeado': a.promedio_redondeado
        }
    
    for al in alumnos:
        c_data = concentrado_dict.get(al.alumno_id, {})
        prom_real = c_data.get('real', 0.0)
        prom_redon = c_data.get('redondeado', 0)
        estado = "Aprobado" if prom_redon >= 70 else "Reprobado"
        
        data.append([
            al.matricula,
            al.nombre_completo,
            f"{prom_real:.2f}",
            str(prom_redon),
            estado
        ])
        
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(t)
    doc.build(elements)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

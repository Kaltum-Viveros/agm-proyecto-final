from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    A canvas that enables multi-pass page numbering ('Page X of Y')
    along with highly aesthetic, corporate header and footer lines.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        # Save state for the second-pass rendering of total page count
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Color Palette
        primary_navy = colors.HexColor('#1E3A8A')
        neutral_slate = colors.HexColor('#64748B')
        border_slate = colors.HexColor('#CBD5E1')
        
        # --- HEADER DECORATION ---
        # Draw a thin header line
        self.setStrokeColor(border_slate)
        self.setLineWidth(0.5)
        self.line(36, 756, 576, 756)
        
        # Header Text
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(primary_navy)
        self.drawString(36, 762, "SISTEMA DE GESTIÓN ESCOLAR")
        
        self.setFont("Helvetica", 8)
        self.setFillColor(neutral_slate)
        self.drawRightString(576, 762, "REPORTE ACADÉMICO OFICIAL")
        
        # --- FOOTER DECORATION ---
        # Draw a thin footer line
        self.line(36, 45, 576, 45)
        
        # Footer Text
        self.setFont("Helvetica", 8)
        self.setFillColor(neutral_slate)
        self.drawString(36, 32, "Documento digital oficial y verificado. Generado automáticamente.")
        
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(576, 32, page_text)
        
        self.restoreState()

def generate_calificaciones_pdf(materia_data: dict, alumnos: list, concentrado_alumnos: list) -> bytes:
    buffer = BytesIO()
    # Margins are set to give enough room for the header (at Y=756) and footer (at Y=45)
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=60,
        bottomMargin=60
    )
    elements = []
    
    # 1. Styles Definition
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=12
    )
    
    label_style = ParagraphStyle(
        'CardLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#475569') # Slate 600
    )
    
    value_style = ParagraphStyle(
        'CardValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#1E293B') # Slate 800
    )
    
    summary_label_style = ParagraphStyle(
        'SummaryLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        alignment=1, # Center
        textColor=colors.HexColor('#475569')
    )
    
    summary_val_style = ParagraphStyle(
        'SummaryValue',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=15,
        alignment=1, # Center
        textColor=colors.HexColor('#1E3A8A')
    )
    
    summary_val_success = ParagraphStyle(
        'SummaryValueSuccess',
        parent=summary_val_style,
        textColor=colors.HexColor('#15803D')
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        alignment=1, # Center
        textColor=colors.white
    )
    
    table_body_style = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=10.5,
        textColor=colors.HexColor('#1E293B')
    )
    
    table_body_center = ParagraphStyle(
        'TableBodyCenter',
        parent=table_body_style,
        alignment=1 # Center
    )
    
    table_body_bold_center = ParagraphStyle(
        'TableBodyBoldCenter',
        parent=table_body_style,
        fontName='Helvetica-Bold',
        alignment=1 # Center
    )

    # 2. Main Title and Header
    elements.append(Paragraph("Reporte de Calificaciones", title_style))
    elements.append(Paragraph("Detalle de ponderación final y estatus académico de estudiantes.", subtitle_style))
    
    # 3. Metadata Card Table
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    meta_data = [
        [
            Paragraph("Materia:", label_style), Paragraph(materia_data.get('nombre', 'N/A'), value_style),
            Paragraph("Docente:", label_style), Paragraph(materia_data.get('docente_nombre', 'N/A'), value_style)
        ],
        [
            Paragraph("NRC:", label_style), Paragraph(materia_data.get('nrc', 'N/A'), value_style),
            Paragraph("Periodo:", label_style), Paragraph(materia_data.get('periodo', {}).get('nombre', 'N/A'), value_style)
        ],
        [
            Paragraph("Sección:", label_style), Paragraph(materia_data.get('seccion', 'N/A'), value_style),
            Paragraph("Fecha Generación:", label_style), Paragraph(fecha_actual, value_style)
        ]
    ]
    
    # Width distribution: 70 + 200 + 90 + 180 = 540 pt (Matches usable width)
    meta_table = Table(meta_data, colWidths=[70, 200, 90, 180])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#E2E8F0')),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 10))
    
    # 4. Process Concentrated Grades and Summary Metrics
    concentrado_dict = {}
    for a in concentrado_alumnos:
        concentrado_dict[a.alumno_id] = {
            'real': getattr(a, 'promedio_real', 0.0),
            'redondeado': getattr(a, 'promedio_redondeado', 0)
        }
        
    total_alumnos = len(alumnos)
    aprobados_count = 0
    suma_promedios = 0.0
    
    for al in alumnos:
        c_data = concentrado_dict.get(al.alumno_id, {})
        suma_promedios += c_data.get('real', 0.0)
        if c_data.get('redondeado', 0) >= 6:
            aprobados_count += 1
            
    reprobados_count = total_alumnos - aprobados_count
    promedio_general = (suma_promedios / total_alumnos) if total_alumnos > 0 else 0.0
    tasa_aprobacion = (aprobados_count / total_alumnos * 100.0) if total_alumnos > 0 else 0.0
    
    # 5. Dashboard Widget Card
    summary_data = [
        [
            Paragraph("TOTAL DE ALUMNOS", summary_label_style),
            Paragraph("PROMEDIO GRUPAL", summary_label_style),
            Paragraph("TASA DE APROBACIÓN", summary_label_style)
        ],
        [
            Paragraph(str(total_alumnos), summary_val_style),
            Paragraph(f"{promedio_general:.2f}", summary_val_style),
            Paragraph(f"{tasa_aprobacion:.1f}% <font size=8.5 color='#64748B'>({aprobados_count}/{total_alumnos})</font>", summary_val_success)
        ]
    ]
    
    # Width distribution: 180 + 180 + 180 = 540 pt
    summary_table = Table(summary_data, colWidths=[180, 180, 180])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F9FF')), # Light Sky Blue Background
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#BAE6FD')),   # Soft Sky Border
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0F2FE')),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 15))
    
    # 6. Build Student Grades Table
    data = [
        [
            Paragraph("Matrícula", table_header_style),
            Paragraph("Nombre Alumno", table_header_style),
            Paragraph("Prom. Real", table_header_style),
            Paragraph("Prom. Final", table_header_style),
            Paragraph("Estado", table_header_style)
        ]
    ]
    
    for al in alumnos:
        c_data = concentrado_dict.get(al.alumno_id, {})
        prom_real = c_data.get('real', 0.0)
        prom_redon = c_data.get('redondeado', 0)
        
        if prom_redon >= 6:
            estado_html = "<font color='#15803D'><b>APROBADO</b></font>"
        else:
            estado_html = "<font color='#B91C1C'><b>REPROBADO</b></font>"
            
        data.append([
            Paragraph(al.matricula, table_body_center),
            Paragraph(al.nombre_completo, table_body_style),
            Paragraph(f"{prom_real:.2f}", table_body_center),
            Paragraph(str(prom_redon), table_body_bold_center),
            Paragraph(estado_html, table_body_center)
        ])
        
    # Usable: 80 + 200 + 80 + 80 + 100 = 540 pt
    t = Table(data, colWidths=[80, 200, 80, 80, 100])
    
    # Premium Table Style with zebra striping
    t_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
    ])
    
    # Alternate row colors dynamically
    for idx in range(1, len(data)):
        bg = colors.HexColor('#F8FAFC') if idx % 2 == 0 else colors.white
        t_style.add('BACKGROUND', (0, idx), (-1, idx), bg)
        
    t.setStyle(t_style)
    elements.append(t)
    
    # Build Document using dynamic NumberedCanvas
    doc.build(elements, canvasmaker=NumberedCanvas)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def generate_asistencias_pdf(materia_data: dict, alumnos: list, asistencias_data: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=60,
        bottomMargin=60
    )
    elements = []
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'ReportSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#64748B'),
        spaceAfter=12
    )
    
    label_style = ParagraphStyle(
        'CardLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#475569')
    )
    
    value_style = ParagraphStyle(
        'CardValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#1E293B')
    )
    
    summary_label_style = ParagraphStyle(
        'SummaryLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10,
        alignment=1, # Center
        textColor=colors.HexColor('#475569')
    )
    
    summary_val_style = ParagraphStyle(
        'SummaryValue',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=15,
        alignment=1, # Center
        textColor=colors.HexColor('#1E3A8A')
    )
    
    summary_val_danger = ParagraphStyle(
        'SummaryValueDanger',
        parent=summary_val_style,
        textColor=colors.HexColor('#B91C1C')
    )
    
    summary_val_ok = ParagraphStyle(
        'SummaryValueOk',
        parent=summary_val_style,
        textColor=colors.HexColor('#15803D')
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        alignment=1, # Center
        textColor=colors.white
    )
    
    table_body_style = ParagraphStyle(
        'TableBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=10.5,
        textColor=colors.HexColor('#1E293B')
    )
    
    table_body_center = ParagraphStyle(
        'TableBodyCenter',
        parent=table_body_style,
        alignment=1 # Center
    )
    
    table_body_bold_center = ParagraphStyle(
        'TableBodyBoldCenter',
        parent=table_body_style,
        fontName='Helvetica-Bold',
        alignment=1 # Center
    )

    # Main Title and Subtitle
    elements.append(Paragraph("Reporte de Asistencias", title_style))
    elements.append(Paragraph("Resumen detallado de sesiones presenciales, faltas y tasa de asistencia.", subtitle_style))
    
    # Metadata Card Table
    fecha_actual = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    meta_data = [
        [
            Paragraph("Materia:", label_style), Paragraph(materia_data.get('nombre', 'N/A'), value_style),
            Paragraph("Docente:", label_style), Paragraph(materia_data.get('docente_nombre', 'N/A'), value_style)
        ],
        [
            Paragraph("NRC:", label_style), Paragraph(materia_data.get('nrc', 'N/A'), value_style),
            Paragraph("Periodo:", label_style), Paragraph(materia_data.get('periodo', {}).get('nombre', 'N/A'), value_style)
        ],
        [
            Paragraph("Sección:", label_style), Paragraph(materia_data.get('seccion', 'N/A'), value_style),
            Paragraph("Fecha Generación:", label_style), Paragraph(fecha_actual, value_style)
        ]
    ]
    
    meta_table = Table(meta_data, colWidths=[70, 200, 90, 180])
    meta_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#E2E8F0')),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 10))
    
    # Calculate Attendance Statistics
    total_alumnos = len(alumnos)
    total_porcentaje = 0.0
    alumnos_riesgo = 0
    
    for al in alumnos:
        a_data = asistencias_data.get(al.alumno_id, {})
        porcentaje = a_data.get("porcentaje", 0.0)
        total_porcentaje += porcentaje
        if porcentaje < 80.0:
            alumnos_riesgo += 1
            
    promedio_asistencia = (total_porcentaje / total_alumnos) if total_alumnos > 0 else 0.0
    
    # Dashboard Widget Card
    risk_style = summary_val_danger if alumnos_riesgo > 0 else summary_val_ok
    summary_data = [
        [
            Paragraph("TOTAL DE ALUMNOS", summary_label_style),
            Paragraph("ASISTENCIA PROMEDIO", summary_label_style),
            Paragraph("ALUMNOS EN RIESGO (&lt;80%)", summary_label_style)
        ],
        [
            Paragraph(str(total_alumnos), summary_val_style),
            Paragraph(f"{promedio_asistencia:.1f}%", summary_val_style),
            Paragraph(str(alumnos_riesgo), risk_style)
        ]
    ]
    
    summary_table = Table(summary_data, colWidths=[180, 180, 180])
    summary_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F0F9FF')),
        ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#BAE6FD')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E0F2FE')),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 15))
    
    # Build Attendance Table
    data = [
        [
            Paragraph("Matrícula", table_header_style),
            Paragraph("Nombre Alumno", table_header_style),
            Paragraph("Presentes", table_header_style),
            Paragraph("Retardos", table_header_style),
            Paragraph("Faltas", table_header_style),
            Paragraph("% Asistencia", table_header_style)
        ]
    ]
    
    for al in alumnos:
        a_data = asistencias_data.get(al.alumno_id, {})
        presentes = a_data.get("presentes", 0)
        retardos = a_data.get("retardos", 0)
        faltas = a_data.get("faltas", 0)
        porcentaje = a_data.get("porcentaje", 0.0)
        
        if porcentaje >= 80.0:
            porcentaje_html = f"<font color='#15803D'><b>{porcentaje:.1f}%</b></font>"
        else:
            porcentaje_html = f"<font color='#B91C1C'><b>{porcentaje:.1f}%</b></font>"
            
        data.append([
            Paragraph(al.matricula, table_body_center),
            Paragraph(al.nombre_completo, table_body_style),
            Paragraph(str(presentes), table_body_center),
            Paragraph(str(retardos), table_body_center),
            Paragraph(str(faltas), table_body_center),
            Paragraph(porcentaje_html, table_body_center)
        ])
        
    # Usable: 75 + 195 + 65 + 65 + 65 + 75 = 540 pt
    t = Table(data, colWidths=[75, 195, 65, 65, 65, 75])
    
    t_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
    ])
    
    for idx in range(1, len(data)):
        bg = colors.HexColor('#F8FAFC') if idx % 2 == 0 else colors.white
        t_style.add('BACKGROUND', (0, idx), (-1, idx), bg)
        
    t.setStyle(t_style)
    elements.append(t)
    
    doc.build(elements, canvasmaker=NumberedCanvas)
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

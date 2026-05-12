import fitz
import re
import uuid

def extraer_alumnos_buap(pdf_content: bytes):
    """
    Extrae datos del PDF institucional de la BUAP con precisión por columnas.
    """
    alumnos_data = []
    nrc_materia = None
    nombre_docente_pdf = None
    id_docente_pdf = None

    try:
        doc = fitz.open(stream=pdf_content, filetype="pdf")
        
        for page in doc:
            text_full = page.get_text()
            text_dict = page.get_text("dict")
            
            # 1. Extraer NRC y Datos del Docente del encabezado
            if not nrc_materia:
                match_nrc = re.search(r"NRC:\s*(\d+)", text_full)
                if match_nrc: nrc_materia = match_nrc.group(1)

            if not id_docente_pdf:
                # El docente aparece al inicio: ID (9 dígitos) + Nombre
                match_docente = re.search(r'(\d{9})\s+([A-Z\s\-]+)', text_full)
                if match_docente:
                    id_docente_pdf = match_docente.group(1)
                    nombre_docente_pdf = match_docente.group(2).split('\n')[0].strip().replace("-", " ")

            # 2. Mapear hipervínculos para los correos reales
            links = page.get_links()
            mailto_links = [{"rect": fitz.Rect(l["from"]), "email": l["uri"].replace("mailto:", "")} 
                            for l in links if l.get("uri", "").startswith("mailto:")]
            
            # 3. Recolectar todos los fragmentos de texto (spans)
            all_spans = []
            for b in text_dict["blocks"]:
                if b["type"] == 0:
                    for l in b["lines"]:
                        for s in l["spans"]:
                            all_spans.append({"text": s["text"].strip(), "bbox": fitz.Rect(s["bbox"])})

            # 4. Procesar Alumnos por filas basadas en la Matrícula
            for span in all_spans:
                txt = span["text"]
                match_id = re.search(r'\b(\d{9})\b', txt)
                
                if match_id:
                    matricula = match_id.group(1)
                    
                    # FILTRO: Ignorar el ID del docente que aparece en el encabezado
                    if matricula == id_docente_pdf:
                        continue
                        
                    # Punto de referencia central de la fila (coordenada Y)
                    y_ref = (span["bbox"].y0 + span["bbox"].y1) / 2
                    
                    # --- EXTRAER NOMBRE (Columna 2: x entre 50 y 300) ---
                    nombre = "Desconocido"
                    for s in all_spans:
                        # Buscamos texto en la misma fila (tolerancia 6px) y a la izquierda de la matrícula
                        if abs((s["bbox"].y0 + s["bbox"].y1)/2 - y_ref) < 6:
                            # La columna de nombres está a la izquierda (x < 300) y no es el número de lista
                            if 50 < s["bbox"].x0 < 280 and not re.match(r'^\d+$', s["text"]):
                                if s["text"] not in ["Registro", "Nombre de Alumno"]:
                                    nombre = s["text"]
                                    break
                    
                    # --- EXTRAER NIVEL (Columna 4: x > 400) ---
                    nivel = "Licenciatura" 
                    for s in all_spans:
                        if abs((s["bbox"].y0 + s["bbox"].y1)/2 - y_ref) < 8:
                            if s["bbox"].x0 > 400:
                                # Capturamos solo la palabra clave del nivel
                                m_nivel = re.search(r'(Licenciatura|Posgrado|Maestría)', s["text"])
                                if m_nivel:
                                    nivel = m_nivel.group(1)
                                    break

                    # --- CORREO: Coincidencia por coordenadas de los links ---
                    correo_final = None
                    for m_link in mailto_links:
                        # El icono del sobre está alineado con la fila del alumno
                        if abs((m_link["rect"].y0 + m_link["rect"].y1)/2 - y_ref) < 15:
                            correo_final = m_link["email"]
                            break
                    
                    # Si no hay link, generamos el institucional por defecto
                    if not correo_final:
                        correo_final = f"{matricula}@alumno.buap.mx"

                    alumnos_data.append({
                        "alumno": {
                            "nombre_completo": nombre,
                            "matricula": matricula,
                            "correo": correo_final,
                            "tipo_formacion": nivel,
                            "user_id": str(uuid.uuid4()),
                            "estatus_academico": True
                        },
                        "inscripcion": {
                            "nrc_materia": nrc_materia,
                            "nombre_docente": nombre_docente_pdf
                        }
                    })
        doc.close()
    except Exception as e:
        raise ValueError(f"Error procesando PDF: {str(e)}")
    return alumnos_data
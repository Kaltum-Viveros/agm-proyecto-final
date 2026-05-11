import pdfplumber
import io
import re

def extraer_docentes_pdf(contenido_pdf):
    docentes = []
    # Regex robusta para correos de la BUAP
    pattern_correo = re.compile(r'[a-zA-Z0-9._%+-]+@correo\.buap\.mx')
    
    try:
        with pdfplumber.open(io.BytesIO(contenido_pdf)) as pdf:
            for page in pdf.pages:
                # Obtenemos todas las palabras individualmente con sus coordenadas
                palabras = page.extract_words(
                    keep_blank_chars=False, 
                    use_text_flow=True,
                    horizontal_ltr=True
                )
                
                # Unimos todo en un solo bloque de texto gigante para procesar
                texto_completo = " ".join([p['text'] for p in palabras])
                
                # Buscamos todos los correos en la página
                correos_encontrados = pattern_correo.findall(texto_completo)
                
                for correo in correos_encontrados:
                    # Buscamos la palabra que es el correo para obtener su posición
                    word_obj = next((p for p in palabras if correo in p['text']), None)
                    
                    if word_obj:
                        # Buscamos el nombre (palabras que están a la izquierda en la misma línea y-top)
                        # El Directorio BUAP pone: [Nombre] [Correo] [Ubicación]
                        palabras_en_linea = [
                            p['text'] for p in palabras 
                            if abs(p['top'] - word_obj['top']) < 3 # Misma altura
                        ]
                        
                        linea_texto = " ".join(palabras_en_linea)
                        
                        # Limpiamos el nombre: todo lo que esté antes del correo
                        nombre_raw = linea_texto.split(correo)[0].strip()
                        # Quitamos números al inicio (ej: "1. ")
                        nombre_limpio = re.sub(r'^\d+[\s\.]+', '', nombre_raw)
                        
                        # Limpiamos ubicación: todo lo que esté después del correo
                        ubicacion_raw = linea_texto.split(correo)[1].strip()
                        cubiculo = ubicacion_raw.replace("Ver PDF", "").strip()

                        if correo and nombre_limpio:
                            docentes.append({
                                "nombre_completo": nombre_limpio,
                                "correo": correo,
                                "cubiculo": cubiculo if cubiculo else "No especificado"
                            })
    except Exception as e:
        print(f"Error crítico en el Motor de Objetos: {e}")
        
    # LOGS para que veas en la terminal si extrajo algo
    print(f"--- INTENTO DE EXTRACCIÓN ---")
    print(f"Total docentes encontrados: {len(docentes)}")
    return docentes
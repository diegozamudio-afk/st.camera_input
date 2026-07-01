import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import Image
from datetime import datetime

# 1. Configuración de la IA (Cargada una sola vez para velocidad)
@st.cache_resource
def cargar_modelo_ocr():
    # El modelo 'es' lee español.
    return easyocr.Reader(['es'], gpu=False)

# 2. Función que procesa y limpia la imagen antes de leerla
def procesar_patente(imagen_bytes):
    reader = cargar_modelo_ocr()
    
    # Abrir la imagen desde bytes
    img = Image.open(imagen_bytes)
    
    # Convertir a formato OpenCV (BGR) y luego a escala de grises
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    # Aplicar un filtro de umbral (threshold) para mejorar el contraste del texto
    # Esto ayuda muchísimo a que la IA "vea" mejor las letras negras sobre fondo blanco
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
    
    # Leer el texto de la imagen procesada
    resultados = reader.readtext(thresh)
    
    # Buscamos coincidencias con patentes argentinas
    for (bbox, text, prob) in resultados:
        text = text.replace(" ", "").upper()
        # Filtramos por longitud típica de patente (6 o 7 caracteres)
        if 6 <= len(text) <= 7:
            return text
    return None

# 3. Interfaz de ISAAC
st.set_page_config(page_title="ISAAC LPR", page_icon="📸")
st.title("📸 ISAAC - Escáner LPR Móvil")
st.write("ISAAC está listo. Enfoca la patente y dispara la cámara.")

foto_capturada = st.camera_input("Capturar Patente")

if foto_capturada is not None:
    with st.spinner("ISAAC analizando imagen..."):
        patente_detectada = procesar_patente(foto_capturada)
        
        if patente_detectada:
            st.success(f"✅ Patente detectada: **{patente_detectada}**")
            
            # Aquí dispararías la lógica de tu sistema:
            # hoja.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), patente_detectada, "VENCIDO"])
            
            st.balloons()
            st.info("Patente enviada a validación de Tribunal.")
        else:
            st.error("❌ No se pudo leer la patente. Intenta acercarte más o buscar un ángulo sin reflejo.")
            st.warning("Consejo: Evita el reflejo del sol sobre el metal de la chapa.")

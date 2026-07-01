import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import Image
from datetime import datetime

# 1. Configuración de la IA (Cargamos el modelo una sola vez para que sea rápido)
@st.cache_resource
def cargar_modelo_ocr():
    # 'es' es para español
    return easyocr.Reader(['es'], gpu=False)

# 2. Función que "lee" la foto
def procesar_patente(imagen_bytes):
    reader = cargar_modelo_ocr()
    # Convertimos los bytes de la foto a una imagen que OpenCV pueda leer
    img = Image.open(imagen_bytes)
    img_np = np.array(img)
    
    # El lector escanea el texto
    resultados = reader.readtext(img_np)
    
    # Buscamos en los resultados algo que parezca una patente argentina (6 o 7 caracteres)
    for (bbox, text, prob) in resultados:
        text = text.replace(" ", "").upper()
        if 6 <= len(text) <= 7: 
            return text
    return None

# 3. Interfaz de ISAAC
st.title("📸 ISAAC - Escáner LPR Móvil")
st.write("Captura una patente para validar su estado automáticamente.")

foto_capturada = st.camera_input("Enfocar patente")

if foto_capturada is not None:
    with st.spinner("ISAAC está analizando la matrícula..."):
        patente_leida = procesar_patente(foto_capturada)
        
        if patente_leida:
            st.success(f"✅ Patente detectada: **{patente_leida}**")
            
            # Aquí es donde conectarías tu validación contra Google Sheets
            st.info("Validando en base de datos central...")
            # [Aquí iría tu lógica de hoja.append_row() ...]
            
        else:
            st.error("❌ No se pudo leer la patente. Asegúrate de que esté bien iluminada y centrada.")

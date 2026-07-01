import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import Image
from datetime import datetime

# 1. Configuración de la IA (Cargada una sola vez para velocidad)
@st.cache_resource
def cargar_modelo_ocr():
    # 'es' para español, gpu=False para compatibilidad total en dispositivos móviles
    return easyocr.Reader(['es'], gpu=False)

# 2. Función maestra que procesa, limpia y corrige la lectura
def procesar_patente(imagen_bytes):
    reader = cargar_modelo_ocr()
    
    # Convertir bytes a imagen PIL y luego a OpenCV
    img = Image.open(imagen_bytes)
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    # Mejora de contraste: binarización
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
    
    # Lectura
    resultados = reader.readtext(thresh)
    
    for (bbox, text, prob) in resultados:
        text = text.replace(" ", "").upper()
        
        # --- Lógica de Corrección Inteligente ---
        # Basada en posiciones de patentes argentinas (ej. AA 123 AA)
        lista_texto = list(text)
        for i in range(len(lista_texto)):
            char = lista_texto[i]
            
            # Posiciones que DEBEN ser LETRAS (0,1 y 5,6)
            if i in [0, 1, 5, 6]:
                if char == '0': lista_texto[i] = 'G'
                elif char == '8': lista_texto[i] = 'B'
                elif char == '1': lista_texto[i] = 'I'
            
            # Posiciones que DEBEN ser NÚMEROS (2, 3, 4)
            elif i in [2, 3, 4]:
                if char == 'O': lista_texto[i] = '0'
                elif char == 'G': lista_texto[i] = '6'
                elif char == 'S': lista_texto[i] = '5'
        
        text_corregido = "".join(lista_texto)
        
        # Filtro de longitud para validar patente argentina (6 o 7 caracteres)
        if 6 <= len(text_corregido) <= 7:
            return text_corregido
            
    return None

# 3. Interfaz de usuario
st.set_page_config(page_title="ISAAC LPR", page_icon="📸")
st.title("📸 ISAAC - Escáner LPR Inteligente")
st.write("ISAAC está listo. Enfoca la patente y dispara la cámara.")

foto_capturada = st.camera_input("Capturar Patente")

if foto_capturada is not None:
    with st.spinner("ISAAC analizando imagen y corrigiendo caracteres..."):
        patente_detectada = procesar_patente(foto_capturada)
        
        if patente_detectada:
            st.success(f"✅ Patente leída correctamente: **{patente_detectada}**")
            
            # Aquí dispararías tu lógica de registro en Google Sheets:
            # hoja.append_row([datetime.now().strftime("%H:%M:%S"), patente_detectada, "PROCESADO"])
            
            st.balloons()
        else:
            st.error("❌ No se pudo leer la patente.")

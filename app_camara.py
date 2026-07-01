import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import Image
from datetime import datetime

# 1. Configuración de la IA (Cargada una sola vez para que sea rápido)
@st.cache_resource
def cargar_modelo_ocr():
    # El modelo 'es' lee español. gpu=False para compatibilidad móvil total.
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
        
        # --- Lógica de Corrección Automática ---
        correcciones = {'8': 'B', '6': 'G', '0': 'O', '1': 'I', '5': 'S', '4': 'A'}
        lista_texto = list(text)
        
        # Corregimos posiciones que suelen ser letras en patentes (posiciones 0,1 y 5,6)
        for i in range(len(lista_texto)):
            if i in [0, 1, 5, 6] and lista_texto[i] in correcciones:
                lista_texto[i] = correcciones[lista_texto[i]]
        
        text_corregido = "".join(lista_texto)
        
        # Filtro de longitud para validar patente argentina
        if 6 <= len(text_corregido) <= 7:
            return text_corregido
            
    return None

# 3. Interfaz de usuario
st.set_page_config(page_title="ISAAC LPR", page_icon="📸")
st.title("📸 ISAAC - Escáner LPR")

foto_capturada = st.camera_input("Enfocar patente y disparar")

if foto_capturada is not None:
    with st.spinner("Analizando placa con IA..."):
        patente_detectada = procesar_patente(foto_capturada)
        
        if patente_detectada:
            st.success(f"✅ Patente leída: **{patente_detectada}**")
            
            # Aquí disparas tu lógica de registro en Google Sheets
            # hoja.append_row([datetime.now().strftime("%H:%M:%S"), patente_detectada, "PROCESADO"])
            
            st.balloons()
        else:
            st.error("❌ No se pudo leer la patente.")
            st.warning("Recomendación: Asegúrate de que la chapa no tenga reflejo de sol directo.")

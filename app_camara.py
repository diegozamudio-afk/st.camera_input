import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Configuración de Google Sheets ---
def conectar_sheets():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
        "https://www.googleapis.com/auth/spreadsheets"
    ]
    # Usamos los secretos de Streamlit para mayor seguridad
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    # Reemplaza 'ISAAC - Monitoreo' con el nombre real de tu archivo en Drive
    return client.open("ISAAC - Monitoreo").sheet1

# --- 2. Configuración de la IA ---
@st.cache_resource
def cargar_modelo_ocr():
    return easyocr.Reader(['es'], gpu=False)

# --- 3. Lógica de procesamiento ---
def procesar_patente(imagen_bytes):
    reader = cargar_modelo_ocr()
    img = Image.open(imagen_bytes)
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
    resultados = reader.readtext(thresh)
    
    for (bbox, text, prob) in resultados:
        text = text.replace(" ", "").upper()
        # Lógica de corrección por posición
        lista = list(text)
        for i in range(len(lista)):
            if i in [0, 1, 5, 6]: # Posiciones de letras
                if lista[i] == '0': lista[i] = 'G'
            elif i in [2, 3, 4]: # Posiciones de números
                if lista[i] == 'O': lista[i] = '0'
        
        texto_final = "".join(lista)
        if 6 <= len(texto_final) <= 7: return texto_final
    return None

# --- 4. Interfaz ---
st.title("📸 ISAAC - Escáner e Impacto en Dash")
foto = st.camera_input("Capturar Patente")

if foto is not None:
    with st.spinner("Analizando y enviando a la base de datos..."):
        patente = procesar_patente(foto)
        if patente:
            try:
                hoja = conectar_sheets()
                fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                # Inyectamos los datos. Ajusta las columnas según tu Sheet
                hoja.append_row([fecha, patente, "Infracción Detectada por IA"])
                
                st.success(f"✅ Patente {patente} enviada al Dashboard correctamente.")
                st.balloons()
            except Exception as e:
                st.error(f"Error al conectar con la base de datos: {e}")
        else:
            st.error("No se pudo leer la patente. Reintente.")
from datetime import datetime, timedelta

def analizar_estado_vehiculo(patente, vencimiento_str):
    vencimiento = datetime.strptime(vencimiento_str, "%d/%m/%Y %H:%M")
    ahora = datetime.now()
    tiempo_restante = vencimiento - ahora
    
    if tiempo_restante <= timedelta(minutes=0):
        return "MULTAR", "⚠️ Vencido. Proceder a infracción."
    elif tiempo_restante <= timedelta(hours=1):
        # Aquí es donde ocurre la magia: agendamos la revisión
        return "SEGUIMIENTO", "🕒 Restan menos de 60 min. Agendar revisión en esta ubicación."
    else:
        return "OK", "Estacionamiento vigente."

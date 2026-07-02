import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import Image
from datetime import datetime, timedelta
import gspread
from google.oauth2.service_account import Credentials

# --- 1. Configuración de Google ---
def conectar_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds).open("ISAAC - Monitoreo")

# --- 2. Lógica de IA ---
@st.cache_resource
def cargar_modelo():
    return easyocr.Reader(['es'], gpu=False)

def procesar_lpr(foto):
    reader = cargar_modelo()
    img = Image.open(foto)
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    resultados = reader.readtext(gray)
    for (_, text, _) in resultados:
        text = text.replace(" ", "").upper()
        if 6 <= len(text) <= 7: return text
    return None

# --- 3. Interfaz Principal ---
st.title("📸 ISAAC - Agente de Campo")

# Interruptor de LPR
lpr_activo = st.toggle("Activar LPR (IA)", value=False)
marca = st.text_input("Ingresar Marca/Modelo (Opcional):")
foto = st.camera_input("Capturar vehículo")

if foto:
    patente = None
    if lpr_activo:
        with st.spinner("Procesando IA..."):
            patente = procesar_lpr(foto)
    
    if st.button("Confirmar y Enviar"):
        try:
            sh = conectar_sheets()
            # Si hay patente, ruteamos a REGISTRO_LPR, sino a MULTAS (o según tu necesidad)
            estado = "MULTAR" if not patente else "OK"
            hoja = sh.worksheet("MULTAS") if estado == "MULTAR" else sh.worksheet("REGISTRO_LPR")
            
            fila = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), patente or "N/A", marca, "0.0", "0.0", estado]
            hoja.append_row(fila)
            
            st.success(f"✅ Enviado a {hoja.title}")
        except Exception as e:
            st.error(f"Error: {e}")

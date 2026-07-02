import streamlit as st
import easyocr
import cv2
import numpy as np
from PIL import Image
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

# --- 1. CONFIGURACIÓN ---
@st.cache_resource
def cargar_ocr():
    return easyocr.Reader(['es'], gpu=False)

def conectar_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive", "https://www.googleapis.com/auth/spreadsheets"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    return gspread.authorize(creds).open("ISAAC - Monitoreo")

# --- 2. LÓGICA DE PROCESAMIENTO ---
def procesar_lpr(foto):
    reader = cargar_ocr()
    img = Image.open(foto)
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
    resultados = reader.readtext(thresh)
    for (_, text, _) in resultados:
        text = text.replace(" ", "").upper()
        if 6 <= len(text) <= 7: return text
    return None

# --- 3. INTERFAZ (AGENTE) ---
st.title("📸 ISAAC - Agente de Campo")

# Interruptor de IA
lpr_activo = st.toggle("Activar LPR (IA)", value=False)
tipo_registro = st.radio("Seleccionar tipo de registro:", ["Control LPR", "Multa Infracción"])

foto = st.camera_input("Capturar vehículo")

if foto:
    patente = None
    if lpr_activo:
        with st.spinner("Procesando IA..."):
            patente = procesar_lpr(foto)
            st.success(f"Patente detectada: {patente or 'No detectada'}")
    
    patente_manual = st.text_input("Patente (editar/ingresar):", value=patente if patente else "")
    marca = st.text_input("Ingresar Marca/Modelo:")
    
    if st.button("Confirmar y Enviar"):
        try:
            sh = conectar_sheets()
            # Ruteo independiente
            hoja = sh.worksheet("MULTAS") if tipo_registro == "Multa Infracción" else sh.worksheet("REGISTRO_LPR")
            
            fila = [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), patente_manual, marca, "0.0", "0.0", "VALIDADO"]
            hoja.append_row(fila)
            st.success(f"✅ Enviado a pestaña: {hoja.title}")
        except Exception as e:
            st.error(f"Error: {e}")

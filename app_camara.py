import streamlit as st
from datetime import datetime

st.title("📸 ISAAC - Prueba de Captura en Vivo")

# Componente nativo de Streamlit para acceder a la cámara (móvil o PC)
foto_capturada = st.camera_input("Enfocar objetivo (Patente / Vehículo)")

if foto_capturada is not None:
    st.success("¡Imagen capturada exitosamente!")
    
    # Mostramos detalles técnicos simulados del disparo
    st.text(f"Sello de Tiempo: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    st.text("Resolución: Optimizada para LPR móvil")
    
    # Aquí es donde posteriormente conectarás tu motor OCR/LPR 
    # st.info("Procesando imagen mediante motor OCR local...")
    
    with st.spinner("Simulando análisis de matrícula..."):
        # En una fase posterior, el resultado de la cámara se enviaría aletoriamente a leer
        pass

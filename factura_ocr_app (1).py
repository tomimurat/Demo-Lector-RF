
import streamlit as st
from PIL import Image
import pytesseract
import pandas as pd
import os

st.set_page_config(page_title="Lector de Facturas", layout="centered")
st.title("📄 Lector Inteligente de Facturas")

pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
uploaded_file = st.file_uploader("Subí una imagen de la factura", type=["jpg", "png", "jpeg", "pdf"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Factura cargada", use_container_width=True)
    
    with st.spinner("🧠 Procesando la imagen..."):
        text = pytesseract.image_to_string(image)
        st.subheader("📝 Texto reconocido:")
        st.text(text)

        # Simulación de extracción de datos (se debe mejorar con regex según el formato de la factura)
        proveedor = "BIOSALUD S.R.L." if "BIOSALUD" in text.upper() else "Proveedor no identificado"
        monto = "10320"  # Podés reemplazar con una expresión regular que busque el monto
        fecha_compra = "2024-04-15"  # Idem
        fecha_vencimiento = "2024-05-15"  # Depende del proveedor
        sucursal = st.selectbox("Seleccioná la sucursal", ["Sucursal 1", "Sucursal 2", "Sucursal 3"])

        # Mostrar datos extraídos
        st.markdown("### ✅ Datos extraídos")
        st.write(f"**Proveedor:** {proveedor}")
        st.write(f"**Monto:** {monto}")
        st.write(f"**Fecha de compra:** {fecha_compra}")
        st.write(f"**Fecha de vencimiento:** {fecha_vencimiento}")
        st.write(f"**Sucursal:** {sucursal}")

        if st.button("📥 Guardar en CSV"):
            datos = {
                "Proveedor": [proveedor],
                "Monto": [monto],
                "Fecha de compra": [fecha_compra],
                "Fecha de vencimiento": [fecha_vencimiento],
                "Sucursal": [sucursal]
            }

            archivo_csv = "facturas_procesadas.csv"

            if os.path.exists(archivo_csv):
                df_existente = pd.read_csv(archivo_csv)
                df_nuevo = pd.DataFrame(datos)
                df_final = pd.concat([df_existente, df_nuevo], ignore_index=True)
            else:
                df_final = pd.DataFrame(datos)

            df_final.to_csv(archivo_csv, index=False)
            st.success("📁 Datos guardados correctamente en 'facturas_procesadas.csv'")

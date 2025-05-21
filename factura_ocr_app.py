
import streamlit as st
import pytesseract
from PIL import Image
from datetime import datetime
from io import BytesIO
import pandas as pd

st.set_page_config(page_title="Lector de Facturas", layout="wide")
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"


st.title("📄 Lector Inteligente de Facturas")
st.write("Subí una imagen de una factura para extraer los datos automáticamente.")

uploaded_file = st.file_uploader("Subir factura (imagen)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Factura subida", use_container_width=True)

    with st.spinner("Procesando imagen con OCR..."):
        text = pytesseract.image_to_string(image)

    # Muestra de texto extraído (debug)
    if st.checkbox("Mostrar texto completo extraído (OCR)"):
        st.text_area("Texto extraído:", text, height=300)

    # Extracción de datos clave
    proveedor = "Bio-Salud S.R.L." if "BIO-SALUD S.R.L." in text.upper() else "Desconocido"
    monto = ""
    fecha_compra = ""
    fecha_vencimiento = ""
    sucursal = ""

    # Buscar monto total
    for line in text.splitlines():
        if "Total" in line and any(char.isdigit() for char in line):
            partes = line.split()
            for parte in partes[::-1]:
                try:
                    monto = float(parte.replace(",", "").replace(".", "", parte.count(".") - 1))
                    break
                except:
                    continue
            if monto:
                break

    # Buscar fechas
    for line in text.splitlines():
        if "Fecha" in line and "/" in line:
            posibles_fechas = [word for word in line.split() if "/" in word]
            for f in posibles_fechas:
                try:
                    fecha = datetime.strptime(f, "%d/%m/%Y")
                    if "compra" not in fecha_compra:
                        fecha_compra = fecha
                    elif "vencimiento" not in fecha_vencimiento:
                        fecha_vencimiento = fecha
                except:
                    continue

    # Buscar sucursal
    for line in text.splitlines():
        if "5105" in line or "Villa Allende" in line:
            sucursal = line.strip()

    # Cálculo de días restantes
    dias_restantes = ""
    if isinstance(fecha_vencimiento, datetime):
        dias_restantes = (fecha_vencimiento - datetime.today()).days

    # Mostrar resultados
    st.subheader("📌 Datos extraídos")
    st.write({
        "Proveedor": proveedor,
        "Monto total": monto,
        "Fecha de compra": fecha_compra.strftime("%d/%m/%Y") if fecha_compra else "No detectada",
        "Fecha de vencimiento": fecha_vencimiento.strftime("%d/%m/%Y") if fecha_vencimiento else "No detectada",
        "Días restantes": dias_restantes,
        "Sucursal": sucursal
    })

    # Guardar como CSV temporal si se desea
    if st.button("💾 Guardar como CSV"):
        df = pd.DataFrame([{
            "Proveedor": proveedor,
            "Monto total": monto,
            "Fecha de compra": fecha_compra.strftime("%d/%m/%Y") if fecha_compra else "",
            "Fecha de vencimiento": fecha_vencimiento.strftime("%d/%m/%Y") if fecha_vencimiento else "",
            "Días restantes": dias_restantes,
            "Sucursal": sucursal
        }])
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descargar CSV", data=csv, file_name="factura_extraida.csv", mime="text/csv")

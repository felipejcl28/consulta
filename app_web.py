# -*- coding: utf-8 -*-
"""
Created on Fri Aug 29 16:11:15 2025
@author: felipe jaramillo"""

import os
import streamlit as st
import pandas as pd
from PIL import Image
import unicodedata
from io import BytesIO


RUTA_EXCEL = os.path.join(os.getcwd(), "personas.xlsx")
RUTA_IMAGENES = os.path.join(os.getcwd(), "IMAGENES")


def normalizar_texto(texto: str) -> str:
    
    if not isinstance(texto, str):
        return ""
    texto = texto.strip().lower()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto

def exportar_excel(df: pd.DataFrame) -> BytesIO:

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()


if not os.path.exists(RUTA_EXCEL):
    st.error(f"❌ No se encontró el archivo Excel en {RUTA_EXCEL}")
    st.stop()

df = pd.read_excel(RUTA_EXCEL)


df["NOMBRE_NORM"] = df["NOMBRE"].apply(normalizar_texto)
df["ID_NORM"] = df["ID"].astype(str).apply(normalizar_texto)  


st.set_page_config(page_title="Consulta Personas", page_icon="🔎", layout="centered")
st.title("🔎 CONSULTA PERSONAS")


criterio = st.selectbox("Buscar por:", ["NOMBRE", "ID"])
query = st.text_input(f"Ingrese {criterio}:")

if st.button("Buscar"):
    query_norm = normalizar_texto(query)

    if criterio == "NOMBRE":
     
        resultados = df[df["NOMBRE_NORM"].str.contains(query_norm, na=False)]
    else:  
        resultados = df[df["ID_NORM"].str.contains(query_norm, na=False)]

    if resultados.empty:
        st.warning("⚠️ No se encontraron resultados")
    else:
        st.success(f"✅ {len(resultados)} resultado(s) encontrado(s)")
        for _, row in resultados.iterrows():
            with st.container():
                cols = st.columns([1, 2])
                with cols[0]:
                    foto_nombre = str(row.get("IMAGEN", "")).strip()
                    foto_path = os.path.join(RUTA_IMAGENES, foto_nombre)

                if os.path.exists(foto_path) and foto_nombre:
                    st.image(Image.open(foto_path), width=250, caption=row["NOMBRE"])
                else:
                    st.warning(f"No se encontró la imagen: {foto_nombre}")
                with cols[1]:
                    st.markdown(f"""
                        <div style="background:#f9f9f9;padding:10px;border-radius:10px;">
                        <p><b>👤 Nombre:</b> {row.get("NOMBRE", "")}</p>
                        <p><b>🆔 ID:</b> {row.get("ID", "")}</p>
                        <p><b>🏙 Municipio:</b> {row.get("MUNICIPIO ", "")}</p>
                        <p><b>🔢 NUNC:</b> {row.get("NUNC", "")}</p>
                        </div>
                    """, unsafe_allow_html=True)

       
        resultados_export = resultados.drop(columns=["NOMBRE_NORM", "ID_NORM"], errors="ignore")
        excel_data = exportar_excel(resultados_export)
        st.download_button(
            label="⬇️ Descargar resultados",
            data=excel_data,
            file_name="resultados_texto.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )






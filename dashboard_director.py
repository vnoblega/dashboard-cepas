import streamlit as st
import pandas as pd
import plotly.express as px
import os

import requests
import io

st.set_page_config(page_title="Panel General CEPAS", layout="wide", page_icon="📝")

# ID mágico de tu archivo en Google Drive (es el código largo del enlace que pasaste)
GOOGLE_DRIVE_FILE_ID = "15X1CpkuIjZ1JPkJo-yWhwLo6PRF_EhSV"
URL_DESCARGA = f"https://drive.google.com/uc?export=download&id={GOOGLE_DRIVE_FILE_ID}"

@st.cache_data(ttl=600) # Se actualiza cada 10 minutos
def cargar_datos():
    try:
        # Streamlit descarga silenciosamente tu excel desde Google Drive en memoria
        headers = {"User-Agent": "Mozilla/5.0"}
        respuesta = requests.get(URL_DESCARGA, headers=headers)
        
        if respuesta.status_code == 200:
            bytes_data = io.BytesIO(respuesta.content)
            df = pd.read_excel(bytes_data, sheet_name="2_BASE_CONCENTRADA")
            return df
        else:
            return None
    except Exception as e:
        st.error(f"Error técnico conectando a Google Drive: {e}")
        return None

# --- ENCBAEZADO ---
st.title("🖥️ Tablero de Dirección - CEPAS 2026")
st.markdown("Monitor analítico general para directivos. Se nutre de los reportes diarios de todos los centros.")

df = cargar_datos()

if df is not None:
    # --- BARRA LATERAL (Filtros) ---
    st.sidebar.header("Menú Interactivo")
    st.sidebar.markdown("Filtra todos los gráficos al instante")
    
    lista_centros = ["Todas las Sedes"] + list(df['Centro_Origen'].dropna().unique())
    centro_elegido = st.sidebar.selectbox("1. Seleccione Centro/Departamento:", lista_centros)
    
    if centro_elegido != "Todas las Sedes":
        df_filtrado = df[df['Centro_Origen'] == centro_elegido]
    else:
        df_filtrado = df.copy()

    # --- FILTRO 2: OFERTA ---
    if 'Oferta Seleccionada' in df_filtrado.columns:
        lista_ofertas = ["Todas las Ofertas"] + list(df_filtrado['Oferta Seleccionada'].dropna().unique())
        oferta_elegida = st.sidebar.selectbox("2. Filtrar por Oferta:", lista_ofertas)
        
        if oferta_elegida != "Todas las Ofertas":
            df_filtrado = df_filtrado[df_filtrado['Oferta Seleccionada'] == oferta_elegida]

    # --- TARJETAS METRICAS ---
    st.markdown("### 📊 Indicadores Clave")
    c1, c2, c3 = st.columns(3)
    
    c1.metric("Preinscriptos Registrados", f"{len(df_filtrado)} alumnos")
    
    col_estado = "Estado Actual (Cursando / No Cursa)"
    if col_estado in df_filtrado.columns:
        cursando = len(df_filtrado[df_filtrado[col_estado] == "Cursando"])
        c2.metric("🟢 Actualmente Cursando", cursando)
        no_cursa = len(df_filtrado[df_filtrado[col_estado] == "No Cursa"])
        c3.metric("🔴 No Cursa", no_cursa)

    st.markdown("---")
    
    # --- PESTAÑAS DE GRAFICOS ---
    tab1, tab2 = st.tabs(["🌎 Distribución de Alumnos y Ofertas", "📈 Reportes de Gestión a Futuro"])
    
    with tab1:
        graf_col1, graf_col2 = st.columns(2)
        
        with graf_col1:
            st.subheader("Por Sede Geográfica")
            if centro_elegido == "Todas las Sedes":
                conteos_dept = df_filtrado['Centro_Origen'].value_counts().reset_index()
                conteos_dept.columns = ['Sede', 'Cantidad']
                fig_torta = px.pie(conteos_dept, values='Cantidad', names='Sede', hole=0.4,
                                   color_discrete_sequence=px.colors.sequential.Plotly3)
                st.plotly_chart(fig_torta, use_container_width=True)
            else:
                st.info(f"Visualizando el 100% de la sede: {centro_elegido}.")

        with graf_col2:
            st.subheader("Por Oferta Cursada")
            if 'Oferta Seleccionada' in df_filtrado.columns:
                conteos_of = df_filtrado['Oferta Seleccionada'].value_counts().reset_index()
                conteos_of.columns = ['Oferta', 'Cantidad']
                fig_torta_of = px.pie(conteos_of, values='Cantidad', names='Oferta', hole=0.4,
                                      color_discrete_sequence=px.colors.sequential.Teal)
                st.plotly_chart(fig_torta_of, use_container_width=True)

    with tab2:
        st.subheader("Control de Trayectoria y Estado")
        if col_estado in df_filtrado.columns:
            estado_agrupado = df_filtrado[col_estado].value_counts().reset_index()
            estado_agrupado.columns = ['Estado', 'Alumnos']
            fig_barra = px.bar(estado_agrupado, x='Estado', y='Alumnos', color='Estado',
                               color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_barra, use_container_width=True)
        else:
            st.info("Columna de gestión no encontrada.")

    # --- TABLA CRUDA ---
    st.markdown("### 📋 Vista Detalles de Alumnos")
    st.dataframe(df_filtrado, use_container_width=True, hide_index=True)
else:
    st.warning(f"¡Atención! No encontré el archivo `{ARCHIVO_DATOS}` local. Ejecuta tu script principal primero para fabricarlo.")

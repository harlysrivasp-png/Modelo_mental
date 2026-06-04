# ==========================================
# APP PRINCIPAL
# MODELOS MENTALES DE CONCIENCIA AMBIENTAL
# ==========================================

import streamlit as st
import pandas as pd

from modulos.sunburst import crear_sunburst
from modulos.radar import crear_radar
from modulos.heatmap import crear_heatmap
from modulos.wordcloud import crear_wordcloud
from modulos.informe import generar_informe
from modulos.exportar_word import generar_word
from modulos.sankey import crear_sankey


# ==========================================
# CONFIGURACIÓN
# ==========================================

st.set_page_config(
    page_title="Modelos Mentales",
    page_icon="🌿",
    layout="wide"
)

# ==========================================
# TÍTULO
# ==========================================

st.title(
    "🌿 Evolución de los Modelos Mentales de Conciencia Ambiental"
)

st.markdown("---")

# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.header("Configuración")

estudiante = st.sidebar.selectbox(
    "Seleccione estudiante",
    [
        "E01",
        "E02",
        "E03",
        "E04",
        "E05"
    ]
)

# ==========================================
# CARGAR ARCHIVO
# ==========================================

archivo_excel = f"datos/{estudiante}.xlsx"

try:

    df = pd.read_excel(archivo_excel)

    st.success(
        f"Archivo cargado correctamente: {archivo_excel}"
    )

except Exception as e:

    st.error(
        f"Error al cargar el archivo: {e}"
    )

    st.stop()
# ==========================================
# VALIDACIÓN DE COLUMNAS
# ==========================================

columnas_obligatorias = [
    "Fase",
    "Categoría",
    "Subcategoría",
    "Código"
]

faltantes = [
    col
    for col in columnas_obligatorias
    if col not in df.columns
]

if faltantes:

    st.error(
        f"Faltan columnas obligatorias: {faltantes}"
    )

    st.stop()

    # ==========================================
# FILTRO DE CATEGORÍA
# ==========================================

categoria_filtro = st.sidebar.selectbox(
    "Filtrar Categoría",
    ["Todas"] + sorted(
        df["Categoría"]
        .dropna()
        .unique()
    )
)
# ==========================================
# FILTRAR DATOS
# ==========================================

df_filtrado = df.copy()

if categoria_filtro != "Todas":

    df_filtrado = df[
        df["Categoría"]
        == categoria_filtro
    ]
# ==========================================
# COLUMNAS DE CITAS
# ==========================================

cols_cita = [

    col

    for col in df.columns

    if "cita" in col.lower()

]

# ==========================================
# FASES
# ==========================================

fases = sorted(
    df["Fase"]
    .dropna()
    .unique()
)

# ==========================================
# MAPA DE COLORES
# ==========================================

color_map = {

    "EP": "#1f77b4",   # Azul
    "ON": "#ff7f0e",   # Naranja
    "CL": "#2ca02c",   # Verde
    "MT": "#d62728"    # Rojo

}

# ==========================================
# INFORMACIÓN DEL ARCHIVO
# ==========================================

with st.expander("📋 Ver columnas del archivo"):

    st.write(df.columns.tolist())

with st.expander("📊 Ver primeras filas"):

    st.dataframe(df.head())

# ==========================================
# VERIFICACIÓN
# ==========================================

st.subheader("Información detectada")

col1, col2, col3 = st.columns(3)

with col1:

    st.write("Fases")

    st.write(fases)

with col2:

    st.write("Categorías")

    st.write(
        sorted(
            df["Categoría"]
            .dropna()
            .unique()
        )
    )

with col3:

    st.write("Columnas de citas")

    st.write(cols_cita)

# ==========================================
# MUESTRA DE DATOS
# ==========================================

st.subheader("Muestra real de datos")

columnas_mostrar = [

    "Fase",
    "Categoría",
    "Subcategoría",
    "Código"

] + cols_cita

st.dataframe(
    df[columnas_mostrar].head(15)
)

# ==========================================
# SUNBURST
# ==========================================

st.markdown("---")

st.subheader("🌳 Sunburst")

try:

    fig_sunburst = crear_sunburst(

        df=df,
        fases=fases,
        cols_cita=cols_cita,
        color_map=color_map,
        titulo=f"Modelo Mental - {estudiante}"

    )

    st.plotly_chart(
        fig_sunburst,
        use_container_width=True
    )

except Exception as e:

    st.error(
        f"Error en Sunburst: {e}"
    )
# ======================================
# SANKEY EVOLUTIVO
# ======================================

st.subheader(
    "🔄 Evolución del Modelo Mental"
)

fig_sankey = crear_sankey(df)

st.plotly_chart(
    fig_sankey,
    use_container_width=True
)
# ==========================================
# RADAR
# ==========================================

st.markdown("---")

st.subheader(
    "📡 Evolución de Categorías (Radar)"
)

try:

    fig_radar = crear_radar(df)

    st.plotly_chart(
        fig_radar,
        use_container_width=True
    )

except Exception as e:

    st.error(
        f"Error Radar: {e}"
    )

# ==========================================
# HEATMAP
# ==========================================

st.markdown("---")

st.subheader(
    "🔥 Mapa de Calor de Categorías"
)

try:

    fig_heatmap = crear_heatmap(df)

    st.plotly_chart(
        fig_heatmap,
        use_container_width=True
    )

except Exception as e:

    st.error(
        f"Error Heatmap: {e}"
    )

# ==========================================
# WORD CLOUD
# ==========================================

st.markdown("---")

st.subheader(
    "☁️ Nube de Palabras"
)

try:

    fig_wordcloud = crear_wordcloud(
        df,
        cols_cita
    )

    if fig_wordcloud:

        st.pyplot(
            fig_wordcloud
        )

    else:

        st.warning(
            "No se encontraron citas para generar la nube de palabras."
        )

except Exception as e:

    st.error(
        f"Error WordCloud: {e}"
    )

# ==========================================
# INFORME COMPARATIVO
# ==========================================

st.markdown("---")

st.subheader("📘 Informe Comparativo")

try:
    informe = generar_informe(df)

    st.text_area(
        "Resultados",
        informe,
        height=600
    )

    # ==========================================
    # DESCARGAR INFORME WORD
    # ==========================================

    archivo_word = generar_word(
        estudiante,
        informe
    )

    st.download_button(
        label="📄 Descargar Informe en Word",
        data=archivo_word,
        file_name=f"Informe_{estudiante}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

except Exception as e:
    st.error(
        f"Error Informe: {e}"
    )
# ==========================================
# MÉTRICAS
# ==========================================

st.markdown("---")

st.subheader("Resumen")

m1, m2, m3 = st.columns(3)

with m1:

    st.metric(
        "Registros",
        len(df)
    )

with m2:

    st.metric(
        "Columnas",
        len(df.columns)
    )

with m3:

    st.metric(
        "Fases",
        len(fases)
    )

# ==========================================
# PIE DE PÁGINA
# ==========================================

st.markdown("---")

st.caption(
    "Proyecto de Investigación - Evolución de los Modelos Mentales de Conciencia Ambiental"
)
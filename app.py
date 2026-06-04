# ==========================================
# APP PRINCIPAL
# MODELOS MENTALES DE CONCIENCIA AMBIENTAL
# ==========================================

import streamlit as st
import pandas as pd
import os

from modulos.sunburst import crear_sunburst
from modulos.radar import crear_radar
from modulos.heatmap import crear_heatmap
from modulos.wordcloud import crear_wordcloud
from modulos.informe import generar_informe
from modulos.exportar_word import generar_word
from modulos.sankey import crear_sankey
from modulos.wordcloud import crear_wordcloud

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
# DOCUMENTOS ATLAS.ti POR ESTUDIANTE Y FASE
# ==========================================

st.markdown("---")

st.subheader("📄 Documentos ATLAS.ti por estudiante y fase")

st.markdown("""
Esta sección permite consultar y descargar los documentos utilizados en ATLAS.ti
para cada estudiante y para cada fase del análisis.
""")

ruta_base_documentos = "documentos"

ruta_documentos_estudiante = os.path.join(
    ruta_base_documentos,
    estudiante
)

if not os.path.exists(ruta_documentos_estudiante):

    st.warning(
        f"No se encontró la carpeta de documentos para el estudiante {estudiante}. "
        f"Verifique que exista la ruta: {ruta_documentos_estudiante}"
    )

else:

    fases_documentos = {
        "FASE 1": ["FASE1", "Fase1", "fase1", "FASE_1", "fase_1"],
        "FASE 2": ["FASE2", "Fase2", "fase2", "FASE_2", "fase_2"],
        "FASE 3": ["FASE3", "Fase3", "fase3", "FASE_3", "fase_3"]
    }

    tab_doc1, tab_doc2, tab_doc3 = st.tabs(
        [
            "Documentos FASE 1",
            "Documentos FASE 2",
            "Documentos FASE 3"
        ]
    )

    tabs_documentos = {
        "FASE 1": tab_doc1,
        "FASE 2": tab_doc2,
        "FASE 3": tab_doc3
    }

    for nombre_fase, tab in tabs_documentos.items():

        with tab:

            st.markdown(
                f"### Documentos usados en {nombre_fase} - {estudiante}"
            )

            carpeta_fase_encontrada = None

            for nombre_carpeta in fases_documentos[nombre_fase]:

                ruta_fase = os.path.join(
                    ruta_documentos_estudiante,
                    nombre_carpeta
                )

                if os.path.exists(ruta_fase):
                    carpeta_fase_encontrada = ruta_fase
                    break

            if carpeta_fase_encontrada is None:

                st.warning(
                    f"No se encontró carpeta de documentos para {nombre_fase} "
                    f"del estudiante {estudiante}."
                )

            else:

                archivos = sorted([
                    archivo for archivo in os.listdir(carpeta_fase_encontrada)
                    if os.path.isfile(
                        os.path.join(carpeta_fase_encontrada, archivo)
                    )
                ])

                if len(archivos) == 0:

                    st.info(
                        f"No hay documentos cargados en {nombre_fase} "
                        f"para {estudiante}."
                    )

                else:

                    st.success(
                        f"Se encontraron {len(archivos)} documentos."
                    )

                    with st.expander("Ver lista de documentos encontrados"):
                        st.write(archivos)

                    # ==========================================
                    # MOSTRAR DOCUMENTOS EN FILAS DE 3 COLUMNAS
                    # ==========================================

                    num_columnas = 3

                    for inicio in range(0, len(archivos), num_columnas):

                        fila_archivos = archivos[
                            inicio:inicio + num_columnas
                        ]

                        columnas_docs = st.columns(num_columnas)

                        for idx, archivo in enumerate(fila_archivos):

                            ruta_archivo = os.path.join(
                                carpeta_fase_encontrada,
                                archivo
                            )

                            with columnas_docs[idx]:

                                st.markdown(
                                    f"""
                                    <div style="
                                        border: 1px solid #D9D9D9;
                                        border-radius: 10px;
                                        padding: 12px;
                                        margin-bottom: 8px;
                                        background-color: #F8F9FA;
                                        min-height: 90px;
                                        font-size: 14px;
                                        word-wrap: break-word;
                                    ">
                                        <b>📎 {archivo}</b>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                                try:
                                    with open(ruta_archivo, "rb") as f:
                                        contenido = f.read()

                                    st.download_button(
                                        label="Descargar",
                                        data=contenido,
                                        file_name=archivo,
                                        mime="application/octet-stream",
                                        key=(
                                            f"doc_{estudiante}_"
                                            f"{nombre_fase}_"
                                            f"{inicio}_{idx}_{archivo}"
                                        )
                                    )

                                except Exception as e:
                                    st.error(
                                        f"No se pudo cargar el documento "
                                        f"{archivo}: {e}"
                                    )
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

    # ==========================================
# REDES ATLAS.ti POR ESTUDIANTE Y FASE
# ==========================================

st.markdown("---")

st.subheader("🧠 Redes ATLAS.ti por estudiante y fase")

st.markdown("""
Esta sección presenta las redes cualitativas generadas en ATLAS.ti
para cada estudiante y para cada fase del análisis del modelo mental ambiental.
Las redes permiten visualizar las relaciones entre categorías, subcategorías,
códigos y vínculos semánticos.
""")

ruta_base_imagenes = "images"

ruta_estudiante = os.path.join(
    ruta_base_imagenes,
    estudiante
)

if not os.path.exists(ruta_estudiante):

    st.warning(
        f"No se encontró la carpeta de imágenes para el estudiante {estudiante}. "
        f"Verifique que exista la ruta: {ruta_estudiante}"
    )

else:

    fases_imagenes = {
        "FASE 1": [
            "FASE1.jpg",
            "Fase1.jpg",
            "fase1.jpg",
            "FASE_1.jpg",
            "fase_1.jpg"
        ],
        "FASE 2": [
            "FASE2.jpg",
            "Fase2.jpg",
            "fase2.jpg",
            "FASE_2.jpg",
            "fase_2.jpg"
        ],
        "FASE 3": [
            "FASE3.jpg",
            "Fase3.jpg",
            "fase3.jpg",
            "FASE_3.jpg",
            "fase_3.jpg"
        ]
    }

    tab_fase1, tab_fase2, tab_fase3 = st.tabs(
        [
            "FASE 1",
            "FASE 2",
            "FASE 3"
        ]
    )

    tabs_redes = {
        "FASE 1": tab_fase1,
        "FASE 2": tab_fase2,
        "FASE 3": tab_fase3
    }

    for nombre_fase, tab in tabs_redes.items():

        with tab:

            st.markdown(
                f"### Red ATLAS.ti - {nombre_fase} - {estudiante}"
            )

            imagen_encontrada = None

            for nombre_archivo in fases_imagenes[nombre_fase]:

                ruta_imagen = os.path.join(
                    ruta_estudiante,
                    nombre_archivo
                )

                if os.path.exists(ruta_imagen):
                    imagen_encontrada = ruta_imagen
                    break

            if imagen_encontrada:

                st.image(
                    imagen_encontrada,
                    caption=f"Red ATLAS.ti - {nombre_fase} - {estudiante}",
                    use_container_width=True
                )

                if nombre_fase == "FASE 1":
                    st.info(
                        "La FASE 1 permite observar la estructura inicial del modelo mental ambiental "
                        "del estudiante, evidenciando las primeras relaciones entre conocimiento ambiental, "
                        "valores, experiencias y percepción del problema ambiental."
                    )

                elif nombre_fase == "FASE 2":
                    st.info(
                        "La FASE 2 muestra la evolución de las relaciones conceptuales, con mayor articulación "
                        "entre experiencia, conocimiento, comunicación, valores ambientales y comprensión del entorno."
                    )

                elif nombre_fase == "FASE 3":
                    st.info(
                        "La FASE 3 permite identificar una organización más compleja del modelo mental, "
                        "incluyendo acciones ambientales, responsabilidad, hábitos sostenibles, contaminación, "
                        "uso de recursos y estrategias de comunicación."
                    )

            else:

                st.warning(
                    f"No se encontró imagen para {nombre_fase} del estudiante {estudiante}."
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
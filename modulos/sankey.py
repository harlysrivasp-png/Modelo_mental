import pandas as pd
import plotly.graph_objects as go
from collections import defaultdict


def acortar_texto(texto, max_len=34):
    """
    Acorta etiquetas largas para mejorar la visualización.
    El texto completo se conserva en el hover.
    """
    texto = str(texto).strip()

    if len(texto) <= max_len:
        return texto

    return texto[:max_len - 3] + "..."


def crear_sankey(df):
    # ==============================
    # Limpiar datos
    # ==============================
    df = df.copy()

    columnas_requeridas = [
        "Fase",
        "Categoría",
        "Subcategoría",
        "Código"
    ]

    for col in columnas_requeridas:
        if col not in df.columns:
            raise ValueError(f"Falta la columna requerida: {col}")

    for col in columnas_requeridas:
        df[col] = df[col].astype(str).str.strip()

    df = df[
        (df["Fase"] != "") &
        (df["Categoría"] != "") &
        (df["Subcategoría"] != "") &
        (df["Código"] != "")
    ].copy()

    fases = sorted(df["Fase"].unique())

    # ==============================
    # Crear nodos y enlaces
    # ==============================
    nodos = []
    enlaces = []

    for fase in fases:
        df_fase = df[df["Fase"] == fase]

        for _, row in df_fase.iterrows():

            categoria = f"{fase} | {row['Categoría']}"
            subcategoria = f"{fase} | {row['Subcategoría']}"
            codigo = f"{fase} | {row['Código']}"

            nodos.extend([
                categoria,
                subcategoria,
                codigo
            ])

            enlaces.append(
                (categoria, subcategoria, 1)
            )

            enlaces.append(
                (subcategoria, codigo, 1)
            )

    # ==============================
    # Evolución entre fases
    # ==============================
    for i in range(len(fases) - 1):

        fase_actual = fases[i]
        fase_siguiente = fases[i + 1]

        df_actual = df[df["Fase"] == fase_actual]
        df_sig = df[df["Fase"] == fase_siguiente]

        comunes = set(
            df_actual["Código"]
        ).intersection(
            set(df_sig["Código"])
        )

        for codigo in comunes:

            origen = f"{fase_actual} | {codigo}"
            destino = f"{fase_siguiente} | {codigo}"

            enlaces.append(
                (origen, destino, 1)
            )

    # ==============================
    # Nodos únicos
    # ==============================
    nodos = list(dict.fromkeys(nodos))

    mapa_nodos = {
        nodo: i
        for i, nodo in enumerate(nodos)
    }

    # ==============================
    # Agrupar enlaces repetidos
    # ==============================
    enlaces_agrupados = defaultdict(int)

    for s, t, v in enlaces:
        if s in mapa_nodos and t in mapa_nodos:
            enlaces_agrupados[(s, t)] += v

    source = []
    target = []
    value = []
    hover_enlaces = []

    for (s, t), v in enlaces_agrupados.items():

        source.append(mapa_nodos[s])
        target.append(mapa_nodos[t])
        value.append(v)

        hover_enlaces.append(
            f"Origen: {s}<br>Destino: {t}<br>Valor: {v}"
        )

    # ==============================
    # Clasificar nodos por nivel
    # ==============================
    tipo_nodo = {}

    categorias_validas = set()
    subcategorias_validas = set()
    codigos_validos = set()

    for fase in fases:

        df_fase = df[df["Fase"] == fase]

        for categoria in df_fase["Categoría"].dropna().unique():
            categorias_validas.add(
                f"{fase} | {categoria}"
            )

        for subcategoria in df_fase["Subcategoría"].dropna().unique():
            subcategorias_validas.add(
                f"{fase} | {subcategoria}"
            )

        for codigo in df_fase["Código"].dropna().unique():
            codigos_validos.add(
                f"{fase} | {codigo}"
            )

    for nodo in nodos:

        if nodo in categorias_validas:
            tipo_nodo[nodo] = "categoria"

        elif nodo in subcategorias_validas:
            tipo_nodo[nodo] = "subcategoria"

        elif nodo in codigos_validos:
            tipo_nodo[nodo] = "codigo"

        else:
            tipo_nodo[nodo] = "otro"

    nodos_categoria = [
        n for n in nodos
        if tipo_nodo[n] == "categoria"
    ]

    nodos_subcategoria = [
        n for n in nodos
        if tipo_nodo[n] == "subcategoria"
    ]

    nodos_codigo = [
        n for n in nodos
        if tipo_nodo[n] == "codigo"
    ]

    def posiciones_verticales(lista):
        """
        Distribuye los nodos verticalmente.
        """
        n = len(lista)

        if n == 0:
            return {}

        if n == 1:
            return {
                lista[0]: 0.5
            }

        return {
            nodo: 0.02 + i * (0.96 / (n - 1))
            for i, nodo in enumerate(lista)
        }

    y_categoria = posiciones_verticales(nodos_categoria)
    y_subcategoria = posiciones_verticales(nodos_subcategoria)
    y_codigo = posiciones_verticales(nodos_codigo)

    # ==============================
    # Posiciones fijas
    # ==============================
    x_pos = []
    y_pos = []

    for nodo in nodos:

        if tipo_nodo[nodo] == "categoria":

            x_pos.append(0.03)
            y_pos.append(y_categoria[nodo])

        elif tipo_nodo[nodo] == "subcategoria":

            x_pos.append(0.36)
            y_pos.append(y_subcategoria[nodo])

        elif tipo_nodo[nodo] == "codigo":

            x_pos.append(0.72)
            y_pos.append(y_codigo[nodo])

        else:

            x_pos.append(0.50)
            y_pos.append(0.50)

    # ==============================
    # Colores de nodos
    # ==============================
    colores_nodos = []

    for nodo in nodos:

        if "EP" in nodo:
            colores_nodos.append("#1565C0")  # Azul

        elif "ON" in nodo:
            colores_nodos.append("#F39C12")  # Naranja

        elif "CL" in nodo:
            colores_nodos.append("#2E7D32")  # Verde

        elif "MT" in nodo:
            colores_nodos.append("#C62828")  # Rojo

        else:
            colores_nodos.append("#8E44AD")  # Morado

    colores_enlaces = [
        "rgba(180,180,180,0.25)"
        for _ in source
    ]

    # ==============================
    # Etiquetas para anotaciones
    # ==============================
    etiquetas_cortas = []

    for nodo in nodos:

        if " | " in nodo:
            fase, texto = nodo.split(" | ", 1)
            etiqueta = f"{fase} | {acortar_texto(texto, 34)}"

        else:
            etiqueta = acortar_texto(nodo, 34)

        etiquetas_cortas.append(etiqueta)

    # ==============================
    # Crear figura Sankey
    # Importante:
    # label vacío para evitar la sombra nativa de Plotly
    # ==============================
    fig = go.Figure(
        go.Sankey(
            arrangement="fixed",
            valueformat=".0f",

            node=dict(
                pad=45,
                thickness=16,

                line=dict(
                    color="rgba(40,40,40,0.35)",
                    width=0.4
                ),

                label=[
                    ""
                    for _ in nodos
                ],

                color=colores_nodos,
                x=x_pos,
                y=y_pos,

                customdata=nodos,

                hovertemplate=(
                    "<b>%{customdata}</b>"
                    "<extra></extra>"
                )
            ),

            link=dict(
                source=source,
                target=target,
                value=value,
                color=colores_enlaces,
                customdata=hover_enlaces,

                hovertemplate=(
                    "%{customdata}"
                    "<extra></extra>"
                )
            )
        )
    )

    # ==============================
    # Agregar etiquetas como anotaciones simples
    # Sin sombra, sin borde, sin relleno
    # ==============================
    anotaciones = []

    for i, nodo in enumerate(nodos):

        x = x_pos[i]
        y = y_pos[i]

        etiqueta = etiquetas_cortas[i]

        # Ubicar texto un poco a la derecha del nodo
        x_texto = x + 0.018

        if x_texto > 0.96:
            x_texto = x - 0.018
            xanchor = "right"
        else:
            xanchor = "left"

        anotaciones.append(
            dict(
                x=x_texto,
                y=y,
                xref="paper",
                yref="paper",
                text=etiqueta,
                showarrow=False,
                xanchor=xanchor,
                yanchor="middle",

                font=dict(
                    family="Arial",
                    size=12,
                    color="#111111"
                ),

                align="left",

                #bgcolor="rgba(255,255,255,0.70)",
                bgcolor="rgba(255,255,255,0.85)"
                bordercolor="rgba(255,255,255,0)",
                borderwidth=0,
                borderpad=1
            )
        )

    # ==============================
    # Layout
    # ==============================
    fig.update_layout(
        title=dict(
            text="Evolución del Modelo Mental de Conciencia Ambiental",
            x=0.5,
            xanchor="center",

            font=dict(
                family="Arial",
                size=24,
                color="#111111"
            )
        ),

        width=2200,
        height=1400,

        font=dict(
            family="Arial",
            size=12,
            color="#111111"
        ),

        margin=dict(
            l=40,
            r=40,
            t=90,
            b=40
        ),

        paper_bgcolor="white",
        plot_bgcolor="white",

        annotations=anotaciones
    )

    return fig
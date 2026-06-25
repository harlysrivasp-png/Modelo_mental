import pandas as pd
import plotly.graph_objects as go
from collections import defaultdict


def acortar_texto(texto, max_len=34):
    """
    Shortens long labels to improve Sankey readability.
    The full text is preserved in the hover information.
    """
    texto = str(texto).strip()
    if len(texto) <= max_len:
        return texto
    return texto[:max_len - 3] + "..."


def crear_sankey(df):
    # ==============================
    # Clean data
    # ==============================
    df = df.copy()

    columnas_requeridas = ["Fase", "Categoría", "Subcategoría", "Código"]
    for col in columnas_requeridas:
        if col not in df.columns:
            raise ValueError(f"Falta la columna requerida: {col}")

    df["Fase"] = df["Fase"].astype(str).str.strip()
    df["Categoría"] = df["Categoría"].astype(str).str.strip()
    df["Subcategoría"] = df["Subcategoría"].astype(str).str.strip()
    df["Código"] = df["Código"].astype(str).str.strip()

    # Remove empty rows
    df = df[
        (df["Fase"] != "") &
        (df["Categoría"] != "") &
        (df["Subcategoría"] != "") &
        (df["Código"] != "")
    ].copy()

    # ==============================
    # Create nodes and links
    # ==============================
    nodos = []
    enlaces = []

    fases = sorted(df["Fase"].unique())

    for fase in fases:
        df_fase = df[df["Fase"] == fase]

        for _, row in df_fase.iterrows():
            categoria = f"{fase} | {row['Categoría']}"
            subcategoria = f"{fase} | {row['Subcategoría']}"
            codigo = f"{fase} | {row['Código']}"

            nodos.extend([categoria, subcategoria, codigo])

            enlaces.append((categoria, subcategoria, 1))
            enlaces.append((subcategoria, codigo, 1))

    # ==============================
    # Evolution between phases
    # Same code appearing in consecutive phases
    # ==============================
    for i in range(len(fases) - 1):
        fase_actual = fases[i]
        fase_siguiente = fases[i + 1]

        df_actual = df[df["Fase"] == fase_actual]
        df_sig = df[df["Fase"] == fase_siguiente]

        comunes = set(df_actual["Código"]).intersection(set(df_sig["Código"]))

        for codigo in comunes:
            origen = f"{fase_actual} | {codigo}"
            destino = f"{fase_siguiente} | {codigo}"
            enlaces.append((origen, destino, 1))

    # ==============================
    # Remove duplicate nodes
    # ==============================
    nodos = list(dict.fromkeys(nodos))

    mapa_nodos = {nodo: i for i, nodo in enumerate(nodos)}

    # ==============================
    # Group repeated links
    # ==============================
    enlaces_agrupados = defaultdict(int)

    for s, t, v in enlaces:
        if s in mapa_nodos and t in mapa_nodos:
            enlaces_agrupados[(s, t)] += v

    source = []
    target = []
    value = []

    for (s, t), v in enlaces_agrupados.items():
        source.append(mapa_nodos[s])
        target.append(mapa_nodos[t])
        value.append(v)

    # ==============================
    # Short labels + full hover labels
    # ==============================
    etiquetas_cortas = []
    etiquetas_completas = []

    for nodo in nodos:
        etiquetas_completas.append(nodo)

        if " | " in nodo:
            fase, texto = nodo.split(" | ", 1)
            etiquetas_cortas.append(f"{fase} | {acortar_texto(texto, 30)}")
        else:
            etiquetas_cortas.append(acortar_texto(nodo, 34))

    # ==============================
    # Colors
    # ==============================
    colores_nodos = []

    for nodo in nodos:
        if "EP" in nodo:
            colores_nodos.append("#1565C0")  # Blue
        elif "ON" in nodo:
            colores_nodos.append("#F39C12")  # Orange
        elif "CL" in nodo:
            colores_nodos.append("#2E7D32")  # Green
        elif "MT" in nodo:
            colores_nodos.append("#C62828")  # Red
        else:
            colores_nodos.append("#8E44AD")  # Purple

    colores_enlaces = ["rgba(160,160,160,0.32)" for _ in source]

    # ==============================
    # Sankey figure
    # ==============================
    fig = go.Figure(
        go.Sankey(
            arrangement="snap",

            node=dict(
                pad=28,
                thickness=17,

                line=dict(
                    color="rgba(60,60,60,0.45)",
                    width=0.4
                ),

                label=etiquetas_cortas,
                color=colores_nodos,
                customdata=etiquetas_completas,

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

                hovertemplate=(
                    "Origen: %{source.label}<br>"
                    "Destino: %{target.label}<br>"
                    "Valor: %{value}"
                    "<extra></extra>"
                )
            )
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
                size=20,
                family="Arial Narrow, Arial, sans-serif",
                color="#333333"
            )
        ),

        width=1700,
        height=1100,

        font=dict(
            family="Arial Narrow, Arial, sans-serif",
            size=9,
            color="#444444"
        ),

        margin=dict(
            l=30,
            r=30,
            t=80,
            b=30
        ),

        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    return fig
import pandas as pd
import plotly.graph_objects as go
from collections import defaultdict


def acortar_texto(texto, max_len=22):
    texto = str(texto).strip()
    if len(texto) <= max_len:
        return texto
    return texto[:max_len - 3] + "..."


def crear_sankey(df):
    # ==============================
    # Limpiar datos
    # ==============================
    df = df.copy()

    columnas_requeridas = ["Fase", "Categoría", "Subcategoría", "Código"]
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

            nodos.extend([categoria, subcategoria, codigo])

            enlaces.append((categoria, subcategoria, 1))
            enlaces.append((subcategoria, codigo, 1))

    # ==============================
    # Evolución entre fases
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
    # Nodos únicos
    # ==============================
    nodos = list(dict.fromkeys(nodos))
    mapa_nodos = {nodo: i for i, nodo in enumerate(nodos)}

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

    for (s, t), v in enlaces_agrupados.items():
        source.append(mapa_nodos[s])
        target.append(mapa_nodos[t])
        value.append(v)

    # ==============================
    # Etiquetas cortas + hover completo
    # ==============================
    etiquetas_cortas = []
    etiquetas_completas = []

    for nodo in nodos:
        etiquetas_completas.append(nodo)

        if " | " in nodo:
            fase, texto = nodo.split(" | ", 1)
            etiquetas_cortas.append(f"{fase} | {acortar_texto(texto, 20)}")
        else:
            etiquetas_cortas.append(acortar_texto(nodo, 22))

    # ==============================
    # Colores nodos
    # ==============================
    colores_nodos = []
    for nodo in nodos:
        if "EP" in nodo:
            colores_nodos.append("#1565C0")
        elif "ON" in nodo:
            colores_nodos.append("#F39C12")
        elif "CL" in nodo:
            colores_nodos.append("#2E7D32")
        elif "MT" in nodo:
            colores_nodos.append("#C62828")
        else:
            colores_nodos.append("#8E44AD")

    # enlaces más suaves pero visibles
    colores_enlaces = ["rgba(140,140,140,0.40)" for _ in source]

    # ==============================
    # Figura Sankey
    # ==============================
    fig = go.Figure(
        go.Sankey(
            arrangement="snap",
            valueformat=".0f",

            node=dict(
                pad=35,
                thickness=18,
                line=dict(
                    color="rgba(70,70,70,0.55)",
                    width=0.5
                ),
                label=etiquetas_cortas,
                color=colores_nodos,
                customdata=etiquetas_completas,
                hovertemplate="<b>%{customdata}</b><extra></extra>",
            ),

            link=dict(
                source=source,
                target=target,
                value=value,
                color=colores_enlaces,
                hovertemplate=(
                    "Origen: %{source.label}<br>"
                    "Destino: %{target.label}<br>"
                    "Valor: %{value}<extra></extra>"
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
                family="Arial, sans-serif",
                size=24,
                color="#222222"
            )
        ),

        width=2200,
        height=1400,

        font=dict(
            family="Arial, sans-serif",
            size=12,
            color="#222222"
        ),

        margin=dict(l=40, r=40, t=90, b=40),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    return fig
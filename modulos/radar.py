import pandas as pd
import plotly.graph_objects as go

def crear_radar(df):

    tabla = (
        df.groupby(
            ["Fase", "Categoría"]
        )["Código"]
        .count()
        .reset_index()
    )

    pivot = tabla.pivot(
        index="Fase",
        columns="Categoría",
        values="Código"
    ).fillna(0)

    categorias = ["EP", "ON", "CL", "MT"]

    fig = go.Figure()

    for fase in pivot.index:

        valores = [
            pivot.loc[fase, cat]
            if cat in pivot.columns
            else 0
            for cat in categorias
        ]

        valores.append(valores[0])

        fig.add_trace(
            go.Scatterpolar(
                r=valores,
                theta=categorias + [categorias[0]],
                fill="toself",
                name=fase
            )
        )

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True
            )
        ),
        title="Evolución de Categorías por Fase",
        showlegend=True
    )

    return fig

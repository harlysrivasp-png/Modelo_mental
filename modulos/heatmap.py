# modulos/heatmap.py

import pandas as pd
import plotly.express as px


def crear_heatmap(df):

    tabla = (

        df.groupby(
            ["Fase", "Categoría"]
        )["Código"]

        .count()

        .reset_index()

    )

    matriz = tabla.pivot(

        index="Categoría",

        columns="Fase",

        values="Código"

    ).fillna(0)

    fig = px.imshow(

        matriz,

        text_auto=True,

        aspect="auto",

        labels=dict(

            x="Fase",

            y="Categoría",

            color="Frecuencia"

        )

    )

    fig.update_layout(

        title="Mapa de Calor de Códigos por Fase",

        height=500

    )

    return fig
import pandas as pd
import plotly.graph_objects as go


def crear_sankey(df):
 
    # ==============================
    # Limpiar datos
    # ==============================
    df = df.copy()

    df["Fase"] = df["Fase"].astype(str).str.strip()
    df["Categoría"] = df["Categoría"].astype(str).str.strip()
    df["Subcategoría"] = df["Subcategoría"].astype(str).str.strip()
    df["Código"] = df["Código"].astype(str).str.strip()

    # ==============================
    # Crear nodos
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
    for i in range(len(fases)-1):

        fase_actual = fases[i]
        fase_siguiente = fases[i+1]

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
    # Diccionario de nodos
    # ==============================
    nodos = list(dict.fromkeys(nodos))

    mapa_nodos = {
        nodo: i
        for i, nodo in enumerate(nodos)
    }

    source = []
    target = []
    value = []

    for s, t, v in enlaces:

        if s in mapa_nodos and t in mapa_nodos:

            source.append(
                mapa_nodos[s]
            )

            target.append(
                mapa_nodos[t]
            )

            value.append(v)

    # ==============================
    # Colores
    # ==============================
    colores = []

    for nodo in nodos:

        if "EP" in nodo:
            colores.append("#0066CC")

        elif "ON" in nodo:
            colores.append("#F39C12")

        elif "CL" in nodo:
            colores.append("#2CA02C")

        elif "MT" in nodo:
            colores.append("#D62728")

        else:
            colores.append("#8E44AD")

    # ==============================
    # Crear figura
    # ==============================
    fig = go.Figure(

        go.Sankey(

            arrangement="snap",

            node=dict(

                pad=20,

                thickness=25,

                line=dict(
                    color="black",
                    width=0.5
                ),

                label=nodos,

                color=colores
            ),

            link=dict(

                source=source,

                target=target,

                value=value
            )
        )
    )

    fig.update_layout(

        title=dict(
            text="Evolución del Modelo Mental de Conciencia Ambiental",
            x=0.5
        ),

        height=1000,

        font=dict(
            size=12
        )
    )

    return fig
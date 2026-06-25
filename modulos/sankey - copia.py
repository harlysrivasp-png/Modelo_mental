import pandas as pd
import plotly.graph_objects as go


def ordenar_fases(fases):
    """
    Ordena las fases de forma natural: F1, F2, F3.
    """
    orden = {
        "F1": 1,
        "FASE 1": 1,
        "FASE1": 1,
        "Fase 1": 1,
        "Fase1": 1,
        "fase 1": 1,
        "fase1": 1,

        "F2": 2,
        "FASE 2": 2,
        "FASE2": 2,
        "Fase 2": 2,
        "Fase2": 2,
        "fase 2": 2,
        "fase2": 2,

        "F3": 3,
        "FASE 3": 3,
        "FASE3": 3,
        "Fase 3": 3,
        "Fase3": 3,
        "fase 3": 3,
        "fase3": 3,
    }

    return sorted(
        fases,
        key=lambda x: orden.get(str(x).strip(), 999)
    )


def construir_datos_sankey(df):
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

    fases = ordenar_fases(df["Fase"].unique())

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

    return nodos, source, target, value, colores


def crear_trace_sankey(nodos, source, target, value, colores, visible=True):
    return go.Sankey(

        arrangement="snap",

        visible=visible,

        node=dict(

            pad=20,

            thickness=25,

            line=dict(
                color="rgba(0,0,0,0.35)",
                width=0.3
            ),

            label=nodos,

            color=colores
        ),

        link=dict(

            source=source,

            target=target,

            value=value,

            color=[
                "rgba(180,180,180,0.22)"
                for _ in source
            ]
        )
    )


def crear_sankey(df):

    df = df.copy()

    df["Fase"] = df["Fase"].astype(str).str.strip()

    fases = ordenar_fases(df["Fase"].unique())

    # ==============================
    # Figura
    # ==============================
    fig = go.Figure()

    traces = []
    nombres_botones = []

    # ==============================
    # Vista general
    # ==============================
    nodos, source, target, value, colores = construir_datos_sankey(df)

    trace_general = crear_trace_sankey(
        nodos,
        source,
        target,
        value,
        colores,
        visible=True
    )

    traces.append(trace_general)
    nombres_botones.append("Todas")

    fig.add_trace(trace_general)

    # ==============================
    # Vistas por fase
    # ==============================
    for fase in fases:

        df_fase = df[df["Fase"] == fase]

        nodos_fase, source_fase, target_fase, value_fase, colores_fase = construir_datos_sankey(
            df_fase
        )

        trace_fase = crear_trace_sankey(
            nodos_fase,
            source_fase,
            target_fase,
            value_fase,
            colores_fase,
            visible=False
        )

        traces.append(trace_fase)
        nombres_botones.append(fase)

        fig.add_trace(trace_fase)

    # ==============================
    # Botones dinámicos
    # ==============================
    botones = []

    for i, nombre in enumerate(nombres_botones):

        visible = [
            False
            for _ in traces
        ]

        visible[i] = True

        if nombre == "Todas":
            titulo = ""
        else:
            titulo = f" - {nombre}"

        botones.append(
            dict(
                label=nombre,
                method="update",
                args=[
                    {
                        "visible": visible
                    },
                    {
                        "title": {
                            "text": titulo,
                            "x": 0.5,
                            "y": 0.88,
                            "xanchor": "center",
                            "yanchor": "top"
                        }
                    }
                ]
            )
        )

    # ==============================
    # Layout
    # ==============================
    fig.update_layout(

        title=dict(
            text="",
            x=0.5,
            y=0.88,
            xanchor="center",
            yanchor="top"
        ),

        height=1000,

        margin=dict(
            l=40,
            r=40,
            t=180,
            b=40
        ),

        font=dict(
            family="Arial",
            size=11,
            color="#222222"
        ),

        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.5,
                y=1.22,
                xanchor="center",
                yanchor="top",
                buttons=botones
            )
        ]
    )

    return fig
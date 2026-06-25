import pandas as pd
import plotly.graph_objects as go
from collections import defaultdict


# ======================================================
# CONFIGURACION GENERAL
# ======================================================

FUENTE = "Times New Roman"   # Puede cambiar a "Arial"
COLOR_TEXTO = "#111111"


def acortar_texto(texto, max_len=34):
    """
    Acorta etiquetas largas para mejorar la visualizacion.
    El texto completo se conserva en el hover.
    """
    texto = str(texto).strip()

    if len(texto) <= max_len:
        return texto

    return texto[:max_len - 3] + "..."


def ordenar_fases(fases):
    """
    Ordena las fases en forma natural: F1, F2, F3.
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


def limpiar_dataframe(df):
    """
    Limpia y valida el dataframe.
    """
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

    return df


def construir_sankey(df, titulo_modo="Todas las fases"):
    """
    Construye los datos de un Sankey para un subconjunto del dataframe.
    Devuelve:
    - trace Sankey
    - anotaciones
    - titulo
    """
    df = limpiar_dataframe(df)

    fases = ordenar_fases(
        df["Fase"].dropna().unique()
    )

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

            # Estructura interna
            enlaces.append(
                (categoria, subcategoria, 1)
            )

            enlaces.append(
                (subcategoria, codigo, 1)
            )

    # ==============================
    # Evolucion entre fases
    # ==============================
    if len(fases) > 1:
        for i in range(len(fases) - 1):
            fase_actual = fases[i]
            fase_siguiente = fases[i + 1]

            df_actual = df[df["Fase"] == fase_actual]
            df_sig = df[df["Fase"] == fase_siguiente]

            codigos_actuales = set(
                df_actual["Código"]
                .dropna()
                .astype(str)
                .str.strip()
            )

            codigos_siguientes = set(
                df_sig["Código"]
                .dropna()
                .astype(str)
                .str.strip()
            )

            comunes = codigos_actuales.intersection(
                codigos_siguientes
            )

            for codigo in comunes:
                origen = f"{fase_actual} | {codigo}"
                destino = f"{fase_siguiente} | {codigo}"

                enlaces.append(
                    (origen, destino, 1)
                )

    # ==============================
    # Nodos unicos
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
    # Posiciones por fase
    # ==============================
    fase_x = {}

    if len(fases) == 1:
        fase_x[fases[0]] = 0.08
    else:
        for i, fase in enumerate(fases):
            fase_x[fase] = 0.05 + i * (0.88 / (len(fases) - 1))

    nodos_por_fase = {}

    for fase in fases:
        nodos_por_fase[fase] = [
            nodo for nodo in nodos
            if nodo.startswith(f"{fase} |")
        ]

    def posiciones_verticales(lista):
        """
        Distribuye los nodos verticalmente iniciando arriba.
        """
        n = len(lista)

        if n == 0:
            return {}

        if n == 1:
            return {
                lista[0]: 0.5
            }

        return {
            nodo: 0.98 - i * (0.96 / (n - 1))
            for i, nodo in enumerate(lista)
        }

    y_por_fase = {
        fase: posiciones_verticales(nodos_por_fase[fase])
        for fase in fases
    }

    x_pos = []
    y_pos = []

    for nodo in nodos:
        fase_nodo = nodo.split(" | ", 1)[0]

        x_pos.append(
            fase_x.get(fase_nodo, 0.5)
        )

        y_pos.append(
            y_por_fase
            .get(fase_nodo, {})
            .get(nodo, 0.5)
        )

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
    # Etiquetas cortas para anotaciones
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
    # Trace Sankey
    # Etiquetas nativas ocultas para evitar sombra.
    # ==============================
    trace = go.Sankey(
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

    # ==============================
    # Anotaciones limpias
    # ==============================
    anotaciones = []

    for i, nodo in enumerate(nodos):
        x = x_pos[i]
        y = y_pos[i]

        etiqueta = etiquetas_cortas[i]

        x_texto = x + 0.018
        xanchor = "left"

        if x_texto > 0.96:
            x_texto = x - 0.018
            xanchor = "right"

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
                    family=FUENTE,
                    size=12,
                    color=COLOR_TEXTO
                ),

                align="left",

                bgcolor="rgba(255,255,255,0.85)",
                bordercolor="rgba(255,255,255,0)",
                borderwidth=0,
                borderpad=1
            )
        )

    # ==============================
    # Encabezados de fase
    # ==============================
    for fase in fases:
        anotaciones.append(
            dict(
                x=fase_x.get(fase, 0.5),
                y=1.04,
                xref="paper",
                yref="paper",
                text=f"<b>{fase}</b>",
                showarrow=False,
                xanchor="center",
                yanchor="bottom",

                font=dict(
                    family=FUENTE,
                    size=18,
                    color=COLOR_TEXTO
                )
            )
        )

    titulo = (
        "Evolución del Modelo Mental de Conciencia Ambiental"
        f" - {titulo_modo}"
    )

    return trace, anotaciones, titulo


def crear_sankey(df):
    # ==============================
    # Limpiar datos
    # ==============================
    df = limpiar_dataframe(df)

    fases = ordenar_fases(
        df["Fase"].dropna().unique()
    )

    # ==============================
    # Construir vista general
    # ==============================
    trace_general, anot_general, titulo_general = construir_sankey(
        df,
        "Todas las fases"
    )

    fig = go.Figure()

    fig.add_trace(trace_general)

    # ==============================
    # Construir vistas por fase
    # ==============================
    traces = [
        trace_general
    ]

    anotaciones_por_vista = [
        anot_general
    ]

    titulos_por_vista = [
        titulo_general
    ]

    nombres_botones = [
        "Todas"
    ]

    for fase in fases:
        df_fase = df[df["Fase"] == fase]

        trace_fase, anot_fase, titulo_fase = construir_sankey(
            df_fase,
            fase
        )

        traces.append(trace_fase)
        anotaciones_por_vista.append(anot_fase)
        titulos_por_vista.append(titulo_fase)
        nombres_botones.append(fase)

    # Agregar las trazas restantes ocultas
    for trace in traces[1:]:
        trace.visible = False
        fig.add_trace(trace)

    # ==============================
    # Botones dinamicos
    # ==============================
    botones = []

    for i, nombre in enumerate(nombres_botones):
        visible = [
            False
            for _ in traces
        ]

        visible[i] = True

        botones.append(
            dict(
                label=nombre,
                method="update",
                args=[
                    {
                        "visible": visible
                    },
                    {
                        "annotations": anotaciones_por_vista[i],
                        "title": {
                            "text": titulos_por_vista[i],
                            "x": 0.5,
                            "xanchor": "center",
                            "font": {
                                "family": FUENTE,
                                "size": 24,
                                "color": COLOR_TEXTO
                            }
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
            text=titulo_general,
            x=0.5,
            xanchor="center",

            font=dict(
                family=FUENTE,
                size=24,
                color=COLOR_TEXTO
            )
        ),

        width=2200,
        height=1400,

        font=dict(
            family=FUENTE,
            size=12,
            color=COLOR_TEXTO
        ),

        margin=dict(
            l=40,
            r=40,
            t=150,
            b=40
        ),

        paper_bgcolor="white",
        plot_bgcolor="white",

        annotations=anot_general,

        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.5,
                y=1.10,
                xanchor="center",
                yanchor="top",

                buttons=botones,

                bgcolor="rgba(245,245,245,0.95)",
                bordercolor="rgba(120,120,120,0.4)",
                borderwidth=1,

                font=dict(
                    family=FUENTE,
                    size=13,
                    color=COLOR_TEXTO
                )
            )
        ]
    )

    return fig
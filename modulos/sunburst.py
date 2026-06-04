import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ==========================================
# DIVIDIR TEXTO
# ==========================================
def dividir_cita(texto, max_len=20):

    palabras = str(texto).split()
    lineas = []
    actual = ""

    for palabra in palabras:

        if len(actual + " " + palabra) <= max_len:
            actual += " " + palabra
        else:
            lineas.append(actual.strip())
            actual = palabra

    if actual:
        lineas.append(actual.strip())

    return "<br>".join(lineas)


# ==========================================
# SUNBURST POR FASE
# ==========================================
def construir_frame_con_citas_hijas(
        df,
        fase,
        cols_cita,
        color_map):

    data_fase = df[df["Fase"] == fase].copy()

    data_fase["Subcategoría"] = (
        data_fase["Subcategoría"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    data_fase["Categoría"] = (
        data_fase["Categoría"]
        .astype(str)
        .str.strip()
    )

    labels = []
    parents = []
    values = []
    hovertexts = []
    colors = []

    añadidos_dim = set()
    añadidos_sub = set()

    for _, row in data_fase.iterrows():

        dim = str(row["Categoría"]).strip()
        sub = str(row["Subcategoría"]).strip()
        cod = str(row["Código"]).strip()

        dim_label = f"📂 {dividir_cita(dim, max_len=13)}"
        sub_label = f"🔶 {dividir_cita(sub, max_len=20)}"

        # ======================================
        # CATEGORÍA
        # ======================================
        if dim_label not in añadidos_dim:

            labels.append(dim_label)
            parents.append("")
            values.append(8)

            hovertexts.append(
                f"Categoría: {dim}"
            )

            colors.append(
                color_map.get(dim, "gray")
            )

            añadidos_dim.add(dim_label)

        # ======================================
        # SUBCATEGORÍA
        # ======================================
        if sub_label not in añadidos_sub:

            labels.append(sub_label)
            parents.append(dim_label)
            values.append(10)

            hovertexts.append(
                f"Subcategoría: {sub}"
            )

            colors.append(
                color_map.get(dim, "gray")
            )

            añadidos_sub.add(sub_label)

        # ======================================
        # CÓDIGO
        # ======================================
        cod_label = (
            f"🟢 {dividir_cita(cod, max_len=15)}"
        )

        labels.append(cod_label)
        parents.append(sub_label)
        values.append(2)

        hovertexts.append(
            f"Código: {cod}"
        )

        colors.append("purple")

        # ======================================
        # CITAS
        # ======================================
        for cita_col in cols_cita:

            if cita_col in row.index and pd.notna(row[cita_col]):

                cita = str(row[cita_col]).strip()

                if cita != "":

                    cita_formateada = dividir_cita(
                        cita[:500],
                        max_len=25
                    )

                    cita_label = (
                        f"• {cita_formateada}"
                    )

                    labels.append(cita_label)
                    parents.append(cod_label)
                    values.append(1)

                    hovertexts.append(
                        cita
                    )

                    colors.append("lightgray")

    return go.Sunburst(

        labels=labels,
        parents=parents,
        values=values,

        hovertext=hovertexts,
        hoverinfo="text",

        marker=dict(
            colors=colors,
            line=dict(
                color="white",
                width=2
            )
        ),

        insidetextfont=dict(
            size=24,
            family="Arial"
        ),

        hoverlabel=dict(
            bgcolor="white",
            font_size=16,
            align="left"
        ),

        sort=False,
        branchvalues="remainder",
        maxdepth=None
    )


# ==========================================
# CREAR SUNBURST GENERAL
# ==========================================
def crear_sunburst(
        df,
        fases,
        cols_cita,
        color_map,
        titulo):

    fig = make_subplots(

        rows=1,
        cols=len(fases),

        specs=[
            [{"type": "domain"}] *
            len(fases)
        ],

        subplot_titles=[
            f"Fase {f}"
            for f in fases
        ],

        horizontal_spacing=0.01
    )

    for i, fase in enumerate(fases):

        fig.add_trace(

            construir_frame_con_citas_hijas(
                df=df,
                fase=fase,
                cols_cita=cols_cita,
                color_map=color_map
            ),

            row=1,
            col=i + 1
        )

    fig.update_layout(

        title=dict(
            text=titulo,
            x=0.5,
            font=dict(
                size=30
            )
        ),

        height=1100,
        width=2600,

        showlegend=False,

        margin=dict(
            t=100,
            l=20,
            r=20,
            b=20
        )
    )

    return fig
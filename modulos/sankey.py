import pandas as pd
import plotly.graph_objects as go
from collections import defaultdict


def acortar_texto(texto, max_len=28):
    texto = str(texto)
    if len(texto) <= max_len:
        return texto
    return texto[:max_len - 3] + "..."


def crear_sankey_mejorado(df):
    # ==============================
    # Limpiar datos
    # ==============================
    df = df.copy()
    df["Fase"] = df["Fase"].astype(str).str.strip()
    df["Categoría"] = df["Categoría"].astype(str).str.strip()
    df["Subcategoría"] = df["Subcategoría"].astype(str).str.strip()
    df["Código"] = df["Código"].astype(str).str.strip()

    # Orden natural de fases
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
    # Eliminar duplicados de nodos
    # ==============================
    nodos = list(dict.fromkeys(nodos))

    # ==============================
    # Agrupar enlaces repetidos
    # ==============================
    enlaces_agrupados = defaultdict(int)
    for s, t, v in enlaces:
        enlaces_agrupados[(s, t)] += v

    mapa_nodos = {nodo: i for i, nodo in enumerate(nodos)}

    source = []
    target = []
    value = []

    for (s, t), v in enlaces_agrupados.items():
        if s in mapa_nodos and t in mapa_nodos:
            source.append(mapa_nodos[s])
            target.append(mapa_nodos[t])
            value.append(v)

    # ==============================
    # Etiquetas visibles y completas
    # ==============================
    labels_visibles = []
    labels_completos = []

    for nodo in nodos:
        labels_completos.append(nodo)

        # Mostrar algo más corto
        partes = nodo.split(" | ", 1)
        if len(partes) == 2:
            fase, resto = partes
            label_corta = f"{fase} | {acortar_texto(resto, 26)}"
        else:
            label_corta = acortar_texto(nodo, 28)

        labels_visibles.append(label_corta)

    # ==============================
    # Colores por tipo/nodo
    # ==============================
    colores = []
    for nodo in nodos:
        if "EP" in nodo:
            colores.append("#1565C0")   # azul
        elif "ON" in nodo:
            colores.append("#F39C12")   # naranja
        elif "CL" in nodo:
            colores.append("#2E7D32")   # verde
        elif "MT" in nodo:
            colores.append("#C62828")   # rojo
        else:
            colores.append("#8E44AD")   # morado

    # ==============================
    # Posiciones manuales
    # ==============================
    # Tres columnas:
    # categorías -> subcategorías -> códigos
    x_pos = []
    y_pos = []

    # separar nodos por "nivel"
    categorias = [n for n in nodos if any(n == f"{fase} | {cat}" for fase in fases for cat in df[df["Fase"] == fase]["Categoría"].unique())]
    # mejor detectar según aparición en enlaces
    origenes = set([e[0] for e in enlaces_agrupados.keys()])
    destinos = set([e[1] for e in enlaces_agrupados.keys()])

    # Clasificación más robusta según estructura
    tipo_nodo = {}
    for nodo in nodos:
        # Si aparece como origen pero no como destino final, y coincide con categorías
        # usamos heurística basada en presencia en dataframe
        encontrado = False
        for fase in fases:
            df_fase = df[df["Fase"] == fase]
            if nodo in [f"{fase} | {c}" for c in df_fase["Categoría"].unique()]:
                tipo_nodo[nodo] = "categoria"
                encontrado = True
                break
            if nodo in [f"{fase} | {s}" for s in df_fase["Subcategoría"].unique()]:
                tipo_nodo[nodo] = "subcategoria"
                encontrado = True
                break
            if nodo in [f"{fase} | {c}" for c in df_fase["Código"].unique()]:
                tipo_nodo[nodo] = "codigo"
                encontrado = True
                break
        if not encontrado:
            tipo_nodo[nodo] = "otro"

    # Agrupar por tipo para ordenar verticalmente
    nodos_categoria = [n for n in nodos if tipo_nodo[n] == "categoria"]
    nodos_subcategoria = [n for n in nodos if tipo_nodo[n] == "subcategoria"]
    nodos_codigo = [n for n in nodos if tipo_nodo[n] == "codigo"]

    def posiciones_verticales(lista):
        n = len(lista)
        if n == 1:
            return {lista[0]: 0.5}
        return {nodo: 0.02 + i * (0.96 / (n - 1)) for i, nodo in enumerate(lista)}

    y_cat = posiciones_verticales(nodos_categoria)
    y_sub = posiciones_verticales(nodos_subcategoria)
    y_cod = posiciones_verticales(nodos_codigo)

    for nodo in nodos:
        if tipo_nodo[nodo] == "categoria":
            x_pos.append(0.02)
            y_pos.append(y_cat[nodo])
        elif tipo_nodo[nodo] == "subcategoria":
            x_pos.append(0.40)
            y_pos.append(y_sub[nodo])
        elif tipo_nodo[nodo] == "codigo":
            x_pos.append(0.82)
            y_pos.append(y_cod[nodo])
        else:
            x_pos.append(0.5)
            y_pos.append(0.5)

    # ==============================
    # Colores de enlaces
    # ==============================
    link_colors = ["rgba(160,160,160,0.35)" for _ in source]

    # ==============================
    # Crear figura
    # ==============================
    fig = go.Figure(
        go.Sankey(
            arrangement="fixed",
            node=dict(
                pad=22,
                thickness=18,
                line=dict(color="rgba(60,60,60,0.7)", width=0.7),
                label=labels_visibles,
                color=colores,
                x=x_pos,
                y=y_pos,
                customdata=labels_completos,
                hovertemplate="<b>%{customdata}</b><extra></extra>"
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                color=link_colors,
                hovertemplate="Origen: %{source.label}<br>Destino: %{target.label}<br>Valor: %{value}<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title=dict(
            text="Evolución del Modelo Mental de Conciencia Ambiental",
            x=0.5,
            xanchor="center"
        ),
        width=1600,
        height=1100,
        font=dict(
            size=12,
            family="Arial"
        ),
        margin=dict(l=30, r=30, t=80, b=30),
        paper_bgcolor="white",
        plot_bgcolor="white"
    )

    return fig
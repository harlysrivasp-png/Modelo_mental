from wordcloud import WordCloud
import matplotlib.pyplot as plt

def crear_wordcloud(df, cols_cita):

    texto = ""

    for col in cols_cita:
        citas = df[col].dropna().astype(str)
        texto += " ".join(citas) + " "

    if texto.strip() == "":
        return None

    nube = WordCloud(
        width=1200,
        height=600,
        background_color="white",
        collocations=False
    ).generate(texto)

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.imshow(nube, interpolation="bilinear")
    ax.axis("off")
    

    return fig
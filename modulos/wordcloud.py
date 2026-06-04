import re
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS


# ==========================================
# CREAR NUBE DE PALABRAS
# ==========================================

def crear_wordcloud(df, cols_cita):

    # ==========================================
    # PALABRAS A EXCLUIR
    # ==========================================

    stopwords_personalizadas = {
        "así", "aquí", "ahora", "también", "etc", "den", "considero","_sd", "sd", "e04", "f1", "f2", "f3", "e1", "e2", "e3", "e4","ser", "estar", "tener", "hacer", "decir", "ir", "ver", "dar", "saber", "querer", "llegar",
        "salgan", "dice", "cuales", "ende", "ser", "puede", "tener","_sd1", "_sd2", "_sd3", "_sd4", "_sd5", "_sd6","son", "están", "están", "están", "están", "están", "están", "están","porque", "cómo", "cuál", "cuáles", "quién", "quiénes", "dónde", "cuándo", "por qué","pienso", "creo", "considero", "me parece", "así que", "además", "sin embargo", "aunque", "por lo tanto", "en consecuencia","ser", "estar", "tener", "hacer", "decir", "ir", "ver", "dar", "saber", "querer", "llegar",
        "pues", "hacer", "decir", "cada", "todo", "muy", "sin","las", "los", "que", "y", "o", "de", "en", "el", "la", "lo", "del", "al","sobre", "entre", "otros", "hacia", "asumir","por ejemplo", "en cambio", "en mi opinión", "desde mi perspectiva", "considero que", "creo que", "me parece que",
        "mayor", "sino", "uno", "e01", "r1", "un", "una", "y", "de","ser", "estar", "tener", "hacer", "decir", "ir", "ver", "dar", "saber", "querer", "llegar","el", "la", "lo", "los", "las", "que", "y", "o", "de", "en", "del", "al","sobre", "entre", "otros", "hacia", "asumir","por ejemplo", "en cambio", "en mi opinión", "desde mi perspectiva", "considero que", "creo que", "me parece que",
        "en", "el", "la", "lo", "del", "al", "con", "por", "para","estudiante", "estudiantes", "profesor", "profesores", "f1", "f2", "f3","formar", "formar", "formación", "formarse", "aprendizaje", "aprender", "enseñar", "enseñanza","ser", "estar", "tener", "hacer", "decir", "ir", "ver", "dar", "saber", "querer", "llegar",
        "que", "e1", "f2", "f3", "como", "se","Todas","todas","sean", "los", "mas", "más","esta", "están", "están", "están", "están", "están", "están", "están","porque", "cómo", "cuál", "cuáles", "quién", "quiénes", "dónde", "cuándo", "por qué","vez", "puede", "pueden", "debe", "deben","ser", "estar", "tener", "hacer", "decir", "ir", "ver", "dar", "saber", "querer", "llegar",
        "sd2", "sd1", "es", "su","mi","toda","forma","sea","estos","hizo", "ejemplo", "f2_sd1", "f2_sd2","fuente", "f1_sd1", "f1_sd2", "f1_sd3", "f3_sd1", "f3_sd2","documento", "f3_sd3", "e04_sd1", "e04_sd2", "e04_sd3", "e04_sd4","tema", "temas", "aspecto", "aspectos", "punto", "puntos","ser", "estar", "tener", "hacer", "decir", "ir", "ver", "dar", "saber", "querer", "llegar",
        "f2_sd3", "f1_sd1", "f1_sd2", "tal","mis","_en","desde","f1_sd3", "ha","hay","si","sí","primero","f3_sd1", "f3_sd2","documento", "f3_sd3", "e04_sd1", "e04_sd2", "e04_sd3", "e04_sd4","_e", "f1_sd1", "f1_sd2", "f1_sd3", "f3_sd1", "f3_sd2","documento", "mismo", "f3_sd3", "e04_sd1", "e04_sd2", "e04_sd3", "e04_sd4","ser", "estar", "tener", "hacer", "decir", "ir", "ver", "dar", "saber", "querer", "llegar",
        "f3_sd3", "e04_sd1", "e04_sd2","entender","hizo", "fue","donde","e04_sd3", "e04_sd4","sd1", "sd2", "sd3", "sd4", "sd5", "sd6", "e04_sd1", "e04_sd2", "e04_sd3", "f","_e04_sd1", "_e04_sd2", "_e04_sd3", "_e04_sd4", "sus","ya", "puede", "pueden", "debe", "deben","ser", "estar", "tener", "hacer", "decir", "ir", "ver", "dar", "saber", "querer", "llegar",
        "e04_sd6", "siento", "solo","si","claro","depende","todos","todo","cuál","cual","si","tiene","está", "eso", "debe","esto", "si","citas", "cita", "código", "códigos", "categoría", "categorías","directamente", "indirectamente", "además", "sin embargo", "aunque", "por lo tanto", "en consecuencia", "así que","e","f1", "f2", "f3", "e1", "e2", "e3", "e4","ser", "estar", "tener", "hacer", "decir", "ir", "ver", "dar", "saber", "querer", "llegar",
        "entre", "otros", "hacia", "asumir","por ejemplo", "en cambio", "en mi opinión", "desde mi perspectiva", "considero que", "creo que", "me parece que","f1_sd1", "f1_sd2", "f1_sd3", "f2_sd1", "f2_sd2", "f2_sd3","porque", "cómo", "cuál", "cuáles", "quién", "quiénes", "dónde", "cuándo", "por qué","f3_sd1", "f3_sd2", "f3_sd3", "e04_sd1", "e04_sd2", "e04_sd3", "e04_sd4"
    }

    stopwords_finales = STOPWORDS.union(stopwords_personalizadas)

    # ==========================================
    # VALIDAR COLUMNAS DE CITAS
    # ==========================================

    if not cols_cita:
        return None

    textos = []

    for col in cols_cita:
        if col in df.columns:
            textos.extend(
                df[col]
                .dropna()
                .astype(str)
                .tolist()
            )

    if len(textos) == 0:
        return None

    # ==========================================
    # UNIR Y LIMPIAR TEXTO
    # ==========================================

    texto_completo = " ".join(textos).lower()

    texto_completo = re.sub(
        r"[^a-záéíóúñü_ ]",
        " ",
        texto_completo
    )

    if texto_completo.strip() == "":
        return None

    # ==========================================
    # CREAR NUBE
    # ==========================================

    wordcloud = WordCloud(
        width=1200,
        height=600,
        background_color="white",
        stopwords=stopwords_finales,
        collocations=False,
        max_words=150
    ).generate(texto_completo)

    fig, ax = plt.subplots(figsize=(14, 7))

    ax.imshow(
        wordcloud,
        interpolation="bilinear"
    )

    ax.axis("off")

    return fig
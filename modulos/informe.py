def generar_informe(df):

    fases = sorted(
        df["Fase"]
        .dropna()
        .unique()
    )

    informe = ""

    for i in range(len(fases) - 1):

        f1 = fases[i]
        f2 = fases[i + 1]

        d1 = df[df["Fase"] == f1]
        d2 = df[df["Fase"] == f2]

        informe += (
            f"\n\n📘 COMPARACIÓN "
            f"{f1} → {f2}\n"
        )

        informe += "-" * 50 + "\n"

        categorias = sorted(

            set(d1["Categoría"])
            |
            set(d2["Categoría"])

        )

        for cat in categorias:

            s1 = set(

                d1[
                    d1["Categoría"] == cat
                ]["Subcategoría"]

                .astype(str)
            )

            s2 = set(

                d2[
                    d2["Categoría"] == cat
                ]["Subcategoría"]

                .astype(str)
            )

            c1 = set(

                d1[
                    d1["Categoría"] == cat
                ]["Código"]

                .astype(str)
            )

            c2 = set(

                d2[
                    d2["Categoría"] == cat
                ]["Código"]

                .astype(str)
            )

            informe += f"\n📂 Categoría: {cat}\n"

            informe += (
                f"🔶 Subcategorías nuevas: "
                f"{', '.join(sorted(s2 - s1)) or 'Ninguna'}\n"
            )

            informe += (
                f"❌ Subcategorías que desaparecen: "
                f"{', '.join(sorted(s1 - s2)) or 'Ninguna'}\n"
            )

            informe += (
                f"🟢 Códigos persistentes: "
                f"{', '.join(sorted(c1 & c2)) or 'Ninguno'}\n"
            )

            informe += (
                f"➕ Códigos nuevos: "
                f"{', '.join(sorted(c2 - c1)) or 'Ninguno'}\n"
            )

            informe += (
                f"➖ Códigos eliminados: "
                f"{', '.join(sorted(c1 - c2)) or 'Ninguno'}\n"
            )

    return informe
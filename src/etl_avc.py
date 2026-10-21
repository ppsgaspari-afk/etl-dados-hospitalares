
from pathlib import Path
import pandas as pd
import unicodedata
import re

BASE_DIR = Path(__file__).resolve().parent.parent
ENTRADA = BASE_DIR / "dados" / "entrada_avc"
SAIDA = BASE_DIR / "dados" / "saida"

COLUNAS = [
    "UNIDADE", "DATA", "FAIXA_ETARIA",
    "TEMPO_PORTA_TOMOGRAFIA",
    "TEMPO_PORTA_AGULHA"
]

ALIASES = {
    "HOSPITAL": "UNIDADE",
    "UNIDADE DE SAUDE": "UNIDADE",
    "DATA ATENDIMENTO": "DATA",
    "IDADE GRUPO": "FAIXA_ETARIA",
    "PORTA TOMOGRAFIA": "TEMPO_PORTA_TOMOGRAFIA",
    "PORTA AGULHA": "TEMPO_PORTA_AGULHA",
}


def normalizar(valor):
    texto = unicodedata.normalize("NFKD", str(valor))
    texto = "".join(
        c for c in texto if not unicodedata.combining(c)
    )
    return re.sub(r"\s+", " ", texto).strip().upper()


def padronizar(df):
    df = df.copy()
    df.columns = [
        ALIASES.get(normalizar(c), normalizar(c))
        for c in df.columns
    ]

    duplicadas = df.columns[df.columns.duplicated()].tolist()
    if duplicadas:
        raise ValueError(f"Colunas duplicadas: {duplicadas}")

    for coluna in COLUNAS:
        if coluna not in df.columns:
            df[coluna] = pd.NA

    return df[COLUNAS]


def executar():
    arquivos = sorted(
        p for p in ENTRADA.glob("*.xlsx")
        if not p.name.startswith("~$")
    )

    if not arquivos:
        raise FileNotFoundError(
            "Nenhum arquivo encontrado em dados/entrada_avc."
        )

    bases = []

    for arquivo in arquivos:
        df = pd.read_excel(arquivo)
        df = padronizar(df)
        df["ARQUIVO_ORIGEM"] = arquivo.name
        bases.append(df)

    consolidado = pd.concat(bases, ignore_index=True)

    consolidado["DATA"] = pd.to_datetime(
        consolidado["DATA"], errors="coerce", dayfirst=True
    )

    colunas_tempo = [
        "TEMPO_PORTA_TOMOGRAFIA",
        "TEMPO_PORTA_AGULHA"
    ]

    for coluna in colunas_tempo:
        consolidado[coluna] = pd.to_numeric(
            consolidado[coluna], errors="coerce"
        )

    problemas = []

    for indice, linha in consolidado.iterrows():
        motivos = []

        if pd.isna(linha["UNIDADE"]) or not str(linha["UNIDADE"]).strip():
            motivos.append("Unidade ausente")

        if pd.isna(linha["DATA"]):
            motivos.append("Data inválida")

        for coluna in colunas_tempo:
            valor = linha[coluna]
            if pd.isna(valor):
                motivos.append(f"{coluna} ausente ou inválido")
            elif valor < 0:
                motivos.append(f"{coluna} negativo")

        if motivos:
            problemas.append({
                "LINHA": indice + 2,
                "ARQUIVO_ORIGEM": linha["ARQUIVO_ORIGEM"],
                "PROBLEMAS": "; ".join(motivos)
            })

    # Apenas sinaliza possíveis duplicidades.
    # Não exclui registros automaticamente.
    chaves = ["UNIDADE", "DATA", "FAIXA_ETARIA"]
    consolidado["POSSIVEL_DUPLICATA"] = (
        consolidado.duplicated(subset=chaves, keep=False)
    )

    SAIDA.mkdir(parents=True, exist_ok=True)
    destino = SAIDA / "consolidado_avc_demo.xlsx"

    with pd.ExcelWriter(destino, engine="openpyxl") as writer:
        consolidado.to_excel(
            writer, sheet_name="Base", index=False
        )
        pd.DataFrame(
            problemas,
            columns=["LINHA", "ARQUIVO_ORIGEM", "PROBLEMAS"]
        ).to_excel(
            writer, sheet_name="Pendencias", index=False
        )

    print(f"Registros: {len(consolidado)}")
    print(f"Pendências: {len(problemas)}")
    print(f"Saída: {destino}")


if __name__ == "__main__":
    executar()

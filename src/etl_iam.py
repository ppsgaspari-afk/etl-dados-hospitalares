"""
ETL de dados hospitalares - IAM.

Módulo demonstrativo para extração,
transformação e consolidação de dados.
"""


from pathlib import Path
import pandas as pd
import unicodedata
import re

# Diretórios do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
PASTA_ENTRADA = BASE_DIR / "dados" / "entrada"
PASTA_SAIDA = BASE_DIR / "dados" / "saida"

# Estrutura demonstrativa, sem dados pessoais
COLUNAS_PADRAO = [
    "UNIDADE", "REGIAO", "DATA", "FAIXA_ETARIA", "SEXO",
    "TEMPO_PORTA_ECG", "TEMPO_ECG_AGULHA",
]

MAPA_COLUNAS = {
    "HOSPITAL": "UNIDADE",
    "UNIDADE DE SAUDE": "UNIDADE",
    "REGIAO DE SAUDE": "REGIAO",
    "DATA ATENDIMENTO": "DATA",
    "IDADE GRUPO": "FAIXA_ETARIA",
    "GENERO": "SEXO",
    "PORTA ECG": "TEMPO_PORTA_ECG",
    "TEMPO PORTA ECG": "TEMPO_PORTA_ECG",
    "ECG AGULHA": "TEMPO_ECG_AGULHA",
    "TEMPO ECG AGULHA": "TEMPO_ECG_AGULHA",
}


def normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = re.sub(r"\s+", " ", texto).strip().upper()
    return texto


def padronizar(df):
    df = df.copy()
    df.columns = [MAPA_COLUNAS.get(normalizar(c), normalizar(c)) for c in df.columns]
    duplicadas = df.columns[df.columns.duplicated()].tolist()
    if duplicadas:
        raise ValueError(f"Colunas duplicadas: {duplicadas}")
    for coluna in COLUNAS_PADRAO:
        if coluna not in df.columns:
            df[coluna] = pd.NA
    df = df[COLUNAS_PADRAO]
    df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce", dayfirst=True)
    for coluna in ["TEMPO_PORTA_ECG", "TEMPO_ECG_AGULHA"]:
        df[coluna] = pd.to_numeric(df[coluna], errors="coerce")
    return df


def executar():
    arquivos = sorted(p for p in PASTA_ENTRADA.glob("*.xlsx") if not p.name.startswith("~$"))
    if not arquivos:
        raise FileNotFoundError("Nenhuma planilha Excel encontrada em dados/entrada.")
    bases = []
    for arquivo in arquivos:
        print(f"Processando: {arquivo.name}")
        df = pd.read_excel(arquivo)
        df = padronizar(df)
        df["ARQUIVO_ORIGEM"] = arquivo.name
        bases.append(df)
    consolidado = pd.concat(bases, ignore_index=True)
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
    destino = PASTA_SAIDA / "consolidado_iam_demo.xlsx"
    consolidado.to_excel(destino, index=False)
    print(f"Registros processados: {len(consolidado)}")
    print(f"Arquivo gerado: {destino}")


if __name__ == "__main__":
    executar()

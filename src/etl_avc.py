"""ETL demonstrativo independente. Entradas exclusivamente sintéticas."""
from pathlib import Path
import re
import unicodedata
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
ENTRADA = BASE_DIR / 'dados/entrada_avc'
SAIDA = BASE_DIR / 'dados/saida'
COLUNAS = ['UNIDADE', 'DATA', 'FAIXA_ETARIA', 'TEMPO_PORTA_TOMOGRAFIA', 'TEMPO_PORTA_AGULHA']
TEMPOS = COLUNAS[3:]
ALIASES = {'HOSPITAL':'UNIDADE', 'UNIDADE DE SAUDE':'UNIDADE',
           'DATA ATENDIMENTO':'DATA', 'IDADE GRUPO':'FAIXA_ETARIA',
           'PORTA TOMOGRAFIA':TEMPOS[0], 'PORTA AGULHA':TEMPOS[1]}

def normalizar(valor):
    texto = unicodedata.normalize('NFKD', str(valor))
    return re.sub(r'\s+', ' ', ''.join(c for c in texto if not unicodedata.combining(c))).strip().upper()

def padronizar(df):
    df = df.copy()
    df.columns = [ALIASES.get(normalizar(c), normalizar(c)) for c in df.columns]
    if df.columns.duplicated().any():
        raise ValueError(f'Colunas duplicadas: {df.columns[df.columns.duplicated()].tolist()}')
    return df.reindex(columns=COLUNAS)

def transformar(base):
    """Preserva registros; sinaliza qualidade e coincidências, sem diagnóstico clínico."""
    base = base.copy()
    motivos = [[] for _ in range(len(base))]
    def registrar(mask, mensagem):
        for pos, ativo in enumerate(mask):
            if ativo:
                motivos[pos].append(mensagem)
    for coluna in ['UNIDADE', 'FAIXA_ETARIA']:
        registrar(base[coluna].isna() | base[coluna].astype(str).str.strip().eq(''), f'{coluna} ausente')
    base['DATA'] = pd.to_datetime(base['DATA'], errors='coerce', dayfirst=True, format='mixed')
    registrar(base.DATA.isna(), 'Data ausente ou inválida')
    for coluna in TEMPOS:
        base[coluna] = pd.to_numeric(base[coluna], errors='coerce')
        registrar(base[coluna].isna(), f'{coluna} ausente ou inválido')
        registrar(base[coluna].isin([float('inf'), -float('inf')]), f'{coluna} não finito')
        registrar(base[coluna].lt(0), f'{coluna} negativo')
    # Coerência cronológica demonstrativa, não um limite de protocolo clínico.
    registrar(base[TEMPOS].notna().all(axis=1) & base[TEMPOS[1]].lt(base[TEMPOS[0]]),
              'Porta-agulha menor que porta-tomografia: revisar cronologia')
    chaves = base[['UNIDADE', 'DATA', 'FAIXA_ETARIA']].copy()
    for coluna in ['UNIDADE', 'FAIXA_ETARIA']:
        chaves[coluna] = chaves[coluna].map(lambda v: '' if pd.isna(v) else normalizar(v))
    completa = chaves.DATA.notna() & chaves.UNIDADE.ne('') & chaves.FAIXA_ETARIA.ne('')
    base['POSSIVEL_DUPLICATA'] = completa & chaves.duplicated(keep=False)
    registrar(base.POSSIVEL_DUPLICATA, 'Possível duplicidade: coincidência de unidade, data e faixa etária')
    pendencias = base[['ARQUIVO_ORIGEM', 'LINHA_ORIGEM']].copy()
    pendencias['PROBLEMAS'] = ['; '.join(itens) for itens in motivos]
    return base, pendencias.loc[pendencias.PROBLEMAS.ne('')].reset_index(drop=True)

def executar(entrada=ENTRADA, saida=SAIDA):
    arquivos = sorted(p for p in Path(entrada).glob('*.xlsx') if not p.name.startswith('~$'))
    if not arquivos:
        raise FileNotFoundError('Nenhum arquivo encontrado em dados/entrada_avc.')
    bases = []
    for arquivo in arquivos:
        df = padronizar(pd.read_excel(arquivo))
        df['ARQUIVO_ORIGEM'] = arquivo.name
        df['LINHA_ORIGEM'] = range(2, len(df)+2)
        bases.append(df)
    base, pendencias = transformar(pd.concat(bases, ignore_index=True))
    Path(saida).mkdir(parents=True, exist_ok=True)
    destino = Path(saida)/'consolidado_avc_demo.xlsx'
    with pd.ExcelWriter(destino, engine='openpyxl') as writer:
        base.to_excel(writer, sheet_name='Base', index=False)
        pendencias.to_excel(writer, sheet_name='Pendencias', index=False)
    print(f'AVC: {len(base)} registros; {len(pendencias)} registros com pendências; {destino}')
    return base, pendencias

if __name__ == '__main__':
    executar()

"""Consolida preços unitários mensais fictícios; não soma preços nem calcula consumo."""
import argparse
import math
import re
import unicodedata
from pathlib import Path
from numbers import Real
import pandas as pd

BASE = Path(__file__).resolve().parent.parent
PASTA_ENTRADA = BASE/'dados/entrada_medicamentos'
PASTA_SAIDA = BASE/'dados/saida'
MESES = dict(zip(['JANEIRO','FEVEREIRO','MARÇO','ABRIL','MAIO','JUNHO','JULHO','AGOSTO','SETEMBRO','OUTUBRO','NOVEMBRO','DEZEMBRO'], range(1,13)))
COLUNAS_POR_SECAO = {'IAM':{'TENECTEPLASE 40 mg':3,'TENECTEPLASE 50 mg':7},
                     'AVC':{'ALTEPLASE 10 mg':3,'ALTEPLASE 20 mg':6,'ALTEPLASE 50 mg':9}}
COLUNAS_VALORES = [c for mapa in COLUNAS_POR_SECAO.values() for c in mapa]
COLUNAS_SAIDA = ['ANO','MÊS','MÊS NÚMERO',*COLUNAS_VALORES]

def normalizar(valor):
    return ' '.join(''.join(c for c in unicodedata.normalize('NFKD',str(valor).upper()) if not unicodedata.combining(c)).split())

MESES_NORMALIZADOS = {normalizar(m):(m,n) for m,n in MESES.items()}

def converter_valor(valor):
    if pd.isna(valor) or isinstance(valor, bool):
        return None
    if isinstance(valor, Real):
        numero = float(valor)
    else:
        texto = re.sub(r'\s+', '', str(valor).replace('R$', ''))
        if ',' in texto:
            texto = texto.replace('.', '').replace(',', '.')
        try:
            numero = float(texto)
        except ValueError:
            return None
    return numero if math.isfinite(numero) else None

def consolidar(pasta_entrada=PASTA_ENTRADA, arquivo_saida=PASTA_SAIDA/'dValoresDosagem.xlsx'):
    pasta_entrada, arquivo_saida = Path(pasta_entrada), Path(arquivo_saida)
    arquivos = sorted(p for p in pasta_entrada.glob('*.xlsx') if not p.name.startswith('~$') and p.resolve()!=arquivo_saida.resolve())
    if not arquivos:
        raise FileNotFoundError(f'Nenhum arquivo .xlsx encontrado em: {pasta_entrada}')
    registros, fontes, pendencias = {}, [], []
    vistos = {}
    def problema(origem, aba, linha, ano, mes, nome, motivo, bruto):
        pendencias.append([origem,aba,linha,ano,mes,nome,motivo,str(bruto)])
    for arquivo in arquivos:
        anos = re.findall(r'(?<!\d)(20\d{2})(?!\d)',arquivo.stem)
        if len(anos)!=1:
            raise ValueError(f'O nome deve conter exatamente um ano: {arquivo.name}')
        ano = int(anos[0])
        with pd.ExcelFile(arquivo) as excel:
            for aba in excel.sheet_names:
                secao = None
                df = pd.read_excel(excel,sheet_name=aba,header=None)
                for indice, linha in df.iterrows():
                    valores = linha.tolist()
                    texto = normalizar(' '.join(str(v) for v in valores if pd.notna(v)))
                    iam = 'INFARTO AGUDO DO MIOCARDIO' in texto or 'TENECTEPLASE' in texto
                    avc = 'ACIDENTE VASCULAR CEREBRAL' in texto or 'ALTEPLASE' in texto
                    if iam or avc:
                        secao = None if iam and avc else ('IAM' if iam else 'AVC')
                        continue
                    mes_info = MESES_NORMALIZADOS.get(normalizar(valores[0]))
                    if not secao or not mes_info:
                        continue
                    mes, numero = mes_info
                    registro = registros.setdefault((ano,numero), dict(zip(COLUNAS_SAIDA,[ano,mes,numero,*([None]*5)])))
                    for nome,col in COLUNAS_POR_SECAO[secao].items():
                        if col>=len(valores):
                            raise ValueError(f'{arquivo.name}/{aba}, linha {indice+1}: coluna de {nome} ausente')
                        bruto = valores[col]
                        valor = converter_valor(bruto)
                        chave = (ano,numero,nome)
                        origem = f'{arquivo.name}/{aba}, linha {indice+1}'
                        if chave in vistos:
                            raise ValueError(f'Registro duplicado de {nome}: {vistos[chave]} e {origem}')
                        vistos[chave] = origem
                        if valor is None or valor<0:
                            problema(arquivo.name,aba,indice+1,ano,mes,nome,'Valor ausente, inválido ou negativo',bruto)
                            continue
                        registro[nome] = valor
                        fontes.append([arquivo.name,aba,indice+1,ano,mes,nome,valor])
    base = pd.DataFrame(registros.values(),columns=COLUNAS_SAIDA)
    if base.empty or base[COLUNAS_VALORES].isna().all().all():
        raise ValueError('Nenhum valor unitário mensal foi encontrado.')
    base = base.sort_values(['ANO','MÊS NÚMERO']).reset_index(drop=True)
    for _,r in base.iterrows():
        for nome in COLUNAS_VALORES:
            if (int(r.ANO),int(r['MÊS NÚMERO']),nome) not in vistos:
                problema('', '', None, r.ANO,r['MÊS'],nome,'Seção ou mês não informado','')
    arquivo_saida.parent.mkdir(parents=True,exist_ok=True)
    with pd.ExcelWriter(arquivo_saida,engine='openpyxl') as writer:
        base.to_excel(writer,sheet_name='Valores',index=False)
        pd.DataFrame(fontes,columns=['ARQUIVO_ORIGEM','ABA','LINHA_ORIGEM','ANO','MÊS','MEDICAMENTO','VALOR_UNITARIO_BRL']).to_excel(writer,sheet_name='Origens',index=False)
        pd.DataFrame(pendencias,columns=['ARQUIVO_ORIGEM','ABA','LINHA_ORIGEM','ANO','MÊS','MEDICAMENTO','PROBLEMA','VALOR_ORIGINAL']).to_excel(writer,sheet_name='Pendencias',index=False)
    print(f'Medicamentos: {len(base)} meses; {len(pendencias)} pendências; {arquivo_saida}')
    return base

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--entrada',type=Path,default=PASTA_ENTRADA)
    parser.add_argument('--saida',type=Path,default=PASTA_SAIDA/'dValoresDosagem.xlsx')
    args = parser.parse_args()
    consolidar(args.entrada,args.saida)

if __name__=='__main__':
    main()

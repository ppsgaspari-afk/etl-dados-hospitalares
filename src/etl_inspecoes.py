"""Consolidação conservadora de inspeções no modelo demonstrativo Inspeções."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import uuid
import unicodedata
from datetime import date, datetime, timezone
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "dados/modelos/inspecoes_demo.json"
SCHEMAS = {
    'dInspecoes': ['ID_INSPECAO', 'HOSPITAL', 'SIGLA', 'DATA_AVALIACAO', 'AVALIADOR'],
    'fAvaliacoes': ['ID', 'NOTA', 'ID_INSPEÇÃO', 'ID_CRITERIO', 'DESCRICAO'],
    'dIndicadores': ['ID', 'INDICADOR', 'CRITICIDADE'],
    'dCriterios': ['ID_INDICADOR', 'NOTA', 'DESCRICAO', 'ID_CRITERIO'],
    'dMarcos': ['ID', 'MARCO_REGULATORIO'],
}
HEADERS = ['Nº', 'Indicador', 'Crit', 'Aval', '0', '1', '2', '3', '4', '5', 'Marco Regulatório']
ISSUE_FIELDS = ['NIVEL', 'CODIGO', 'ARQUIVO', 'ABA', 'CELULA', 'MENSAGEM']


def text(value):
    return '' if value is None else str(value).strip()


def norm(value):
    return ' '.join(unicodedata.normalize('NFC', text(value)).split())


def integer(value):
    if isinstance(value, bool) or value is None or text(value) == '':
        raise ValueError('Valor inteiro obrigatório.')
    n = float(str(value).strip().replace(',', '.'))
    if not math.isfinite(n) or not n.is_integer():
        raise ValueError('Valor não inteiro.')
    return int(n)


def inspection_key(sigla, day, evaluator, document):
    # Nome do arquivo e nome abreviado do hospital não participam da identidade.
    return json.dumps([norm(sigla).upper(), day, norm(evaluator).upper(), document],
                      ensure_ascii=False, separators=(',', ':'))


def ler_validar(input_dir, output_dir, config_file=DEFAULT_CONFIG):
    input_dir, output_dir, config_file = map(Path, (input_dir, output_dir, config_file))
    if input_dir.resolve() == output_dir.resolve() or input_dir.resolve() in output_dir.resolve().parents:
        raise ValueError('A saída deve ficar fora da pasta de entrada.')
    cfg = json.loads(config_file.read_text(encoding='utf-8'))
    hospital_records = cfg['hospitais']
    hospitals = {}
    for h in hospital_records:
        s = norm(h['SIGLA']).upper()
        if s:
            if s in hospitals:
                raise ValueError('SIGLA duplicada no cadastro: ' + s)
            hospitals[s] = h
    catalogue = {r['ID']: r for r in cfg['indicadores']}
    criteria = {r['ID_CRITERIO']: r for r in cfg['criterios']}
    marco = {r['ID']: r['MARCO_REGULATORIO'] for r in cfg['marcos']}
    issues, accepted, provenance = [], {}, []
    ids = {v: k for k, v in cfg['ids_existentes'].items()}
    summary = {'inicio_utc': datetime.now(timezone.utc).isoformat(), 'status': 'BLOQUEADO',
               'arquivos': 0, 'abas_validas': 0, 'inspecoes': 0, 'avaliacoes': 0}

    def issue(level, code, file='', sheet='', cell='', message=''):
        issues.append(dict(zip(ISSUE_FIELDS, [level, code, str(file), sheet, cell, message])))

    if not input_dir.is_dir():
        issue('ERRO', 'ENTRADA_AUSENTE', message='Pasta de entrada inexistente.')
        files = []
    else:
        files = sorted(p for p in input_dir.iterdir() if p.is_file() and not p.name.startswith('~$')
                       and p.suffix.lower() in {'.xlsx', '.xlsm', '.xls', '.xlsb'})
    if not files:
        issue('ERRO', 'SEM_ARQUIVOS', message='Nenhum arquivo Excel encontrado; saída anterior preservada.')
    for path in files:
        summary['arquivos'] += 1
        if path.suffix.lower() not in {'.xlsx', '.xlsm'}:
            issue('ERRO', 'FORMATO_NAO_SUPORTADO', path.name, message='Salvar como .xlsx antes de processar.')
            continue
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            wb = openpyxl.load_workbook(path, data_only=False, read_only=True)
        except Exception as exc:
            issue('ERRO', 'ARQUIVO_ILEGIVEL', path.name, message=str(exc))
            continue
        matched = 0
        try:
            for ws in wb:
                rows = list(ws.iter_rows())
                header_rows = [i for i, row in enumerate(rows[:10])
                               if [norm(c.value) for c in row[:11]] == HEADERS]
                if not header_rows:
                    if any(c.value is not None for row in rows for c in row):
                        issue('AVISO', 'ABA_IGNORADA', path.name, ws.title,
                              message='Aba sem cabeçalho do roteiro CC reconhecido.')
                    continue
                matched += 1
                start = len(issues)
                if len(header_rows) != 1:
                    issue('ERRO', 'CABECALHO_AMBIGUO', path.name, ws.title)
                    continue
                hrow = header_rows[0]
                if hrow not in (3, 4):
                    issue('ERRO', 'LINHA_CABECALHO', path.name, ws.title,
                          message='Cabeçalho permitido na linha 4 ou 5.')
                # Localiza rótulos, sem depender de F2/F3/J3/J4 nem preencher mescladas.
                meta = {}
                labels = {'Unidade de Saúde': 'hospital', 'Identificação': 'sigla',
                          'Data': 'data', 'Avaliador': 'avaliador'}
                versions, documents, titles = [], [], []
                for row in rows[:hrow]:
                    for col, cell in enumerate(row):
                        value = cell.value
                        if cell.data_type == 'f':
                            issue('ERRO', 'FORMULA_METADADO', path.name, ws.title, cell.coordinate,
                                  'Metadados devem conter valores explícitos.')
                        raw = text(value)
                        if raw.startswith('Roteiro Objetivo de Inspeção:'):
                            titles.append(norm(raw))
                        if raw.startswith('Documento:'):
                            for line in raw.splitlines():
                                if line.startswith('Documento:'): documents.append(text(line.split(':', 1)[1]))
                                if line.startswith('Versão:'): versions.append(text(line.split(':', 1)[1]))
                        if ':' not in raw:
                            continue
                        label, val = raw.split(':', 1)
                        if label not in labels or '\n' in raw:
                            continue
                        key = labels[label]
                        following = next((c.value for c in row[col + 1:] if c.value is not None), None)
                        resolved = val.strip() if val.strip() else following
                        if key in meta:
                            issue('ERRO', 'METADADO_DUPLICADO', path.name, ws.title, cell.coordinate,
                                  'Rótulo repetido: ' + label)
                        meta[key] = resolved
                if titles != [cfg['titulo']] or versions != [cfg['versao']] or documents != [cfg['documento']]:
                    issue('ERRO', 'MODELO_NAO_APROVADO', path.name, ws.title,
                          message='Título, documento ou versão divergem do modelo configurado.')
                for key in ['hospital', 'sigla', 'data', 'avaliador']:
                    if not text(meta.get(key)):
                        issue('ERRO', 'METADADO_AUSENTE', path.name, ws.title, message=key)
                sigla = norm(meta.get('sigla')).upper()
                if sigla not in hospitals:
                    issue('ERRO', 'SIGLA_DESCONHECIDA', path.name, ws.title, message=sigla)
                day = None
                original_date = meta.get('data')
                if isinstance(original_date, (datetime, date)):
                    day = original_date.date() if isinstance(original_date, datetime) else original_date
                elif isinstance(original_date, str):
                    for pattern in ('%d/%m/%Y', '%Y-%m-%d'):
                        try:
                            day = datetime.strptime(original_date.strip(), pattern).date()
                            break
                        except ValueError:
                            pass
                if day is None:
                    issue('ERRO', 'DATA_INVALIDA', path.name, ws.title,
                          message='Usar data Excel, dd/mm/aaaa ou aaaa-mm-dd.')
                elif not (date(2020, 1, 1) <= day <= date(2030, 12, 31)):
                    issue('ERRO', 'FORA_CALENDARIO_BI', path.name, ws.title,
                          message='Calendário atual do BI cobre 2020 a 2030.')
                seen, notes = set(), {}
                for row in rows[hrow + 1:]:
                    if all(c.value is None for c in row):
                        continue
                    if len(row) < 11:
                        issue('ERRO', 'LINHA_INCOMPLETA', path.name, ws.title, message=str(row[0].row))
                        continue
                    if any(c.data_type == 'f' for c in row):
                        issue('ERRO', 'FORMULA_DADOS', path.name, ws.title, row[0].coordinate,
                              'Fórmulas não são avaliadas; usar valores explícitos.')
                        continue
                    try:
                        ind = integer(row[0].value)
                    except (ValueError, TypeError, OverflowError):
                        issue('ERRO', 'ID_INVALIDO', path.name, ws.title, row[0].coordinate)
                        continue
                    if ind not in catalogue:
                        issue('ERRO', 'INDICADOR_NAO_APROVADO', path.name, ws.title, row[0].coordinate, str(ind))
                        continue
                    if ind in seen:
                        issue('ERRO', 'INDICADOR_DUPLICADO', path.name, ws.title, row[0].coordinate, str(ind))
                    seen.add(ind)
                    checks = [(1, catalogue[ind]['INDICADOR']), (2, catalogue[ind]['CRITICIDADE']),
                              (10, marco[ind])]
                    checks += [(4 + n, criteria[f'{ind}-{n}']['DESCRICAO']) for n in range(6)]
                    for col, approved in checks:
                        if norm(row[col].value) != norm(approved):
                            issue('ERRO', 'CATALOGO_DIVERGENTE', path.name, ws.title, row[col].coordinate,
                                  'Indicador, criticidade, marco ou critério diverge do catálogo aprovado.')
                    try:
                        note = integer(row[3].value)
                        if note not in range(6):
                            raise ValueError('Nota fora de 0–5.')
                        notes[ind] = note
                    except (ValueError, TypeError, OverflowError):
                        issue('ERRO', 'NOTA_INVALIDA', path.name, ws.title, row[3].coordinate,
                              'Nota obrigatória inteira de 0 a 5. Vazio não equivale a zero.')
                if seen != set(catalogue):
                    issue('ERRO', 'INDICADORES_AUSENTES', path.name, ws.title,
                          message=str(sorted(set(catalogue) - seen)))
                if any(x['NIVEL'] == 'ERRO' for x in issues[start:]):
                    continue
                key = inspection_key(sigla, day.isoformat(), meta['avaliador'], cfg['documento'])
                inspection_id = cfg['ids_existentes'].get(key)
                if inspection_id is None:
                    # Inteiro até 52 bits: exato também quando lido como número no Excel.
                    inspection_id = 2 + (int(hashlib.sha256(key.encode('utf8')).hexdigest()[:13], 16)
                                         % ((1 << 52) - 2))
                if inspection_id in ids and ids[inspection_id] != key:
                    issue('ERRO', 'COLISAO_CHAVE', path.name, ws.title, message='Identidades distintas com mesmo ID.')
                    continue
                ids[inspection_id] = key
                record = {'ID_INSPECAO': inspection_id, 'HOSPITAL': text(meta['hospital']), 'SIGLA': sigla,
                          'DATA_AVALIACAO': day.isoformat(), 'AVALIADOR': text(meta['avaliador'])}
                content = {'inspecao': record, 'notas': notes}
                previous = accepted.get(key)
                if previous:
                    if previous != content:
                        issue('ERRO', 'INSPECAO_CONFLITANTE', path.name, ws.title,
                              message='Mesma sigla/data/avaliador/documento com conteúdo diferente. Revisar arquivos.')
                    else:
                        issue('AVISO', 'COPIA_IGNORADA', path.name, ws.title,
                              message='Cópia idêntica da inspeção; não duplica avaliações.')
                else:
                    accepted[key] = content
                provenance.append({'ARQUIVO': path.name, 'ABA': ws.title, 'SHA256': digest,
                                   'ID_INSPECAO': inspection_id, 'LINHA_CABECALHO': hrow + 1})
                summary['abas_validas'] += 1
            if not matched:
                issue('ERRO', 'SEM_ABA_COMPATIVEL', path.name,
                      message='Nenhuma aba reconhecida. Usar o layout e catálogo demonstrativos documentados.')
        except Exception as exc:
            issue('ERRO', 'FALHA_LEITURA', path.name, message=f'{type(exc).__name__}: {exc}')
        finally:
            wb.close()
    tables = {name: [] for name in SCHEMAS}
    tables['dIndicadores'] = cfg['indicadores']
    tables['dCriterios'] = cfg['criterios']
    tables['dMarcos'] = cfg['marcos']
    for content in sorted(accepted.values(), key=lambda c: c['inspecao']['ID_INSPECAO']):
        record = content['inspecao']
        tables['dInspecoes'].append(record)
        for ind, note in sorted(content['notas'].items()):
            ck = f'{ind}-{note}'
            tables['fAvaliacoes'].append({'ID': ind, 'NOTA': note, 'ID_INSPEÇÃO': record['ID_INSPECAO'],
                                         'ID_CRITERIO': ck, 'DESCRICAO': criteria[ck]['DESCRICAO']})
    summary['inspecoes'] = len(tables['dInspecoes'])
    summary['avaliacoes'] = len(tables['fAvaliacoes'])
    summary['erros'] = sum(x['NIVEL'] == 'ERRO' for x in issues)
    summary['avisos'] = sum(x['NIVEL'] == 'AVISO' for x in issues)
    summary['status'] = 'BLOQUEADO' if summary['erros'] else 'VALIDADO'
    summary['tabelas'] = {name: len(rows) for name, rows in tables.items()}
    return tables, issues, provenance, summary


def run(input_dir=ROOT / 'dados/entrada_inspecoes', output_dir=ROOT / 'dados/saida/inspecoes', config_file=DEFAULT_CONFIG):
    tables, issues, provenance, summary = ler_validar(input_dir, output_dir, config_file)
    if summary['erros']:
        print('\nCONSOLIDAÇÃO BLOQUEADA. O Excel anterior foi preservado.\n')
        for problem in issues:
            print(' | '.join(str(problem[c]) for c in ISSUE_FIELDS))
        return 2
    cfg = json.loads(Path(config_file).read_text(encoding='utf8'))
    catalogue = {r['ID']: r for r in cfg['indicadores']}
    criteria = {r['ID_CRITERIO']: r for r in cfg['criterios']}
    marcos = {r['ID']: r['MARCO_REGULATORIO'] for r in cfg['marcos']}
    inspections = {r['ID_INSPECAO']: r for r in tables['dInspecoes']}
    sources = {}
    for origin in provenance:
        sources.setdefault(origin['ID_INSPECAO'], set()).add(origin['ARQUIVO'])
    headers = ['ID_INSPECAO', 'HOSPITAL', 'SIGLA', 'DATA_AVALIACAO', 'AVALIADOR'] + HEADERS + ['ARQUIVO_ORIGEM']
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Consolidado'
    ws.append(headers)
    for fact in tables['fAvaliacoes']:
        ind = fact['ID']
        meta = inspections[fact['ID_INSPEÇÃO']]
        ws.append([meta['ID_INSPECAO'], meta['HOSPITAL'], meta['SIGLA'],
                   date.fromisoformat(meta['DATA_AVALIACAO']), meta['AVALIADOR'],
                   ind, catalogue[ind]['INDICADOR'], catalogue[ind]['CRITICIDADE'], fact['NOTA'],
                   *[criteria[f'{ind}-{n}']['DESCRICAO'] for n in range(6)], marcos[ind],
                   ' | '.join(sorted(sources[meta['ID_INSPECAO']]))])
    table = Table(displayName='tbConsolidado', ref=f'A1:Q{ws.max_row}')
    table.tableStyleInfo = TableStyleInfo(name='TableStyleMedium2', showRowStripes=True)
    ws.add_table(table)
    # Os critérios longos permanecem completos, com colunas agrupadas para consulta.
    ws.column_dimensions.group('J', 'P', hidden=True)
    widths = {'A': 20, 'B': 46, 'C': 15, 'D': 21, 'E': 18, 'F': 9, 'G': 53, 'H': 10, 'I': 9, 'Q': 55}
    for col in 'JKLMNOP':
        widths[col] = 65
    for col, width in widths.items():
        ws.column_dimensions[col].width = width
    ws.freeze_panes = 'D2'
    ws.sheet_view.zoomScale = 85
    for row in ws.iter_rows(min_row=2):
        row[0].number_format = '0'
        row[3].number_format = 'dd/mm/yyyy'
        ws.row_dimensions[row[0].row].height = 65
    validation = wb.create_sheet('Validacao')
    validation.append(ISSUE_FIELDS)
    if issues:
        for issue in issues:
            validation.append([issue[c] for c in ISSUE_FIELDS])
    else:
        validation.append(['INFO', 'SEM_INCONSISTENCIAS', '', '', '',
                           f"{summary['inspecoes']} inspeção(ões); {summary['avaliacoes']} avaliações. Sem inconsistências."])
    for col, width in zip('ABCDEF', [12, 30, 60, 20, 14, 90]):
        validation.column_dimensions[col].width = width
    validation.freeze_panes = 'A2'
    origin_sheet = wb.create_sheet('Origens')
    origin_fields = ['ARQUIVO', 'ABA', 'SHA256', 'ID_INSPECAO', 'LINHA_CABECALHO']
    origin_sheet.append(origin_fields)
    for origin in provenance:
        origin_sheet.append([origin[k] for k in origin_fields])
    origin_sheet.freeze_panes = 'A2'
    for col in 'ABCDE':
        origin_sheet.column_dimensions[col].width = 30
    for sheet in wb:
        sheet.sheet_view.showGridLines = False
        for row in sheet:
            for cell in row:
                # Texto de origem nunca se transforma em fórmula de Excel.
                if isinstance(cell.value, str):
                    cell.data_type = 's'
                cell.font = Font(name='Arial', size=10, color='1F2937')
                cell.alignment = Alignment(vertical='top', wrap_text=True)
        for cell in sheet[1]:
            cell.font = Font(name='Arial', size=10, bold=True, color='FFFFFF')
            cell.fill = PatternFill('solid', fgColor='24476A')
            cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        sheet.row_dimensions[1].height = 32
    validation.row_dimensions[2].height = 40
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / 'Consolidado.xlsx'
    temporary = output_dir / ('.consolidado_' + uuid.uuid4().hex + '.xlsx')
    try:
        wb.save(temporary)
        wb.close()
        os.replace(temporary, target)
    except PermissionError:
        print('Não foi possível atualizar. Feche o Consolidado.xlsx no Excel e tente novamente.')
        return 2
    finally:
        wb.close()
        if temporary.exists():
            temporary.unlink()
    print(f"CONCLUÍDO: {summary['inspecoes']} inspeção(ões), {summary['avaliacoes']} avaliações.\n{target}")
    return 0


def main():
    parser = argparse.ArgumentParser(description='Consolida os roteiros CC em um único Excel para o BI Inspeções.')
    parser.add_argument('--entrada', type=Path, default=ROOT / 'dados/entrada_inspecoes')
    parser.add_argument('--modelo', type=Path, default=DEFAULT_CONFIG)
    parser.add_argument('--saida', type=Path, default=ROOT / 'dados/saida/inspecoes')
    args = parser.parse_args()
    return run(args.entrada, args.saida, args.modelo)


if __name__ == '__main__':
    raise SystemExit(main())

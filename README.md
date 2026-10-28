# ETL de Dados Hospitalares | Python

**Pipeline de Engenharia de Dados para extração, transformação, padronização e validação de informações hospitalares.**

Projeto de portfólio desenvolvido em Python, com foco na automação do processamento de planilhas Excel, consolidação de bases e identificação de inconsistências.

A solução demonstra práticas de Engenharia de Dados aplicadas a quatro conjuntos de informações: Infarto Agudo do Miocárdio (IAM), Acidente Vascular Cerebral (AVC), preços unitários de medicamentos e inspeções hospitalares (Inspeções).

> **Privacidade:** projeto demonstrativo independente, desenvolvido exclusivamente com dados sintéticos, sem informações reais de pacientes ou código institucional restrito.

## Objetivo

Demonstrar como processos ETL (*Extract, Transform, Load*) podem transformar planilhas heterogêneas em bases estruturadas, rastreáveis e adequadas para análises posteriores.

O projeto aborda problemas frequentes no tratamento de dados:

- Divergências na nomenclatura e estrutura das colunas.
- Necessidade de consolidar múltiplos arquivos Excel.
- Campos ausentes, valores inválidos e inconsistências.
- Dificuldade de identificar a origem de registros.
- Processos manuais repetitivos de preparação de dados.

## Arquitetura do pipeline

```text
Planilhas Excel (dados sintéticos)
               |
               v
         EXTRAÇÃO
      Leitura dos arquivos
               |
               v
       TRANSFORMAÇÃO
   Normalização e padronização
               |
               v
          VALIDAÇÃO
    Verificação de qualidade
               |
               v
         CONSOLIDAÇÃO
      Integração dos dados
               |
               v
          EXPORTAÇÃO
    Arquivos Excel tratados
    + relatórios de pendências
```

## Módulos desenvolvidos

| Módulo | Funcionalidade principal |
|---|---|
| IAM | Padronização de colunas e consolidação de registros de atendimento |
| AVC | Consolidação, rastreabilidade, verificação de inconsistências e sinalização de possíveis duplicidades |
| Medicamentos | Consolidação histórica de preços unitários, identificação de origens e geração de pendências |
| Inspeções | Consolidação de inspeções, bloqueio de inconsistências e rastreabilidade por SHA-256 |

## Tecnologias utilizadas

**Python 3.12** para implementação dos processos de ETL.

**Pandas** para manipulação, transformação e consolidação dos dados.

**OpenPyXL** para leitura e escrita de arquivos Excel.

**Unittest** para testes automatizados.

**GitHub Actions** para execução automatizada dos testes e dos quatro módulos.

## Resultados demonstrativos

Os arquivos sintéticos incluídos no projeto permitem verificar o comportamento dos pipelines.

| Módulo | Resultado esperado dos exemplos |
|---|---|
| IAM | 20 registros consolidados |
| AVC | 8 registros, com 7 registros apresentando pendências e 2 sinalizados como possíveis duplicatas |
| Medicamentos | 6 meses de referência, 28 valores aceitos e 2 pendências |
| Inspeções | 2 inspeções fictícias, 40 avaliações, sem pendências |

As inconsistências foram incluídas intencionalmente nos exemplos para demonstrar os mecanismos de validação e auditoria.

## Competências demonstradas

- Desenvolvimento de pipelines ETL com Python.
- Tratamento e padronização de dados estruturados.
- Automação de processos com planilhas Excel.
- Validação da qualidade e rastreabilidade dos dados.
- Tratamento de exceções e inconsistências.
- Testes automatizados e integração contínua.

---

## Documentação técnica

As próximas seções apresentam os requisitos, a estrutura das entradas, as instruções de execução, as regras de validação e as limitações de cada módulo.

Na raiz do projeto, instale as dependências e execute:

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python src/etl_iam.py
python src/etl_avc.py
python src/etl_medicamentos.py
python src/etl_inspecoes.py
```

No Windows, use `py` se necessário. O workflow `ETL completo` executa esses mesmos
passos em pushes, pull requests ou execução manual. Os resultados ficam no artefato
`resultados-etl`; o workflow não faz commit das saídas.

## Inspeções hospitalares — Inspeções

Versão de portfólio baseada no motor de validação do pacote Inspeções. O catálogo
`dados/modelos/inspecoes_demo.json` e as duas entradas foram criados para demonstração:
2 hospitais fictícios, 2 avaliadores fictícios, 20 indicadores por inspeção e notas
inteiras de 0 a 5. Resultado esperado: 2 inspeções e 40 avaliações, sem pendências.
Os critérios e referências são fictícios, sem valor clínico ou normativo.
O pacote institucional original e seu consolidado não fazem parte desta integração.

```sh
python src/etl_inspecoes.py
python src/etl_inspecoes.py --entrada dados/entrada_inspecoes --saida dados/saida/inspecoes --modelo dados/modelos/inspecoes_demo.json
```

Execute na raiz do repositório. Os caminhos padrão independem da pasta atual.
`dados/saida/inspecoes/Consolidado.xlsx` contém `Consolidado`, `Validacao` e `Origens`
(arquivo, aba, SHA-256, ID e linha do cabeçalho). O hash identifica o arquivo lido;
não anonimiza seus dados. A tabela interna de avaliações não é exportada como aba.

O cabeçalho deve estar na linha 4 ou 5, com 11 colunas na ordem dos exemplos.
Título, documento, versão, indicadores, critérios e referências devem corresponder
ao JSON. Metadados obrigatórios: unidade, sigla cadastrada, data e avaliador.
Datas aceitas: Excel, dd/mm/aaaa ou aaaa-mm-dd, de 2020 a 2030.
Fórmulas, notas vazias, fracionárias ou fora de 0–5 bloqueiam a carga.
Zero é uma nota válida. Abas não reconhecidas geram aviso; arquivo sem aba
compatível bloqueia a carga. Formatos aceitos: xlsx e xlsm (macros não executadas).

Sigla, data, avaliador e documento formam a identidade estável da inspeção.
Cópias idênticas são ignoradas; versões conflitantes bloqueiam toda a carga.
Duas visitas com a mesma identidade exigem extensão do modelo. Em caso de erro,
o processo retorna código 2 e mantém o consolidado anterior. O relatório do erro
aparece no terminal; a aba Validacao anterior continua pertencendo à carga anterior.
A saída é reconstruída de todas as entradas, sem acumular o histórico anterior.
A substituição do Excel usa arquivo temporário e troca atômica.

O JSON é configuração confiável e deve passar por revisão antes de ser alterado.
O cadastro demonstra validação de sigla; não verifica a correspondência entre o
nome livre do hospital e seu nome cadastrado. A integração não inclui PBIX nem
comprova compatibilidade com consultas de um BI institucional.
Não substitua os exemplos por inspeções reais em uma cópia destinada ao GitHub.

# ETL de Dados Hospitalares — IAM

Projeto demonstrativo em Python para leitura, padronização e consolidação de planilhas Excel no contexto de infarto agudo do miocárdio (IAM).

**Todos os dados de exemplo são inteiramente sintéticos. O projeto não utiliza dados pessoais, informações de pacientes ou código institucional restrito.**

## Objetivo

Demonstrar um processo de ETL — extração, transformação e carga — que reúne arquivos com cabeçalhos diferentes em uma base padronizada.

## Funcionalidades

- Leitura de arquivos `.xlsx` na pasta `dados/entrada`.
- Normalização dos cabeçalhos, removendo acentos e espaços excedentes.
- Mapeamento de nomes alternativos, como `Hospital` e `Unidade de Saúde`, para `UNIDADE`.
- Conversão de datas e campos numéricos.
- Inclusão de colunas ausentes.
- Identificação do arquivo de origem de cada registro.
- Exportação dos dados consolidados para Excel.
- Execução manual pelo GitHub Actions.

## Tecnologias

- Python
- pandas
- openpyxl
- GitHub Actions

## Estrutura

```text
etl-dados-hospitalares/
├── .github/
│   └── workflows/
│       └── etl-demo.yml
├── dados/
│   ├── entrada/
│   │   ├── iam_sintetico_alfa.xlsx
│   │   └── iam_sintetico_beta.xlsx
│   └── saida/
│       └── consolidado_iam_demo.xlsx
├── src/
│   └── etl_iam.py
├── requirements.txt
└── README.md
```

## Dados de exemplo

As duas planilhas contêm 10 atendimentos fictícios cada, com cabeçalhos diferentes para testar a padronização.

| Campo final | Descrição |
| --- | --- |
| UNIDADE | Unidade fictícia |
| REGIAO | Região fictícia |
| DATA | Data do atendimento fictício |
| FAIXA_ETARIA | Faixa etária em anos |
| SEXO | Categoria sintética M/F |
| TEMPO_PORTA_ECG | Tempo sintético em minutos |
| TEMPO_ECG_AGULHA | Tempo sintético em minutos |
| ARQUIVO_ORIGEM | Nome da planilha de entrada |

Os valores servem apenas para testar o software e não representam indicadores clínicos reais.

## Executar no GitHub

1. Abra a aba **Actions**.
2. Selecione **ETL demonstrativo**.
3. Clique em **Run workflow** e confirme.
4. Aguarde a conclusão com a marca verde.
5. Abra o resumo da execução.
6. Em **Artifacts**, baixe **consolidado-iam-demo**.
7. Extraia o ZIP e abra a planilha gerada.

O resultado fica disponível para download na execução. O fluxo não faz commit automático da saída no repositório.

## Executar localmente

Com Python 3.12 instalado, baixe o repositório, extraia os arquivos e abra um terminal na pasta principal.

Instale as dependências:

```sh
python -m pip install -r requirements.txt
```

Execute o pipeline:

```sh
python src/etl_iam.py
```

No Windows, caso `python` não seja reconhecido, utilize `py`.

A saída será salva em:

```text
dados/saida/consolidado_iam_demo.xlsx
```

## Resultado validado

O pipeline foi executado localmente e pelo GitHub Actions. Com as duas entradas de exemplo, o resultado contém:

- 20 registros consolidados.
- 8 colunas padronizadas.
- Identificação da origem de cada registro.

Na validação local, datas, tempos e demais valores foram comparados com os dados sintéticos esperados.

## Comportamento e limitações

- Apenas a primeira aba de cada arquivo é lida.
- Datas e números inválidos são convertidos em valores ausentes.
- Colunas esperadas que não existem na entrada são preenchidas com valores ausentes.
- Colunas extras são descartadas.
- Cabeçalhos que resultam na mesma coluna após o mapeamento geram erro.
- Registros duplicados não são removidos automaticamente.
- Não há validação de regras clínicas ou faixas de valores.
- Uma nova execução substitui o arquivo consolidado no ambiente de execução.

## Uso dos exemplos

Mantenha somente planilhas sintéticas em `dados/entrada`. Preserve os cabeçalhos na primeira linha e mantenha os arquivos consolidados fora dessa pasta.

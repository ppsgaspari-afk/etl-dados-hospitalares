# ETL de Dados Hospitalares — IAM

Projeto demonstrativo em Python para leitura, padronização e consolidação de planilhas Excel no contexto de infarto agudo do miocárdio (IAM).

**Todos os dados de exemplo são inteiramente sintéticos. O projeto não utiliza dados pessoais, informações de pacientes ou código institucional restrito.**

## Objetivo

Demonstrar um processo de ETL — extração, transformação e carga — que reúne arquivos com cabeçalhos diferentes em uma base padronizada.

## Funcionalidades

- Leitura de arquivos `.xlsx` na pasta `dados/entrada`.
- Normalização dos cabeçalhos, removendo acentos e espaços excedentes.
- Mapeamento de nomes alternativos, como

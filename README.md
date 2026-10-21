# ETL de Dados Hospitalares | Python

**Pipeline de Engenharia de Dados para extração, transformação, padronização e validação de informações hospitalares.**

Projeto de portfólio desenvolvido em Python, com foco na automação do processamento de planilhas Excel, consolidação de bases e identificação de inconsistências.

A solução demonstra práticas de Engenharia de Dados aplicadas a três conjuntos de informações: Infarto Agudo do Miocárdio (IAM), Acidente Vascular Cerebral (AVC) e preços unitários de medicamentos.

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

## Tecnologias utilizadas

**Python 3.12** para implementação dos processos de ETL.

**Pandas** para manipulação, transformação e consolidação dos dados.

**OpenPyXL** para leitura e escrita de arquivos Excel.

**Unittest** para testes automatizados.

**GitHub Actions** para execução automatizada dos testes e dos três módulos.

## Resultados demonstrativos

Os arquivos sintéticos incluídos no projeto permitem verificar o comportamento dos pipelines.

| Módulo | Resultado esperado dos exemplos |
|---|---|
| IAM | 20 registros consolidados |
| AVC | 8 registros, com 7 registros apresentando pendências e 2 sinalizados como possíveis duplicatas |
| Medicamentos | 6 meses de referência, 28 valores aceitos e 2 pendências |

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

# ETL de Dados Hospitalares

Projeto de portfólio em Python para padronização de planilhas, consolidação de registros e geração de relatórios de qualidade de dados.

Os módulos demonstram processos de IAM, AVC e preços unitários de medicamentos. **Todos os exemplos são sintéticos. Não há dados de pacientes nem código institucional restrito.**

## Módulos

| Módulo | Entrada | Resultado |
| --- | --- | --- |
| IAM | `dados/entrada/*.xlsx` | Base padronizada com arquivo de origem |
| AVC | `dados/entrada_avc/*.xlsx` | Base, origem de cada linha, possíveis duplicidades e pendências |
| Medicamentos | `dados/entrada_medicamentos/*.xlsx` | Preços por ano/mês, rastreabilidade e pendências |

Tecnologias: Python 3.12, pandas, openpyxl, unittest e GitHub Actions.

## Executar localmente

Abra o terminal na raiz do projeto e execute:

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python src/etl_iam.py
python src/etl_avc.py
python src/etl_medicamentos.py
```

No Windows, use `py` em lugar de `python` se necessário.

Os resultados ficam em `dados/saida/`. Uma nova execução substitui os respectivos arquivos de saída. Não coloque os consolidados nas pastas de entrada.

## Executar no GitHub

O arquivo `.github/workflows/etl-completo.yml` executa os testes e os três módulos. Após salvar os arquivos na branch padrão:

1. Abra **Actions → ETL completo**.
2. Clique em **Run workflow** e confirme.
3. Aguarde a conclusão.
4. Abra o resumo e baixe **resultados-etl** na seção **Artifacts**.

Os arquivos são disponibilizados para download. O workflow não faz commit automático dos resultados. Também é executado em pushes e pull requests.

## Formato das entradas de AVC

A primeira linha deve conter cabeçalhos e os dados devem estar na primeira aba. Cada linha é um atendimento fictício. Tempos em minutos, datas em dia/mês/ano ou como datas do Excel e faixa etária em anos.

| Coluna final | Cabeçalhos alternativos |
| --- | --- |
| UNIDADE | Hospital; Unidade de Saúde |
| DATA | Data Atendimento |
| FAIXA_ETARIA | Idade Grupo |
| TEMPO_PORTA_TOMOGRAFIA | Porta Tomografia |
| TEMPO_PORTA_AGULHA | Porta Agulha |

O mapeamento ignora acentos, caixa e espaços excedentes nos cabeçalhos. Cabeçalhos duplicados após mapeamento interrompem o processamento.

O arquivo `consolidado_avc_demo.xlsx` contém:

- **Base:** todos os registros, `ARQUIVO_ORIGEM`, `LINHA_ORIGEM` e `POSSIVEL_DUPLICATA`.
- **Pendencias:** arquivo, número da linha no Excel de origem e motivos para revisão.

São sinalizados campos obrigatórios ausentes, datas inválidas, tempos ausentes, inválidos, negativos ou não finitos e porta-agulha inferior a porta-tomografia. Esta última regra é uma verificação demonstrativa de cronologia, não um protocolo clínico. Nenhum limite clínico foi estabelecido.

Possíveis duplicidades são coincidências de unidade, data e faixa etária, com normalização de texto e apenas chaves completas. Pessoas distintas podem compartilhar esses atributos. **O sinalizador não comprova duplicidade e não exclui registros.**

## Formato das entradas de medicamentos

O nome do arquivo precisa conter exatamente um ano entre 2000 e 2099, como `valores_sinteticos_2026.xlsx`. Todas as abas são lidas, sem cabeçalho fixo. A primeira coluna contém os meses por extenso.

O layout posicional demonstrativo é:

| Seção identificada pelo título | Coluna Excel | Preço unitário em BRL |
| --- | --- | --- |
| IAM / Infarto Agudo do Miocárdio / Tenecteplase | D | TENECTEPLASE 40 mg |
| IAM | H | TENECTEPLASE 50 mg |
| AVC / Acidente Vascular Cerebral / Alteplase | D | ALTEPLASE 10 mg |
| AVC | G | ALTEPLASE 20 mg |
| AVC | J | ALTEPLASE 50 mg |

O título da seção deve estar em uma linha anterior aos meses. Uma linha TOTAL não encerra a leitura. Linhas com títulos das duas seções simultaneamente suspendem a identificação até o próximo título inequívoco. Os arquivos de exemplo demonstram esse layout.

O arquivo `dValoresDosagem.xlsx` contém:

- **Valores:** uma linha por ano/mês encontrado e cinco preços unitários.
- **Origens:** arquivo, aba e linha dos valores aceitos.
- **Pendencias:** valores vazios, inválidos, negativos ou campos sem seção correspondente em um mês encontrado.

Aceita números e textos monetários brasileiros, como `R$ 1.234,56`. Valores inválidos ficam em branco, sem substituição por zero. Zero é preservado. Repetições de ano/mês/medicamento interrompem o processamento, mesmo quando o primeiro valor é inválido. Não são somados preços, não é calculado consumo e não há escolha automática entre preços repetidos.

## Exemplos e resultados esperados

| Conjunto sintético | Resultado esperado |
| --- | --- |
| IAM: 2 arquivos | 20 registros |
| AVC: 2 arquivos | 8 registros; 7 registros com pendências; 2 possíveis duplicatas |
| Medicamentos: 2 arquivos | 6 meses, janeiro a março de 2025 e 2026; 28 valores aceitos; 2 pendências |

As entradas de AVC e medicamentos incluem erros deliberados para demonstrar a revisão de qualidade. Pendências não impedem a exportação quando existem dados processáveis. Erros estruturais, como cabeçalhos duplicados ou preços repetidos, interrompem a execução.

## Testes automatizados

```sh
python -m unittest discover -s tests -v
```

A suíte cobre aliases, campos ausentes, cabeçalhos duplicados, conversão de datas e preços, tempos negativos, cronologia, origem das pendências, duplicidades, ano ausente, pasta vazia e leitura dos resultados exportados. Veja `VALIDACAO.md` para os resultados da execução local.

## Limitações

- IAM e AVC leem somente a primeira aba.
- O IAM mantém a lógica demonstrativa já validada, sem relatório de pendências.
- O layout de medicamentos depende das posições documentadas; mudanças na estrutura exigem ajuste do mapeamento.
- Os meses completamente ausentes de todas as entradas não são criados nem sinalizados.
- As verificações tratam qualidade de dados e não fornecem recomendações clínicas ou financeiras.
- Entradas originais são preservadas. Datas e números inválidos podem aparecer vazios na base exportada; as pendências apontam a origem para conferência.

## Segurança e privacidade

Este repositório foi preparado para uso com dados inteiramente sintéticos. Não envie nomes, prontuários, documentos, dados reais de pacientes ou código de sistemas institucionais.

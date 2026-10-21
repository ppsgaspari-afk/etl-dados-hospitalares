# Exemplos sintéticos para etl-dados-hospitalares

Este pacote contém duas planilhas com 10 atendimentos fictícios cada, o script demonstrativo fornecido pelo usuário (com a mesma lógica), a saída de uma execução local e o relatório de validação. Não contém dados pessoais nem código institucional restrito.

## Arquivos de entrada

Coloque os dois arquivos .xlsx em `dados/entrada/`. Mantenha a primeira linha como cabeçalho e os dados na primeira aba. Não coloque o consolidado nessa pasta.

| Coluna final | Arquivo Alfa | Arquivo Beta |
| --- | --- | --- |
| UNIDADE | hospital (com espaços nas pontas) | Unidade de Saúde |
| REGIAO | Região de Saúde | REGIÃO |
| DATA | Data Atendimento | DATA |
| FAIXA_ETARIA | Idade Grupo | FAIXA_ETARIA |
| SEXO | Gênero | SEXO |
| TEMPO_PORTA_ECG | Porta ECG | Tempo Porta ECG |
| TEMPO_ECG_AGULHA | ECG Agulha | Tempo ECG Agulha |

Cada linha é um atendimento sintético. Datas são valores de data do Excel. Tempos são números em minutos. M/F são categorias de teste. Faixas etárias são rótulos em anos. Unidades e regiões são fictícias. As duas planilhas têm dados diferentes para testar a consolidação.

## Executar no computador

1. Instale Python 3.11 ou superior.
2. Extraia o ZIP e abra um terminal na pasta `pacote_iam`, onde está este arquivo. Se estiver usando o repositório existente, copie os arquivos mantendo as mesmas pastas e abra o terminal na raiz dele.
3. Execute:

```sh
python -m pip install -r requirements.txt
python src/etl_iam.py
```

No Windows, se `python` não for reconhecido, use `py` nos dois comandos.

O terminal deve informar `Registros processados: 20`. Abra `dados/saida/consolidado_iam_demo.xlsx`: serão 20 linhas de dados e 8 colunas, incluindo `ARQUIVO_ORIGEM`, com 10 linhas de cada entrada. O script substitui esse arquivo ao executar novamente. A saída já incluída no pacote foi gerada nesta sessão.

## Enviar ao GitHub

1. Abra seu repositório `etl-dados-hospitalares` e vá à aba **Code**.
2. Na raiz, escolha **Add file > Upload files**. Arraste as pastas extraídas `src` e `dados`, além de `requirements.txt`, `LEIA-ME.md` e `VALIDACAO.md`. Preserve os caminhos. Pode enviar somente `dados/entrada` se preferir gerar a saída ao executar.
3. Confira os arquivos listados e clique em **Commit changes**. Se `src/etl_iam.py` já tiver o código fornecido, mantenha essa versão existente.
4. Para baixar e executar no computador, use **Code > Download ZIP**, extraia e siga os comandos acima na raiz do projeto.

## Executar dentro do GitHub

O upload por si só não executa Python. Para habilitar uma execução manual:

1. Use **Add file > Create new file** na raiz do repositório.
2. Dê o nome `.github/workflows/etl-demo.yml` e cole o conteúdo de `etl-demo.yml` incluído na raiz deste pacote. Confirme o commit na branch padrão.
3. Abra **Actions > ETL demonstrativo > Run workflow > Run workflow**. O repositório precisa permitir GitHub Actions.
4. Após concluir, abra a execução e baixe o artefato `consolidado-iam-demo`. O fluxo gera a saída em um ambiente temporário e a disponibiliza para download; não faz commit da saída.

Envie apenas os exemplos sintéticos deste pacote. O arquivo `etl-demo.yml` na raiz é um modelo: só será executável pelo GitHub quando salvo no caminho `.github/workflows/etl-demo.yml`.

Referências oficiais: [execução manual de workflows](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow) e [Python no GitHub Actions](https://docs.github.com/en/actions/tutorials/build-and-test-code/python).

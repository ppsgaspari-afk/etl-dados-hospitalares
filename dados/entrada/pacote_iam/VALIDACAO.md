# Validação do ETL demonstrativo

Execução local realizada em 21/10/2026 com Python 3.12.14, pandas 3.0.1 e openpyxl 3.1.5.

- Duas entradas Excel lidas, com 10 linhas cada.
- Saída conferida: 20 linhas e 8 colunas, na ordem esperada.
- Todos os valores, datas e arquivos de origem comparados com o conjunto sintético esperado.
- Nenhum campo vazio nas entradas ou na saída de demonstração.
- Datas preservadas como datas e tempos preservados como números.
- Cabeçalhos alternativos, acentos, espaços e caixa reconhecidos.
- Testes adicionais em memória: data/número inválidos tornam-se ausentes; número em texto é convertido; coluna ausente é preenchida; cabeçalhos duplicados após mapeamento são rejeitados.
- Pasta sem arquivos gera FileNotFoundError.
- As duas entradas foram renderizadas e revisadas visualmente.

Somatórios de controle: TEMPO_PORTA_ECG = 200 minutos; TEMPO_ECG_AGULHA = 590 minutos.

As entradas são inteiramente sintéticas. Cada linha representa um atendimento fictício. Tempos em minutos; M e F são categorias de teste. Não há nomes, documentos, prontuários ou unidades reais. Nenhum resultado representa indicador clínico real.

Limites do script fornecido: lê apenas a primeira aba; não remove linhas duplicadas; não valida faixas clínicas, categorias ou valores negativos; converte entradas inválidas em ausentes. A validação acima verifica comportamento de software, sem avaliação clínica. O GitHub Actions foi preparado, mas não executado em uma conta GitHub nesta sessão.

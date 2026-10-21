# Validação local — 21/10/2026

Ambiente: Python 3.12.14, pandas 3.0.1, openpyxl 3.1.5.

Os três scripts foram executados com sucesso com as entradas sintéticas incluídas. A suíte automatizada passou com 13 testes. O novo workflow foi preparado para GitHub Actions, mas ainda não foi executado no repositório remoto nesta sessão.

| Módulo | Resultado |
| --- | --- |
| IAM | 20 registros; somas de controle 200 e 590 minutos |
| AVC | 8 registros preservados; 7 registros com pendências; 2 possíveis duplicatas |
| Medicamentos | 6 meses; 28 valores aceitos; 2 pendências |

As quatro novas entradas Excel foram renderizadas e revisadas. Os arquivos de saída foram abertos novamente pelos testes para verificar abas e contagens. Erros deliberados nos exemplos exercitam conversão inválida, campo vazio, tempo negativo, cronologia inconsistente e coincidência de chaves.

## Ajustes no código de AVC fornecido

- Pendências agora apontam a linha do Excel de origem, mesmo após concatenar arquivos.
- Incluída faixa etária ausente e tempo não finito nas verificações.
- Incluída revisão de cronologia quando porta-agulha é inferior a porta-tomografia, sem limites clínicos.
- Coincidências usam texto normalizado e exigem chaves completas. Também aparecem nas pendências.
- Nenhum registro é excluído automaticamente.

## Ajustes no código de medicamentos fornecido

- Entrada exclusiva `dados/entrada_medicamentos`, separada do IAM.
- Preços permanecem unitários mensais, sem soma ou cálculo de consumo.
- Saída inclui rastreabilidade dos preços aceitos e relatório de pendências persistente.
- Valores negativos são sinalizados e permanecem vazios na saída. Zero é aceito.
- Nome deve conter exatamente um ano; repetições de ano/mês/medicamento são rejeitadas mesmo se o primeiro valor não for válido.
- Mapeamento posicional documentado no README como formato demonstrativo. Não depende de acesso a imagens ou sistemas institucionais.

## Limites

Os testes comprovam o comportamento para os casos descritos e o layout sintético. Não comprovam compatibilidade com qualquer planilha externa nem validam protocolos clínicos ou preços reais. Os três módulos usam somente dados sintéticos.

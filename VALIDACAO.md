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


## Integração Inspeções — 28/10/2026

Base inspecionada: `311fbb0b7e857753b069d70b511341db042bcf6e`.
Ambiente desta revisão: Python 3.13.15, pandas 3.0.5, openpyxl 3.1.5.
20 testes aprovados: 13 existentes e 7 novos (com subcasos).
Os quatro comandos de execução foram concluídos com sucesso.
IAM: 20 registros. AVC: 8 registros, 7 com pendências. Medicamentos: 6 meses,
2 pendências. Inspeções: 2 inspeções, 40 avaliações, sem erros ou avisos.
Os scripts, testes e dados preexistentes foram preservados byte a byte;
as saídas preexistentes foram restauradas após os testes, sem incluí-las na alteração.

O Inspeções cobre exportação/reabertura, hashes, notas inválidas e fórmulas,
preservação da saída anterior, cópias idênticas/conflitantes, IDs estáveis,
metadados, catálogo divergente, entrada vazia e pasta de saída inválida.
As novas entradas foram geradas do zero, sem reaproveitar o Excel original.
O catálogo de publicação também foi recriado com textos fictícios.

O ZIP de origem não era inteiramente sintético: continha cadastro institucional,
CNES, identificação de avaliador, data e notas de inspeção, além de nomes em
propriedades do Excel. Não é possível atestar se as notas são reais; o pacote
original foi excluído da proposta pública. Nenhum nome pessoal, cadastro real,
CNES ou chave histórica foi transferido para os novos exemplos.
Não foram identificados segredos nos novos arquivos revisados. Esta revisão não
é uma auditoria de todo o histórico Git nem comprova direitos de publicação do
código original; o responsável deve confirmar sua autorização antes de publicar.

Dependências: o módulo novo utiliza apenas openpyxl (já fixado em 3.1.5) e a
biblioteca padrão. requirements.txt foi preservado. A instalação isolada de
pandas 3.0.1 falhou por restrição de acesso a arquivos temporários locais;
por isso os testes desta sessão usam pandas 3.0.5. Python 3.12 com pandas 3.0.1
permanece pendente de confirmação pelo workflow. Não foi feita auditoria de
vulnerabilidades das dependências. GitHub Actions foi atualizado, sem execução
remota nesta sessão. Nenhum push, commit remoto ou pull request foi criado.

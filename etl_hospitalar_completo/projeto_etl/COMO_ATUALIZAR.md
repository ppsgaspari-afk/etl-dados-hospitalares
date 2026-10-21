# Atualizar o repositório existente

1. Extraia o ZIP no computador.
2. No GitHub, abra o repositório e vá à aba **Code**, na raiz.
3. Escolha **Add file → Upload files**.
4. De dentro da pasta `projeto_etl`, arraste as pastas `src`, `tests` e `dados`, mais `README.md`, `requirements.txt` e `VALIDACAO.md`. Não arraste a pasta externa `projeto_etl`, pois ela criaria um nível extra.
5. Confira que aparecem caminhos como `src/etl_avc.py` e `dados/entrada_avc/avc_alfa.xlsx`. Confirme o commit. O IAM deste pacote tem a mesma lógica demonstrativa anterior.
6. Para adicionar o novo workflow, use **Add file → Create new file**. Nome: `.github/workflows/etl-completo.yml`. Cole o conteúdo do arquivo de mesmo nome dentro da pasta `.github/workflows` do pacote e confirme na branch padrão. Essa pasta pode estar oculta no computador.
7. Abra **Actions → ETL completo → Run workflow**. Ao concluir, baixe **resultados-etl** no resumo da execução.

Pode manter o antigo `ETL demonstrativo`: ele continua executando somente o IAM. O novo `ETL completo` executa testes e os três módulos.

Pendências nos exemplos são intencionais: não é esperado que os relatórios venham vazios. Não envie arquivos reais ou institucionais.

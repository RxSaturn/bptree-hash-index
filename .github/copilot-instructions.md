# Copilot Instructions - B+ Tree e Hash Extensível

## Contexto
Este repositório contém a implementação de índices B+ Tree e Hash Extensível
em Python para trabalho acadêmico do IFMG.

## Regras

### Código Python
- Use type hints em todas as funções
- Docstrings em formato Google/NumPy
- Siga PEP 8
- Testes unitários com pytest

### B+ Tree
- Nós folha devem ser encadeados (next/prev)
- Valores apenas nos nós folha
- Suporta range_search

### Hash Extensível
- Gerenciar global_depth e local_depth
- NÃO implementar range_search (hash não suporta)
- Bucket splitting quando cheio

### Experimentos
- Usar SIOgen para gerar dados
- Métricas: tempo, page reads/writes, splits
- Salvar resultados em CSV

Consulte docs/master-prompt. md para instruções detalhadas.

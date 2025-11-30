# 🌳 Índices B+ Tree e Hash Extensível

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Implementação de estruturas de índice para banco de dados em Python puro, desenvolvido como trabalho acadêmico para o IFMG. 

## 📋 Sumário

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Requisitos](#requisitos)
- [Instalação](#instalação)
- [Uso](#uso)
- [Experimentos](#experimentos)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Documentação](#documentação)
- [Licença](#licença)

## 📖 Sobre o Projeto

Este projeto implementa dois tipos de índices de banco de dados:

1. **Árvore B+ (B+ Tree)**: Estrutura balanceada otimizada para operações em disco, suportando busca por igualdade e por intervalo. 

2. **Hash Extensível (Extendible Hash)**: Estrutura dinâmica de hash que cresce conforme necessário, otimizada para busca por igualdade. 

### Características

- ✅ Registros com campos inteiros configuráveis
- ✅ Tamanho de página configurável (mínimo 256 bytes)
- ✅ Operações: inserção, remoção, busca por igualdade
- ✅ Busca por intervalo (apenas B+ Tree)
- ✅ Métricas de desempenho para experimentos
- ✅ Integração com SIOgen para geração de dados

## 🎯 Funcionalidades

### B+ Tree
| Operação | Complexidade | Descrição |
|----------|--------------|-----------|
| `insert(key, record)` | O(log n) | Insere um registro |
| `search(key)` | O(log n) | Busca por igualdade |
| `range_search(start, end)` | O(log n + k) | Busca por intervalo |
| `delete(key)` | O(log n) | Remove um registro |

### Hash Extensível
| Operação | Complexidade | Descrição |
|----------|--------------|-----------|
| `insert(key, record)` | O(1)* | Insere um registro |
| `search(key)` | O(1) | Busca por igualdade |
| `delete(key)` | O(1) | Remove um registro |

*Amortizado, considerando splits ocasionais

## 💻 Requisitos

- Python 3. 8 ou superior
- Nenhuma biblioteca externa (implementação pura)

Para experimentos e gráficos:
- matplotlib (opcional, para visualização)
- pandas (opcional, para análise)

## 🚀 Instalação

### Clone o repositório

```bash
git clone https://github.com/RxSaturn/bptree-hash-index.git
cd bptree-hash-index
```
### Instale as dependências (opcional)

```bash
pip install -r requirements.txt
```
### Instale o pacote em modo desenvolvimento

```bash
pip install -e . 
```
## 📚 Uso

### B+ Tree

```python
from src.bplustree. tree import BPlusTree
from src.common.record import Record

# Cria árvore com página de 512 bytes e 10 campos por registro
tree = BPlusTree(page_size=512, num_fields=10)

# Inserção
record = Record([1, 100, 200, 300, 400, 500, 600, 700, 800, 900])
tree.insert(key=1, record=record)

# Busca por igualdade
result = tree.search(key=1)
print(f"Encontrado: {result}")

# Busca por intervalo
results = tree.range_search(start_key=1, end_key=100)
print(f"Registros no intervalo: {len(results)}")

# Remoção
removed = tree.delete(key=1)

# Estatísticas
stats = tree.get_stats()
print(f"Page reads: {stats['page_reads']}")
print(f"Splits: {stats['splits']}")
```

### Hash Extensível

```python
from src.hash. extendible import ExtendibleHash
from src.common. record import Record

# Cria hash com página de 512 bytes
hash_index = ExtendibleHash(page_size=512, num_fields=10)

# Inserção
record = Record([1, 100, 200, 300, 400, 500, 600, 700, 800, 900])
hash_index. insert(key=1, record=record)

# Busca por igualdade (APENAS suportado)
result = hash_index.search(key=1)
print(f"Encontrado: {result}")

# Remoção
removed = hash_index.delete(key=1)

# Estatísticas
stats = hash_index.get_stats()
print(f"Global depth: {stats['global_depth']}")
print(f"Bucket splits: {stats['splits']}")
```

## 🧪 Experimentos

### Gerando dados com SIOgen

```bash
# Navega para pasta de ferramentas
cd tools

# Gera dataset com 10 atributos, 5000 inserções, 3000 buscas, 500 deleções
python siogen.py -a 10 -i 5000 -s 3000 -d 500 -f ../data/experiment1.csv
```

### Executando experimentos

```bash
cd experiments
python run_experiments. py
```

### Configurações testadas

| Parâmetro | Valores |
|-----------|---------|
| Número de campos | 5, 10, 20, 50 |
| Tamanho de página | 256, 512, 1024, 2048 bytes |
| Inserções | 1000, 5000, 10000, 50000 |
| Buscas | 1000, 5000, 10000 |
| Remoções | 100, 500, 1000 |

Os resultados são salvos em `results/experiment_results.csv`. 

## 📁 Estrutura do Projeto

```
bptree-hash-index/
├── src/                    # Código fonte
│   ├── common/             # Código compartilhado
│   ├── bplustree/          # Implementação B+ Tree
│   └── hash/               # Implementação Hash Extensível
├── tests/                  # Testes unitários
├── experiments/            # Scripts de experimentos
├── data/                   # Dados gerados pelo SIOgen
├── results/                # Resultados dos experimentos
├── artigo/                 # Artigo LaTeX (iftex2024)
├── tools/                  # Ferramentas auxiliares (SIOgen)
└── docs/                   # Documentação adicional
```

## 📖 Documentação
- [Referência SIOgen](docs/siogen-reference.md) - Como usar o gerador de dados
- [Arquitetura](docs/architecture.md) - Decisões de design

## 📄 Licença

Este projeto é para fins acadêmicos - IFMG. 

## 👥 Autores

- Henrique Augusto, Rayssa Mendes e Henrique Evangelista - Desenvolvimento e documentação

## 🙏 Agradecimentos

- Prof.  Marcos Ribeiro - Orientação e SIOgen
- IFMG - Instituição
---

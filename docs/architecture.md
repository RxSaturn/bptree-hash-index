# Arquitetura do Projeto - Índices B+ Tree e Hash Extensível

Este documento descreve a arquitetura e o design das estruturas de índice
implementadas neste projeto para o trabalho acadêmico do IFMG.

---

## 1. Visão Geral

Este projeto implementa duas estruturas de índice fundamentais para bancos de dados:

1. **B+ Tree** - Árvore balanceada otimizada para acesso em disco
2. **Hash Extensível** - Estrutura hash dinâmica com crescimento sob demanda

Ambas as estruturas são implementadas em Python puro, com foco em:
- Correção algorítmica
- Instrumentação para experimentos
- Código limpo e bem documentado

### Estrutura do Projeto

```
projeto/
├── src/
│   ├── bplustree/          # Implementação B+ Tree
│   │   ├── node.py         # Classes Node, LeafNode, InternalNode
│   │   └── tree.py         # Classe BPlusTree
│   ├── hash/               # Implementação Hash Extensível
│   │   ├── bucket.py       # Classe Bucket
│   │   └── extendible.py   # Classe ExtendibleHash
│   └── common/             # Código compartilhado
│       ├── record.py       # Classe Record
│       └── config.py       # Configurações
├── tests/                  # Testes unitários (pytest)
├── experiments/            # Scripts de experimentos
├── data/                   # Dados de teste (SIOgen)
├── results/                # Resultados dos experimentos
└── docs/                   # Documentação
```

---

## 2. Arquitetura B+ Tree

A B+ Tree é uma árvore de busca balanceada onde:
- Todos os valores (registros) estão nos nós folha
- Nós internos contêm apenas chaves de roteamento
- Nós folha são encadeados para busca por intervalo eficiente

### 2.1 Diagrama de Classes

```mermaid
classDiagram
    class Node {
        <<abstract>>
        -order: int
        -keys: List[int]
        -parent: Optional[InternalNode]
        +is_leaf: bool*
        +is_full() bool
        +is_underflow() bool
        +is_root() bool
        +split()* Tuple[Node, int]
        #_binary_search(key) int
    }

    class LeafNode {
        -records: List[Record]
        -next: Optional[LeafNode]
        -prev: Optional[LeafNode]
        +is_leaf: bool = True
        +insert(key, record) bool
        +search(key) Optional[Record]
        +delete(key) Optional[Record]
        +split() Tuple[LeafNode, int]
    }

    class InternalNode {
        -children: List[Node]
        +is_leaf: bool = False
        +find_child(key) Node
        +find_child_index(key) int
        +insert_child(key, child) None
        +split() Tuple[InternalNode, int]
    }

    class BPlusTree {
        -order: int
        -root: Node
        -config: Config
        -stats: Dict[str, int]
        +insert(key, record) bool
        +search(key) Optional[Record]
        +range_search(start, end) List[Record]
        +delete(key) Optional[Record]
        +get_stats() Dict[str, int]
        +reset_stats() None
        +get_height() int
    }

    class Record {
        -fields: List[int]
        +key: int
        +num_fields: int
        +serialize() bytes
        +deserialize(data, num_fields) Record
    }

    Node <|-- LeafNode
    Node <|-- InternalNode
    BPlusTree --> Node : root
    LeafNode --> Record : records
    LeafNode --> LeafNode : next, prev
    InternalNode --> Node : children
```

### 2.2 Descrição dos Componentes

#### Node (Classe Base Abstrata)
Classe base que define a interface comum para nós da árvore.

| Atributo/Método | Descrição |
|-----------------|-----------|
| `order` | Ordem da árvore (máximo de chaves por nó) |
| `keys` | Lista de chaves armazenadas |
| `parent` | Referência para o nó pai |
| `is_leaf` | Propriedade abstrata - True se nó folha |
| `is_full()` | Retorna True se `len(keys) >= order` |
| `is_underflow()` | Retorna True se abaixo do mínimo de chaves |
| `split()` | Método abstrato para dividir o nó |

#### LeafNode (Nó Folha)
Armazena os registros reais e mantém encadeamento bidirecional.

| Atributo/Método | Descrição |
|-----------------|-----------|
| `records` | Lista de registros (Record) |
| `next` | Ponteiro para próximo nó folha |
| `prev` | Ponteiro para nó folha anterior |
| `insert(key, record)` | Insere mantendo ordem, retorna False se duplicado |
| `search(key)` | Busca binária, retorna Record ou None |
| `delete(key)` | Remove e retorna registro |
| `split()` | Divide ao meio, **COPIA** primeira chave do novo nó |

#### InternalNode (Nó Interno)
Contém apenas chaves de roteamento e ponteiros para filhos.

| Atributo/Método | Descrição |
|-----------------|-----------|
| `children` | Lista de nós filhos |
| `find_child(key)` | Retorna filho apropriado para a chave |
| `insert_child(key, child)` | Insere nova chave e filho após split |
| `split()` | Divide ao meio, **MOVE** chave do meio para pai |

**Invariante:** `len(children) == len(keys) + 1`

#### BPlusTree (Árvore Principal)
Gerencia toda a estrutura e operações.

| Atributo/Método | Descrição |
|-----------------|-----------|
| `order` | Ordem calculada ou especificada |
| `root` | Nó raiz (começa como LeafNode vazio) |
| `stats` | Contadores para experimentos |
| `insert()` | Inserção com split automático |
| `search()` | Busca por igualdade O(log n) |
| `range_search()` | Busca por intervalo O(log n + k) |
| `delete()` | Remoção (simplificada, sem merge) |

### 2.3 Invariantes da Estrutura

1. **Balanceamento:** Todos os nós folha estão no mesmo nível
2. **Ordem:** Cada nó tem no máximo `order` chaves
3. **Mínimo:** Nós não-raiz têm pelo menos `ceil(order/2) - 1` chaves
4. **Encadeamento:** Nós folha formam lista duplamente encadeada
5. **Valores nas folhas:** Registros estão apenas nos nós folha
6. **Ordenação:** Chaves em cada nó estão em ordem crescente

### 2.4 Fluxo de Operações

#### Insert (Inserção)

```mermaid
flowchart TD
    A[insert key, record] --> B[_find_leaf key]
    B --> C{leaf.insert ok?}
    C -->|Sim| D[stats page_writes++]
    C -->|Não - duplicado| E[return False]
    D --> F{leaf.is_full?}
    F -->|Não| G[return True]
    F -->|Sim| H[_handle_split leaf]
    H --> I[leaf.split]
    I --> J{leaf.parent is None?}
    J -->|Sim| K[_create_new_root]
    J -->|Não| L[parent.insert_child]
    L --> M{parent.is_full?}
    M -->|Sim| N[_handle_split parent]
    M -->|Não| G
    K --> G
    N --> M
```

#### Search (Busca por Igualdade)

```mermaid
flowchart TD
    A[search key] --> B[_find_leaf key]
    B --> C[leaf.search key]
    C --> D{encontrado?}
    D -->|Sim| E[return Record]
    D -->|Não| F[return None]
```

#### Range Search (Busca por Intervalo)

```mermaid
flowchart TD
    A[range_search start, end] --> B{start > end?}
    B -->|Sim| C[return lista vazia]
    B -->|Não| D[_find_leaf start]
    D --> E[Percorre nós folha via next]
    E --> F{key > end?}
    F -->|Sim| G[return resultados]
    F -->|Não| H{start <= key <= end?}
    H -->|Sim| I[adiciona registro]
    H -->|Não| J[continua]
    I --> K{leaf.next existe?}
    J --> K
    K -->|Sim| E
    K -->|Não| G
```

#### Delete (Remoção)

```mermaid
flowchart TD
    A[delete key] --> B[_find_leaf key]
    B --> C[leaf.delete key]
    C --> D{registro removido?}
    D -->|Sim| E[stats page_writes++]
    D -->|Não| F[return None]
    E --> G[return registro]
```

### 2.5 Split: Cópia vs. Movimento

A diferença crítica entre split de nó folha e interno:

| Tipo de Nó | Comportamento da Chave Promovida |
|------------|----------------------------------|
| **LeafNode** | Chave é **COPIADA** - permanece no novo nó |
| **InternalNode** | Chave é **MOVIDA** - removida do nó original |

**Por que a diferença?**
- Em nós folha, a chave precisa existir junto com o registro
- Em nós internos, a chave é apenas separador, não precisa duplicar

---

## 3. Arquitetura Hash Extensível

O Hash Extensível é uma estrutura de índice dinâmica que:
- Cresce conforme necessário (sem rehash completo)
- Usa profundidade global e local para gerenciar buckets
- Oferece acesso O(1) amortizado

**IMPORTANTE:** Hash Extensível **NÃO** suporta busca por intervalo!

### 3.1 Diagrama de Classes

```mermaid
classDiagram
    class Bucket {
        -local_depth: int
        -capacity: int
        -records: List[Tuple[int, Record]]
        +is_full() bool
        +is_empty() bool
        +insert(key, record) bool
        +search(key) Optional[Record]
        +delete(key) Optional[Record]
        +split() Tuple[Bucket, Bucket]
    }

    class ExtendibleHash {
        -global_depth: int
        -bucket_capacity: int
        -directory: List[Bucket]
        -config: Config
        -stats: Dict[str, int]
        +insert(key, record) bool
        +search(key) Optional[Record]
        +delete(key) Optional[Record]
        +get_stats() Dict[str, Any]
        +reset_stats() None
        -_hash(key) int
        -_get_bucket(key) Bucket
        -_double_directory() None
        -_split_bucket(index) None
    }

    class Record {
        -fields: List[int]
        +key: int
    }

    ExtendibleHash --> Bucket : directory
    Bucket --> Record : records
```

### 3.2 Descrição dos Componentes

#### Bucket
Armazena pares (chave, registro) até sua capacidade.

| Atributo/Método | Descrição |
|-----------------|-----------|
| `local_depth` | Profundidade local (bits usados) |
| `capacity` | Capacidade máxima |
| `records` | Lista de (chave, registro) |
| `insert()` | Insere se não cheio e não duplicado |
| `search()` | Busca linear no bucket |
| `delete()` | Remove e retorna registro |
| `split()` | Divide baseado no novo bit |

#### ExtendibleHash
Gerencia o diretório e operações.

| Atributo/Método | Descrição |
|-----------------|-----------|
| `global_depth` | Profundidade global do diretório |
| `directory` | Lista de ponteiros para buckets |
| `_hash(key)` | Usa últimos `global_depth` bits |
| `_double_directory()` | Duplica entradas do diretório |
| `_split_bucket()` | Divide bucket e atualiza ponteiros |

### 3.3 Funcionamento do Directory Doubling

Quando um bucket está cheio e `local_depth == global_depth`:

1. `global_depth++`
2. Cada entrada do diretório é duplicada
3. Bucket é dividido
4. Ponteiros são atualizados

```
Antes (global_depth=1):
Directory: [B0, B1]

Após doubling (global_depth=2):
Directory: [B0, B0, B1, B1]
           ↑duplicado↑ ↑duplicado↑

Após split de B0:
Directory: [B0', B0'', B1, B1]
```

### 3.4 Bucket Splitting

Quando um bucket está cheio mas `local_depth < global_depth`:

1. `local_depth++` no novo bucket
2. Registros redistribuídos pelo novo bit
3. Atualiza apenas ponteiros relevantes no diretório

---

## 4. Módulo Comum

### 4.1 Record

Representa um registro com campos inteiros.

```python
@dataclass
class Record:
    fields: List[int]
    
    @property
    def key(self) -> int:
        """Primeiro campo é a chave."""
        return self.fields[0]
```

**Serialização:** Cada campo ocupa 4 bytes (int32).

### 4.2 Config

Configuração global para os índices.

```python
@dataclass
class Config:
    page_size: int = 512      # Mínimo 256 bytes
    num_fields: int = 10
    field_size: int = 4       # bytes por int
    min_order: int = 3        # mínimo para B+ Tree
```

**Métodos:**
- `calculate_bplus_order()` - Calcula ordem baseada em page_size
- `calculate_hash_bucket_capacity()` - Calcula capacidade do bucket

---

## 5. Decisões de Design

### 5.1 Separação LeafNode e InternalNode

**Motivação:**
- Comportamentos diferentes de split (cópia vs. movimento)
- LeafNode tem `records`, InternalNode tem `children`
- LeafNode tem encadeamento (`next`, `prev`)

**Alternativa considerada:**
Uma única classe `Node` com flag `is_leaf` - rejeitada por:
- Código menos limpo (muitos ifs)
- Violação do princípio de responsabilidade única

### 5.2 Cálculo Dinâmico de Ordem

A ordem é calculada automaticamente baseada em:
```python
entry_size = key_size + record_size
order = page_size // entry_size
return max(3, order)  # Mínimo 3 para splits corretos
```

**Por que mínimo 3?**
- Com ordem 2, split pode gerar nó vazio
- Ordem 3 garante pelo menos 1 chave após split

### 5.3 Encadeamento Bidirecional

Nós folha mantêm `next` e `prev` para:
- Busca por intervalo eficiente (percorre via `next`)
- Possibilidade de busca reversa (via `prev`)
- Facilita debug e visualização

---

## 6. Métricas e Experimentos

### 6.1 Estatísticas Coletadas

#### B+ Tree
| Métrica | Descrição |
|---------|-----------|
| `page_reads` | Leituras de página (navegação) |
| `page_writes` | Escritas de página (inserção/deleção) |
| `splits` | Número de splits realizados |
| `merges` | Número de merges (não implementado) |
| `height` | Altura atual da árvore |

#### Hash Extensível
| Métrica | Descrição |
|---------|-----------|
| `bucket_reads` | Leituras de bucket |
| `bucket_writes` | Escritas de bucket |
| `splits` | Número de bucket splits |
| `directory_doublings` | Vezes que diretório dobrou |
| `global_depth` | Profundidade global atual |
| `num_buckets` | Número de buckets únicos |

### 6.2 Integração com SIOgen

O SIOgen gera datasets sintéticos no formato:

```csv
OP,A1,A2,A3,...
+,10,100,200,...    # Inserção
?,10,0,0,...        # Busca
-,10,0,0,...        # Deleção
```

**Uso:**
```bash
python siogen.py -a 10 -i 5000 -s 3000 -d 500 -f data.csv
```

**Carregamento:**
```python
from src.common.record import Record

# Usando método da classe Record
record = Record.from_siogen_row(row)
```

---

## 7. Complexidade das Operações

### B+ Tree

| Operação | Tempo | Espaço |
|----------|-------|--------|
| `insert` | O(log n) | O(1) |
| `search` | O(log n) | O(1) |
| `range_search` | O(log n + k) | O(k) |
| `delete` | O(log n) | O(1) |

Onde:
- n = número de registros
- k = número de resultados no intervalo

### Hash Extensível

| Operação | Tempo | Espaço |
|----------|-------|--------|
| `insert` | O(1) amortizado | O(1) |
| `search` | O(1) | O(1) |
| `delete` | O(1) | O(1) |

**Nota:** Splits podem causar O(n) no pior caso, mas amortizado é O(1).

### Comparação

| Aspecto | B+ Tree | Hash |
|---------|---------|------|
| Busca por igualdade | O(log n) | O(1) |
| Busca por intervalo | O(log n + k) | ❌ Não suportado |
| Inserção | O(log n) | O(1) amortizado |
| Ordenação | Mantida | Não mantida |
| Uso de espaço | Moderado | Alto (diretório) |

---

## 8. Referências

- Ramakrishnan, R., Gehrke, J. "Database Management Systems", 3rd Ed.
- Elmasri, R., Navathe, S. "Fundamentals of Database Systems", 7th Ed.
- [docs/master-prompt.md](master-prompt.md) - Guia de implementação
- [docs/siogen-reference.md](siogen-reference.md) - Referência do SIOgen

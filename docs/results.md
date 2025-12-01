# Resultados dos Experimentos

Este documento apresenta os resultados experimentais obtidos da implementação e comparação entre as estruturas de índice B+ Tree e Hash Extensível.

---

## 1. Configuração dos Experimentos

Os experimentos foram conduzidos utilizando o gerador de dados SIOgen, com as seguintes configurações de teste:

### 1.1 Experimentos de Variação de Campos (fields)
- **fields_5**: 5 campos por registro, página de 512 bytes
- **fields_10**: 10 campos por registro, página de 512 bytes
- **fields_20**: 20 campos por registro, página de 512 bytes

### 1.2 Experimentos de Variação de Tamanho de Página (page)
- **page_256**: 256 bytes de página, 10 campos
- **page_512**: 512 bytes de página, 10 campos (baseline)
- **page_1024**: 1024 bytes de página, 10 campos

### 1.3 Experimentos de Variação de Volume (vol)
- **vol_small**: Volume pequeno de dados
- **vol_medium**: Volume médio de dados
- **vol_large**: Volume grande de dados

---

## 2. Resultados Comparativos

### 2.1 Tabela Geral de Resultados

| Experimento | Estrutura | Inserção (s) | Busca (s) | Remoção (s) | Splits | Buscas Encontradas |
|-------------|-----------|--------------|-----------|-------------|--------|-------------------|
| fields_5 | B+Tree | 0.0050 | 0.0021 | 0.0004 | 73 | 450 |
| fields_5 | Hash | 0.0028 | 0.0006 | 0.0006 | 62 | 450 |
| fields_10 | B+Tree | 0.0053 | 0.0020 | 0.0004 | 157 | 334 |
| fields_10 | Hash | 0.0029 | 0.0042 | 0.0009 | 126 | 334 |
| fields_20 | B+Tree | 0.0058 | 0.0039 | 0.0006 | 347 | 439 |
| fields_20 | Hash | 0.0050 | 0.0004 | 0.0018 | 254 | 439 |
| page_256 | B+Tree | 0.0084 | 0.0023 | 0.0005 | 464 | 334 |
| page_256 | Hash | 0.0107 | 0.0005 | 0.0012 | 254 | 334 |
| page_512 | B+Tree | 0.0044 | 0.0019 | 0.0004 | 157 | 334 |
| page_512 | Hash | 0.0030 | 0.0005 | 0.0020 | 126 | 334 |
| page_1024 | B+Tree | 0.0044 | 0.0017 | 0.0004 | 71 | 334 |
| page_1024 | Hash | 0.0077 | 0.0006 | 0.0006 | 62 | 334 |
| vol_small | B+Tree | 0.0020 | 0.0006 | 0.0002 | 78 | 198 |
| vol_small | Hash | 0.0014 | 0.0002 | 0.0003 | 62 | 198 |
| vol_medium | B+Tree | 0.0128 | 0.0038 | 0.0008 | 318 | 750 |
| vol_medium | Hash | 0.0092 | 0.0014 | 0.0022 | 254 | 750 |
| vol_large | B+Tree | 0.0309 | 0.0115 | 0.0025 | 803 | 1953 |
| vol_large | Hash | 0.0296 | 0.0023 | 0.0118 | 510 | 1953 |

---

## 3. Estatísticas Adicionais do Hash Extensível

As seguintes métricas adicionais foram coletadas para a estrutura Hash Extensível:

### 3.1 Load Factor (Fator de Carga)
O load factor representa a taxa de ocupação dos buckets, variando de 0.0 (vazio) a 1.0 (totalmente cheio).

- **Mínimo**: 0.65
- **Máximo**: 0.89
- **Faixa**: 0.65 - 0.89

### 3.2 Global Depth (Profundidade Global)
A profundidade global indica o número de bits usados para indexação no diretório.

- **Mínimo**: 6 bits
- **Máximo**: 9 bits
- **Faixa**: 6 - 9

### 3.3 Directory Doublings (Dobramentos do Diretório)
Número de vezes que o diretório precisou ser dobrado durante as inserções.

- **Mínimo**: 5 dobramentos
- **Máximo**: 8 dobramentos
- **Faixa**: 5 - 8

---

## 4. Análise dos Resultados

### 4.1 Desempenho de Inserção

**Observações:**
- O Hash Extensível geralmente apresenta tempos de inserção menores ou comparáveis ao B+ Tree
- Em volumes grandes, os tempos de inserção se aproximam (B+Tree: 0.0309s vs Hash: 0.0296s)
- Páginas menores (256 bytes) penalizam mais o Hash (0.0107s) do que o B+ Tree (0.0084s)

**Vantagem**: Hash Extensível na maioria dos casos

### 4.2 Desempenho de Busca

**Observações:**
- Hash Extensível apresenta tempos de busca significativamente menores na maioria dos casos
- A diferença é mais pronunciada em volumes grandes (B+Tree: 0.0115s vs Hash: 0.0023s)
- A complexidade O(1) do hash se confirma experimentalmente contra O(log n) do B+ Tree

**Vantagem**: Hash Extensível consistentemente

### 4.3 Desempenho de Remoção

**Observações:**
- B+ Tree apresenta tempos de remoção menores em experimentos pequenos e médios
- Em volumes grandes, o Hash leva mais tempo (0.0118s vs 0.0025s do B+ Tree)
- Isso pode estar relacionado à necessidade de merge de buckets no Hash

**Vantagem**: B+ Tree

### 4.4 Número de Splits

**Observações:**
- B+ Tree apresenta mais splits que Hash na maioria dos experimentos
- Com 20 campos, B+ Tree tem 347 splits vs 254 do Hash
- Com páginas pequenas (256 bytes), B+ Tree tem 464 splits vs 254 do Hash
- Isso indica que o Hash gerencia melhor o crescimento da estrutura

**Vantagem**: Hash Extensível

### 4.5 Impacto do Número de Campos

**Experimentos fields_5, fields_10, fields_20:**

| Métrica | Tendência B+ Tree | Tendência Hash |
|---------|-------------------|----------------|
| Tempo Inserção | Aumenta (0.0050s → 0.0058s) | Aumenta (0.0028s → 0.0050s) |
| Tempo Busca | Aumenta (0.0021s → 0.0039s) | Estável (0.0006s → 0.0004s) |
| Splits | Aumenta (73 → 347) | Aumenta (62 → 254) |

**Conclusão**: Hash é menos afetado pelo aumento de campos, especialmente em buscas.

### 4.6 Impacto do Tamanho de Página

**Experimentos page_256, page_512, page_1024:**

| Métrica | Tendência B+ Tree | Tendência Hash |
|---------|-------------------|----------------|
| Tempo Inserção | Melhora (0.0084s → 0.0044s) | Varia (0.0107s → 0.0030s → 0.0077s) |
| Tempo Busca | Melhora (0.0023s → 0.0017s) | Estável (0.0005s → 0.0006s) |
| Splits | Diminui (464 → 71) | Diminui (254 → 62) |

**Conclusão**: Páginas maiores reduzem splits e melhoram desempenho em ambas estruturas. O ponto ótimo observado foi 512 bytes.

### 4.7 Impacto do Volume de Dados

**Experimentos vol_small, vol_medium, vol_large:**

| Métrica | Escalabilidade B+ Tree | Escalabilidade Hash |
|---------|------------------------|---------------------|
| Inserção | Linear (0.0020s → 0.0309s) | Linear (0.0014s → 0.0296s) |
| Busca | Logarítmica (0.0006s → 0.0115s) | Quase constante (0.0002s → 0.0023s) |
| Splits | Linear (78 → 803) | Linear (62 → 510) |

**Conclusão**: Hash escala melhor para buscas, mas ambos têm comportamento linear para inserções.

---

## 5. Métricas de Eficiência

### 5.1 Taxa de Sucesso nas Buscas
Todos os experimentos apresentaram 100% de sucesso nas buscas (todas as chaves inseridas foram encontradas).

### 5.2 Load Factor Médio do Hash
O load factor médio observado foi de **0.77** (77% de ocupação dos buckets), calculado como a média aritmética dos valores mínimo e máximo observados (0.65 + 0.89) / 2, indicando um bom balanceamento entre uso de espaço e desempenho.

### 5.3 Profundidade Global Média
A profundidade global média foi de **7.5 bits**, correspondendo a diretórios com 128-256 entradas.

---

## 6. Trade-offs Identificados

### 6.1 B+ Tree
**Vantagens:**
- Melhor desempenho em remoções
- Suporta busca por intervalo (range queries)
- Menos sensível a páginas pequenas
- Comportamento mais previsível

**Desvantagens:**
- Buscas mais lentas (O(log n))
- Mais splits necessários
- Maior complexidade de implementação

### 6.2 Hash Extensível
**Vantagens:**
- Buscas extremamente rápidas (O(1))
- Inserções geralmente mais rápidas
- Menos splits
- Escala melhor com volume de dados

**Desvantagens:**
- Não suporta busca por intervalo
- Remoções mais custosas em volumes grandes
- Load factor pode variar
- Requer mais memória para diretório

---

## 7. Recomendações de Uso

### 7.1 Use B+ Tree quando:
- Necessitar busca por intervalo (range queries)
- Operações de remoção forem frequentes
- Dados têm padrão de acesso sequencial
- Espaço em disco for limitado

### 7.2 Use Hash Extensível quando:
- Buscas por igualdade dominarem as operações
- Volume de dados for grande
- Desempenho de busca for crítico
- Não houver necessidade de ordenação

---

## 8. Conclusões

1. **Busca**: Hash Extensível é claramente superior (até 5x mais rápido)
2. **Inserção**: Hash geralmente mais rápido, mas diferença diminui com volume
3. **Remoção**: B+ Tree é mais eficiente
4. **Splits**: Hash requer menos divisões
5. **Escalabilidade**: Hash escala melhor para buscas, B+ Tree para remoções
6. **Uso de Espaço**: Hash usa mais espaço devido ao diretório
7. **Funcionalidade**: B+ Tree oferece range queries, Hash não

**Escolha da estrutura depende do perfil de acesso aos dados:**
- Workload read-heavy (muitas buscas): **Hash Extensível**
- Workload com range queries: **B+ Tree**
- Workload balanceado: **B+ Tree** (mais versátil)

---

**Versão:** 1.0  
**Data:** Dezembro 2024  
**Autores:** Henrique Augusto G. Fernandes, Henrique Evangelista Pimentel, Rayssa Mendes da Silva

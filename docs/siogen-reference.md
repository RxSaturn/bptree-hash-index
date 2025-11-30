# SIOgen - Referência Rápida

## Descrição
SIOgen (Simple Insert Delete Dataset Generator) gera datasets sintéticos para testes de estruturas de índice. 

## Uso

```bash
python siogen.py [opções]
```

## Parâmetros

| Flag | Longo | Descrição | Default |
|------|-------|-----------|---------|
| `-a` | `--attributes` | Número de atributos por registro | 10 |
| `-i` | `--insertions` | Número de inserções | 2000 |
| `-d` | `--deletions` | Número de deleções | 500 |
| `-s` | `--searches` | Número de buscas | 3000 |
| `-f` | `--filename` | Arquivo de saída | output.csv |
| `-e` | `--seed` | Seed para reprodutibilidade | 42 |

## Formato de Saída

O arquivo CSV gerado contém:
- Coluna `OP`: Operação (`+` inserção, `-` deleção, `? ` busca)
- Colunas `A1` a `An`: Valores dos atributos (inteiros 0-1000)
- `A1` é sempre a chave primária

## Exemplos

```bash
# Experimento básico
python siogen.py -a 10 -i 5000 -d 500 -s 3000 -f exp1.csv

# Muitos campos
python siogen. py -a 50 -i 10000 -d 1000 -s 5000 -f exp2.csv

# Volume alto
python siogen. py -a 10 -i 50000 -d 5000 -s 20000 -f exp3.csv
```

## Processamento no Python

```python
import csv

def load_siogen_data(filename):
    operations = []
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            op = row['OP']
            # Extrai campos (exceto OP)
            fields = [int(row[k]) for k in row if k != 'OP']
            operations.append((op, fields))
    return operations

# Uso
data = load_siogen_data('output.csv')
for op, fields in data:
    key = fields[0]  # A1 é a chave
    if op == '+':
        index. insert(key, Record(fields))
    elif op == '-':
        index.delete(key)
    elif op == '? ':
        result = index.search(key)
```

## Configurações Recomendadas para Experimentos

| Experimento | Campos | Inserções | Buscas | Deleções |
|-------------|--------|-----------|--------|----------|
| Pequeno     | 5-10   | 1000      | 1000   | 100      |
| Médio       | 10-20  | 5000      | 3000   | 500      |
| Grande      | 10-50  | 10000     | 5000   | 1000     |
| Stress      | 10     | 50000     | 20000  | 5000     |

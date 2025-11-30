#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script Principal de Experimentos

Executa experimentos comparativos entre B+ Tree e Hash Extensível
usando dados gerados pelo SIOgen. 

Uso:
    python run_experiments.py
"""

import csv
import time
import os
import sys
from dataclasses import dataclass
from typing import List, Tuple, Dict, Any

# Adiciona diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bplustree.tree import BPlusTree
from src.hash.extendible import ExtendibleHash
from src.common.record import Record


@dataclass
class ExperimentConfig:
    """Configuração de um experimento."""
    name: str
    num_fields: int
    page_size: int
    num_insertions: int
    num_searches: int
    num_deletions: int
    seed: int = 42


@dataclass
class ExperimentResult:
    """Resultado de um experimento."""
    config: ExperimentConfig
    index_type: str
    insert_time: float
    search_time: float
    delete_time: float
    stats: Dict[str, Any]


def load_siogen_data(filename: str) -> List[Tuple[str, List[int]]]:
    """
    Carrega dados gerados pelo SIOgen.
    
    Args:
        filename: Caminho para o arquivo CSV
        
    Returns:
        Lista de (operação, campos)
    """
    operations = []
    
    if not os.path.exists(filename):
        print(f"⚠️  Arquivo não encontrado: {filename}")
        return operations
    
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            op = row['OP']
            # Extrai campos (exceto OP)
            fields = []
            i = 1
            while f'A{i}' in row:
                fields.append(int(row[f'A{i}']))
                i += 1
            operations.append((op, fields))
    
    return operations


def generate_siogen_data(config: ExperimentConfig, output_dir: str) -> str:
    """
    Gera dados usando SIOgen. 
    
    Args:
        config: Configuração do experimento
        output_dir: Diretório de saída
        
    Returns:
        Caminho do arquivo gerado
    """
    import subprocess
    
    os.makedirs(output_dir, exist_ok=True)
    
    filename = os.path.join(
        output_dir,
        f"data_{config.name}_{config.num_fields}f_{config.page_size}p.csv"
    )
    
    siogen_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'tools', 'siogen.py'
    )
    
    if os.path.exists(siogen_path):
        cmd = [
            sys.executable, siogen_path,
            '-a', str(config.num_fields),
            '-i', str(config.num_insertions),
            '-d', str(config.num_deletions),
            '-s', str(config.num_searches),
            '-f', filename,
            '-e', str(config.seed)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ Dados gerados: {filename}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erro ao gerar dados: {e}")
    else:
        print(f"⚠️  SIOgen não encontrado em: {siogen_path}")
        # Gera dados simples manualmente
        generate_simple_data(config, filename)
    
    return filename


def generate_simple_data(config: ExperimentConfig, filename: str):
    """
    Gera dados simples sem SIOgen (fallback).
    """
    import random
    random.seed(config.seed)
    
    operations = []
    keys = list(range(config.num_insertions))
    random.shuffle(keys)
    
    # Gera inserções
    for key in keys:
        fields = [key] + [random.randint(0, 1000) for _ in range(config.num_fields - 1)]
        operations.append(('+', fields))
    
    # Gera buscas
    for _ in range(config.num_searches):
        key = random.randint(0, config.num_insertions * 2)
        fields = [key] * config.num_fields
        operations.append(('?', fields))
    
    # Gera deleções
    delete_keys = random.sample(keys, min(config.num_deletions, len(keys)))
    for key in delete_keys:
        fields = [key] * config.num_fields
        operations.append(('-', fields))
    
    # Salva arquivo
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['OP'] + [f'A{i+1}' for i in range(config.num_fields)]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for op, fields in operations:
            row = {'OP': op}
            for i, val in enumerate(fields):
                row[f'A{i+1}'] = val
            writer.writerow(row)
    
    print(f"✅ Dados gerados (fallback): {filename}")


def run_bplus_experiment(
    config: ExperimentConfig,
    data: List[Tuple[str, List[int]]]
) -> ExperimentResult:
    """
    Executa experimento com B+ Tree. 
    """
    tree = BPlusTree(
        page_size=config.page_size,
        num_fields=config.num_fields
    )
    
    # Separa operações
    insert_ops = [(fields[0], Record(fields)) for op, fields in data if op == '+']
    search_ops = [fields[0] for op, fields in data if op == '?']
    delete_ops = [fields[0] for op, fields in data if op == '-']
    
    # Inserções
    tree.reset_stats()
    start = time.perf_counter()
    for key, record in insert_ops:
        tree.insert(key, record)
    insert_time = time.perf_counter() - start
    insert_stats = tree.get_stats()
    
    # Buscas
    tree.reset_stats()
    start = time.perf_counter()
    found_count = 0
    for key in search_ops:
        if tree.search(key):
            found_count += 1
    search_time = time.perf_counter() - start
    search_stats = tree.get_stats()
    search_stats['found'] = found_count
    
    # Remoções
    tree.reset_stats()
    start = time.perf_counter()
    removed_count = 0
    for key in delete_ops:
        if tree.delete(key):
            removed_count += 1
    delete_time = time.perf_counter() - start
    delete_stats = tree.get_stats()
    delete_stats['removed'] = removed_count
    
    return ExperimentResult(
        config=config,
        index_type='B+Tree',
        insert_time=insert_time,
        search_time=search_time,
        delete_time=delete_time,
        stats={
            'insert': insert_stats,
            'search': search_stats,
            'delete': delete_stats,
            'final_height': tree.get_height()
        }
    )


def run_hash_experiment(
    config: ExperimentConfig,
    data: List[Tuple[str, List[int]]]
) -> ExperimentResult:
    """
    Executa experimento com Hash Extensível. 
    """
    hash_idx = ExtendibleHash(
        page_size=config.page_size,
        num_fields=config.num_fields
    )
    
    # Separa operações
    insert_ops = [(fields[0], Record(fields)) for op, fields in data if op == '+']
    search_ops = [fields[0] for op, fields in data if op == '?']
    delete_ops = [fields[0] for op, fields in data if op == '-']
    
    # Inserções
    hash_idx.reset_stats()
    start = time.perf_counter()
    for key, record in insert_ops:
        hash_idx.insert(key, record)
    insert_time = time.perf_counter() - start
    insert_stats = hash_idx.get_stats()
    
    # Buscas
    hash_idx.reset_stats()
    start = time.perf_counter()
    found_count = 0
    for key in search_ops:
        if hash_idx.search(key):
            found_count += 1
    search_time = time.perf_counter() - start
    search_stats = hash_idx.get_stats()
    search_stats['found'] = found_count
    
    # Remoções
    hash_idx.reset_stats()
    start = time.perf_counter()
    removed_count = 0
    for key in delete_ops:
        if hash_idx.delete(key):
            removed_count += 1
    delete_time = time.perf_counter() - start
    delete_stats = hash_idx.get_stats()
    delete_stats['removed'] = removed_count
    
    return ExperimentResult(
        config=config,
        index_type='ExtendibleHash',
        insert_time=insert_time,
        search_time=search_time,
        delete_time=delete_time,
        stats={
            'insert': insert_stats,
            'search': search_stats,
            'delete': delete_stats,
            'final_global_depth': hash_idx.global_depth,
            'final_num_buckets': hash_idx._count_unique_buckets()
        }
    )


def print_result(result: ExperimentResult):
    """Imprime resultado formatado."""
    print(f"\n{'─' * 60}")
    print(f"📊 {result.index_type}")
    print(f"{'─' * 60}")
    print(f"⏱️  Inserção: {result.insert_time:.4f}s")
    print(f"⏱️  Busca:    {result.search_time:.4f}s")
    print(f"⏱️  Remoção:  {result.delete_time:.4f}s")
    print(f"📈 Estatísticas de Inserção: {result.stats['insert']}")
    print(f"🔍 Buscas encontradas: {result.stats['search'].get('found', 'N/A')}")


def save_results(results: List[ExperimentResult], output_dir: str):
    """Salva resultados em CSV."""
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, 'experiment_results.csv')
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'experiment_name', 'index_type', 'num_fields', 'page_size',
            'num_insertions', 'num_searches', 'num_deletions',
            'insert_time', 'search_time', 'delete_time',
            'insert_page_ops', 'insert_splits',
            'search_found', 'delete_removed'
        ])
        
        for r in results:
            insert_stats = r.stats.get('insert', {})
            search_stats = r.stats.get('search', {})
            delete_stats = r.stats.get('delete', {})
            
            page_ops = insert_stats.get('page_writes', 0) + insert_stats.get('bucket_writes', 0)
            splits = insert_stats.get('splits', 0)
            
            writer.writerow([
                r.config.name,
                r.index_type,
                r.config.num_fields,
                r.config.page_size,
                r.config.num_insertions,
                r.config.num_searches,
                r.config.num_deletions,
                f"{r.insert_time:.6f}",
                f"{r.search_time:.6f}",
                f"{r.delete_time:.6f}",
                page_ops,
                splits,
                search_stats.get('found', 0),
                delete_stats.get('removed', 0)
            ])
    
    print(f"\n✅ Resultados salvos em: {filename}")


def main():
    """Executa todos os experimentos."""
    print("=" * 70)
    print("🧪 EXPERIMENTOS: B+ TREE vs HASH EXTENSÍVEL")
    print("=" * 70)
    
    # Configurações dos experimentos
    configs = [
        # Variação de número de campos
        ExperimentConfig("fields_5", num_fields=5, page_size=512, 
                        num_insertions=1000, num_searches=500, num_deletions=100),
        ExperimentConfig("fields_10", num_fields=10, page_size=512,
                        num_insertions=1000, num_searches=500, num_deletions=100),
        ExperimentConfig("fields_20", num_fields=20, page_size=512,
                        num_insertions=1000, num_searches=500, num_deletions=100),
        
        # Variação de tamanho de página
        ExperimentConfig("page_256", num_fields=10, page_size=256,
                        num_insertions=1000, num_searches=500, num_deletions=100),
        ExperimentConfig("page_512", num_fields=10, page_size=512,
                        num_insertions=1000, num_searches=500, num_deletions=100),
        ExperimentConfig("page_1024", num_fields=10, page_size=1024,
                        num_insertions=1000, num_searches=500, num_deletions=100),
        
        # Variação de volume
        ExperimentConfig("vol_small", num_fields=10, page_size=512,
                        num_insertions=500, num_searches=200, num_deletions=50),
        ExperimentConfig("vol_medium", num_fields=10, page_size=512,
                        num_insertions=2000, num_searches=1000, num_deletions=200),
        ExperimentConfig("vol_large", num_fields=10, page_size=512,
                        num_insertions=5000, num_searches=2000, num_deletions=500),
    ]
    
    # Diretórios
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    results_dir = os.path.join(base_dir, 'results')
    
    results = []
    
    for config in configs:
        print(f"\n{'=' * 70}")
        print(f"📋 Experimento: {config.name}")
        print(f"   Campos: {config.num_fields}, Página: {config.page_size} bytes")
        print(f"   Inserções: {config.num_insertions}, Buscas: {config.num_searches}, Deleções: {config.num_deletions}")
        print("=" * 70)
        
        # Gera dados
        data_file = generate_siogen_data(config, data_dir)
        
        # Carrega dados
        data = load_siogen_data(data_file)
        
        if not data:
            print(f"⚠️  Sem dados para experimento {config.name}, pulando...")
            continue
        
        print(f"📂 Dados carregados: {len(data)} operações")
        
        # Executa experimentos
        bplus_result = run_bplus_experiment(config, data)
        print_result(bplus_result)
        results.append(bplus_result)
        
        hash_result = run_hash_experiment(config, data)
        print_result(hash_result)
        results.append(hash_result)
    
    # Salva resultados
    save_results(results, results_dir)
    
    print("\n" + "=" * 70)
    print("✅ EXPERIMENTOS CONCLUÍDOS!")
    print("=" * 70)


if __name__ == '__main__':
    main()
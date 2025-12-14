#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Testes Unitários para SIOgen e funções de experimentos

Execute com: pytest tests/test_experiments.py -v
"""

import pytest
import os
import sys
import tempfile
import csv

sys.path.insert(0, '..')

from experiments.run_experiments import (
    ExperimentConfig,
    load_siogen_data,
    generate_simple_data,
    generate_siogen_data
)


class TestLoadSiogenData:
    """Testes para load_siogen_data."""
    
    def test_load_valid_file(self, tmp_path):
        """Testa carregamento de arquivo válido."""
        filepath = tmp_path / "valid.csv"
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['OP', 'A1', 'A2'])
            writer.writeheader()
            writer.writerow({'OP': '+', 'A1': '1', 'A2': '100'})
            writer.writerow({'OP': '?', 'A1': '1', 'A2': '1'})
            writer.writerow({'OP': '-', 'A1': '1', 'A2': '1'})
        
        operations = load_siogen_data(str(filepath))
        
        assert len(operations) == 3
        assert operations[0] == ('+', [1, 100])
        assert operations[1] == ('?', [1, 1])
        assert operations[2] == ('-', [1, 1])
    
    def test_load_nonexistent_file(self, tmp_path):
        """Testa carregamento de arquivo inexistente."""
        nonexistent_file = tmp_path / "nonexistent_file.csv"
        operations = load_siogen_data(str(nonexistent_file))
        
        assert operations == []
    
    def test_load_empty_file(self, tmp_path):
        """Testa carregamento de arquivo vazio."""
        filepath = tmp_path / "empty.csv"
        filepath.touch()
        
        operations = load_siogen_data(str(filepath))
        
        assert operations == []
    
    def test_load_invalid_format(self, tmp_path):
        """Testa carregamento de arquivo com formato inválido."""
        filepath = tmp_path / "invalid.csv"
        with open(filepath, 'w') as f:
            f.write("A,B,C\n1,2,3\n")
        
        operations = load_siogen_data(str(filepath))
        
        assert operations == []
    
    def test_load_invalid_operation(self, tmp_path):
        """Testa que operações inválidas são ignoradas."""
        filepath = tmp_path / "invalid_ops.csv"
        with open(filepath, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['OP', 'A1', 'A2'])
            writer.writeheader()
            writer.writerow({'OP': '+', 'A1': '1', 'A2': '100'})
            writer.writerow({'OP': 'X', 'A1': '2', 'A2': '200'})  # Invalid
            writer.writerow({'OP': '-', 'A1': '3', 'A2': '300'})
        
        operations = load_siogen_data(str(filepath))
        
        assert len(operations) == 2
        assert operations[0][0] == '+'
        assert operations[1][0] == '-'


class TestGenerateSimpleData:
    """Testes para generate_simple_data."""
    
    def test_generates_correct_counts(self, tmp_path):
        """Testa que gera contagens corretas de operações."""
        filepath = tmp_path / "data.csv"
        config = ExperimentConfig(
            name='test',
            num_fields=3,
            page_size=512,
            num_insertions=10,
            num_searches=5,
            num_deletions=3
        )
        
        generate_simple_data(config, str(filepath))
        operations = load_siogen_data(str(filepath))
        
        insert_count = sum(1 for op, _ in operations if op == '+')
        search_count = sum(1 for op, _ in operations if op == '?')
        delete_count = sum(1 for op, _ in operations if op == '-')
        
        assert insert_count == 10
        assert search_count == 5
        assert delete_count == 3
    
    def test_intercalates_operations(self, tmp_path):
        """Testa que operações são intercaladas."""
        filepath = tmp_path / "data.csv"
        config = ExperimentConfig(
            name='test',
            num_fields=3,
            page_size=512,
            num_insertions=50,
            num_searches=30,
            num_deletions=10
        )
        
        generate_simple_data(config, str(filepath))
        
        with open(filepath, 'r') as f:
            next(f)  # skip header
            ops = [line.strip().split(',')[0] for line in f]
        
        # Count operation blocks
        blocks = 0
        prev_op = None
        for op in ops:
            if op != prev_op:
                blocks += 1
                prev_op = op
        
        # With intercalation, we should have multiple blocks
        # (more than 3 blocks which would be just insert->search->delete)
        assert blocks > 3
    
    def test_handles_deletions_exceeding_insertions(self, tmp_path):
        """Testa que deleções são limitadas ao número de inserções."""
        filepath = tmp_path / "data.csv"
        config = ExperimentConfig(
            name='test',
            num_fields=3,
            page_size=512,
            num_insertions=5,
            num_searches=10,
            num_deletions=20  # More than insertions
        )
        
        generate_simple_data(config, str(filepath))
        operations = load_siogen_data(str(filepath))
        
        insert_count = sum(1 for op, _ in operations if op == '+')
        delete_count = sum(1 for op, _ in operations if op == '-')
        
        assert insert_count == 5
        # Deletions should be at most equal to insertions
        assert delete_count <= insert_count
    
    def test_creates_directory_if_needed(self, tmp_path):
        """Testa que cria diretório se necessário."""
        subdir = tmp_path / "subdir" / "nested"
        filepath = subdir / "data.csv"
        config = ExperimentConfig(
            name='test',
            num_fields=3,
            page_size=512,
            num_insertions=5,
            num_searches=3,
            num_deletions=1
        )
        
        generate_simple_data(config, str(filepath))
        
        assert os.path.exists(filepath)


class TestGenerateSiogenData:
    """Testes para generate_siogen_data."""
    
    def test_generates_data_file(self, tmp_path):
        """Testa que gera arquivo de dados."""
        config = ExperimentConfig(
            name='test',
            num_fields=3,
            page_size=512,
            num_insertions=10,
            num_searches=5,
            num_deletions=3
        )
        
        filepath = generate_siogen_data(config, str(tmp_path))
        
        assert os.path.exists(filepath)
        assert os.path.getsize(filepath) > 0
    
    def test_uses_fallback_on_invalid_params(self, tmp_path):
        """Testa que usa fallback quando parâmetros são inválidos."""
        config = ExperimentConfig(
            name='test',
            num_fields=3,
            page_size=512,
            num_insertions=5,
            num_searches=10,
            num_deletions=20  # Invalid: more deletions than insertions
        )
        
        filepath = generate_siogen_data(config, str(tmp_path))
        
        # Should still generate a file (via fallback)
        assert os.path.exists(filepath)
        operations = load_siogen_data(filepath)
        assert len(operations) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

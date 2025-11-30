#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Testes Unitários para Hash Extensível

Execute com: pytest tests/test_hash.py -v
"""

import pytest
import sys
sys.path.insert(0, '. .')

from src. hash.extendible import ExtendibleHash
from src.common.record import Record


class TestExtendibleHashBasic:
    """Testes básicos de inserção e busca."""
    
    def test_create_hash(self):
        """Testa criação do hash."""
        hash_idx = ExtendibleHash(bucket_capacity=4, page_size=512, num_fields=5)
        assert hash_idx.global_depth == 1
        assert hash_idx.bucket_capacity == 4
    
    def test_insert_single(self):
        """Testa inserção de um registro."""
        hash_idx = ExtendibleHash(bucket_capacity=4, num_fields=3)
        record = Record([1, 100, 200])
        
        result = hash_idx.insert(1, record)
        
        assert result is True
    
    def test_search_existing(self):
        """Testa busca de registro existente."""
        hash_idx = ExtendibleHash(bucket_capacity=4, num_fields=3)
        record = Record([1, 100, 200])
        hash_idx.insert(1, record)
        
        found = hash_idx.search(1)
        
        assert found is not None
        assert found. key == 1
        assert found.fields == [1, 100, 200]
    
    def test_search_nonexistent(self):
        """Testa busca de registro inexistente."""
        hash_idx = ExtendibleHash(bucket_capacity=4, num_fields=3)
        
        found = hash_idx.search(999)
        
        assert found is None
    
    def test_insert_duplicate(self):
        """Testa inserção de chave duplicada."""
        hash_idx = ExtendibleHash(bucket_capacity=4, num_fields=3)
        record1 = Record([1, 100, 200])
        record2 = Record([1, 300, 400])
        
        hash_idx.insert(1, record1)
        result = hash_idx.insert(1, record2)
        
        assert result is False


class TestExtendibleHashSplit:
    """Testes de split de buckets."""
    
    def test_bucket_split(self):
        """Testa split de bucket."""
        hash_idx = ExtendibleHash(bucket_capacity=2, num_fields=2)
        
        # Insere registros suficientes para causar split
        for i in range(10):
            hash_idx.insert(i, Record([i, i * 10]))
        
        # Verifica que todos podem ser encontrados
        for i in range(10):
            found = hash_idx. search(i)
            assert found is not None
            assert found.key == i
    
    def test_directory_doubling(self):
        """Testa que diretório dobra quando necessário."""
        hash_idx = ExtendibleHash(bucket_capacity=2, num_fields=2)
        initial_size = len(hash_idx. directory)
        
        # Insere muitos registros
        for i in range(20):
            hash_idx.insert(i, Record([i, i * 10]))
        
        # Diretório deve ter crescido
        assert len(hash_idx. directory) > initial_size
    
    def test_global_depth_increases(self):
        """Testa que profundidade global aumenta."""
        hash_idx = ExtendibleHash(bucket_capacity=2, num_fields=2)
        initial_depth = hash_idx. global_depth
        
        # Insere muitos registros
        for i in range(50):
            hash_idx. insert(i, Record([i, i * 10]))
        
        assert hash_idx.global_depth > initial_depth


class TestExtendibleHashDelete:
    """Testes de remoção."""
    
    def test_delete_existing(self):
        """Testa remoção de registro existente."""
        hash_idx = ExtendibleHash(bucket_capacity=4, num_fields=2)
        hash_idx.insert(1, Record([1, 100]))
        
        removed = hash_idx.delete(1)
        
        assert removed is not None
        assert removed.key == 1
        assert hash_idx.search(1) is None
    
    def test_delete_nonexistent(self):
        """Testa remoção de registro inexistente."""
        hash_idx = ExtendibleHash(bucket_capacity=4, num_fields=2)
        
        removed = hash_idx.delete(999)
        
        assert removed is None
    
    def test_delete_multiple(self):
        """Testa remoção de múltiplos registros."""
        hash_idx = ExtendibleHash(bucket_capacity=4, num_fields=2)
        for i in range(10):
            hash_idx.insert(i, Record([i, i * 10]))
        
        # Remove alguns
        for i in [0, 5, 9]:
            hash_idx.delete(i)
        
        # Verifica removidos
        for i in [0, 5, 9]:
            assert hash_idx.search(i) is None
        
        # Verifica restantes
        for i in [1, 2, 3, 4, 6, 7, 8]:
            assert hash_idx.search(i) is not None


class TestExtendibleHashStats:
    """Testes de estatísticas."""
    
    def test_stats_initial(self):
        """Testa estatísticas iniciais."""
        hash_idx = ExtendibleHash(bucket_capacity=4, num_fields=2)
        stats = hash_idx.get_stats()
        
        assert stats['bucket_reads'] == 0
        assert stats['bucket_writes'] == 0
        assert stats['splits'] == 0
        assert stats['directory_doublings'] == 0
    
    def test_stats_after_operations(self):
        """Testa estatísticas após operações."""
        hash_idx = ExtendibleHash(bucket_capacity=2, num_fields=2)
        
        for i in range(20):
            hash_idx.insert(i, Record([i, i * 10]))
        
        stats = hash_idx. get_stats()
        
        assert stats['bucket_writes'] > 0
        assert stats['splits'] > 0
    
    def test_stats_reset(self):
        """Testa reset de estatísticas."""
        hash_idx = ExtendibleHash(bucket_capacity=4, num_fields=2)
        hash_idx.insert(1, Record([1, 100]))
        hash_idx.reset_stats()
        
        stats = hash_idx.get_stats()
        
        assert stats['bucket_reads'] == 0
        assert stats['bucket_writes'] == 0


class TestExtendibleHashNoRangeSearch:
    """Testes para confirmar que range search NÃO é suportado."""
    
    def test_no_range_search_method(self):
        """Confirma que não existe método range_search."""
        hash_idx = ExtendibleHash(bucket_capacity=4, num_fields=2)
        
        # Hash não deve ter método range_search
        assert not hasattr(hash_idx, 'range_search')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
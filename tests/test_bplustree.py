#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Testes Unitários para B+ Tree

Execute com: pytest tests/test_bplustree.py -v
"""

import pytest
import sys
sys.path. insert(0, '. .')

from src. bplustree. tree import BPlusTree
from src. common.record import Record


class TestBPlusTreeBasic:
    """Testes básicos de inserção e busca."""
    
    def test_create_tree(self):
        """Testa criação da árvore."""
        tree = BPlusTree(order=4, page_size=512, num_fields=5)
        assert tree.order == 4
        assert tree. get_height() == 1
    
    def test_insert_single(self):
        """Testa inserção de um registro."""
        tree = BPlusTree(order=4, num_fields=3)
        record = Record([1, 100, 200])
        
        result = tree.insert(1, record)
        
        assert result is True
    
    def test_search_existing(self):
        """Testa busca de registro existente."""
        tree = BPlusTree(order=4, num_fields=3)
        record = Record([1, 100, 200])
        tree.insert(1, record)
        
        found = tree.search(1)
        
        assert found is not None
        assert found.key == 1
        assert found. fields == [1, 100, 200]
    
    def test_search_nonexistent(self):
        """Testa busca de registro inexistente."""
        tree = BPlusTree(order=4, num_fields=3)
        
        found = tree. search(999)
        
        assert found is None
    
    def test_insert_duplicate(self):
        """Testa inserção de chave duplicada."""
        tree = BPlusTree(order=4, num_fields=3)
        record1 = Record([1, 100, 200])
        record2 = Record([1, 300, 400])
        
        tree. insert(1, record1)
        result = tree.insert(1, record2)
        
        assert result is False


class TestBPlusTreeSplit:
    """Testes de split de nós."""
    
    def test_leaf_split(self):
        """Testa split de nó folha."""
        tree = BPlusTree(order=3, num_fields=2)
        
        # Insere registros suficientes para causar split
        for i in range(5):
            tree. insert(i, Record([i, i * 10]))
        
        # Verifica que todos os registros podem ser encontrados
        for i in range(5):
            found = tree.search(i)
            assert found is not None
            assert found.key == i
    
    def test_multiple_splits(self):
        """Testa múltiplos splits."""
        tree = BPlusTree(order=3, num_fields=2)
        
        # Insere muitos registros
        for i in range(20):
            tree. insert(i, Record([i, i * 10]))
        
        # Verifica todos
        for i in range(20):
            found = tree.search(i)
            assert found is not None
    
    def test_height_increases(self):
        """Testa que altura aumenta com splits."""
        tree = BPlusTree(order=3, num_fields=2)
        initial_height = tree. get_height()
        
        # Insere muitos registros
        for i in range(50):
            tree.insert(i, Record([i, i * 10]))
        
        assert tree.get_height() > initial_height


class TestBPlusTreeRangeSearch:
    """Testes de busca por intervalo."""
    
    def test_range_search_empty(self):
        """Testa range search em árvore vazia."""
        tree = BPlusTree(order=4, num_fields=2)
        
        results = tree.range_search(1, 10)
        
        assert results == []
    
    def test_range_search_all(self):
        """Testa range search que retorna todos."""
        tree = BPlusTree(order=4, num_fields=2)
        for i in range(10):
            tree. insert(i, Record([i, i * 10]))
        
        results = tree.range_search(0, 9)
        
        assert len(results) == 10
    
    def test_range_search_partial(self):
        """Testa range search parcial."""
        tree = BPlusTree(order=4, num_fields=2)
        for i in range(20):
            tree. insert(i, Record([i, i * 10]))
        
        results = tree.range_search(5, 10)
        
        assert len(results) == 6
        keys = [r.key for r in results]
        assert keys == [5, 6, 7, 8, 9, 10]
    
    def test_range_search_none(self):
        """Testa range search sem resultados."""
        tree = BPlusTree(order=4, num_fields=2)
        for i in range(10):
            tree. insert(i, Record([i, i * 10]))
        
        results = tree.range_search(100, 200)
        
        assert results == []


class TestBPlusTreeDelete:
    """Testes de remoção."""
    
    def test_delete_existing(self):
        """Testa remoção de registro existente."""
        tree = BPlusTree(order=4, num_fields=2)
        tree.insert(1, Record([1, 100]))
        
        removed = tree.delete(1)
        
        assert removed is not None
        assert removed.key == 1
        assert tree.search(1) is None
    
    def test_delete_nonexistent(self):
        """Testa remoção de registro inexistente."""
        tree = BPlusTree(order=4, num_fields=2)
        
        removed = tree.delete(999)
        
        assert removed is None
    
    def test_delete_multiple(self):
        """Testa remoção de múltiplos registros."""
        tree = BPlusTree(order=4, num_fields=2)
        for i in range(10):
            tree. insert(i, Record([i, i * 10]))
        
        # Remove alguns
        for i in [0, 5, 9]:
            tree.delete(i)
        
        # Verifica removidos
        for i in [0, 5, 9]:
            assert tree.search(i) is None
        
        # Verifica restantes
        for i in [1, 2, 3, 4, 6, 7, 8]:
            assert tree. search(i) is not None


class TestBPlusTreeStats:
    """Testes de estatísticas."""
    
    def test_stats_initial(self):
        """Testa estatísticas iniciais."""
        tree = BPlusTree(order=4, num_fields=2)
        stats = tree.get_stats()
        
        assert stats['page_reads'] == 0
        assert stats['page_writes'] == 0
        assert stats['splits'] == 0
    
    def test_stats_after_operations(self):
        """Testa estatísticas após operações."""
        tree = BPlusTree(order=3, num_fields=2)
        
        for i in range(10):
            tree. insert(i, Record([i, i * 10]))
        
        stats = tree.get_stats()
        
        assert stats['page_writes'] > 0
        assert stats['splits'] > 0
    
    def test_stats_reset(self):
        """Testa reset de estatísticas."""
        tree = BPlusTree(order=4, num_fields=2)
        tree.insert(1, Record([1, 100]))
        tree.reset_stats()
        
        stats = tree.get_stats()
        
        assert stats['page_reads'] == 0
        assert stats['page_writes'] == 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
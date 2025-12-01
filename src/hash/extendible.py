#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo Principal do Hash Extensível

Implementa a classe ExtendibleHash que gerencia toda a estrutura do
índice hash extensível, incluindo o diretório e os buckets.
"""

from typing import Optional, List, Dict, Any, Set
from .bucket import Bucket
from ..common.record import Record
from ..common.config import Config


class ExtendibleHash:
    """
    Implementação de Hash Extensível. 
    
    O hash extensível é uma estrutura dinâmica que cresce conforme
    necessário, dobrando o diretório quando buckets ficam cheios.
    
    IMPORTANTE: Hash extensível NÃO suporta busca por intervalo! 
    Use apenas para busca por igualdade. 
    
    Attributes:
        global_depth: Profundidade global do diretório
        bucket_capacity: Capacidade máxima de cada bucket
        directory: Lista de ponteiros para buckets
        config: Configuração do índice
        stats: Estatísticas de operações
        
    Example:
        >>> hash_idx = ExtendibleHash(page_size=512, num_fields=10)
        >>> hash_idx.insert(1, Record([1, 100]))
        True
        >>> hash_idx.search(1)
        Record(key=1, fields=[1, 100])
    """
    
    def __init__(
        self,
        bucket_capacity: Optional[int] = None,
        page_size: int = 512,
        num_fields: int = 10
    ):
        """
        Inicializa o hash extensível. 
        
        Args:
            bucket_capacity: Capacidade por bucket (se None, calculado)
            page_size: Tamanho da página em bytes
            num_fields: Número de campos por registro
        """
        # Configuração
        self.config = Config(page_size=page_size, num_fields=num_fields)
        
        # Calcula capacidade se não fornecida
        if bucket_capacity is None:
            self.bucket_capacity = self.config.calculate_hash_bucket_capacity()
        else:
            self.bucket_capacity = max(2, bucket_capacity)
        
        # Inicializa com profundidade global 1 (2 buckets)
        self.global_depth = 1
        
        # Cria buckets iniciais
        bucket0 = Bucket(local_depth=1, capacity=self.bucket_capacity)
        bucket1 = Bucket(local_depth=1, capacity=self.bucket_capacity)
        self.directory: List[Bucket] = [bucket0, bucket1]
        
        # Estatísticas para experimentos
        self.stats: Dict[str, int] = {
            'bucket_reads': 0,
            'bucket_writes': 0,
            'splits': 0,
            'directory_doublings': 0
        }
    
    def _hash(self, key: int) -> int:
        """
        Função hash - usa os últimos global_depth bits da chave.
        
        Args:
            key: Chave a hashear
            
        Returns:
            Índice no diretório (0 a 2^global_depth - 1)
        """
        return key & ((1 << self.global_depth) - 1)
    
    def _get_bucket(self, key: int) -> Bucket:
        """
        Retorna o bucket para uma chave. 
        
        Args:
            key: Chave de busca
            
        Returns:
            Bucket correspondente
        """
        index = self._hash(key)
        self.stats['bucket_reads'] += 1
        return self.directory[index]
    
    def insert(self, key: int, record: Record) -> bool:
        """
        Insere um registro no hash. 
        
        Args:
            key: Chave do registro
            record: Registro a inserir
            
        Returns:
            True se inserido com sucesso
            
        Complexity:
            Time: O(1) amortizado
            Space: O(1)
        """
        bucket = self._get_bucket(key)
        
        # Tenta inserir diretamente
        if bucket.insert(key, record):
            self.stats['bucket_writes'] += 1
            return True
        
        # Verifica se é duplicata
        if bucket.search(key) is not None:
            return False
        
        # Bucket cheio - precisa split
        self._handle_overflow(key, record)
        return True
    
    def _handle_overflow(self, key: int, record: Record) -> None:
        """
        Trata overflow de bucket com split.
        
        Args:
            key: Chave do registro a inserir
            record: Registro a inserir
        """
        index = self._hash(key)
        bucket = self.directory[index]
        
        if bucket.local_depth < self.global_depth:
            # Split apenas o bucket
            self._split_bucket(index)
        else:
            # Precisa dobrar o diretório primeiro
            self._double_directory()
            self._split_bucket(self._hash(key))
        
        # Reinsere o registro
        new_bucket = self._get_bucket(key)
        if not new_bucket.insert(key, record):
            # Recursão se ainda cheio (raro, mas possível)
            self._handle_overflow(key, record)
        else:
            self.stats['bucket_writes'] += 1
    
    def _double_directory(self) -> None:
        """
        Dobra o tamanho do diretório.
        
        Duplica cada entrada do diretório, mantendo os ponteiros
        para os mesmos buckets. 
        """
        self.stats['directory_doublings'] += 1
        self.global_depth += 1
        
        # Duplica entradas
        new_directory: List[Bucket] = []
        for bucket in self.directory:
            new_directory.append(bucket)
            new_directory.append(bucket)
        
        self.directory = new_directory
    
    def _split_bucket(self, index: int) -> None:
        """
        Divide um bucket em dois. 
        
        Args:
            index: Índice do bucket no diretório
        """
        self.stats['splits'] += 1
        
        old_bucket = self.directory[index]
        bucket0, bucket1 = old_bucket.split()
        
        self.stats['bucket_writes'] += 2
        
        # Atualiza ponteiros do diretório
        old_local_depth = old_bucket.local_depth
        new_local_depth = bucket0.local_depth
        
        # Encontra todas as entradas que apontavam para o bucket antigo
        mask = (1 << new_local_depth) - 1
        high_bit = 1 << (new_local_depth - 1)
        
        for i in range(len(self.directory)):
            if self.directory[i] is old_bucket:
                if i & high_bit:
                    self.directory[i] = bucket1
                else:
                    self.directory[i] = bucket0
    
    def search(self, key: int) -> Optional[Record]:
        """
        Busca um registro pela chave (busca por igualdade).
        
        IMPORTANTE: Hash NÃO suporta busca por intervalo!
        
        Args:
            key: Chave a buscar
            
        Returns:
            Record se encontrado, None caso contrário
            
        Complexity:
            Time: O(1) - acesso direto ao bucket
            Space: O(1)
        """
        bucket = self._get_bucket(key)
        return bucket.search(key)
    
    def delete(self, key: int) -> Optional[Record]:
        """
        Remove um registro pela chave. 
        
        Args:
            key: Chave a remover
            
        Returns:
            Record removido ou None se não encontrado
        """
        bucket = self._get_bucket(key)
        record = bucket.delete(key)
        
        if record:
            self.stats['bucket_writes'] += 1
            # TODO: Implementar merge de buckets se desejado
        
        return record
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estatísticas de operações.
        
        Returns:
            Dicionário com contadores e métricas
        """
        stats = self.stats.copy()
        stats['global_depth'] = self.global_depth
        stats['num_buckets'] = self._count_unique_buckets()
        stats['directory_size'] = len(self.directory)
        return stats
    
    def _count_unique_buckets(self) -> int:
        """Conta o número de buckets únicos no diretório."""
        unique_buckets: Set[int] = set()
        for bucket in self.directory:
            unique_buckets.add(id(bucket))
        return len(unique_buckets)
    
    def reset_stats(self) -> None:
        """Reseta contadores de estatísticas."""
        for key in ['bucket_reads', 'bucket_writes', 'splits', 'directory_doublings']:
            self.stats[key] = 0
    
    def get_info(self) -> Dict[str, Any]:
        """
        Retorna informações gerais sobre o hash. 
        
        Returns:
            Dicionário com informações da estrutura
        """
        return {
            'global_depth': self.global_depth,
            'bucket_capacity': self.bucket_capacity,
            'num_buckets': self._count_unique_buckets(),
            'directory_size': len(self.directory),
            'page_size': self.config.page_size,
            'num_fields': self.config.num_fields,
            'stats': self.get_stats()
        }
    
    def __repr__(self) -> str:
        """Representação string do hash."""
        return (
            f"ExtendibleHash(global_depth={self.global_depth}, "
            f"buckets={self._count_unique_buckets()}, "
            f"directory_size={len(self.directory)})"
        )
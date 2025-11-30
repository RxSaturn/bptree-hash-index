#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo de Bucket do Hash Extensível

Define a classe Bucket que armazena registros em uma tabela hash extensível. 
Cada bucket tem uma profundidade local que indica quantos bits da chave
são usados para direcionar registros a este bucket.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..common.record import Record


@dataclass
class Bucket:
    """
    Bucket do hash extensível. 
    
    Um bucket armazena uma lista de pares (chave, registro) até sua
    capacidade máxima.  Quando cheio, o bucket pode ser dividido (split).
    
    Attributes:
        local_depth: Profundidade local (bits usados para este bucket)
        capacity: Capacidade máxima de registros
        records: Lista de pares (chave, registro)
        
    Example:
        >>> bucket = Bucket(local_depth=2, capacity=4)
        >>> bucket. insert(5, record)
        True
        >>> bucket. is_full()
        False
    """
    local_depth: int
    capacity: int
    records: List[Tuple[int, 'Record']] = field(default_factory=list)
    
    def is_full(self) -> bool:
        """
        Verifica se o bucket está cheio.
        
        Returns:
            True se número de registros >= capacidade
        """
        return len(self.records) >= self.capacity
    
    def is_empty(self) -> bool:
        """Verifica se o bucket está vazio."""
        return len(self.records) == 0
    
    def insert(self, key: int, record: 'Record') -> bool:
        """
        Insere um registro no bucket.
        
        Args:
            key: Chave do registro
            record: Registro a inserir
            
        Returns:
            True se inserido, False se cheio ou duplicado
        """
        # Verifica duplicata
        for k, _ in self.records:
            if k == key:
                return False
        
        if self.is_full():
            return False
        
        self.records.append((key, record))
        return True
    
    def search(self, key: int) -> Optional['Record']:
        """
        Busca um registro pela chave.
        
        Args:
            key: Chave a buscar
            
        Returns:
            Record se encontrado, None caso contrário
            
        Complexity:
            Time: O(n) onde n é o número de registros no bucket
        """
        for k, record in self. records:
            if k == key:
                return record
        return None
    
    def delete(self, key: int) -> Optional['Record']:
        """
        Remove um registro pela chave.
        
        Args:
            key: Chave a remover
            
        Returns:
            Record removido ou None se não encontrado
        """
        for i, (k, record) in enumerate(self.records):
            if k == key:
                self.records.pop(i)
                return record
        return None
    
    def split(self) -> Tuple['Bucket', 'Bucket']:
        """
        Divide o bucket em dois baseado no novo bit. 
        
        A profundidade local é incrementada e os registros são
        redistribuídos baseados no novo bit mais significativo.
        
        Returns:
            Tuple com dois novos buckets (bucket0, bucket1)
        """
        new_depth = self. local_depth + 1
        bucket0 = Bucket(local_depth=new_depth, capacity=self.capacity)
        bucket1 = Bucket(local_depth=new_depth, capacity=self.capacity)
        
        # Máscara para o novo bit
        mask = 1 << (new_depth - 1)
        
        # Redistribui registros baseado no novo bit
        for key, record in self. records:
            if key & mask:
                bucket1.records.append((key, record))
            else:
                bucket0.records. append((key, record))
        
        return bucket0, bucket1
    
    def __len__(self) -> int:
        """Retorna o número de registros no bucket."""
        return len(self.records)
    
    def __repr__(self) -> str:
        """Representação string do bucket."""
        return (
            f"Bucket(local_depth={self.local_depth}, "
            f"records={len(self. records)}/{self.capacity})"
        )
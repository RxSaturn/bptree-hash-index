#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo de Registro (Record)

Define a estrutura de dados para registros armazenados nos índices. 
Cada registro contém uma lista de campos inteiros, onde o primeiro
campo (A1) é sempre a chave primária. 
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional
import struct


@dataclass
class Record:
    """
    Registro com campos inteiros. 
    
    Um registro representa uma entrada de dados no índice, composto por
    uma lista de valores inteiros.  O primeiro campo é considerado a chave. 
    
    Attributes:
        fields: Lista de valores inteiros do registro
        
    Example:
        >>> record = Record([1, 100, 200, 300])
        >>> record. key
        1
        >>> record.num_fields
        4
        >>> data = record.serialize()
        >>> restored = Record.deserialize(data, 4)
        >>> restored.fields
        [1, 100, 200, 300]
    """
    fields: List[int] = field(default_factory=list)
    
    @property
    def key(self) -> int:
        """
        Retorna a chave do registro (primeiro campo).
        
        Returns:
            Valor do primeiro campo ou 0 se registro vazio
        """
        return self.fields[0] if self.fields else 0
    
    @property
    def num_fields(self) -> int:
        """Retorna o número de campos do registro."""
        return len(self.fields)
    
    def serialize(self) -> bytes:
        """
        Serializa o registro para bytes.
        
        Cada campo inteiro é convertido para 4 bytes (32 bits, signed).
        
        Returns:
            Representação em bytes do registro
            
        Example:
            >>> record = Record([1, 2, 3])
            >>> len(record.serialize())
            12  # 3 campos * 4 bytes
        """
        if not self.fields:
            return b''
        return struct.pack(f'{len(self.fields)}i', *self.fields)
    
    @classmethod
    def deserialize(cls, data: bytes, num_fields: int) -> 'Record':
        """
        Deserializa bytes para um registro. 
        
        Args:
            data: Bytes a deserializar
            num_fields: Número de campos esperados
            
        Returns:
            Novo objeto Record com os campos deserializados
            
        Raises:
            struct.error: Se os dados não correspondem ao formato esperado
        """
        if not data:
            return cls(fields=[])
        fields = list(struct.unpack(f'{num_fields}i', data[:num_fields * 4]))
        return cls(fields=fields)
    
    @classmethod
    def from_siogen_row(cls, row: dict) -> 'Record':
        """
        Cria um registro a partir de uma linha do SIOgen.
        
        Args:
            row: Dicionário com colunas A1, A2, ..., An
            
        Returns:
            Novo objeto Record
            
        Example:
            >>> row = {'OP': '+', 'A1': 10, 'A2': 20, 'A3': 30}
            >>> record = Record.from_siogen_row(row)
            >>> record.fields
            [10, 20, 30]
        """
        fields = []
        i = 1
        while f'A{i}' in row:
            fields.append(int(row[f'A{i}']))
            i += 1
        return cls(fields=fields)
    
    def __repr__(self) -> str:
        """Representação string do registro."""
        return f"Record(key={self.key}, fields={self.fields})"
    
    def __eq__(self, other: object) -> bool:
        """Compara dois registros por seus campos."""
        if not isinstance(other, Record):
            return False
        return self.fields == other. fields
    
    def __hash__(self) -> int:
        """Hash baseado nos campos do registro."""
        return hash(tuple(self.fields))
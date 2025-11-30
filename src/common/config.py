#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo de Configuração

Define constantes e configurações globais para as estruturas de índice.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """
    Configuração global para as estruturas de índice.
    
    Attributes:
        page_size: Tamanho da página em bytes (mínimo 256)
        num_fields: Número de campos por registro
        field_size: Tamanho de cada campo em bytes (4 para int32)
        min_order: Ordem mínima para B+ Tree (3 para garantir splits corretos)
    """
    page_size: int = 512
    num_fields: int = 10
    field_size: int = 4  # bytes por int
    min_order: int = 3   # mínimo de chaves por nó
    
    def __post_init__(self):
        """Valida a configuração após inicialização."""
        if self.page_size < 256:
            raise ValueError(
                f"Tamanho de página deve ser >= 256 bytes, recebido: {self.page_size}"
            )
        if self. num_fields < 1:
            raise ValueError(
                f"Número de campos deve ser >= 1, recebido: {self.num_fields}"
            )
    
    @property
    def record_size(self) -> int:
        """Tamanho de um registro em bytes."""
        return self. num_fields * self. field_size
    
    @property
    def key_size(self) -> int:
        """Tamanho de uma chave em bytes."""
        return self.field_size
    
    def calculate_bplus_order(self) -> int:
        """
        Calcula a ordem ideal da B+ Tree baseada no tamanho da página.
        
        Para nós folha: cada entrada = chave + registro
        Para garantir mínimo 3 chaves, ordem deve ser >= 3
        
        Returns:
            Ordem calculada (mínimo 3)
        """
        # Tamanho de uma entrada no nó folha
        entry_size = self.key_size + self. record_size
        
        # Ordem = quantas entradas cabem na página
        order = self.page_size // entry_size
        
        return max(self.min_order, order)
    
    def calculate_hash_bucket_capacity(self) -> int:
        """
        Calcula a capacidade ideal de um bucket hash.
        
        Returns:
            Número de registros por bucket (mínimo 2)
        """
        entry_size = self. key_size + self.record_size
        capacity = self.page_size // entry_size
        return max(2, capacity)


# Configuração padrão
DEFAULT_CONFIG = Config()


# Configurações para experimentos
EXPERIMENT_CONFIGS = {
    'small': Config(page_size=256, num_fields=5),
    'medium': Config(page_size=512, num_fields=10),
    'large': Config(page_size=1024, num_fields=20),
    'xlarge': Config(page_size=2048, num_fields=50),
}
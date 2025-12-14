#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo de Nós da Árvore B+

Define as classes Node, LeafNode e InternalNode que compõem a estrutura
da árvore B+. Os nós folha armazenam os registros reais e são encadeados
para suportar busca por intervalo eficiente.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ..common.record import Record


class Node(ABC):
    """
    Classe base abstrata para nós da árvore B+.
    
    Define a interface comum para nós folha e internos, incluindo
    operações básicas como verificação de overflow/underflow e split.
    
    Attributes:
        order: Ordem da árvore (máximo de chaves por nó)
        keys: Lista de chaves armazenadas no nó
        parent: Referência para o nó pai (None se for raiz)
    """
    
    def __init__(self, order: int):
        """
        Inicializa um nó. 
        
        Args:
            order: Ordem da árvore (máximo de chaves por nó)
            
        Raises:
            ValueError: Se order < 3
        """
        if order < 3:
            raise ValueError(f"Ordem deve ser >= 3, recebido: {order}")
        
        self.order = order
        self.keys: List[int] = []
        self.parent: Optional['InternalNode'] = None
    
    @property
    @abstractmethod
    def is_leaf(self) -> bool:
        """Retorna True se for nó folha."""
        pass
    
    def is_full(self) -> bool:
        """
        Verifica se o nó está cheio (precisa de split).
        
        Returns:
            True se número de chaves >= ordem
        """
        return len(self.keys) >= self.order
    
    def is_underflow(self) -> bool:
        """
        Verifica se o nó tem menos que o mínimo de chaves.
        
        O mínimo é ceil(order/2) - 1 para nós não-raiz.
        
        Returns:
            True se número de chaves < mínimo
        """
        min_keys = (self.order + 1) // 2 - 1
        return len(self.keys) < min_keys
    
    def is_root(self) -> bool:
        """Verifica se é o nó raiz."""
        return self.parent is None
    
    @abstractmethod
    def split(self) -> Tuple['Node', int]:
        """
        Divide o nó quando está cheio.
        
        Returns:
            Tuple (novo_nó, chave_promovida)
        """
        pass
    
    def _binary_search(self, key: int) -> int:
        """
        Busca binária para encontrar posição de inserção.
        
        Args:
            key: Chave a buscar
            
        Returns:
            Índice onde a chave deveria ser inserida
        """
        left, right = 0, len(self.keys)
        while left < right:
            mid = (left + right) // 2
            if self.keys[mid] < key:
                left = mid + 1
            else:
                right = mid
        return left


class LeafNode(Node):
    """
    Nó folha da árvore B+. 
    
    Armazena os registros reais e mantém ponteiros para os nós folha
    adjacentes (next e prev) para permitir busca por intervalo eficiente. 
    
    Attributes:
        records: Lista de registros armazenados
        next: Ponteiro para o próximo nó folha
        prev: Ponteiro para o nó folha anterior
    """
    
    def __init__(self, order: int):
        """
        Inicializa um nó folha. 
        
        Args:
            order: Ordem da árvore
        """
        super().__init__(order)
        self.records: List['Record'] = []
        self.next: Optional['LeafNode'] = None
        self.prev: Optional['LeafNode'] = None
    
    @property
    def is_leaf(self) -> bool:
        """Sempre True para nós folha."""
        return True
    
    def insert(self, key: int, record: 'Record') -> bool:
        """
        Insere um registro no nó folha mantendo ordem crescente.
        
        Args:
            key: Chave do registro
            record: Registro a ser inserido
            
        Returns:
            True se inserido com sucesso, False se chave duplicada
        """
        pos = self._binary_search(key)
        
        # Verifica duplicata
        if pos < len(self.keys) and self.keys[pos] == key:
            return False
        
        # Insere na posição correta
        self.keys.insert(pos, key)
        self.records.insert(pos, record)
        return True
    
    def search(self, key: int) -> Optional['Record']:
        """
        Busca um registro pela chave.
        
        Args:
            key: Chave a buscar
            
        Returns:
            Record se encontrado, None caso contrário
        """
        pos = self._binary_search(key)
        if pos < len(self.keys) and self.keys[pos] == key:
            return self.records[pos]
        return None
    
    def delete(self, key: int) -> Optional['Record']:
        """
        Remove um registro pela chave.
        
        Args:
            key: Chave a remover
            
        Returns:
            Record removido ou None se não encontrado
        """
        pos = self._binary_search(key)
        if pos < len(self.keys) and self.keys[pos] == key:
            self.keys.pop(pos)
            return self.records.pop(pos)
        return None
    
    def split(self) -> Tuple['LeafNode', int]:
        """
        Divide o nó folha ao meio.
        
        A primeira chave do novo nó é COPIADA (não movida) para o pai,
        diferente de nós internos onde a chave é movida.
        
        Returns:
            Tuple (novo_nó_folha, chave_a_promover)
        """
        mid = len(self.keys) // 2
        
        # Cria novo nó com metade superior
        new_node = LeafNode(self.order)
        new_node.keys = self.keys[mid:]
        new_node.records = self.records[mid:]
        
        # Mantém metade inferior no nó atual
        self.keys = self.keys[:mid]
        self.records = self.records[:mid]
        
        # Atualiza ponteiros de lista encadeada
        new_node.next = self.next
        new_node.prev = self
        if self.next:
            self.next.prev = new_node
        self.next = new_node
        
        # Promove CÓPIA da primeira chave do novo nó
        return new_node, new_node.keys[0]
    
    def __repr__(self) -> str:
        """Representação string do nó folha."""
        return f"LeafNode(keys={self.keys}, records={len(self.records)})"


class InternalNode(Node):
    """
    Nó interno da árvore B+.
    
    Armazena apenas chaves de roteamento e ponteiros para filhos.
    Não armazena registros - estes estão apenas nos nós folha.
    
    Invariante: len(children) == len(keys) + 1
    
    Attributes:
        children: Lista de ponteiros para nós filhos
    """
    
    def __init__(self, order: int):
        """
        Inicializa um nó interno. 
        
        Args:
            order: Ordem da árvore
        """
        super().__init__(order)
        self.children: List[Node] = []
    
    @property
    def is_leaf(self) -> bool:
        """Sempre False para nós internos."""
        return False
    
    def find_child(self, key: int) -> Node:
        """
        Encontra o filho apropriado para uma chave.
        
        Usa busca binária para encontrar o intervalo correto.
        
        Args:
            key: Chave de busca
            
        Returns:
            Nó filho apropriado para continuar a busca
        """
        for i, k in enumerate(self.keys):
            if key < k:
                return self.children[i]
        return self.children[-1]
    
    def find_child_index(self, key: int) -> int:
        """
        Encontra o índice do filho apropriado para uma chave. 
        
        Args:
            key: Chave de busca
            
        Returns:
            Índice do filho no array children
        """
        for i, k in enumerate(self.keys):
            if key < k:
                return i
        return len(self.children) - 1
    
    def insert_child(self, key: int, child: Node) -> None:
        """
        Insere uma nova chave e filho após split de um filho.
        
        Args:
            key: Chave promovida do split
            child: Novo nó filho criado pelo split
        """
        pos = 0
        while pos < len(self.keys) and self.keys[pos] < key:
            pos += 1
        
        self.keys.insert(pos, key)
        self.children.insert(pos + 1, child)
        child.parent = self
    
    def split(self) -> Tuple['InternalNode', int]:
        """
        Divide o nó interno. 
        
        Diferente do nó folha, a chave do meio é MOVIDA (não copiada)
        para o pai durante o split.
        
        Returns:
            Tuple (novo_nó_interno, chave_promovida)
        """
        mid = len(self.keys) // 2
        promoted_key = self.keys[mid]
        
        # Cria novo nó com metade superior
        new_node = InternalNode(self.order)
        new_node.keys = self.keys[mid + 1:]  # Exclui chave promovida
        new_node.children = self.children[mid + 1:]
        
        # Atualiza parent dos filhos movidos
        for child in new_node.children:
            child.parent = new_node
        
        # Mantém metade inferior no nó atual
        self.keys = self.keys[:mid]
        self.children = self.children[:mid + 1]
        
        return new_node, promoted_key
    
    def __repr__(self) -> str:
        """Representação string do nó interno."""
        return f"InternalNode(keys={self.keys}, children={len(self.children)})"
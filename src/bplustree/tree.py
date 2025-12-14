#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo Principal da Árvore B+

Implementa a classe BPlusTree que gerencia toda a estrutura da árvore,
incluindo operações de inserção, busca, busca por intervalo e remoção.

Para detalhes de arquitetura e uso, veja: docs/architecture.md
"""

from typing import List, Optional, Dict, Any
from .node import Node, LeafNode, InternalNode
from ..common.record import Record
from ..common.config import Config


class BPlusTree:
    """
    Implementação de Árvore B+ para indexação.

    A árvore B+ é uma estrutura de dados balanceada otimizada para
    operações em disco. Todas as chaves e registros são armazenados
    nos nós folha, que são encadeados para permitir busca por intervalo.

    Attributes
    ----------
    order : int
        Ordem da árvore (máximo de chaves por nó)
    root : Node
        Raiz da árvore
    config : Config
        Configuração da árvore (página, campos)
    stats : Dict[str, int]
        Estatísticas instrumentadas para experimentos (leituras, splits, etc)

    Examples
    --------
    >>> tree = BPlusTree(page_size=512, num_fields=10)
    >>> tree.insert(1, Record([1, 100, 200]))
    True
    >>> tree.search(1)
    Record(key=1, fields=[1, 100, 200])
    >>> tree.range_search(0, 10)
    [Record(key=1, ...)]
    """

    def __init__(
        self,
        order: Optional[int] = None,
        page_size: int = 512,
        num_fields: int = 10
    ):
        """
        Inicializa a árvore B+.

        Parameters
        ----------
        order : Optional[int]
            Ordem da árvore (se None, calculado a partir do page_size)
        page_size : int
            Tamanho da página em bytes (mínimo 256)
        num_fields : int
            Número de campos por registro

        Raises
        ------
        ValueError
            Se page_size < 256
        """
        self.config = Config(page_size=page_size, num_fields=num_fields)
        if order is None:
            self.order = self.config.calculate_bplus_order()
        else:
            self.order = max(3, order)

        self.root: Node = LeafNode(self.order)
        self.stats: Dict[str, int] = {
            'page_reads': 0,
            'page_writes': 0,
            'splits': 0,
            'merges': 0,
            'height': 1
        }

    def insert(self, key: int, record: Record) -> bool:
        """
        Insere um registro na árvore.

        Parameters
        ----------
        key : int
            Chave do registro
        record : Record
            Registro a inserir

        Returns
        -------
        bool
            True se inserido com sucesso, False se chave duplicada

        Complexity
        ----------
        O(log n) leitura, O(log n) splits
        """
        leaf = self._find_leaf(key)
        self.stats['page_reads'] += 1

        if not leaf.insert(key, record):
            return False  # Chave duplicada

        self.stats['page_writes'] += 1

        if leaf.is_full():
            self._handle_split(leaf)

        return True

    def _find_leaf(self, key: int) -> LeafNode:
        """
        Navega até o nó folha apropriado para a chave.

        Parameters
        ----------
        key : int

        Returns
        -------
        LeafNode
            Nó folha apropriado
        """
        node = self.root
        while not node.is_leaf:
            self.stats['page_reads'] += 1
            node = node.find_child(key)
        return node  # type: ignore

    def _handle_split(self, node: Node) -> None:
        """
        Executa e propaga split quando necessário.

        Parameters
        ----------
        node : Node
            Nó a ser dividido
        """
        self.stats['splits'] += 1
        new_node, promoted_key = node.split()
        self.stats['page_writes'] += 2

        if node.parent is None:
            self._create_new_root(node, new_node, promoted_key)
        else:
            node.parent.insert_child(promoted_key, new_node)
            if node.parent.is_full():
                self._handle_split(node.parent)

    def _create_new_root(
        self,
        left_child: Node,
        right_child: Node,
        key: int
    ) -> None:
        """
        Cria nova raiz após split da raiz original.

        Parameters
        ----------
        left_child : Node
            Filho esquerdo/original
        right_child : Node
            Novo nó do split
        key : int
            Chave promovida
        """
        new_root = InternalNode(self.order)
        new_root.keys = [key]
        new_root.children = [left_child, right_child]
        left_child.parent = new_root
        right_child.parent = new_root
        self.root = new_root
        self.stats['page_writes'] += 1
        self.stats['height'] += 1

    def search(self, key: int) -> Optional[Record]:
        """
        Busca um registro pela chave (igualdade).

        Parameters
        ----------
        key : int

        Returns
        -------
        Optional[Record]
            Registro encontrado ou None
        """
        leaf = self._find_leaf(key)
        self.stats['page_reads'] += 1
        return leaf.search(key)

    def range_search(self, start_key: int, end_key: int) -> List[Record]:
        """
        Busca por intervalo [start_key, end_key].

        Parameters
        ----------
        start_key : int
        end_key : int

        Returns
        -------
        List[Record]
            Todos registros do intervalo [start_key, end_key]

        Complexity
        ----------
        O(log n + k) onde k válidos
        """
        if start_key > end_key:
            return []

        results: List[Record] = []
        leaf = self._find_leaf(start_key)
        self.stats['page_reads'] += 1

        while leaf is not None:
            for i, key in enumerate(leaf.keys):
                if key > end_key:
                    return results
                if start_key <= key <= end_key:
                    results.append(leaf.records[i])
            leaf = leaf.next
            if leaf is not None:
                self.stats['page_reads'] += 1

        return results

    def delete(self, key: int) -> Optional[Record]:
        """
        Remove um registro pela chave.

        Parameters
        ----------
        key : int

        Returns
        -------
        Optional[Record]
            Registro removido, ou None

        Notes
        -----
        Merge/redistribute não implementados aqui (apenas simples)

        Complexity
        ----------
        O(log n)
        """
        leaf = self._find_leaf(key)
        self.stats['page_reads'] += 1

        record = leaf.delete(key)

        if record:
            self.stats['page_writes'] += 1
            # Underflow/merge opcional

        return record

    def get_stats(self) -> Dict[str, int]:
        """
        Retorna estatísticas de operações.

        Returns
        -------
        Dict[str, int]
            Contadores de operações
        """
        return self.stats.copy()

    def reset_stats(self) -> None:
        """Reseta todos os contadores de estatísticas."""
        for key in self.stats:
            if key != 'height':
                self.stats[key] = 0

    def get_height(self) -> int:
        """
        Retorna altura atual da árvore.

        Returns
        -------
        int
        """
        return self.stats['height']

    def get_info(self) -> Dict[str, Any]:
        """
        Retorna informações gerais da estrutura.

        Returns
        -------
        Dict[str, Any]
        """
        return {
            'order': self.order,
            'height': self.stats['height'],
            'page_size': self.config.page_size,
            'num_fields': self.config.num_fields,
            'stats': self.get_stats()
        }

    def __repr__(self) -> str:
        """Representação string da árvore."""
        return (
            f"BPlusTree(order={self.order}, height={self.stats['height']}, "
            f"page_size={self.config.page_size})"
        )
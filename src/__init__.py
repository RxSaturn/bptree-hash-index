"""Módulo raiz do projeto de índices."""

from .bplustree import BPlusTree, Node, LeafNode, InternalNode
from .hash import ExtendibleHash, Bucket
from .common import Record, Config

__all__ = [
    "BPlusTree", "Node", "LeafNode", "InternalNode",
    "ExtendibleHash", "Bucket", 
    "Record", "Config"
]

__version__ = "1.0.0"
__author__ = "Henrique Augusto, Rayssa Mendes, Henrique Evangelista"

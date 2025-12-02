#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gera figura da estrutura de diretórios do projeto.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def criar_estrutura_projeto():
    """Cria diagrama da estrutura de diretórios."""
    
    # Estrutura do projeto
    estrutura = """
bptree-hash-index/
├── src/
│   ├── bplustree/
│   │   ├── __init__.py
│   │   ├── node.py
│   │   └── tree.py
│   ├── hash/
│   │   ├── __init__.py
│   │   ├── bucket.py
│   │   └── extendible.py
│   └── common/
│       ├── __init__.py
│       ├── record.py
│       └── config.py
├── tests/
├── experiments/
├── data/
├── results/
├── artigo/
└── tools/
    └── siogen.py
    """.strip()
    
    # Criar figura
    fig, ax = plt.subplots(figsize=(8, 10))
    ax.axis('off')
    
    # Adicionar texto com fonte monoespaçada
    ax.text(0.05, 0.95, estrutura, 
            transform=ax.transAxes,
            fontsize=11,
            fontfamily='monospace',
            verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='#f5f5f5', edgecolor='#cccccc'))
    
    plt.title('Estrutura de Diretórios do Projeto', 
              fontsize=14, fontweight='bold', pad=10)
    
    # Salvar
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'figuras')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'estrutura_projeto.png')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"✅ Figura salva em: {output_path}")
    return output_path

if __name__ == '__main__':
    criar_estrutura_projeto()
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gera tabela de comparação teórica como imagem PNG. 
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

def criar_tabela_comparacao():
    """Cria tabela de comparação teórica entre B+ Tree e Hash."""
    
    # Dados da tabela
    colunas = ['Operação', 'B+ Tree', 'Hash Extensível']
    dados = [
        ['Busca por igualdade', 'O(log n)', 'O(1)'],
        ['Busca por intervalo', 'O(log n + k)', 'Não suportado'],
        ['Inserção', 'O(log n)', 'O(1) amortizado'],
        ['Remoção', 'O(log n)', 'O(1)'],
        ['Uso de memória', 'Moderado', 'Variável'],
        ['Ordenação natural', 'Sim', 'Não'],
    ]
    
    # Criar figura
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.axis('off')
    ax.axis('tight')
    
    # Criar tabela
    tabela = ax.table(
        cellText=dados,
        colLabels=colunas,
        loc='center',
        cellLoc='center',
        colColours=['#4472C4', '#4472C4', '#4472C4'],
        colWidths=[0.35, 0.25, 0.25]
    )
    
    # Estilizar tabela
    tabela.auto_set_font_size(False)
    tabela.set_fontsize(11)
    tabela.scale(1.2, 1.8)
    
    # Cores do cabeçalho (texto branco)
    for j in range(len(colunas)):
        tabela[(0, j)].set_text_props(color='white', fontweight='bold')
    
    # Cores alternadas nas linhas
    for i in range(1, len(dados) + 1):
        for j in range(len(colunas)):
            if i % 2 == 0:
                tabela[(i, j)].set_facecolor('#D9E2F3')
            else:
                tabela[(i, j)].set_facecolor('#FFFFFF')
    
    plt.title('Comparação Teórica: B+ Tree vs Hash Extensível', 
              fontsize=14, fontweight='bold', pad=20)
    
    # Salvar
    output_dir = os.path.join(os.path.dirname(__file__), '..', 'figuras')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'tabela_comparacao_teorica.png')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"✅ Tabela salva em: {output_path}")
    return output_path

if __name__ == '__main__':
    criar_tabela_comparacao()
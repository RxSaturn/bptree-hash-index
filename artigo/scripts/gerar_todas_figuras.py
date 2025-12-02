#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gera todas as figuras e tabelas necessárias para o artigo. 

Uso:
    python artigo/scripts/gerar_todas_figuras.py
"""

import os
import sys

# Adiciona diretório ao path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

def main():
    print("=" * 60)
    print("🎨 GERADOR DE FIGURAS E TABELAS PARA O ARTIGO")
    print("=" * 60)
    
    # 1.  Tabela de comparação teórica
    print("\n📊 1. Gerando tabela de comparação teórica...")
    try:
        from gerar_tabela_comparacao import criar_tabela_comparacao
        criar_tabela_comparacao()
    except Exception as e:
        print(f" ❌ Erro: {e}")
    
    # 2. Figura da estrutura do projeto
    print("\n📁 2. Gerando figura da estrutura do projeto...")
    try:
        from gerar_estrutura_projeto import criar_estrutura_projeto
        criar_estrutura_projeto()
    except Exception as e:
        print(f" ❌ Erro: {e}")
    
    # 3. Tabela de resultados
    print("\n📈 3. Gerando tabela de resultados...")
    try:
        from gerar_tabela_resultados import criar_tabela_resultados, gerar_latex_tabela
        criar_tabela_resultados()
        gerar_latex_tabela()
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 60)
    print("✅ GERAÇÃO CONCLUÍDA!")
    print("=" * 60)
    
    # Lista arquivos gerados
    figuras_dir = os.path.join(script_dir, '..', 'figuras')
    if os.path.exists(figuras_dir):
        print("\n📂 Arquivos gerados em artigo/figuras/:")
        for f in sorted(os.listdir(figuras_dir)):
            if f.endswith(('.png', '.pdf', '.tex')):
                print(f" • {f}")

if __name__ == '__main__':
    main()
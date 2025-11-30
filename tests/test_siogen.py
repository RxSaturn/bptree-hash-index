#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Testes Unitários para SIOgen

Execute com: pytest tests/test_siogen.py -v
"""

import pytest
import os
import sys
import subprocess

sys.path.insert(0, '..')


class TestSiogenCLI:
    """Testes para o CLI do SIOgen."""
    
    def get_siogen_path(self):
        """Retorna o caminho para siogen.py."""
        return os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'tools', 'siogen.py'
        )
    
    def test_generates_valid_output(self, tmp_path):
        """Testa que gera arquivo válido."""
        output_file = tmp_path / "output.csv"
        result = subprocess.run([
            sys.executable, self.get_siogen_path(),
            '-a', '3',
            '-i', '10',
            '-s', '5',
            '-d', '2',
            '-f', str(output_file)
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert os.path.exists(output_file)
        
        with open(output_file, 'r') as f:
            lines = f.readlines()
        
        # Header + operations
        assert len(lines) > 1
        # Verify header
        assert 'OP' in lines[0]
    
    def test_creates_directory(self, tmp_path):
        """Testa que cria diretório se necessário."""
        output_dir = tmp_path / "nested" / "dir"
        output_file = output_dir / "output.csv"
        
        result = subprocess.run([
            sys.executable, self.get_siogen_path(),
            '-a', '3',
            '-i', '10',
            '-s', '5',
            '-d', '2',
            '-f', str(output_file)
        ], capture_output=True, text=True)
        
        assert result.returncode == 0
        assert os.path.exists(output_file)
    
    def test_validates_deletions_greater_than_insertions(self, tmp_path):
        """Testa erro quando deleções > inserções."""
        output_file = tmp_path / "output.csv"
        result = subprocess.run([
            sys.executable, self.get_siogen_path(),
            '-a', '3',
            '-i', '5',
            '-s', '5',
            '-d', '10',  # More deletions than insertions
            '-f', str(output_file)
        ], capture_output=True, text=True)
        
        assert result.returncode != 0
        assert 'deleções' in result.stderr.lower() or 'deletions' in result.stderr.lower()
    
    def test_validates_negative_insertions(self, tmp_path):
        """Testa erro com inserções negativas."""
        output_file = tmp_path / "output.csv"
        result = subprocess.run([
            sys.executable, self.get_siogen_path(),
            '-a', '3',
            '-i', '-5',
            '-s', '5',
            '-d', '2',
            '-f', str(output_file)
        ], capture_output=True, text=True)
        
        # argparse might catch this or our validation will
        assert result.returncode != 0 or not os.path.exists(output_file)
    
    def test_reproducible_with_seed(self, tmp_path):
        """Testa que mesma seed gera mesmos dados."""
        output_file1 = tmp_path / "output1.csv"
        output_file2 = tmp_path / "output2.csv"
        
        # Run with same seed twice
        for output_file in [output_file1, output_file2]:
            subprocess.run([
                sys.executable, self.get_siogen_path(),
                '-a', '3',
                '-i', '10',
                '-s', '5',
                '-d', '2',
                '-f', str(output_file),
                '-e', '12345'  # Same seed
            ], capture_output=True, text=True)
        
        with open(output_file1, 'r') as f1, open(output_file2, 'r') as f2:
            content1 = f1.read()
            content2 = f2.read()
        
        assert content1 == content2
    
    def test_handles_zero_insertions(self, tmp_path):
        """Testa com zero inserções."""
        output_file = tmp_path / "output.csv"
        result = subprocess.run([
            sys.executable, self.get_siogen_path(),
            '-a', '3',
            '-i', '0',
            '-s', '5',
            '-d', '0',
            '-f', str(output_file)
        ], capture_output=True, text=True)
        
        # Should succeed but generate only searches
        assert result.returncode == 0
        assert os.path.exists(output_file)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

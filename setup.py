#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bptree-hash-index",
    version="1.0.0",
    author="Seu Nome",
    author_email="seu.email@exemplo.com",
    description="Implementação de índices B+ Tree e Hash Extensível em Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RxSaturn/bptree-hash-index",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Database :: Database Engines/Servers",
    ],
    python_requires=">=3.8",
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
        "viz": [
            "matplotlib>=3.5.0",
            "pandas>=1.4.0",
            "numpy>=1.21.0",
        ],
    },
)
"""Extração: uv run python -m uerj.extracao (lê data/raw/ e grava data/bronze/)."""
from .bronze import main

if __name__ == '__main__':
    main()

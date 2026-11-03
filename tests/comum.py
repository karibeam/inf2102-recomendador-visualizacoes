"""Ajudante compartilhado pelos testes: imprime OK/FALHA e para no primeiro erro."""

import sys


def confere(descricao, condicao):
    print(f"  {'OK   ' if condicao else 'FALHA'} {descricao}")
    if not condicao:
        raise SystemExit(1)


def caminho_src():
    """Permite `import config` etc. a partir de tests/."""
    from pathlib import Path

    src = str(Path(__file__).resolve().parent.parent / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    return src

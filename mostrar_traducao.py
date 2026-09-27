"""Mostra, passo a passo, a traducao da pergunta e o que ela encontra na base.

Serve para documentar o sistema: imprime a pergunta original, a traducao feita
pelo LLM, a consulta tecnica e os trechos da base recuperados -- e compara a
busca COM traducao contra a busca com a pergunta crua.

    .venv/bin/python mostrar_traducao.py "quero comparar as vendas de 5 lojas"
    .venv/bin/python mostrar_traducao.py            # usa a pergunta de exemplo
"""

import sys
import textwrap
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

import config
from indexar import abrir_banco
from recomendar import buscar, consulta_tecnica, referencia, traduzir_pergunta

EXEMPLO = "Quero mostrar a distribuição das idades dos meus clientes"
TRECHOS = 2  # quantos achados da base mostrar por extenso


def titulo(texto):
    print(f"\n{texto}\n{'-' * len(texto)}")


def indentar(texto, espacos=4):
    return textwrap.indent(texto, " " * espacos)


def main(pergunta):
    llm, banco = config.get_chat(), abrir_banco()

    titulo("PERGUNTA DO USUÁRIO")
    print(indentar(f'"{pergunta}"'))

    titulo("PASSO 1 · TRADUÇÃO PELO LLM (classifica, não recomenda gráfico)")
    traducao = traduzir_pergunta(pergunta, llm)
    print(indentar(f"tarefa ........: {traducao.get('tarefa')}"))
    print(indentar(f"tipos de dado .: {', '.join(traducao.get('tipos_de_dado') or []) or '—'}"))
    print(indentar(f"descrição .....: {traducao.get('descricao')}"))

    if traducao.get("tarefa") == "nenhuma":
        print(indentar("\n(pergunta fora do escopo: o sistema recusa sem buscar na base)"))
        return

    titulo("PASSO 2 · CONSULTA TÉCNICA (mesmo formato dos documentos da base)")
    consulta = consulta_tecnica(traducao)
    print(indentar(consulta))

    titulo(f"PASSO 3 · TRECHOS DA BASE MAIS PARECIDOS (similaridade de cosseno)")
    resultados = buscar(consulta, banco)
    for i, (doc, similaridade) in enumerate(resultados[:TRECHOS], 1):
        print(indentar(f"\n[{i}] similaridade {similaridade:.3f} · {referencia(doc.metadata['fonte'])}"))
        print(indentar(f"    fonte: {doc.metadata['fonte']}"))
        print(indentar(doc.page_content, 8))
    restantes = [f"{s:.3f}" for _, s in resultados[TRECHOS:]]
    if restantes:
        print(indentar(f"\n(mais {len(restantes)} achados recuperados: {', '.join(restantes)})"))

    titulo("EFEITO DA TRADUÇÃO (a mesma busca, sem traduzir a pergunta)")
    crua = buscar(pergunta, banco)
    print(indentar(f"pergunta crua      -> melhor similaridade {crua[0][1]:.3f}"))
    print(indentar(f"pergunta traduzida -> melhor similaridade {resultados[0][1]:.3f}"))
    iguais = sum(d.metadata["fonte"] == c.metadata["fonte"] for (d, _), (c, _) in zip(resultados, crua))
    print(indentar(f"achados em comum entre as duas buscas: {iguais} de {len(resultados)}"))


if __name__ == "__main__":
    main(" ".join(sys.argv[1:]) or EXEMPLO)

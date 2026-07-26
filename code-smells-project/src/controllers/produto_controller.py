"""Produto controller: validation + orchestration. Returns (data, status)."""
from src.models import produto_model

CATEGORIAS_VALIDAS = [
    "informatica", "moveis", "vestuario", "geral", "eletronicos", "livros",
]


def listar():
    produtos = produto_model.get_all()
    return {"dados": produtos, "sucesso": True}, 200


def buscar(produto_id):
    produto = produto_model.get_by_id(produto_id)
    if produto:
        return {"dados": produto, "sucesso": True}, 200
    return {"erro": "Produto não encontrado", "sucesso": False}, 404


def _validar_payload(dados):
    if not dados:
        return "Dados inválidos"
    if "nome" not in dados:
        return "Nome é obrigatório"
    if "preco" not in dados:
        return "Preço é obrigatório"
    if "estoque" not in dados:
        return "Estoque é obrigatório"
    if not isinstance(dados["preco"], (int, float)) or dados["preco"] < 0:
        return "Preço não pode ser negativo"
    if not isinstance(dados["estoque"], int) or dados["estoque"] < 0:
        return "Estoque não pode ser negativo"
    nome = dados["nome"]
    if not isinstance(nome, str) or len(nome) < 2:
        return "Nome muito curto"
    if len(nome) > 200:
        return "Nome muito longo"
    return None


def criar(dados):
    erro = _validar_payload(dados)
    if erro:
        return {"erro": erro}, 400

    categoria = dados.get("categoria", "geral")
    if categoria not in CATEGORIAS_VALIDAS:
        return {"erro": "Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS)}, 400

    produto_id = produto_model.create(
        dados["nome"], dados.get("descricao", ""), dados["preco"],
        dados["estoque"], categoria,
    )
    return {"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}, 201


def atualizar(produto_id, dados):
    if not produto_model.get_by_id(produto_id):
        return {"erro": "Produto não encontrado"}, 404

    erro = _validar_payload(dados)
    if erro:
        return {"erro": erro}, 400

    produto_model.update(
        produto_id, dados["nome"], dados.get("descricao", ""), dados["preco"],
        dados["estoque"], dados.get("categoria", "geral"),
    )
    return {"sucesso": True, "mensagem": "Produto atualizado"}, 200


def deletar(produto_id):
    if not produto_model.get_by_id(produto_id):
        return {"erro": "Produto não encontrado"}, 404
    produto_model.delete(produto_id)
    return {"sucesso": True, "mensagem": "Produto deletado"}, 200


def buscar_lista(termo, categoria, preco_min, preco_max):
    try:
        preco_min = float(preco_min) if preco_min not in (None, "") else None
        preco_max = float(preco_max) if preco_max not in (None, "") else None
    except (TypeError, ValueError):
        return {"erro": "preco_min/preco_max devem ser numéricos"}, 400

    resultados = produto_model.search(termo, categoria, preco_min, preco_max)
    return {"dados": resultados, "total": len(resultados), "sucesso": True}, 200

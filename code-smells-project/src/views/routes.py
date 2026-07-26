"""Route declarations (thin views).

Map the HTTP request/body/query/params to controller calls and translate the
controller's ``(data, status)`` return into a JSON response. No business logic,
no SQL here. Public paths, methods and response shapes are unchanged.
"""
from flask import Blueprint, jsonify, request

from src.controllers import (
    pedido_controller,
    produto_controller,
    relatorio_controller,
    usuario_controller,
)

api = Blueprint("api", __name__)


def _respond(result):
    data, status = result
    return jsonify(data), status


# ---- Root & health -------------------------------------------------------
@api.route("/")
def index():
    return jsonify({
        "mensagem": "Bem-vindo à API da Loja",
        "versao": "1.0.0",
        "endpoints": {
            "produtos": "/produtos",
            "usuarios": "/usuarios",
            "pedidos": "/pedidos",
            "login": "/login",
            "relatorios": "/relatorios/vendas",
            "health": "/health",
        },
    })


@api.route("/health", methods=["GET"])
def health_check():
    return _respond(relatorio_controller.health())


# ---- Produtos ------------------------------------------------------------
@api.route("/produtos", methods=["GET"])
def listar_produtos():
    return _respond(produto_controller.listar())


@api.route("/produtos/busca", methods=["GET"])
def buscar_produtos():
    return _respond(produto_controller.buscar_lista(
        request.args.get("q", ""),
        request.args.get("categoria", None),
        request.args.get("preco_min", None),
        request.args.get("preco_max", None),
    ))


@api.route("/produtos/<int:id>", methods=["GET"])
def buscar_produto(id):
    return _respond(produto_controller.buscar(id))


@api.route("/produtos", methods=["POST"])
def criar_produto():
    return _respond(produto_controller.criar(request.get_json(silent=True)))


@api.route("/produtos/<int:id>", methods=["PUT"])
def atualizar_produto(id):
    return _respond(produto_controller.atualizar(id, request.get_json(silent=True)))


@api.route("/produtos/<int:id>", methods=["DELETE"])
def deletar_produto(id):
    return _respond(produto_controller.deletar(id))


# ---- Usuarios ------------------------------------------------------------
@api.route("/usuarios", methods=["GET"])
def listar_usuarios():
    return _respond(usuario_controller.listar())


@api.route("/usuarios/<int:id>", methods=["GET"])
def buscar_usuario(id):
    return _respond(usuario_controller.buscar(id))


@api.route("/usuarios", methods=["POST"])
def criar_usuario():
    return _respond(usuario_controller.criar(request.get_json(silent=True)))


@api.route("/login", methods=["POST"])
def login():
    return _respond(usuario_controller.login(request.get_json(silent=True)))


# ---- Pedidos -------------------------------------------------------------
@api.route("/pedidos", methods=["POST"])
def criar_pedido():
    return _respond(pedido_controller.criar(request.get_json(silent=True)))


@api.route("/pedidos", methods=["GET"])
def listar_todos_pedidos():
    return _respond(pedido_controller.listar_todos())


@api.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
def listar_pedidos_usuario(usuario_id):
    return _respond(pedido_controller.listar_por_usuario(usuario_id))


@api.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
def atualizar_status_pedido(pedido_id):
    return _respond(pedido_controller.atualizar_status(
        pedido_id, request.get_json(silent=True)
    ))


# ---- Relatorios ----------------------------------------------------------
@api.route("/relatorios/vendas", methods=["GET"])
def relatorio_vendas():
    return _respond(relatorio_controller.relatorio_vendas())


# ---- Admin (fixed, non-arbitrary ops) ------------------------------------
@api.route("/admin/reset-db", methods=["POST"])
def reset_database():
    return _respond(relatorio_controller.reset_db())


def register_routes(app):
    app.register_blueprint(api)

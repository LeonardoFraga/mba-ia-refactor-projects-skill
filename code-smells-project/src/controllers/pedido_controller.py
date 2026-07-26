"""Pedido controller: validation + orchestration. Returns (data, status)."""
from src.models import pedido_model
from src.services import notification_service

STATUS_VALIDOS = ["pendente", "aprovado", "enviado", "entregue", "cancelado"]


def criar(dados):
    if not dados:
        return {"erro": "Dados inválidos"}, 400

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        return {"erro": "Usuario ID é obrigatório"}, 400
    if not itens or len(itens) == 0:
        return {"erro": "Pedido deve ter pelo menos 1 item"}, 400

    for item in itens:
        if not isinstance(item, dict) or "produto_id" not in item or "quantidade" not in item:
            return {"erro": "Cada item requer produto_id e quantidade"}, 400
        if not isinstance(item["quantidade"], int) or item["quantidade"] <= 0:
            return {"erro": "Quantidade deve ser um inteiro positivo"}, 400

    resultado = pedido_model.create(usuario_id, itens)
    if "erro" in resultado:
        return {"erro": resultado["erro"], "sucesso": False}, 400

    notification_service.notify_pedido_criado(resultado["pedido_id"], usuario_id)
    return {"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}, 201


def listar_por_usuario(usuario_id):
    return {"dados": pedido_model.get_by_usuario(usuario_id), "sucesso": True}, 200


def listar_todos():
    return {"dados": pedido_model.get_all(), "sucesso": True}, 200


def atualizar_status(pedido_id, dados):
    novo_status = (dados or {}).get("status", "")
    if novo_status not in STATUS_VALIDOS:
        return {"erro": "Status inválido"}, 400

    pedido_model.update_status(pedido_id, novo_status)
    notification_service.notify_status_alterado(pedido_id, novo_status)
    return {"sucesso": True, "mensagem": "Status atualizado"}, 200

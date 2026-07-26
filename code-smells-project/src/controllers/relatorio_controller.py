"""Relatorio + health controllers. Returns (data, status)."""
from src.models import pedido_model, produto_model, usuario_model


def relatorio_vendas():
    stats = pedido_model.get_vendas_stats()
    faturamento = stats["faturamento"]
    total_pedidos = stats["total_pedidos"]

    if faturamento > 10000:
        desconto = faturamento * 0.1
    elif faturamento > 5000:
        desconto = faturamento * 0.05
    elif faturamento > 1000:
        desconto = faturamento * 0.02
    else:
        desconto = 0

    relatorio = {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": stats["pendentes"],
        "pedidos_aprovados": stats["aprovados"],
        "pedidos_cancelados": stats["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }
    return {"dados": relatorio, "sucesso": True}, 200


def health():
    # Liveness + counts only — no secrets or internal config leaked.
    return {
        "status": "ok",
        "database": "connected",
        "counts": {
            "produtos": produto_model.count(),
            "usuarios": usuario_model.count(),
            "pedidos": pedido_model.count(),
        },
        "versao": "1.0.0",
    }, 200


def reset_db():
    from src.config.database import reset_database
    reset_database()
    return {"mensagem": "Banco de dados resetado", "sucesso": True}, 200

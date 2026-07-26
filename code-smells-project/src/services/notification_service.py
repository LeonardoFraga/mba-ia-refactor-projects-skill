"""Side-effect notifications (email / SMS / push) isolated from controllers.

Uses the logging module instead of print. In a real system these would call
external providers; here they log, keeping the concern out of HTTP handlers.
"""
import logging

logger = logging.getLogger("loja.notifications")


def notify_pedido_criado(pedido_id, usuario_id):
    logger.info("EMAIL: Pedido %s criado para usuario %s", pedido_id, usuario_id)
    logger.info("SMS: Seu pedido foi recebido!")
    logger.info("PUSH: Novo pedido recebido pelo sistema")


def notify_status_alterado(pedido_id, novo_status):
    if novo_status == "aprovado":
        logger.info("Pedido %s foi aprovado! Preparar envio.", pedido_id)
    elif novo_status == "cancelado":
        logger.info("Pedido %s cancelado. Devolver estoque.", pedido_id)

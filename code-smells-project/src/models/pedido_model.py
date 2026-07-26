"""Pedido data access. Parameterized SQL, single-JOIN reads (no N+1)."""
from src.config.database import get_connection


def create(usuario_id, itens):
    """Create an order with its items, decrementing stock. Parameterized.

    Returns {"pedido_id", "total"} on success or {"erro": ...} on a domain
    validation failure (product missing / insufficient stock).
    """
    conn = get_connection()
    try:
        total = 0
        for item in itens:
            produto = conn.execute(
                "SELECT * FROM produtos WHERE id = ?", (item["produto_id"],)
            ).fetchone()
            if produto is None:
                return {"erro": "Produto " + str(item["produto_id"]) + " não encontrado"}
            if produto["estoque"] < item["quantidade"]:
                return {"erro": "Estoque insuficiente para " + produto["nome"]}
            total += produto["preco"] * item["quantidade"]

        cursor = conn.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total),
        )
        pedido_id = cursor.lastrowid

        for item in itens:
            produto = conn.execute(
                "SELECT preco FROM produtos WHERE id = ?", (item["produto_id"],)
            ).fetchone()
            conn.execute(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade,"
                " preco_unitario) VALUES (?, ?, ?, ?)",
                (pedido_id, item["produto_id"], item["quantidade"], produto["preco"]),
            )
            conn.execute(
                "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
                (item["quantidade"], item["produto_id"]),
            )

        conn.commit()
        return {"pedido_id": pedido_id, "total": total}
    finally:
        conn.close()


def _fetch_pedidos(usuario_id=None):
    """Fetch orders (optionally by user) plus their items in ONE JOIN query.

    Replaces the previous N+1 pattern and de-duplicates the two near-identical
    order builders into a single function.
    """
    query = (
        "SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,"
        " ip.produto_id, ip.quantidade, ip.preco_unitario, pr.nome AS produto_nome"
        " FROM pedidos p"
        " LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id"
        " LEFT JOIN produtos pr ON pr.id = ip.produto_id"
    )
    params = []
    if usuario_id is not None:
        query += " WHERE p.usuario_id = ?"
        params.append(usuario_id)
    query += " ORDER BY p.id"

    conn = get_connection()
    try:
        rows = conn.execute(query, params).fetchall()
    finally:
        conn.close()

    pedidos = {}
    ordem = []
    for row in rows:
        pid = row["id"]
        if pid not in pedidos:
            pedidos[pid] = {
                "id": pid,
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
            ordem.append(pid)
        if row["produto_id"] is not None:
            pedidos[pid]["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"] or "Desconhecido",
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return [pedidos[pid] for pid in ordem]


def get_by_usuario(usuario_id):
    return _fetch_pedidos(usuario_id=usuario_id)


def get_all():
    return _fetch_pedidos()


def update_status(pedido_id, novo_status):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id)
        )
        conn.commit()
        return True
    finally:
        conn.close()


def get_vendas_stats():
    """Aggregate order metrics for the sales report (data only)."""
    conn = get_connection()
    try:
        total_pedidos = conn.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
        faturamento = conn.execute("SELECT SUM(total) FROM pedidos").fetchone()[0] or 0
        pendentes = conn.execute(
            "SELECT COUNT(*) FROM pedidos WHERE status = ?", ("pendente",)
        ).fetchone()[0]
        aprovados = conn.execute(
            "SELECT COUNT(*) FROM pedidos WHERE status = ?", ("aprovado",)
        ).fetchone()[0]
        cancelados = conn.execute(
            "SELECT COUNT(*) FROM pedidos WHERE status = ?", ("cancelado",)
        ).fetchone()[0]
        return {
            "total_pedidos": total_pedidos,
            "faturamento": faturamento,
            "pendentes": pendentes,
            "aprovados": aprovados,
            "cancelados": cancelados,
        }
    finally:
        conn.close()


def count():
    conn = get_connection()
    try:
        return conn.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
    finally:
        conn.close()

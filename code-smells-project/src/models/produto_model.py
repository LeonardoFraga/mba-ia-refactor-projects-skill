"""Produto data access. Parameterized SQL only, no HTTP objects."""
from src.config.database import get_connection


def _serialize(row):
    return {
        "id": row["id"],
        "nome": row["nome"],
        "descricao": row["descricao"],
        "preco": row["preco"],
        "estoque": row["estoque"],
        "categoria": row["categoria"],
        "ativo": row["ativo"],
        "criado_em": row["criado_em"],
    }


def get_all():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM produtos").fetchall()
        return [_serialize(row) for row in rows]
    finally:
        conn.close()


def get_by_id(produto_id):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM produtos WHERE id = ?", (produto_id,)
        ).fetchone()
        return _serialize(row) if row else None
    finally:
        conn.close()


def create(nome, descricao, preco, estoque, categoria):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria)"
            " VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def update(produto_id, nome, descricao, preco, estoque, categoria):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?,"
            " estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def delete(produto_id):
    conn = get_connection()
    try:
        conn.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        conn.commit()
        return True
    finally:
        conn.close()


def search(termo=None, categoria=None, preco_min=None, preco_max=None):
    query = "SELECT * FROM produtos WHERE 1=1"
    params = []
    if termo:
        query += " AND (nome LIKE ? OR descricao LIKE ?)"
        like = "%" + termo + "%"
        params.extend([like, like])
    if categoria:
        query += " AND categoria = ?"
        params.append(categoria)
    if preco_min is not None:
        query += " AND preco >= ?"
        params.append(preco_min)
    if preco_max is not None:
        query += " AND preco <= ?"
        params.append(preco_max)

    conn = get_connection()
    try:
        rows = conn.execute(query, params).fetchall()
        return [_serialize(row) for row in rows]
    finally:
        conn.close()


def count():
    conn = get_connection()
    try:
        return conn.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
    finally:
        conn.close()

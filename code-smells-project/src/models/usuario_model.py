"""Usuario data access. Passwords are hashed; never serialized back out."""
from werkzeug.security import check_password_hash, generate_password_hash

from src.config.database import get_connection


def _serialize(row):
    # The senha/hash field is deliberately NEVER included in serialization.
    return {
        "id": row["id"],
        "nome": row["nome"],
        "email": row["email"],
        "tipo": row["tipo"],
        "criado_em": row["criado_em"],
    }


def get_all():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM usuarios").fetchall()
        return [_serialize(row) for row in rows]
    finally:
        conn.close()


def get_by_id(usuario_id):
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM usuarios WHERE id = ?", (usuario_id,)
        ).fetchone()
        return _serialize(row) if row else None
    finally:
        conn.close()


def get_by_email(email):
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM usuarios WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()


def create(nome, email, senha, tipo="cliente"):
    conn = get_connection()
    try:
        cursor = conn.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, generate_password_hash(senha, method="pbkdf2:sha256"), tipo),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def authenticate(email, senha):
    """Return the serialized user (no password) if credentials are valid."""
    row = get_by_email(email)
    if row and check_password_hash(row["senha"], senha):
        return {
            "id": row["id"],
            "nome": row["nome"],
            "email": row["email"],
            "tipo": row["tipo"],
        }
    return None


def count():
    conn = get_connection()
    try:
        return conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
    finally:
        conn.close()

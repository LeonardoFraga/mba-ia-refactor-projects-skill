"""Usuario controller: validation + orchestration. Returns (data, status)."""
import re

from src.models import usuario_model

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def listar():
    # Passwords are never serialized by the model, so none leak here.
    return {"dados": usuario_model.get_all(), "sucesso": True}, 200


def buscar(usuario_id):
    usuario = usuario_model.get_by_id(usuario_id)
    if usuario:
        return {"dados": usuario, "sucesso": True}, 200
    return {"erro": "Usuário não encontrado"}, 404


def criar(dados):
    if not dados:
        return {"erro": "Dados inválidos"}, 400

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        return {"erro": "Nome, email e senha são obrigatórios"}, 400
    if not _EMAIL_RE.match(email):
        return {"erro": "Email inválido"}, 400
    if len(senha) < 6:
        return {"erro": "Senha deve ter ao menos 6 caracteres"}, 400

    usuario_id = usuario_model.create(nome, email, senha)
    return {"dados": {"id": usuario_id}, "sucesso": True}, 201


def login(dados):
    if not dados:
        return {"erro": "Dados inválidos"}, 400
    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not email or not senha:
        return {"erro": "Email e senha são obrigatórios"}, 400

    usuario = usuario_model.authenticate(email, senha)
    if usuario:
        return {"dados": usuario, "sucesso": True, "mensagem": "Login OK"}, 200
    return {"erro": "Email ou senha inválidos", "sucesso": False}, 401

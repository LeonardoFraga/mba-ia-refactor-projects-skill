"""User orchestration: validation, persistence and serialization for users."""
import re
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError

from database import db
from models.user import User
from models.task import Task
from middlewares.error_handler import ApiError
from utils.helpers import VALID_ROLES, MIN_PASSWORD_LENGTH

EMAIL_RE = r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$'


def _validate_email(email):
    if not re.match(EMAIL_RE, email):
        raise ApiError(400, 'Email inválido')


def list_users():
    # Eager-load tasks so task_count doesn't trigger a query per user.
    users = User.query.options(joinedload(User.tasks)).all()
    result = []
    for u in users:
        data = u.to_dict()
        data['task_count'] = len(u.tasks)
        result.append(data)
    return result


def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise ApiError(404, 'Usuário não encontrado')
    data = user.to_dict()
    tasks = Task.query.filter_by(user_id=user_id).all()
    data['tasks'] = [t.to_dict() for t in tasks]
    return data


def create_user(data):
    if not data:
        raise ApiError(400, 'Dados inválidos')

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not name:
        raise ApiError(400, 'Nome é obrigatório')
    if not email:
        raise ApiError(400, 'Email é obrigatório')
    if not password:
        raise ApiError(400, 'Senha é obrigatória')

    _validate_email(email)

    if len(password) < MIN_PASSWORD_LENGTH:
        raise ApiError(400, 'Senha deve ter no mínimo 4 caracteres')

    if User.query.filter_by(email=email).first():
        raise ApiError(409, 'Email já cadastrado')

    if role not in VALID_ROLES:
        raise ApiError(400, 'Role inválido')

    user = User()
    user.name = name
    user.email = email
    user.set_password(password)
    user.role = role

    try:
        db.session.add(user)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise ApiError(500, 'Erro ao criar usuário')
    return user.to_dict()


def update_user(user_id, data):
    user = db.session.get(User, user_id)
    if not user:
        raise ApiError(404, 'Usuário não encontrado')
    if not data:
        raise ApiError(400, 'Dados inválidos')

    if 'name' in data:
        user.name = data['name']

    if 'email' in data:
        _validate_email(data['email'])
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            raise ApiError(409, 'Email já cadastrado')
        user.email = data['email']

    if 'password' in data:
        if len(data['password']) < MIN_PASSWORD_LENGTH:
            raise ApiError(400, 'Senha muito curta')
        user.set_password(data['password'])

    if 'role' in data:
        if data['role'] not in VALID_ROLES:
            raise ApiError(400, 'Role inválido')
        user.role = data['role']

    if 'active' in data:
        user.active = data['active']

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise ApiError(500, 'Erro ao atualizar')
    return user.to_dict()


def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        raise ApiError(404, 'Usuário não encontrado')

    Task.query.filter_by(user_id=user_id).delete()
    try:
        db.session.delete(user)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise ApiError(500, 'Erro ao deletar')
    return {'message': 'Usuário deletado com sucesso'}


def login(data):
    if not data:
        raise ApiError(400, 'Dados inválidos')

    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        raise ApiError(400, 'Email e senha são obrigatórios')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise ApiError(401, 'Credenciais inválidas')
    if not user.active:
        raise ApiError(403, 'Usuário inativo')

    return {
        'message': 'Login realizado com sucesso',
        'user': user.to_dict(),
        'token': 'fake-jwt-token-' + str(user.id),
    }

"""Category orchestration."""
from sqlalchemy.exc import SQLAlchemyError

from database import db
from models.task import Task
from models.category import Category
from middlewares.error_handler import ApiError


def list_categories():
    # Batch the per-category task counts into one grouped query (no N+1).
    counts = dict(
        db.session.query(Task.category_id, db.func.count(Task.id))
        .group_by(Task.category_id).all()
    )
    result = []
    for c in Category.query.all():
        data = c.to_dict()
        data['task_count'] = counts.get(c.id, 0)
        result.append(data)
    return result


def create_category(data):
    if not data:
        raise ApiError(400, 'Dados inválidos')

    name = data.get('name')
    if not name:
        raise ApiError(400, 'Nome é obrigatório')

    category = Category()
    category.name = name
    category.description = data.get('description', '')
    category.color = data.get('color', '#000000')

    try:
        db.session.add(category)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise ApiError(500, 'Erro ao criar categoria')
    return category.to_dict()


def update_category(cat_id, data):
    cat = db.session.get(Category, cat_id)
    if not cat:
        raise ApiError(404, 'Categoria não encontrada')
    if not data:
        raise ApiError(400, 'Dados inválidos')

    if 'name' in data:
        cat.name = data['name']
    if 'description' in data:
        cat.description = data['description']
    if 'color' in data:
        cat.color = data['color']

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise ApiError(500, 'Erro ao atualizar')
    return cat.to_dict()


def delete_category(cat_id):
    cat = db.session.get(Category, cat_id)
    if not cat:
        raise ApiError(404, 'Categoria não encontrada')
    try:
        db.session.delete(cat)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise ApiError(500, 'Erro ao deletar')
    return {'message': 'Categoria deletada'}

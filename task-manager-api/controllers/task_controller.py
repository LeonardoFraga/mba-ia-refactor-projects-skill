"""Task orchestration: validation, persistence and serialization for tasks.

Returns plain serializable data; raises ApiError for expected failures. No
Flask request/response objects here.
"""
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError

from database import db
from models.task import Task
from models.user import User
from models.category import Category
from middlewares.error_handler import ApiError
from utils.helpers import VALID_STATUSES, MIN_TITLE_LENGTH, MAX_TITLE_LENGTH


def _validate_title(title):
    if not title:
        raise ApiError(400, 'Título é obrigatório')
    if len(title) < MIN_TITLE_LENGTH:
        raise ApiError(400, 'Título muito curto')
    if len(title) > MAX_TITLE_LENGTH:
        raise ApiError(400, 'Título muito longo')


def _validate_status(status):
    if status not in VALID_STATUSES:
        raise ApiError(400, 'Status inválido')


def _validate_priority(priority):
    if priority is None or priority < 1 or priority > 5:
        raise ApiError(400, 'Prioridade deve ser entre 1 e 5')


def _parse_due_date(value):
    try:
        return datetime.strptime(value, '%Y-%m-%d')
    except (ValueError, TypeError):
        raise ApiError(400, 'Formato de data inválido. Use YYYY-MM-DD')


def list_tasks():
    # Eager-load relations to avoid N+1 (one query instead of 1 + 2N).
    tasks = Task.query.options(
        joinedload(Task.user), joinedload(Task.category)
    ).all()
    return [t.to_dict(include_overdue=True, include_relations=True) for t in tasks]


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        raise ApiError(404, 'Task não encontrada')
    return task.to_dict(include_overdue=True)


def create_task(data):
    if not data:
        raise ApiError(400, 'Dados inválidos')

    title = data.get('title')
    _validate_title(title)

    status = data.get('status', 'pending')
    priority = data.get('priority', 3)
    user_id = data.get('user_id')
    category_id = data.get('category_id')
    due_date = data.get('due_date')
    tags = data.get('tags')

    _validate_status(status)
    _validate_priority(priority)

    if user_id and not db.session.get(User, user_id):
        raise ApiError(404, 'Usuário não encontrado')
    if category_id and not db.session.get(Category, category_id):
        raise ApiError(404, 'Categoria não encontrada')

    task = Task()
    task.title = title
    task.description = data.get('description', '')
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    if due_date:
        task.due_date = _parse_due_date(due_date)

    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    try:
        db.session.add(task)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise ApiError(500, 'Erro ao criar task')
    return task.to_dict()


def update_task(task_id, data):
    task = db.session.get(Task, task_id)
    if not task:
        raise ApiError(404, 'Task não encontrada')
    if not data:
        raise ApiError(400, 'Dados inválidos')

    if 'title' in data:
        _validate_title(data['title'])
        task.title = data['title']

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        _validate_status(data['status'])
        task.status = data['status']

    if 'priority' in data:
        _validate_priority(data['priority'])
        task.priority = data['priority']

    if 'user_id' in data:
        if data['user_id'] and not db.session.get(User, data['user_id']):
            raise ApiError(404, 'Usuário não encontrado')
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id'] and not db.session.get(Category, data['category_id']):
            raise ApiError(404, 'Categoria não encontrada')
        task.category_id = data['category_id']

    if 'due_date' in data:
        task.due_date = _parse_due_date(data['due_date']) if data['due_date'] else None

    if 'tags' in data:
        tags = data['tags']
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise ApiError(500, 'Erro ao atualizar')
    return task.to_dict()


def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        raise ApiError(404, 'Task não encontrada')
    try:
        db.session.delete(task)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise ApiError(500, 'Erro ao deletar')
    return {'message': 'Task deletada com sucesso'}


def search_tasks(query='', status='', priority='', user_id=''):
    tasks = Task.query
    if query:
        tasks = tasks.filter(
            db.or_(Task.title.like(f'%{query}%'), Task.description.like(f'%{query}%'))
        )
    if status:
        tasks = tasks.filter(Task.status == status)
    if priority:
        try:
            tasks = tasks.filter(Task.priority == int(priority))
        except ValueError:
            raise ApiError(400, 'Prioridade inválida')
    if user_id:
        try:
            tasks = tasks.filter(Task.user_id == int(user_id))
        except ValueError:
            raise ApiError(400, 'user_id inválido')
    return [t.to_dict() for t in tasks.all()]


def task_stats():
    counts = dict(
        db.session.query(Task.status, db.func.count(Task.id)).group_by(Task.status).all()
    )
    total = sum(counts.values())
    done = counts.get('done', 0)
    overdue_count = sum(1 for t in Task.query.all() if t.is_overdue())
    return {
        'total': total,
        'pending': counts.get('pending', 0),
        'in_progress': counts.get('in_progress', 0),
        'done': done,
        'cancelled': counts.get('cancelled', 0),
        'overdue': overdue_count,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0,
    }


def list_user_tasks(user_id):
    if not db.session.get(User, user_id):
        raise ApiError(404, 'Usuário não encontrado')
    tasks = Task.query.filter_by(user_id=user_id).all()
    result = []
    for t in tasks:
        result.append({
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'status': t.status,
            'priority': t.priority,
            'created_at': str(t.created_at),
            'due_date': str(t.due_date) if t.due_date else None,
            'overdue': t.is_overdue(),
        })
    return result

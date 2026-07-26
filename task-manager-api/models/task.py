from database import db
from utils.helpers import utcnow

VALID_STATUSES = ['pending', 'in_progress', 'done', 'cancelled']
_CLOSED_STATUSES = ('done', 'cancelled')


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='pending')
    priority = db.Column(db.Integer, default=3)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    def to_dict(self, include_overdue=False, include_relations=False):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'due_date': str(self.due_date) if self.due_date else None,
            'tags': self.tags.split(',') if self.tags else [],
        }
        if include_overdue:
            data['overdue'] = self.is_overdue()
        if include_relations:
            data['user_name'] = self.user.name if self.user else None
            data['category_name'] = self.category.name if self.category else None
        return data

    def validate_status(self, new_status):
        return new_status in VALID_STATUSES

    def validate_priority(self, p):
        return 1 <= p <= 5

    def is_overdue(self):
        """Single source of truth for the overdue rule."""
        if not self.due_date:
            return False
        if self.status in _CLOSED_STATUSES:
            return False
        due = self.due_date
        if due.tzinfo is not None:
            due = due.replace(tzinfo=None)
        return due < utcnow()

    def days_overdue(self):
        if not self.is_overdue():
            return 0
        due = self.due_date
        if due.tzinfo is not None:
            due = due.replace(tzinfo=None)
        return (utcnow() - due).days

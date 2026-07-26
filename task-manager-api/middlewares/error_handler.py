"""Centralized error handling.

Controllers raise ``ApiError`` for expected domain/validation failures; the
registered handlers translate every error into a consistent JSON response,
so route functions never build error payloads themselves.
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    """Domain/validation error carrying an HTTP status code."""

    def __init__(self, status_code, message):
        super().__init__(message)
        self.status_code = status_code
        self.message = message


def register_error_handlers(app):
    @app.errorhandler(ApiError)
    def handle_api_error(err):
        return jsonify({'error': err.message}), err.status_code

    @app.errorhandler(404)
    def handle_not_found(err):
        return jsonify({'error': 'Recurso não encontrado'}), 404

    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        return jsonify({'error': err.description}), err.code

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        app.logger.exception('Unhandled error: %s', err)
        return jsonify({'error': 'Erro interno'}), 500

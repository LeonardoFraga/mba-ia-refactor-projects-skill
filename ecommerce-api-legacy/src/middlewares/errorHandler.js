// Centralized error handling. Domain errors carry an HTTP status code.
'use strict';

class AppError extends Error {
    constructor(message, statusCode = 500) {
        super(message);
        this.name = 'AppError';
        this.statusCode = statusCode;
    }
}

// Express error-handling middleware (4 args). Must be mounted last.
// eslint-disable-next-line no-unused-vars
function errorHandler(err, req, res, next) {
    const status = err.statusCode || 500;
    const message = status === 500 ? 'Erro interno do servidor' : err.message;
    if (status === 500) {
        // Log server faults (never card data / secrets) for diagnostics.
        console.error('[ERROR]', err.message);
    }
    res.status(status).json({ error: message });
}

// 404 fallback for unmatched routes.
function notFound(req, res) {
    res.status(404).json({ error: 'Rota não encontrada' });
}

module.exports = { AppError, errorHandler, notFound };

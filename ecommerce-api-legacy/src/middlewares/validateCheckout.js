// Input validation for POST /api/checkout. Runs before the controller.
'use strict';

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

module.exports = function validateCheckout(req, res, next) {
    const b = req.body || {};
    const errors = [];

    if (!b.usr || typeof b.usr !== 'string') errors.push('usr é obrigatório');
    if (!b.eml || typeof b.eml !== 'string' || !EMAIL_RE.test(b.eml)) {
        errors.push('eml deve ser um e-mail válido');
    }
    const courseId = Number(b.c_id);
    if (!Number.isInteger(courseId) || courseId <= 0) {
        errors.push('c_id deve ser um inteiro positivo');
    }
    const card = String(b.card || '').replace(/\D/g, '');
    if (card.length < 12) errors.push('card deve conter os dígitos do cartão');

    if (errors.length) {
        return res.status(400).json({ error: 'Bad Request', details: errors });
    }

    // Normalize the parsed course id for downstream layers.
    req.body.c_id = courseId;
    return next();
};

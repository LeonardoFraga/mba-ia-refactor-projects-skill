// Validates the :id path param for user routes.
'use strict';

module.exports = function validateUserId(req, res, next) {
    const id = Number(req.params.id);
    if (!Number.isInteger(id) || id <= 0) {
        return res.status(400).json({ error: 'id inválido' });
    }
    return next();
};

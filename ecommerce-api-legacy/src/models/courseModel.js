// Course data access. Parameterized queries only.
'use strict';

const db = require('../config/database');

function findActiveById(id) {
    return db.get("SELECT id, title, price, active FROM courses WHERE id = ? AND active = 1", [id]);
}

function findAll() {
    return db.all("SELECT id, title, price, active FROM courses");
}

module.exports = { findActiveById, findAll };

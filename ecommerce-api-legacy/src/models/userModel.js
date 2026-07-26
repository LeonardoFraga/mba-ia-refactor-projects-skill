// User data access. Parameterized queries only; no HTTP objects here.
'use strict';

const db = require('../config/database');

function findByEmail(email) {
    return db.get("SELECT id, name, email FROM users WHERE email = ?", [email]);
}

function findById(id) {
    return db.get("SELECT id, name, email FROM users WHERE id = ?", [id]);
}

async function create(name, email, passHash) {
    const { lastID } = await db.run(
        "INSERT INTO users (name, email, pass) VALUES (?, ?, ?)",
        [name, email, passHash]
    );
    return lastID;
}

function deleteById(id) {
    return db.run("DELETE FROM users WHERE id = ?", [id]);
}

module.exports = { findByEmail, findById, create, deleteById };

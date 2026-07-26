// Audit log data access. Parameterized queries only.
'use strict';

const db = require('../config/database');

function log(action) {
    return db.run(
        "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
        [action]
    );
}

module.exports = { log };

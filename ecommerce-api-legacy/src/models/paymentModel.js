// Payment data access. Parameterized queries only.
'use strict';

const db = require('../config/database');

async function create(enrollmentId, amount, status) {
    const { lastID } = await db.run(
        "INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)",
        [enrollmentId, amount, status]
    );
    return lastID;
}

// Delete every payment tied to any of the given enrollment ids.
function deleteByEnrollmentIds(enrollmentIds) {
    if (!enrollmentIds.length) return Promise.resolve({ changes: 0 });
    const placeholders = enrollmentIds.map(() => '?').join(',');
    return db.run(
        `DELETE FROM payments WHERE enrollment_id IN (${placeholders})`,
        enrollmentIds
    );
}

module.exports = { create, deleteByEnrollmentIds };

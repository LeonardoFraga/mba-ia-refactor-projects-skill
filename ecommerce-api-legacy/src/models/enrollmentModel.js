// Enrollment data access. Parameterized queries only.
'use strict';

const db = require('../config/database');

async function create(userId, courseId) {
    const { lastID } = await db.run(
        "INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)",
        [userId, courseId]
    );
    return lastID;
}

function findIdsByUser(userId) {
    return db.all("SELECT id FROM enrollments WHERE user_id = ?", [userId]);
}

function deleteByUser(userId) {
    return db.run("DELETE FROM enrollments WHERE user_id = ?", [userId]);
}

module.exports = { create, findIdsByUser, deleteByUser };

// Financial report orchestration. Groups the single JOIN result in memory.
'use strict';

const reportModel = require('../models/reportModel');

async function financialReport(req, res, next) {
    try {
        const rows = await reportModel.getFinancialRows();

        // Group rows by course, preserving the original response shape:
        // [{ course, revenue, students: [{ student, paid }] }]
        const byCourse = new Map();

        for (const row of rows) {
            if (!byCourse.has(row.course_id)) {
                byCourse.set(row.course_id, {
                    course: row.course_title,
                    revenue: 0,
                    students: []
                });
            }
            const entry = byCourse.get(row.course_id);

            // A course with no enrollments yields a single row with null student.
            if (row.student_name === null && row.payment_amount === null) continue;

            if (row.payment_status === 'PAID') {
                entry.revenue += row.payment_amount;
            }
            entry.students.push({
                student: row.student_name || 'Unknown',
                paid: row.payment_amount != null ? row.payment_amount : 0
            });
        }

        return res.json(Array.from(byCourse.values()));
    } catch (err) {
        return next(err);
    }
}

module.exports = { financialReport };

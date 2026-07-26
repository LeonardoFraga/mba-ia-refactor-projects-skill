// User orchestration. Deleting a user cleans up related rows (no orphans).
'use strict';

const db = require('../config/database');
const userModel = require('../models/userModel');
const enrollmentModel = require('../models/enrollmentModel');
const paymentModel = require('../models/paymentModel');

async function deleteUser(req, res, next) {
    try {
        const id = parseInt(req.params.id, 10);

        await db.withTransaction(async () => {
            // Cascade: remove payments -> enrollments -> the user itself.
            const enrollments = await enrollmentModel.findIdsByUser(id);
            const enrollmentIds = enrollments.map((e) => e.id);

            await paymentModel.deleteByEnrollmentIds(enrollmentIds);
            await enrollmentModel.deleteByUser(id);
            await userModel.deleteById(id);
        });

        return res.json({
            msg: 'Usuário deletado. Matrículas e pagamentos relacionados foram removidos.'
        });
    } catch (err) {
        return next(err);
    }
}

module.exports = { deleteUser };

// Checkout orchestration. No SQL, no HTTP-building here beyond returning data.
'use strict';

const db = require('../config/database');
const courseModel = require('../models/courseModel');
const userModel = require('../models/userModel');
const enrollmentModel = require('../models/enrollmentModel');
const paymentModel = require('../models/paymentModel');
const auditModel = require('../models/auditModel');
const cryptoService = require('../services/cryptoService');
const paymentService = require('../services/paymentService');
const cacheService = require('../services/cacheService');
const { AppError } = require('../middlewares/errorHandler');

// Body is validated upstream by validateCheckout middleware.
async function checkout(req, res, next) {
    try {
        const name = req.body.usr;
        const email = req.body.eml;
        const password = req.body.pwd;
        const courseId = req.body.c_id;
        const card = req.body.card;

        const course = await courseModel.findActiveById(courseId);
        if (!course) throw new AppError('Curso não encontrado', 404);

        // Charge first — a denied card must not persist anything.
        const { status } = paymentService.charge(card, course.price);
        if (status === 'DENIED') throw new AppError('Pagamento recusado', 400);

        // Find or create the user (password stored as a real salted hash).
        let user = await userModel.findByEmail(email);
        let userId;
        if (!user) {
            const passHash = cryptoService.hash(password || '123456');
            userId = await userModel.create(name, email, passHash);
        } else {
            userId = user.id;
        }

        // Persist enrollment + payment + audit atomically.
        const enrollmentId = await db.withTransaction(async () => {
            const enrId = await enrollmentModel.create(userId, courseId);
            await paymentModel.create(enrId, course.price, status);
            await auditModel.log(`Checkout curso ${courseId} por ${userId}`);
            return enrId;
        });

        cacheService.set(`last_checkout_${userId}`, course.title);

        return res.status(200).json({
            msg: 'Sucesso',
            enrollment_id: enrollmentId,
            status
        });
    } catch (err) {
        return next(err);
    }
}

module.exports = { checkout };

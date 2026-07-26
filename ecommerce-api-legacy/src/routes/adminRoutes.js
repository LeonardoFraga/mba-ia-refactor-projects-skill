// Thin route layer for admin reporting.
'use strict';

const express = require('express');
const reportController = require('../controllers/reportController');

const router = express.Router();

router.get('/api/admin/financial-report', reportController.financialReport);

module.exports = router;

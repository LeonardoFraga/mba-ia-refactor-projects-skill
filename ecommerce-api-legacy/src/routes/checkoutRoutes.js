// Thin route layer for checkout.
'use strict';

const express = require('express');
const checkoutController = require('../controllers/checkoutController');
const validateCheckout = require('../middlewares/validateCheckout');

const router = express.Router();

router.post('/api/checkout', validateCheckout, checkoutController.checkout);

module.exports = router;

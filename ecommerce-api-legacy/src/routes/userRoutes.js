// Thin route layer for users.
'use strict';

const express = require('express');
const userController = require('../controllers/userController');
const validateUserId = require('../middlewares/validateUserId');

const router = express.Router();

router.delete('/api/users/:id', validateUserId, userController.deleteUser);

module.exports = router;

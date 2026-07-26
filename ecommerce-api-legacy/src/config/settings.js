// Central configuration — every value comes from the environment.
// NO secret is hardcoded here. Provide real values via env vars / .env.
'use strict';

module.exports = {
    port: parseInt(process.env.PORT, 10) || 3000,

    // Payment gateway
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',

    // Database credentials (kept for parity with the original config; the
    // in-memory SQLite instance does not require them, but real deployments do).
    db: {
        user: process.env.DB_USER || '',
        pass: process.env.DB_PASS || '',
        // ':memory:' preserves the original behavior (reseeded on boot).
        path: process.env.DB_PATH || ':memory:'
    },

    // Mail
    smtpUser: process.env.SMTP_USER || ''
};

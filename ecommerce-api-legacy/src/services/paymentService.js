// Payment processing. Isolates gateway logic from the controller/route.
// NEVER logs the card number or the gateway key (fixes the data-exposure finding).
'use strict';

const settings = require('../config/settings');

// Mask a PAN so only the last 4 digits are ever visible in any diagnostics.
function maskCard(card) {
    const digits = String(card).replace(/\D/g, '');
    return `**** **** **** ${digits.slice(-4)}`;
}

// Charge a card. Preserves the original business rule: cards starting with "4"
// are approved (PAID), everything else is denied (DENIED).
function charge(card, amount) {
    // The gateway key is read from config (env) and is intentionally NOT logged.
    void settings.paymentGatewayKey;
    void amount;

    const status = String(card).startsWith('4') ? 'PAID' : 'DENIED';
    return { status, maskedCard: maskCard(card) };
}

module.exports = { charge, maskCard };

// Real password hashing using Node's built-in crypto.scrypt (salted).
// Replaces the insecure homemade badCrypto().
'use strict';

const crypto = require('crypto');

const KEYLEN = 64;

// Returns a salted scrypt hash in the form: salt:derivedKey (both hex).
function hash(password) {
    const salt = crypto.randomBytes(16).toString('hex');
    const derived = crypto.scryptSync(String(password), salt, KEYLEN).toString('hex');
    return `${salt}:${derived}`;
}

// Constant-time verification of a plaintext password against a stored hash.
function verify(password, stored) {
    if (typeof stored !== 'string' || !stored.includes(':')) return false;
    const [salt, key] = stored.split(':');
    const derived = crypto.scryptSync(String(password), salt, KEYLEN);
    const keyBuffer = Buffer.from(key, 'hex');
    if (keyBuffer.length !== derived.length) return false;
    return crypto.timingSafeEqual(keyBuffer, derived);
}

module.exports = { hash, verify };

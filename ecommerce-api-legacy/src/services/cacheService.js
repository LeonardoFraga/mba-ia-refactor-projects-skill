// Encapsulated cache — replaces the shared mutable module globals
// (globalCache / totalRevenue) that were exported from utils.js.
'use strict';

class CacheService {
    #store = {};

    set(key, value) {
        this.#store[key] = value;
    }

    get(key) {
        return this.#store[key];
    }

    has(key) {
        return Object.prototype.hasOwnProperty.call(this.#store, key);
    }
}

// A single encapsulated instance; state is private and only reachable via methods.
module.exports = new CacheService();

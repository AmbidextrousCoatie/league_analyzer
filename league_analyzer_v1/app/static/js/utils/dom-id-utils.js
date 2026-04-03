/**
 * DOM / CSS selector–safe HTML id tokens.
 * User-facing labels (league short names, team names, etc.) must never be used raw in
 * id="...", for="...", or querySelector('#...') — parentheses, dots, and spaces break selectors.
 *
 * Load this script before any code that builds dynamic element IDs.
 */
(function (global) {
    'use strict';

    /**
     * @param {*} value - Arbitrary label or id fragment
     * @returns {string} Token safe for HTML id and CSS ID selectors ([A-Za-z0-9_-], starts with letter or _)
     */
    function toSafeDomIdToken(value) {
        if (value === null || value === undefined) {
            return 'unknown';
        }
        let token = String(value).trim().replace(/[^A-Za-z0-9_-]+/g, '_');
        token = token.replace(/_+/g, '_').replace(/^_|_$/g, '');
        if (!token) {
            token = 'unknown';
        }
        if (!/^[A-Za-z_]/.test(token)) {
            token = 'id_' + token;
        }
        return token;
    }

    /**
     * @param {...*} parts - Fragments joined with single underscores (each part sanitized)
     * @returns {string}
     */
    function composeDomId() {
        const parts = Array.prototype.slice.call(arguments);
        return parts
            .filter(function (p) {
                return p !== null && p !== undefined && String(p).trim() !== '';
            })
            .map(function (p) {
                return toSafeDomIdToken(p);
            })
            .join('_');
    }

    var api = {
        toSafeDomIdToken: toSafeDomIdToken,
        composeDomId: composeDomId
    };

    global.DomIdUtils = api;
})(typeof window !== 'undefined' ? window : typeof globalThis !== 'undefined' ? globalThis : this);

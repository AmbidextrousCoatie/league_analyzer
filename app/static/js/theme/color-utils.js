(() => {
    const globalObj = window || {};

    const TEAM_COLOR_PALETTES = {
        harmonic10: [
            "#1F77B4", "#FF7F0E", "#2CA02C", "#D62728", "#9467BD",
            "#8C564B", "#E377C2", "#7F7F7F", "#BCBD22", "#17BECF"
        ],
        rainbowPastel: [
            "#1B8CA6", "#2CA89A", "#8CBF8A", "#E6C86E", "#F7A86E",
            "#E86E56", "#D95A6A", "#C94C8A", "#A04CBF", "#D6A4E6"
        ]
    };

    const SEMANTIC_COLOR_MAPPINGS = {
        harmonic10: { positive: 2, negative: 3, highlight: 9 },
        rainbowPastel: { positive: 2, negative: 5, highlight: 9 }
    };

    // Theme colors - used throughout the application
    const THEME_COLORS = {
        // Primary colors
        //primary: "#0a9dc7",           // Dark blue - navbar, card headers
        primary: "#1B8CA6",           // Dark blue - navbar, card headers
        secondary: "#4aa8c2",         // Light blue - buttons, interactive elements
        accent: "#7dcfe6",             // Lightest blue - highlights, accents
        
        // Background colors
        background: "#f8f9fa",        // Main page background
        surface: "#ffffff",           // Card/container background
        surfaceAlt: "#e9ecef",        // Alternate surface (lighter gray)
        surfaceLight: "#f0f0f0",      // Light gray variant
        
        // Text colors
        textOnPrimary: "#ffffff",     // Text on primary background
        textOnSecondary: "#ffffff",   // Text on secondary background
        textOnLight: "#1F77B4",       // Text on light background
        
        // Border colors
        border: "#264653",             // Dark teal/green borders
        borderLight: "#dee2e6",        // Light borders
        borderSoft: "rgba(15, 23, 42, 0.08)", // Soft border (light mode)
        
        // Table colors
        tableHeaderBg: "#eef2f7",     // Table header background
        tableHeaderText: "#0f172a",   // Table header text
        tableBodyText: "#1f2933",     // Table body text
        tableMutedText: "#64748b",    // Muted text
        
        // Heat map colors
        heatMapStart: "#dddddd",      // Heat map start color
        heatMapEnd: "#1b8da7",        // Heat map end color
        heatMapLow: "#d9596a",        // Heat map low value
        heatMapHigh: "#1b8da7",       // Heat map high value
        
        // Status colors
        warning: "#86e1b3",            // Warning states
        info: "#a1e8c4",              // Info states
        success: "#d4edda",           // Success states
        danger: "#f8d7da",            // Danger states
    };

    // Dark mode theme colors
    const THEME_COLORS_DARK = {
        // Primary colors (same as light mode)
        primary: "#1B8CA6",
        secondary: "#4aa8c2",
        accent: "#7dcfe6",
        
        // Background colors (dark)
        background: "#0f172a",        // Dark slate background
        surface: "#1e293b",           // Dark surface
        surfaceAlt: "#334155",        // Alternate dark surface
        surfaceLight: "#475569",      // Light dark variant
        
        // Text colors (light for dark backgrounds)
        textOnPrimary: "#ffffff",
        textOnSecondary: "#ffffff",
        textOnLight: "#e2e8f0",       // Light text on dark background
        
        // Border colors (light for dark mode)
        border: "#475569",            // Lighter border for dark mode
        borderLight: "#64748b",       // Light border
        borderSoft: "rgba(226, 232, 240, 0.12)", // Soft border (dark mode)
        
        // Table colors (dark)
        tableHeaderBg: "#182645",     // Dark table header background
        tableHeaderText: "#e2e8f0",   // Light table header text
        tableBodyText: "#f1f5f9",     // Light table body text
        tableMutedText: "#94a3b8",    // Muted text (dark mode)
        
        // Heat map colors (same as light mode)
        heatMapStart: "#dddddd",
        heatMapEnd: "#1b8da7",
        heatMapLow: "#d9596a",
        heatMapHigh: "#1b8da7",
        
        // Status colors (adjusted for dark mode)
        warning: "#86e1b3",
        info: "#a1e8c4",
        success: "#d4edda",
        danger: "#f8d7da",
    };

    // First color = base table background, second = accent stripe
    // This makes one of the stripe colors effectively the "default" color.
    //const DEFAULT_STRIPE_PALETTE = ["#ffffff", "#e9f0ff"];
    const DEFAULT_STRIPE_PALETTE = ["#ffffff", THEME_COLORS.primary];

    let currentPaletteName = "rainbowPastel";
    let currentPalette = TEAM_COLOR_PALETTES[currentPaletteName];
    const teamColorMap = globalObj.teamColorMap || {};

    function hexToRgb(hex) {
        if (!hex) return [255, 255, 255];
        let clean = hex.replace("#", "");
        if (clean.length === 3) {
            clean = clean.split("").map(c => c + c).join("");
        }
        const bigint = parseInt(clean, 16);
        return [(bigint >> 16) & 255, (bigint >> 8) & 255, bigint & 255];
    }

    function toRgba(color, alpha = 1) {
        if (!color) return `rgba(255,255,255,${alpha})`;
        if (color.startsWith("rgb")) {
            return color.replace(")", `, ${alpha})`).replace("rgb", "rgba");
        }
        const [r, g, b] = hexToRgb(color);
        return `rgba(${r}, ${g}, ${b}, ${alpha})`;
    }

    function getGradientColors(count, start = "#ffffff", end = "#2196F3") {
        if (!count || count <= 1) {
            return [start];
        }
        const startRgb = hexToRgb(start);
        const endRgb = hexToRgb(end);

        return Array.from({ length: count }, (_, index) => {
            if (index === 0) return start;
            if (index === count - 1) return end;
            const factor = index / (count - 1);
            const r = Math.round(startRgb[0] + (endRgb[0] - startRgb[0]) * factor);
            const g = Math.round(startRgb[1] + (endRgb[1] - startRgb[1]) * factor);
            const b = Math.round(startRgb[2] + (endRgb[2] - startRgb[2]) * factor);
            return `rgb(${r}, ${g}, ${b})`;
        });
    }

    function getStripeColors(groupIndex, options = {}) {
        if (options.enabled === false) {
            return null;
        }
        const palette = options.palette || DEFAULT_STRIPE_PALETTE;
        const color = palette[groupIndex % palette.length];
        const headerAlpha = typeof options.headerAlpha === "number" ? options.headerAlpha : 0.55;
        const cellAlpha = typeof options.cellAlpha === "number" ? options.cellAlpha : 0.25;
        return {
            headerBg: toRgba(color, headerAlpha),
            cellBg: toRgba(color, cellAlpha)
        };
    }

    /**
     * Assigns CSS classes to column groups for striped coloring.
     * Call this before creating the Tabulator instance.
     * @param {Array} groups - Array of column group definitions
     */
    function assignGroupStripeCss(groups) {
        groups.forEach((group, index) => {
            // Add class to the group itself (for group header)
            group.cssClass = ((group.cssClass || "") + " col-group-" + index).trim();
            // Add class to all leaf columns
            if (group.columns) {
                assignLeafColumnCss(group.columns, index);
            }
        });
    }

    function assignLeafColumnCss(columns, groupIndex) {
        columns.forEach(col => {
            if (col.columns) {
                // Nested group - recurse
                assignLeafColumnCss(col.columns, groupIndex);
            } else {
                // Leaf column - cssClass for cells, headerClass for column headers
                col.cssClass = ((col.cssClass || "") + " col-group-" + groupIndex).trim();
                col.headerClass = ((col.headerClass || "") + " col-group-" + groupIndex).trim();
            }
        });
    }

    /**
     * Generates CSS rules for striped column groups.
     * @param {number} groupCount - Number of groups to generate rules for
     * @param {Object} options - Options for colors
     * @returns {string} CSS rules as a string
     */
    function generateStripeCss(groupCount, options = {}) {
        const palette = options.palette || DEFAULT_STRIPE_PALETTE;
        const headerAlpha = typeof options.headerAlpha === "number" ? options.headerAlpha : 0.55;
        const cellAlpha = typeof options.cellAlpha === "number" ? options.cellAlpha : 0.25;
        
        let css = "";
        for (let i = 0; i < groupCount; i++) {
            const color = palette[i % palette.length];
            const headerBg = toRgba(color, headerAlpha);
            const cellBg = toRgba(color, cellAlpha);
            // Body cells (but NOT frozen ones – they use solid row backgrounds to avoid see‑through)
            css += `.tabulator-cell.col-group-${i}:not(.tabulator-frozen) { background-color: ${cellBg} !important; }\n`;
            // Full header cells for this group (no small boxes just behind text), but not frozen headers
            css += `.tabulator-col.col-group-${i}:not(.tabulator-frozen) { background-color: ${headerBg} !important; }\n`;
            css += `.tabulator-col-group.col-group-${i}:not(.tabulator-frozen) { background-color: ${headerBg} !important; }\n`;
        }
        return css;
    }

    /**
     * Injects stripe CSS into the document if not already present.
     * @param {number} groupCount - Number of groups
     * @param {Object} options - Color options
     */
    function injectStripeCss(groupCount, options = {}) {
        const styleId = "tabulator-stripe-styles";
        let styleEl = document.getElementById(styleId);
        if (!styleEl) {
            styleEl = document.createElement("style");
            styleEl.id = styleId;
            document.head.appendChild(styleEl);
        }
        styleEl.textContent = generateStripeCss(groupCount, options);
    }

    function interpolateValue(value, minVal, maxVal) {
        if (maxVal === minVal) return 0;
        return (value - minVal) / (maxVal - minVal);
    }

    function getThemeColor(colorName) {
        return THEME_COLORS[colorName] || null;
    }

    function getHeatMapColor(value, minVal, maxVal, options = {}) {
        const startColor = options.startColor || THEME_COLORS.heatMapStart;
        const endColor = options.endColor || THEME_COLORS.heatMapEnd;

        const ratio = Math.min(Math.max(interpolateValue(value, minVal, maxVal), 0), 1);
        const [r1, g1, b1] = hexToRgb(startColor);
        const [r2, g2, b2] = hexToRgb(endColor);

        const r = Math.round(r1 + (r2 - r1) * ratio);
        const g = Math.round(g1 + (g2 - g1) * ratio);
        const b = Math.round(b1 + (b2 - b1) * ratio);
        return `rgb(${r}, ${g}, ${b})`;
    }

    function getPaletteColor(index) {
        if (!currentPalette.length) return "#888";
        return currentPalette[Math.abs(index) % currentPalette.length];
    }

    function updateTeamColorMap(currentTeams = []) {
        if (!Array.isArray(currentTeams)) return;

        Object.keys(teamColorMap).forEach(team => {
            if (!currentTeams.includes(team)) {
                delete teamColorMap[team];
            }
        });

        let paletteIdx = 0;
        currentTeams.forEach(team => {
            if (!teamColorMap[team]) {
                teamColorMap[team] = getPaletteColor(paletteIdx++);
            }
        });
    }

    function getTeamColor(teamName, fallbackIndex = 0) {
        if (teamName && teamColorMap[teamName]) {
            return teamColorMap[teamName];
        }
        // Also check playerColorMap as fallback (for player names in charts)
        if (teamName && playerColorMap[teamName]) {
            return playerColorMap[teamName];
        }
        return getPaletteColor(fallbackIndex);
    }

    // Player name color map (similar to team color map but for player names)
    const playerColorMap = globalObj.playerColorMap || {};

    function updatePlayerColorMap(currentPlayers = []) {
        if (!Array.isArray(currentPlayers)) return;

        Object.keys(playerColorMap).forEach(player => {
            if (!currentPlayers.includes(player)) {
                delete playerColorMap[player];
            }
        });

        let paletteIdx = 0;
        currentPlayers.forEach(player => {
            if (!playerColorMap[player]) {
                playerColorMap[player] = getPaletteColor(paletteIdx++);
            }
        });
    }

    function getPlayerColor(playerName, fallbackIndex = 0) {
        if (playerName && playerColorMap[playerName]) {
            return playerColorMap[playerName];
        }
        // If not in map, assign a color based on hash of name for consistency
        if (playerName) {
            let hash = 0;
            for (let i = 0; i < playerName.length; i++) {
                hash = playerName.charCodeAt(i) + ((hash << 5) - hash);
            }
            const index = Math.abs(hash) % currentPalette.length;
            return getPaletteColor(index);
        }
        return getPaletteColor(fallbackIndex);
    }

    function setPalette(name) {
        if (TEAM_COLOR_PALETTES[name]) {
            currentPaletteName = name;
            currentPalette = TEAM_COLOR_PALETTES[name];
            return true;
        }
        return false;
    }

    function getSemanticColor(semanticName) {
        const mapping = SEMANTIC_COLOR_MAPPINGS[currentPaletteName];
        if (mapping && mapping[semanticName] !== undefined) {
            return getPaletteColor(mapping[semanticName]);
        }
        const fallbacks = {
            positive: "#2CA02C",
            negative: "#D62728",
            highlight: "#ffd700"
        };
        return fallbacks[semanticName] || "#888";
    }

    // Dark mode management
    function isDarkMode() {
        if (typeof localStorage !== 'undefined') {
            const stored = localStorage.getItem('darkMode');
            if (stored !== null) {
                return stored === 'true';
            }
        }
        // Check if system prefers dark mode
        if (typeof window !== 'undefined' && window.matchMedia) {
            return window.matchMedia('(prefers-color-scheme: dark)').matches;
        }
        return false;
    }

    function setDarkMode(enabled) {
        if (typeof localStorage !== 'undefined') {
            localStorage.setItem('darkMode', enabled ? 'true' : 'false');
        }
        applyDarkMode(enabled);
    }

    function toggleDarkMode() {
        const current = isDarkMode();
        setDarkMode(!current);
        return !current;
    }

    function applyDarkMode(enabled) {
        const root = document.documentElement;
        const body = document.body;
        const theme = enabled ? THEME_COLORS_DARK : THEME_COLORS;
        
        // Set data-theme attribute
        if (enabled) {
            root.setAttribute('data-theme', 'dark');
            body.classList.add('dark-mode');
        } else {
            root.setAttribute('data-theme', 'light');
            body.classList.remove('dark-mode');
        }
        
        // Apply theme colors as CSS variables
        Object.keys(theme).forEach(key => {
            const cssKey = '--theme-' + key.replace(/([A-Z])/g, '-$1').toLowerCase();
            root.style.setProperty(cssKey, theme[key]);
        });
        
        // Apply table-specific dark mode variables
        if (enabled) {
            root.style.setProperty('--table-surface', theme.surface);
            root.style.setProperty('--table-surface-alt', theme.surfaceAlt);
            root.style.setProperty('--table-border-soft', theme.borderSoft);
            root.style.setProperty('--table-header-bg', theme.tableHeaderBg);
            root.style.setProperty('--table-header-text', theme.tableHeaderText);
            root.style.setProperty('--table-body-text', theme.tableBodyText);
            root.style.setProperty('--table-muted-text', theme.tableMutedText);
            root.style.setProperty('--table-hover-bg', 'rgba(56, 189, 248, 0.14)');
            root.style.setProperty('--table-selected-bg', 'rgba(99, 102, 241, 0.28)');
            root.style.setProperty('--table-highlight-bg', 'rgba(14, 165, 233, 0.2)');
            root.style.setProperty('--table-shadow', '0 12px 30px rgba(2, 6, 23, 0.65)');
        } else {
            root.style.setProperty('--table-surface', THEME_COLORS.surface);
            root.style.setProperty('--table-surface-alt', '#f6f8fb');
            root.style.setProperty('--table-border-soft', THEME_COLORS.borderSoft);
            root.style.setProperty('--table-header-bg', THEME_COLORS.tableHeaderBg);
            root.style.setProperty('--table-header-text', THEME_COLORS.tableHeaderText);
            root.style.setProperty('--table-body-text', THEME_COLORS.tableBodyText);
            root.style.setProperty('--table-muted-text', THEME_COLORS.tableMutedText);
            root.style.setProperty('--table-hover-bg', 'rgba(59, 130, 246, 0.08)');
            root.style.setProperty('--table-selected-bg', 'rgba(99, 102, 241, 0.18)');
            root.style.setProperty('--table-highlight-bg', 'rgba(15, 118, 110, 0.12)');
            root.style.setProperty('--table-shadow', '0 12px 25px rgba(15, 23, 42, 0.08)');
        }
        
        // Dispatch event for other components
        if (typeof window !== 'undefined') {
            window.dispatchEvent(new CustomEvent('themeChanged', { 
                detail: { darkMode: enabled } 
            }));
        }
    }

    // Initialize dark mode on load
    if (typeof document !== 'undefined') {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                applyDarkMode(isDarkMode());
            });
        } else {
            applyDarkMode(isDarkMode());
        }
    }

    const ColorUtils = {
        TEAM_COLOR_PALETTES,
        SEMANTIC_COLOR_MAPPINGS,
        THEME_COLORS,
        THEME_COLORS_DARK,
        DEFAULT_STRIPE_PALETTE,
        getCurrentPaletteName: () => currentPaletteName,
        getCurrentPalette: () => [...currentPalette],
        setPalette,
        getPaletteColor,
        getSemanticColor,
        getThemeColor,
        updateTeamColorMap,
        getTeamColor,
        updatePlayerColorMap,
        getPlayerColor,
        getGradientColors,
        getStripeColors,
        getHeatMapColor,
        hexToRgb,
        toRgba,
        teamColorMap,
        playerColorMap,
        assignGroupStripeCss,
        generateStripeCss,
        injectStripeCss,
        isDarkMode,
        setDarkMode,
        toggleDarkMode,
        applyDarkMode
    };

    globalObj.ColorUtils = ColorUtils;
    globalObj.teamColorMap = teamColorMap;
    globalObj.playerColorMap = playerColorMap;
    globalObj.getTeamColor = getTeamColor;
    globalObj.getPlayerColor = getPlayerColor;
    globalObj.updateTeamColorMap = updateTeamColorMap;
    globalObj.updatePlayerColorMap = updatePlayerColorMap;
})();


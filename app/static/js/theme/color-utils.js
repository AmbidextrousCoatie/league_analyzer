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

    const DEFAULT_STRIPE_PALETTE = ["#e9f0ff", "#e9f0ff"];
    //const DEFAULT_STRIPE_PALETTE = ["#e9f0ff", "#c2effc"];

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
            // Use same color for cells as headers
            const cellBg = toRgba(color, headerAlpha);
            // Cells (via formatter adding class)
            css += `.tabulator-cell.col-group-${i} { background-color: ${cellBg} !important; }\n`;
            // Column headers (via headerClass) - target the title element
            css += `.tabulator-col.col-group-${i} .tabulator-col-title { background-color: ${headerBg} !important; }\n`;
            // Group headers - target the group title element
            css += `.tabulator-col-group.col-group-${i} .tabulator-col-group-title { background-color: ${headerBg} !important; }\n`;
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

    function getHeatMapColor(value, minVal, maxVal, options = {}) {
        const startColor = options.startColor || "#dddddd";
        const endColor = options.endColor || "#1b8da7";

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

    const ColorUtils = {
        TEAM_COLOR_PALETTES,
        SEMANTIC_COLOR_MAPPINGS,
        getCurrentPaletteName: () => currentPaletteName,
        getCurrentPalette: () => [...currentPalette],
        setPalette,
        getPaletteColor,
        getSemanticColor,
        updateTeamColorMap,
        getTeamColor,
        getGradientColors,
        getStripeColors,
        getHeatMapColor,
        hexToRgb,
        toRgba,
        teamColorMap,
        assignGroupStripeCss,
        generateStripeCss,
        injectStripeCss
    };

    globalObj.ColorUtils = ColorUtils;
    globalObj.teamColorMap = teamColorMap;
    globalObj.getTeamColor = getTeamColor;
    globalObj.updateTeamColorMap = updateTeamColorMap;
})();


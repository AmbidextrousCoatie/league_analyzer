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

    const DEFAULT_STRIPE_PALETTE = ["#e9f0ff", "#f6f1ff"];

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
        teamColorMap
    };

    globalObj.ColorUtils = ColorUtils;
    globalObj.teamColorMap = teamColorMap;
    globalObj.getTeamColor = getTeamColor;
    globalObj.updateTeamColorMap = updateTeamColorMap;
})();


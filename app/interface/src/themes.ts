// Theme System - Step 1.1: Basic Interface Only
export interface Theme {
    name: string;
    colors: {
        background: {
            primary: string;
            secondary: string;
            tertiary: string;
        };
        text: {
            primary: string;
            secondary: string;
            accent: string;
        };
        border: {
            primary: string;
            secondary: string;
        };
        accent: {
            primary: string;
            secondary: string;
        };
        status: {
            success: string;
            warning: string;
            error: string;
            info: string;
        };
    };
}

// Step 1.2: Add 3 Basic Themes + Phase 4: Expand to 10 Themes
export const THEMES: Record<string, Theme> = {
    navy: {
        name: 'Navy (V2.0 Original)',
        colors: {
            background: { primary: '#0a0a0a', secondary: '#0d1b2a', tertiary: '#1b263b' },
            text: { primary: '#ffffff', secondary: '#a0a0a0', accent: '#00d9ff' },
            border: { primary: '#1b263b', secondary: '#2a3547' },
            accent: { primary: '#00d9ff', secondary: '#a855f7' },
            status: { success: '#22c55e', warning: '#facc15', error: '#ef4444', info: '#3b82f6' },
        },
    },
    matrix: {
        name: 'Matrix',
        colors: {
            background: { primary: '#000000', secondary: '#001a00', tertiary: '#003300' },
            text: { primary: '#00ff00', secondary: '#00aa00', accent: '#00ff00' },
            border: { primary: '#003300', secondary: '#005500' },
            accent: { primary: '#00ff00', secondary: '#00cc00' },
            status: { success: '#00ff00', warning: '#ffff00', error: '#ff3300', info: '#00ccff' },
        },
    },
    sunset: {
        name: 'Sunset',
        colors: {
            background: { primary: '#1a0500', secondary: '#331100', tertiary: '#4d1f00' },
            text: { primary: '#ffffff', secondary: '#ffcc99', accent: '#ff6600' },
            border: { primary: '#662200', secondary: '#993300' },
            accent: { primary: '#ff6600', secondary: '#ff9933' },
            status: { success: '#66bb6a', warning: '#ffca28', error: '#f44336', info: '#ab47bc' },
        },
    },
    cyberpunk: {
        name: 'Cyberpunk',
        colors: {
            background: { primary: '#0a0014', secondary: '#1a0033', tertiary: '#2d0052' },
            text: { primary: '#ffffff', secondary: '#b8a0d6', accent: '#ff00ff' },
            border: { primary: '#4a0080', secondary: '#6b00b3' },
            accent: { primary: '#ff00ff', secondary: '#00ffff' },
            status: { success: '#00ff88', warning: '#ffaa00', error: '#ff0066', info: '#00ccff' },
        },
    },
    ocean: {
        name: 'Ocean',
        colors: {
            background: { primary: '#001a33', secondary: '#003366', tertiary: '#004d99' },
            text: { primary: '#ffffff', secondary: '#a0c4e0', accent: '#00e5ff' },
            border: { primary: '#0066cc', secondary: '#0088ff' },
            accent: { primary: '#00e5ff', secondary: '#00bcd4' },
            status: { success: '#26c6da', warning: '#ffa726', error: '#ef5350', info: '#42a5f5' },
        },
    },
    forest: {
        name: 'Forest',
        colors: {
            background: { primary: '#0d1f0d', secondary: '#1a331a', tertiary: '#2d4d2d' },
            text: { primary: '#e8f5e8', secondary: '#a8c9a8', accent: '#66ff66' },
            border: { primary: '#335533', secondary: '#447744' },
            accent: { primary: '#66ff66', secondary: '#88dd88' },
            status: { success: '#4caf50', warning: '#ffb300', error: '#e53935', info: '#29b6f6' },
        },
    },
    midnight: {
        name: 'Midnight',
        colors: {
            background: { primary: '#0a0a1f', secondary: '#141433', tertiary: '#1f1f4d' },
            text: { primary: '#e8e8ff', secondary: '#a8a8cc', accent: '#6666ff' },
            border: { primary: '#2a2a66', secondary: '#3d3d99' },
            accent: { primary: '#6666ff', secondary: '#8888ff' },
            status: { success: '#7c4dff', warning: '#ffd54f', error: '#ff5252', info: '#448aff' },
        },
    },
    rosegold: {
        name: 'Rose Gold',
        colors: {
            background: { primary: '#1f0a14', secondary: '#331a28', tertiary: '#4d2d3d' },
            text: { primary: '#ffe8f0', secondary: '#d4a8b8', accent: '#ffb3d9' },
            border: { primary: '#664455', secondary: '#885577' },
            accent: { primary: '#ffb3d9', secondary: '#d4af37' },
            status: { success: '#81c784', warning: '#ffb74d', error: '#e57373', info: '#64b5f6' },
        },
    },
    arctic: {
        name: 'Arctic',
        colors: {
            background: { primary: '#0a1419', secondary: '#142833', tertiary: '#1f3d4d' },
            text: { primary: '#e8f4f8', secondary: '#b8d4e0', accent: '#66d9ff' },
            border: { primary: '#2a5566', secondary: '#3d7788' },
            accent: { primary: '#66d9ff', secondary: '#b3ecff' },
            status: { success: '#4dd0e1', warning: '#ffca28', error: '#ef5350', info: '#42a5f5' },
        },
    },
    ember: {
        name: 'Ember',
        colors: {
            background: { primary: '#1a0a00', secondary: '#331400', tertiary: '#4d2200' },
            text: { primary: '#ffe8d9', secondary: '#d4b8a0', accent: '#ff6633' },
            border: { primary: '#663311', secondary: '#994d22' },
            accent: { primary: '#ff6633', secondary: '#ff9966' },
            status: { success: '#66bb6a', warning: '#ffb74d', error: '#f4511e', info: '#ff7043' },
        },
    },
    custom: {
        name: 'Custom (Eigene Farben)',
        colors: {
            background: { primary: '#0a0a0a', secondary: '#0d1b2a', tertiary: '#1b263b' },
            text: { primary: '#ffffff', secondary: '#a0a0a0', accent: '#00d9ff' },
            border: { primary: '#1b263b', secondary: '#2a3547' },
            accent: { primary: '#00d9ff', secondary: '#a855f7' },
            status: { success: '#22c55e', warning: '#facc15', error: '#ef4444', info: '#3b82f6' },
        },
    },
};

export const DEFAULT_THEME = 'navy';

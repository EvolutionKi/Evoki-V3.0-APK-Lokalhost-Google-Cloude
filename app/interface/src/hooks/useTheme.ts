// Step 1.3 + Phase 3.1 + 3.3 + Custom Theme + Display Modes: Full Theme Hook
import { useState, useEffect } from 'react';
import { THEMES, DEFAULT_THEME, type Theme } from '../themes';
import { DISPLAY_MODES, DEFAULT_DISPLAY_MODE } from '../displayModes';

const THEME_STORAGE_KEY = 'evoki_theme';
const CUSTOM_THEME_STORAGE_KEY = 'evoki_custom_theme';
const DISPLAY_MODE_STORAGE_KEY = 'evoki_display_mode';

export function useTheme() {
    // Load custom theme if exists
    const loadCustomTheme = () => {
        const saved = localStorage.getItem(CUSTOM_THEME_STORAGE_KEY);
        if (saved) {
            try {
                THEMES.custom = JSON.parse(saved);
            } catch (e) {
                console.error('Failed to load custom theme:', e);
            }
        }
    };

    // Initialize: load custom theme first, then load active theme
    const [currentTheme, setCurrentTheme] = useState<string>(() => {
        loadCustomTheme();
        const saved = localStorage.getItem(THEME_STORAGE_KEY);
        return saved || DEFAULT_THEME;
    });

    // Phase 2.1: Display Mode State with localStorage
    const [displayMode, setDisplayMode] = useState<string>(() => {
        const saved = localStorage.getItem(DISPLAY_MODE_STORAGE_KEY);
        return saved || DEFAULT_DISPLAY_MODE;
    });

    const theme = THEMES[currentTheme] || THEMES[DEFAULT_THEME];
    const display = DISPLAY_MODES[displayMode] || DISPLAY_MODES[DEFAULT_DISPLAY_MODE];

    // Apply CSS variables + save to localStorage
    useEffect(() => {
        const root = document.documentElement;

        // Background colors
        root.style.setProperty('--bg-primary', theme.colors.background.primary);
        root.style.setProperty('--bg-secondary', theme.colors.background.secondary);
        root.style.setProperty('--bg-tertiary', theme.colors.background.tertiary);

        // Text colors
        root.style.setProperty('--text-primary', theme.colors.text.primary);
        root.style.setProperty('--text-secondary', theme.colors.text.secondary);
        root.style.setProperty('--text-accent', theme.colors.text.accent);

        // Border colors
        root.style.setProperty('--border-primary', theme.colors.border.primary);
        root.style.setProperty('--border-secondary', theme.colors.border.secondary);

        // Accent colors
        root.style.setProperty('--accent-primary', theme.colors.accent.primary);
        root.style.setProperty('--accent-secondary', theme.colors.accent.secondary);

        // Status colors
        root.style.setProperty('--status-success', theme.colors.status.success);
        root.style.setProperty('--status-warning', theme.colors.status.warning);
        root.style.setProperty('--status-error', theme.colors.status.error);
        root.style.setProperty('--status-info', theme.colors.status.info);

        // Phase 2.2: Display Mode CSS Variables
        root.style.setProperty('--font-size-base', display.fontSize.base);
        root.style.setProperty('--font-size-heading', display.fontSize.heading);
        root.style.setProperty('--font-size-small', display.fontSize.small);

        root.style.setProperty('--spacing-sm', display.spacing.sm);
        root.style.setProperty('--spacing-md', display.spacing.md);
        root.style.setProperty('--spacing-lg', display.spacing.lg);

        root.style.setProperty('--container-max-width', display.container.maxWidth);

        root.style.setProperty('--icon-size-sm', display.iconSize.sm);
        root.style.setProperty('--icon-size-md', display.iconSize.md);
        root.style.setProperty('--icon-size-lg', display.iconSize.lg);

        // Save theme selection to localStorage
        localStorage.setItem(THEME_STORAGE_KEY, currentTheme);
        // Save display mode to localStorage
        localStorage.setItem(DISPLAY_MODE_STORAGE_KEY, displayMode);

        console.log('✅ CSS Variables applied - Theme:', currentTheme, 'Display:', displayMode);
    }, [currentTheme, theme, displayMode, display]);

    const switchTheme = (themeKey: string) => {
        if (THEMES[themeKey]) {
            setCurrentTheme(themeKey);
            console.log('Theme switched to:', themeKey);
        }
    };

    const updateCustomTheme = (customTheme: Theme) => {
        THEMES.custom = customTheme;
        localStorage.setItem(CUSTOM_THEME_STORAGE_KEY, JSON.stringify(customTheme));
        // Force re-render by switching to custom theme
        setCurrentTheme('custom');
    };

    const switchDisplayMode = (modeKey: string) => {
        if (DISPLAY_MODES[modeKey]) {
            setDisplayMode(modeKey);
            console.log('Display mode switched to:', modeKey);
        }
    };

    return {
        currentTheme,
        theme,
        switchTheme,
        availableThemes: Object.keys(THEMES),
        updateCustomTheme,
        customTheme: THEMES.custom,
        // Display Mode
        displayMode,
        switchDisplayMode,
        availableDisplayModes: Object.keys(DISPLAY_MODES),
    };
}

import { useState, useEffect } from 'react';
import { THEMES, DEFAULT_THEME, Theme } from '../themes';

const THEME_STORAGE_KEY = 'evoki_theme';

export function useTheme() {
    const [currentTheme, setCurrentTheme] = useState<string>(() => {
        // Load from localStorage on init
        const saved = localStorage.getItem(THEME_STORAGE_KEY);
        return saved || DEFAULT_THEME;
    });

    const theme: Theme = THEMES[currentTheme] || THEMES[DEFAULT_THEME];

    useEffect(() => {
        // Save to localStorage when theme changes
        localStorage.setItem(THEME_STORAGE_KEY, currentTheme);

        // Apply CSS variables to :root for global access
        const root = document.documentElement;

        root.style.setProperty('--bg-primary', theme.colors.background.primary);
        root.style.setProperty('--bg-secondary', theme.colors.background.secondary);
        root.style.setProperty('--bg-tertiary', theme.colors.background.tertiary);

        root.style.setProperty('--text-primary', theme.colors.text.primary);
        root.style.setProperty('--text-secondary', theme.colors.text.secondary);
        root.style.setProperty('--text-accent', theme.colors.text.accent);

        root.style.setProperty('--border-primary', theme.colors.border.primary);
        root.style.setProperty('--border-secondary', theme.colors.border.secondary);

        root.style.setProperty('--accent-primary', theme.colors.accent.primary);
        root.style.setProperty('--accent-secondary', theme.colors.accent.secondary);

        root.style.setProperty('--status-success', theme.colors.status.success);
        root.style.setProperty('--status-warning', theme.colors.status.warning);
        root.style.setProperty('--status-error', theme.colors.status.error);
        root.style.setProperty('--status-info', theme.colors.status.info);
    }, [currentTheme, theme]);

    const switchTheme = (themeKey: string) => {
        if (THEMES[themeKey]) {
            setCurrentTheme(themeKey);
        }
    };

    const updateCustomTheme = (newTheme: Theme) => {
        // Save custom theme to localStorage
        localStorage.setItem('evoki_custom_theme', JSON.stringify(newTheme));

        // Update THEMES object
        THEMES.custom = newTheme;

        // Switch to custom theme
        setCurrentTheme('custom');
    };

    const loadCustomTheme = (): Theme | null => {
        const saved = localStorage.getItem('evoki_custom_theme');
        if (saved) {
            try {
                return JSON.parse(saved);
            } catch {
                return null;
            }
        }
        return null;
    };

    return {
        currentTheme,
        theme,
        switchTheme,
        updateCustomTheme,
        loadCustomTheme,
        availableThemes: Object.keys(THEMES),
    };
}

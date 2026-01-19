import { useState, useEffect } from 'react';
import { THEMES } from '../themes';
import CustomThemeEditor from './CustomThemeEditor';

interface ThemeSwitcherProps {
    currentTheme: string;
    onThemeChange: (theme: string) => void;
    onCustomThemeUpdate?: (theme: any) => void;
}

export default function ThemeSwitcher({ currentTheme, onThemeChange, onCustomThemeUpdate }: ThemeSwitcherProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [isEditingCustom, setIsEditingCustom] = useState(false);

    // Load custom theme from localStorage on mount
    useEffect(() => {
        const saved = localStorage.getItem('evoki_custom_theme');
        if (saved && onCustomThemeUpdate) {
            try {
                const customTheme = JSON.parse(saved);
                THEMES.custom = customTheme;
            } catch (e) {
                console.error('Failed to load custom theme:', e);
            }
        }
    }, [onCustomThemeUpdate]);

    const handleCustomThemeClick = () => {
        setIsEditingCustom(true);
        setIsOpen(false);
    };

    const handleCustomThemeSave = (theme: any) => {
        if (onCustomThemeUpdate) {
            onCustomThemeUpdate(theme);
        }
    };

    return (
        <div className="relative">
            {/* Theme Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="p-3 rounded-lg bg-gradient-to-r from-cyan-400 to-purple-500 hover:opacity-90 transition-opacity"
                title="Change Theme"
            >
                <svg
                    className="w-5 h-5 text-black"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01"
                    />
                </svg>
            </button>

            {/* Theme Picker Modal */}
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <div
                        className="fixed inset-0 bg-black/50 z-40"
                        onClick={() => setIsOpen(false)}
                    />

                    {/* Modal */}
                    <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 w-[600px] max-h-[80vh] overflow-y-auto">
                        <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 shadow-2xl">
                            <div className="flex items-center justify-between mb-4">
                                <h2 className="text-2xl font-bold text-white">Choose Your Theme</h2>
                                <button
                                    onClick={() => setIsOpen(false)}
                                    className="text-gray-400 hover:text-white transition-colors"
                                >
                                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                {Object.entries(THEMES).map(([key, theme]) => (
                                    <button
                                        key={key}
                                        onClick={() => {
                                            onThemeChange(key);
                                            setIsOpen(false);
                                        }}
                                        className={`p-4 rounded-lg border-2 transition-all ${currentTheme === key
                                            ? 'border-cyan-400 bg-cyan-400/10'
                                            : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                                            }`}
                                    >
                                        {/* Theme Name */}
                                        <div className="text-sm font-bold text-white mb-3">{theme.name}</div>

                                        {/* Color Preview */}
                                        <div className="grid grid-cols-5 gap-1 mb-2">
                                            <div
                                                className="h-8 rounded"
                                                style={{ backgroundColor: theme.colors.background.primary }}
                                            />
                                            <div
                                                className="h-8 rounded"
                                                style={{ backgroundColor: theme.colors.background.secondary }}
                                            />
                                            <div
                                                className="h-8 rounded"
                                                style={{ backgroundColor: theme.colors.accent.primary }}
                                            />
                                            <div
                                                className="h-8 rounded"
                                                style={{ backgroundColor: theme.colors.accent.secondary }}
                                            />
                                            <div
                                                className="h-8 rounded"
                                                style={{ backgroundColor: theme.colors.text.accent }}
                                            />
                                        </div>

                                        {/* Status Colors */}
                                        <div className="grid grid-cols-4 gap-1">
                                            <div
                                                className="h-4 rounded-full"
                                                style={{ backgroundColor: theme.colors.status.success }}
                                                title="Success"
                                            />
                                            <div
                                                className="h-4 rounded-full"
                                                style={{ backgroundColor: theme.colors.status.warning }}
                                                title="Warning"
                                            />
                                            <div
                                                className="h-4 rounded-full"
                                                style={{ backgroundColor: theme.colors.status.error }}
                                                title="Error"
                                            />
                                            <div
                                                className="h-4 rounded-full"
                                                style={{ backgroundColor: theme.colors.status.info }}
                                                title="Info"
                                            />
                                        </div>

                                        {/* Selected Indicator */}
                                        {currentTheme === key && (
                                            <div className="mt-3 text-center">
                                                <span className="text-xs text-cyan-400 font-bold">✓ ACTIVE</span>
                                            </div>
                                        )}
                                    </button>
                                ))}
                            </div>

                            <div className="mt-6 text-center text-sm text-gray-500">
                                Theme preferences are saved automatically
                            </div>
                        </div>
                    </div>
                </>
            )}

            {/* Custom Theme Editor */}
            {isEditingCustom && (
                <CustomThemeEditor
                    customTheme={THEMES.custom}
                    onSave={handleCustomThemeSave}
                    onClose={() => setIsEditingCustom(false)}
                />
            )}
        </div>
    );
}

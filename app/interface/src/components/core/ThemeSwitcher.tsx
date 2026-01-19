// Theme Switcher with Custom Theme Editor Integration
import { useState } from 'react';
import type { Theme } from '../../themes';
import CustomThemeEditor from './CustomThemeEditor';

interface ThemeSwitcherProps {
    isOpen: boolean;
    onClose: () => void;
    currentTheme: string;
    availableThemes: string[];
    onThemeChange: (theme: string) => void;
    customTheme: Theme;
    onCustomThemeUpdate: (theme: Theme) => void;
}

export default function ThemeSwitcher({
    isOpen,
    onClose,
    currentTheme,
    availableThemes,
    onThemeChange,
    customTheme,
    onCustomThemeUpdate
}: ThemeSwitcherProps) {
    const [isEditorOpen, setIsEditorOpen] = useState(false);

    if (!isOpen) return null;

    return (
        <>
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-black/70 z-40"
                onClick={onClose}
            />

            {/* Modal */}
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                <div className="bg-gray-900 border border-gray-700 rounded-lg p-6 w-full max-w-md">
                    {/* Header */}
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-xl font-bold text-white">⚙️ Theme Settings</h2>
                        <button
                            onClick={onClose}
                            className="text-gray-400 hover:text-white text-2xl"
                        >
                            ✕
                        </button>
                    </div>

                    {/* Theme Buttons */}
                    <div className="space-y-2 mb-4">
                        {availableThemes.map((themeKey) => {
                            // Skip custom theme from list - it has its own editor button
                            if (themeKey === 'custom') return null;

                            return (
                                <button
                                    key={themeKey}
                                    onClick={() => {
                                        onThemeChange(themeKey);
                                        console.log('Switched to:', themeKey);
                                    }}
                                    className={`w-full px-4 py-2 rounded font-medium transition-colors ${currentTheme === themeKey
                                        ? 'bg-cyan-400 text-black'
                                        : 'bg-gray-800 text-white hover:bg-gray-700'
                                        }`}
                                >
                                    {themeKey.charAt(0).toUpperCase() + themeKey.slice(1)}
                                    {currentTheme === themeKey && ' ✓'}
                                </button>
                            );
                        })}
                    </div>

                    {/* Custom Theme Button */}
                    <div className="pt-4 border-t border-gray-700">
                        <button
                            onClick={() => setIsEditorOpen(true)}
                            className={`w-full px-4 py-3 rounded font-medium transition-all flex items-center justify-between ${currentTheme === 'custom'
                                ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                                : 'bg-gray-800 text-white hover:bg-gray-700'
                                }`}
                        >
                            <span>
                                🎨 Custom Theme (Eigene Farben)
                                {currentTheme === 'custom' && ' ✓'}
                            </span>
                            <span className="text-sm opacity-75">→</span>
                        </button>
                    </div>
                </div>
            </div>

            {/* Custom Theme Editor */}
            <CustomThemeEditor
                isOpen={isEditorOpen}
                onClose={() => setIsEditorOpen(false)}
                currentCustomTheme={customTheme}
                onSave={onCustomThemeUpdate}
            />
        </>
    );
}

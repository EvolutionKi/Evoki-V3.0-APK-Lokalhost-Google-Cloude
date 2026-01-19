import { useState } from 'react';
import { Theme } from '../themes';

interface CustomThemeEditorProps {
    customTheme: Theme;
    onSave: (theme: Theme) => void;
    onClose: () => void;
}

export default function CustomThemeEditor({ customTheme, onSave, onClose }: CustomThemeEditorProps) {
    const [theme, setTheme] = useState<Theme>(customTheme);

    const updateColor = (path: string, value: string) => {
        const newTheme = { ...theme };
        const keys = path.split('.');
        let current: any = newTheme.colors;

        for (let i = 0; i < keys.length - 1; i++) {
            current = current[keys[i]];
        }
        current[keys[keys.length - 1]] = value;

        setTheme(newTheme);
    };

    const handleSave = () => {
        onSave(theme);
        onClose();
    };

    return (
        <div className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4">
            <div className="bg-gray-900 border border-gray-700 rounded-lg w-full max-w-4xl max-h-[90vh] overflow-y-auto">
                <div className="p-6">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-2xl font-bold text-white">🎨 Custom Theme Builder</h2>
                        <button
                            onClick={onClose}
                            className="text-gray-400 hover:text-white transition-colors"
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    {/* Color Sections */}
                    <div className="space-y-6">
                        {/* Background Colors */}
                        <div className="bg-gray-800 rounded-lg p-4">
                            <h3 className="text-lg font-bold text-white mb-4">📱 Background Colors</h3>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <ColorPicker
                                    label="Primary Background"
                                    value={theme.colors.background.primary}
                                    onChange={(v) => updateColor('background.primary', v)}
                                />
                                <ColorPicker
                                    label="Secondary Background"
                                    value={theme.colors.background.secondary}
                                    onChange={(v) => updateColor('background.secondary', v)}
                                />
                                <ColorPicker
                                    label="Tertiary Background"
                                    value={theme.colors.background.tertiary}
                                    onChange={(v) => updateColor('background.tertiary', v)}
                                />
                            </div>
                        </div>

                        {/* Text Colors */}
                        <div className="bg-gray-800 rounded-lg p-4">
                            <h3 className="text-lg font-bold text-white mb-4">✍️ Text Colors</h3>
                            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                <ColorPicker
                                    label="Primary Text"
                                    value={theme.colors.text.primary}
                                    onChange={(v) => updateColor('text.primary', v)}
                                />
                                <ColorPicker
                                    label="Secondary Text"
                                    value={theme.colors.text.secondary}
                                    onChange={(v) => updateColor('text.secondary', v)}
                                />
                                <ColorPicker
                                    label="Accent Text"
                                    value={theme.colors.text.accent}
                                    onChange={(v) => updateColor('text.accent', v)}
                                />
                            </div>
                        </div>

                        {/* Border Colors */}
                        <div className="bg-gray-800 rounded-lg p-4">
                            <h3 className="text-lg font-bold text-white mb-4">📐 Border Colors</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <ColorPicker
                                    label="Primary Border"
                                    value={theme.colors.border.primary}
                                    onChange={(v) => updateColor('border.primary', v)}
                                />
                                <ColorPicker
                                    label="Secondary Border"
                                    value={theme.colors.border.secondary}
                                    onChange={(v) => updateColor('border.secondary', v)}
                                />
                            </div>
                        </div>

                        {/* Accent Colors */}
                        <div className="bg-gray-800 rounded-lg p-4">
                            <h3 className="text-lg font-bold text-white mb-4">✨ Accent Colors</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <ColorPicker
                                    label="Primary Accent"
                                    value={theme.colors.accent.primary}
                                    onChange={(v) => updateColor('accent.primary', v)}
                                />
                                <ColorPicker
                                    label="Secondary Accent"
                                    value={theme.colors.accent.secondary}
                                    onChange={(v) => updateColor('accent.secondary', v)}
                                />
                            </div>
                        </div>

                        {/* Status Colors */}
                        <div className="bg-gray-800 rounded-lg p-4">
                            <h3 className="text-lg font-bold text-white mb-4">🚦 Status Colors</h3>
                            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                                <ColorPicker
                                    label="Success"
                                    value={theme.colors.status.success}
                                    onChange={(v) => updateColor('status.success', v)}
                                />
                                <ColorPicker
                                    label="Warning"
                                    value={theme.colors.status.warning}
                                    onChange={(v) => updateColor('status.warning', v)}
                                />
                                <ColorPicker
                                    label="Error"
                                    value={theme.colors.status.error}
                                    onChange={(v) => updateColor('status.error', v)}
                                />
                                <ColorPicker
                                    label="Info"
                                    value={theme.colors.status.info}
                                    onChange={(v) => updateColor('status.info', v)}
                                />
                            </div>
                        </div>

                        {/* Preview */}
                        <div className="bg-gray-800 rounded-lg p-4">
                            <h3 className="text-lg font-bold text-white mb-4">👁️ Preview</h3>
                            <div
                                className="p-6 rounded-lg border-2"
                                style={{
                                    backgroundColor: theme.colors.background.primary,
                                    borderColor: theme.colors.border.primary
                                }}
                            >
                                <h4
                                    className="text-xl font-bold mb-2"
                                    style={{ color: theme.colors.text.primary }}
                                >
                                    Sample Header
                                </h4>
                                <p
                                    className="mb-4"
                                    style={{ color: theme.colors.text.secondary }}
                                >
                                    This is how your text will look with the current theme.
                                </p>
                                <div
                                    className="inline-block px-4 py-2 rounded"
                                    style={{
                                        backgroundColor: theme.colors.accent.primary,
                                        color: theme.colors.background.primary
                                    }}
                                >
                                    Accent Button
                                </div>
                                <div className="flex gap-2 mt-4">
                                    <div
                                        className="px-3 py-1 rounded text-xs"
                                        style={{
                                            backgroundColor: `${theme.colors.status.success}20`,
                                            color: theme.colors.status.success
                                        }}
                                    >
                                        Success
                                    </div>
                                    <div
                                        className="px-3 py-1 rounded text-xs"
                                        style={{
                                            backgroundColor: `${theme.colors.status.warning}20`,
                                            color: theme.colors.status.warning
                                        }}
                                    >
                                        Warning
                                    </div>
                                    <div
                                        className="px-3 py-1 rounded text-xs"
                                        style={{
                                            backgroundColor: `${theme.colors.status.error}20`,
                                            color: theme.colors.status.error
                                        }}
                                    >
                                        Error
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3 mt-6">
                        <button
                            onClick={handleSave}
                            className="flex-1 px-6 py-3 bg-gradient-to-r from-cyan-400 to-purple-500 text-black font-bold rounded-lg hover:opacity-90 transition-opacity"
                        >
                            💾 Save Custom Theme
                        </button>
                        <button
                            onClick={onClose}
                            className="px-6 py-3 bg-gray-700 text-white font-bold rounded-lg hover:bg-gray-600 transition-colors"
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

interface ColorPickerProps {
    label: string;
    value: string;
    onChange: (value: string) => void;
}

function ColorPicker({ label, value, onChange }: ColorPickerProps) {
    return (
        <div className="flex flex-col gap-2">
            <label className="text-sm text-gray-400">{label}</label>
            <div className="flex gap-2">
                <input
                    type="color"
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    className="w-12 h-10 rounded cursor-pointer"
                />
                <input
                    type="text"
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    className="flex-1 px-3 py-2 bg-gray-700 text-white rounded border border-gray-600 focus:border-cyan-400 outline-none text-sm font-mono"
                    placeholder="#000000"
                />
            </div>
        </div>
    );
}

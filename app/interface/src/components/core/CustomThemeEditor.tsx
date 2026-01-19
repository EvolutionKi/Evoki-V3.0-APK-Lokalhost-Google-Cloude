// Custom Theme Editor - Simple color picker for each theme property
import { useState } from 'react';
import type { Theme } from '../../themes';

interface CustomThemeEditorProps {
    isOpen: boolean;
    onClose: () => void;
    currentCustomTheme: Theme;
    onSave: (theme: Theme) => void;
}

export default function CustomThemeEditor({
    isOpen,
    onClose,
    currentCustomTheme,
    onSave
}: CustomThemeEditorProps) {
    const [editedTheme, setEditedTheme] = useState<Theme>(currentCustomTheme);

    if (!isOpen) return null;

    const updateColor = (category: string, key: string, value: string) => {
        setEditedTheme(prev => ({
            ...prev,
            colors: {
                ...prev.colors,
                [category]: {
                    ...prev.colors[category as keyof typeof prev.colors],
                    [key]: value
                }
            }
        }));
    };

    const handleSave = () => {
        onSave(editedTheme);
        onClose();
    };

    return (
        <>
            {/* Backdrop */}
            <div className="fixed inset-0 bg-black/80 z-50" onClick={onClose} />

            {/* Modal */}
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                <div
                    className="w-full max-w-4xl max-h-[90vh] overflow-y-auto rounded-lg p-6"
                    style={{
                        backgroundColor: 'var(--bg-secondary)',
                        border: '2px solid var(--border-primary)'
                    }}
                >
                    {/* Header */}
                    <div className="flex justify-between items-center mb-6">
                        <h2 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
                            🎨 Custom Theme Editor
                        </h2>
                        <button
                            onClick={onClose}
                            className="text-2xl"
                            style={{ color: 'var(--text-secondary)' }}
                        >
                            ✕
                        </button>
                    </div>

                    {/* Color Pickers Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* Background Colors */}
                        <div>
                            <h3 className="text-lg font-bold mb-3" style={{ color: 'var(--accent-primary)' }}>
                                Hintergrund-Farben
                            </h3>
                            <ColorInput
                                label="Primary (Haupthintergrund)"
                                value={editedTheme.colors.background.primary}
                                onChange={(v) => updateColor('background', 'primary', v)}
                            />
                            <ColorInput
                                label="Secondary (Tabs, Cards)"
                                value={editedTheme.colors.background.secondary}
                                onChange={(v) => updateColor('background', 'secondary', v)}
                            />
                            <ColorInput
                                label="Tertiary (Chat-Container)"
                                value={editedTheme.colors.background.tertiary}
                                onChange={(v) => updateColor('background', 'tertiary', v)}
                            />
                        </div>

                        {/* Text Colors */}
                        <div>
                            <h3 className="text-lg font-bold mb-3" style={{ color: 'var(--accent-primary)' }}>
                                Text-Farben
                            </h3>
                            <ColorInput
                                label="Primary (Haupttext)"
                                value={editedTheme.colors.text.primary}
                                onChange={(v) => updateColor('text', 'primary', v)}
                            />
                            <ColorInput
                                label="Secondary (Nebentext)"
                                value={editedTheme.colors.text.secondary}
                                onChange={(v) => updateColor('text', 'secondary', v)}
                            />
                            <ColorInput
                                label="Accent (Highlights)"
                                value={editedTheme.colors.text.accent}
                                onChange={(v) => updateColor('text', 'accent', v)}
                            />
                        </div>

                        {/* Border Colors */}
                        <div>
                            <h3 className="text-lg font-bold mb-3" style={{ color: 'var(--accent-primary)' }}>
                                Rahmen-Farben
                            </h3>
                            <ColorInput
                                label="Primary (Hauptrahmen)"
                                value={editedTheme.colors.border.primary}
                                onChange={(v) => updateColor('border', 'primary', v)}
                            />
                            <ColorInput
                                label="Secondary (Nebenrahmen)"
                                value={editedTheme.colors.border.secondary}
                                onChange={(v) => updateColor('border', 'secondary', v)}
                            />
                        </div>

                        {/* Accent Colors */}
                        <div>
                            <h3 className="text-lg font-bold mb-3" style={{ color: 'var(--accent-primary)' }}>
                                Akzent-Farben
                            </h3>
                            <ColorInput
                                label="Primary (Buttons, Icons)"
                                value={editedTheme.colors.accent.primary}
                                onChange={(v) => updateColor('accent', 'primary', v)}
                            />
                            <ColorInput
                                label="Secondary (Gradienten)"
                                value={editedTheme.colors.accent.secondary}
                                onChange={(v) => updateColor('accent', 'secondary', v)}
                            />
                        </div>

                        {/* Status Colors */}
                        <div className="md:col-span-2">
                            <h3 className="text-lg font-bold mb-3" style={{ color: 'var(--accent-primary)' }}>
                                Status-Farben
                            </h3>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                                <ColorInput
                                    label="Success (Erfolg)"
                                    value={editedTheme.colors.status.success}
                                    onChange={(v) => updateColor('status', 'success', v)}
                                />
                                <ColorInput
                                    label="Warning (Warnung)"
                                    value={editedTheme.colors.status.warning}
                                    onChange={(v) => updateColor('status', 'warning', v)}
                                />
                                <ColorInput
                                    label="Error (Fehler)"
                                    value={editedTheme.colors.status.error}
                                    onChange={(v) => updateColor('status', 'error', v)}
                                />
                                <ColorInput
                                    label="Info (Information)"
                                    value={editedTheme.colors.status.info}
                                    onChange={(v) => updateColor('status', 'info', v)}
                                />
                            </div>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex justify-end gap-3 mt-6 pt-6" style={{ borderTop: '1px solid var(--border-primary)' }}>
                        <button
                            onClick={onClose}
                            className="px-6 py-2 rounded font-medium"
                            style={{
                                backgroundColor: 'var(--bg-tertiary)',
                                color: 'var(--text-secondary)'
                            }}
                        >
                            Abbrechen
                        </button>
                        <button
                            onClick={handleSave}
                            className="px-6 py-2 rounded font-medium"
                            style={{
                                background: `linear-gradient(135deg, var(--accent-primary), var(--accent-secondary))`,
                                color: '#000'
                            }}
                        >
                            Speichern & Anwenden
                        </button>
                    </div>
                </div>
            </div>
        </>
    );
}

// Color Input Component
function ColorInput({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
    return (
        <div className="mb-3">
            <label className="block text-sm mb-1" style={{ color: 'var(--text-secondary)' }}>
                {label}
            </label>
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
                    className="flex-1 px-3 py-2 rounded font-mono text-sm"
                    style={{
                        backgroundColor: 'var(--bg-tertiary)',
                        border: '1px solid var(--border-primary)',
                        color: 'var(--text-primary)'
                    }}
                    placeholder="#000000"
                />
            </div>
        </div>
    );
}

// Settings Panel with Tabs - Theme/Display + Placeholder Tabs
import { useState } from 'react';
import type { Theme } from '../../themes';
import CustomThemeEditor from './CustomThemeEditor';

interface SettingsPanelProps {
    isOpen: boolean;
    onClose: () => void;
    // Theme props
    currentTheme: string;
    availableThemes: string[];
    onThemeChange: (theme: string) => void;
    customTheme: Theme;
    onCustomThemeUpdate: (theme: Theme) => void;
    // Display mode props
    displayMode: string;
    availableDisplayModes: string[];
    onDisplayModeChange: (mode: string) => void;
}

type SettingsTab = 'appearance' | 'account' | 'agents' | 'export' | 'privacy' | 'accessibility' | 'voice';

export default function SettingsPanel({
    isOpen,
    onClose,
    currentTheme,
    availableThemes,
    onThemeChange,
    customTheme,
    onCustomThemeUpdate,
    displayMode,
    availableDisplayModes,
    onDisplayModeChange
}: SettingsPanelProps) {
    const [activeTab, setActiveTab] = useState<SettingsTab>('appearance');
    const [isEditorOpen, setIsEditorOpen] = useState(false);

    if (!isOpen) return null;

    return (
        <>
            {/* Backdrop */}
            <div className="fixed inset-0 bg-black/70 z-40" onClick={onClose} />

            {/* Modal */}
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                <div className="bg-gray-900 border border-gray-700 rounded-lg w-full max-w-3xl max-h-[90vh] flex flex-col">
                    {/* Header */}
                    <div className="flex justify-between items-center p-6 border-b border-gray-700">
                        <h2 className="text-2xl font-bold text-white">⚙️ Settings</h2>
                        <button onClick={onClose} className="text-gray-400 hover:text-white text-2xl">
                            ✕
                        </button>
                    </div>

                    {/* Tabs */}
                    <div className="flex gap-2 px-6 pt-4 border-b border-gray-700 overflow-x-auto">
                        {[
                            { id: 'appearance', label: '🎨 Appearance', icon: '🎨' },
                            { id: 'account', label: '👤 Account', icon: '👤' },
                            { id: 'agents', label: '🤖 Agents', icon: '🤖' },
                            { id: 'export', label: '📥 Export', icon: '📥' },
                            { id: 'privacy', label: '🔒 Privacy', icon: '🔒' },
                            { id: 'accessibility', label: '♿ Accessibility', icon: '♿' },
                            { id: 'voice', label: '🎤 Voice', icon: '🎤' },
                        ].map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id as SettingsTab)}
                                className={`px-4 py-2 text-sm font-medium transition-colors border-b-2 ${activeTab === tab.id
                                        ? 'border-cyan-400 text-cyan-400'
                                        : 'border-transparent text-gray-400 hover:text-white'
                                    }`}
                            >
                                {tab.label}
                            </button>
                        ))}
                    </div>

                    {/* Content */}
                    <div className="flex-1 overflow-y-auto p-6">
                        {activeTab === 'appearance' && (
                            <div className="space-y-6">
                                {/* Theme Section */}
                                <div>
                                    <h3 className="text-lg font-bold text-white mb-3">Theme</h3>
                                    <div className="space-y-2">
                                        {availableThemes.map((themeKey) => {
                                            if (themeKey === 'custom') return null;
                                            return (
                                                <button
                                                    key={themeKey}
                                                    onClick={() => onThemeChange(themeKey)}
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

                                    {/* Custom Theme */}
                                    <div className="mt-4 pt-4 border-t border-gray-700">
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

                                {/* Display Mode Section */}
                                <div>
                                    <h3 className="text-lg font-bold text-white mb-3">Display Mode</h3>
                                    <div className="grid grid-cols-3 gap-2">
                                        {availableDisplayModes.map((mode) => (
                                            <button
                                                key={mode}
                                                onClick={() => onDisplayModeChange(mode)}
                                                className={`px-3 py-2 rounded text-sm font-medium transition-colors ${displayMode === mode
                                                        ? 'bg-cyan-400 text-black'
                                                        : 'bg-gray-800 text-white hover:bg-gray-700'
                                                    }`}
                                            >
                                                {mode === 'mobile' && '📱'}
                                                {mode === 'tablet' && '📱💻'}
                                                {mode === 'desktop' && '💻'}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}

                        {activeTab === 'account' && (
                            <div className="text-gray-300">
                                <h3 className="text-lg font-bold text-white mb-4">Account Settings (Coming Soon)</h3>
                                <ul className="space-y-2 list-disc list-inside">
                                    <li>Google Account Integration</li>
                                    <li>Profile Information</li>
                                    <li>Session Management</li>
                                    <li>Connected Devices</li>
                                    <li>Account Security</li>
                                    <li>Logout / Sign Out</li>
                                </ul>
                            </div>
                        )}

                        {activeTab === 'agents' && (
                            <div className="text-gray-300">
                                <h3 className="text-lg font-bold text-white mb-4">Agent Configuration (Coming Soon)</h3>
                                <ul className="space-y-2 list-disc list-inside">
                                    <li>Agent Personality Settings</li>
                                    <li>Response Style Preferences</li>
                                    <li>Custom Agent Instructions</li>
                                    <li>Agent Memory Management</li>
                                    <li>Multi-Agent Team Setup</li>
                                    <li>Agent Permissions & Capabilities</li>
                                </ul>
                            </div>
                        )}

                        {activeTab === 'export' && (
                            <div className="text-gray-300">
                                <h3 className="text-lg font-bold text-white mb-4">Data Export (Coming Soon)</h3>
                                <ul className="space-y-2 list-disc list-inside">
                                    <li>Export Chat History (JSON)</li>
                                    <li>Export Chat History (Markdown)</li>
                                    <li>Export Chat History (CSV)</li>
                                    <li>Export Chat History (PDF)</li>
                                    <li>Export Metrics Data</li>
                                    <li>Export Agent Configurations</li>
                                    <li>Bulk Export (All Data)</li>
                                </ul>
                            </div>
                        )}

                        {activeTab === 'privacy' && (
                            <div className="text-gray-300">
                                <h3 className="text-lg font-bold text-white mb-4">Privacy & Data (Coming Soon)</h3>
                                <ul className="space-y-2 list-disc list-inside">
                                    <li>Chat History Auto-Delete</li>
                                    <li>Analytics Opt-Out</li>
                                    <li>Data Collection Preferences</li>
                                    <li>Third-Party Data Sharing</li>
                                    <li>Clear All Data</li>
                                    <li>GDPR Data Request</li>
                                    <li>Privacy Policy</li>
                                </ul>
                            </div>
                        )}

                        {activeTab === 'accessibility' && (
                            <div className="text-gray-300">
                                <h3 className="text-lg font-bold text-white mb-4">Accessibility (Coming Soon)</h3>
                                <ul className="space-y-2 list-disc list-inside">
                                    <li>High Contrast Mode</li>
                                    <li>Dyslexia-Friendly Font</li>
                                    <li>Larger Text Size</li>
                                    <li>Keyboard Navigation</li>
                                    <li>Screen Reader Support</li>
                                    <li>Reduced Motion</li>
                                    <li>Color Blind Mode</li>
                                </ul>
                            </div>
                        )}

                        {activeTab === 'voice' && (
                            <div className="text-gray-300">
                                <h3 className="text-lg font-bold text-white mb-4">Voice & TTS (Coming Soon)</h3>
                                <ul className="space-y-2 list-disc list-inside">
                                    <li>Text-to-Speech Enable/Disable</li>
                                    <li>Voice Selection</li>
                                    <li>Speech Rate</li>
                                    <li>Speech Volume</li>
                                    <li>Speech Pitch</li>
                                    <li>Auto-Read Responses</li>
                                    <li>Voice Input (Speech-to-Text)</li>
                                </ul>
                            </div>
                        )}
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

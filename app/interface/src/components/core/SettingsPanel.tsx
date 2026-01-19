import { useState } from 'react';
import { useTheme } from '../../hooks/useTheme';
import { THEMES } from '../../themes';
import { DISPLAY_MODES, DisplayMode } from '../../displayModes';
import CustomThemeEditor from './CustomThemeEditor';

interface SettingsPanelProps {
    isOpen: boolean;
    onClose: () => void;
}

type SettingsTab = 'appearance' | 'account' | 'agents' | 'export' | 'privacy' | 'accessibility' | 'voice';

export default function SettingsPanel({ isOpen, onClose }: SettingsPanelProps) {
    const { currentTheme, displayMode, switchTheme, switchDisplayMode, updateCustomTheme } = useTheme();
    const [activeTab, setActiveTab] = useState<SettingsTab>('appearance');
    const [isEditingCustom, setIsEditingCustom] = useState(false);

    if (!isOpen) return null;

    return (
        <>
            {/* Backdrop */}
            <div
                className="fixed inset-0 bg-black/70 z-40"
                onClick={onClose}
            />

            {/* Settings Modal */}
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                <div className="bg-gray-900 border border-gray-700 rounded-lg w-full max-w-5xl max-h-[85vh] overflow-hidden flex flex-col">
                    {/* Header */}
                    <div className="flex items-center justify-between p-6 border-b border-gray-700">
                        <h2 className="text-2xl font-bold text-white">⚙️ Settings</h2>
                        <button
                            onClick={onClose}
                            className="text-gray-400 hover:text-white transition-colors"
                        >
                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                        </button>
                    </div>

                    {/* Tabs + Content */}
                    <div className="flex flex-1 overflow-hidden">
                        {/* Sidebar Tabs */}
                        <div className="w-48 bg-gray-800 border-r border-gray-700 p-4">
                            <div className="space-y-1">
                                <TabButton
                                    icon="🎨"
                                    label="Appearance"
                                    isActive={activeTab === 'appearance'}
                                    onClick={() => setActiveTab('appearance')}
                                />
                                <TabButton
                                    icon="👤"
                                    label="Account"
                                    isActive={activeTab === 'account'}
                                    onClick={() => setActiveTab('account')}
                                />
                                <TabButton
                                    icon="🤖"
                                    label="Agents"
                                    isActive={activeTab === 'agents'}
                                    onClick={() => setActiveTab('agents')}
                                />
                                <TabButton
                                    icon="📤"
                                    label="Export"
                                    isActive={activeTab === 'export'}
                                    onClick={() => setActiveTab('export')}
                                />
                                <TabButton
                                    icon="🔒"
                                    label="Privacy"
                                    isActive={activeTab === 'privacy'}
                                    onClick={() => setActiveTab('privacy')}
                                />
                                <TabButton
                                    icon="♿"
                                    label="Accessibility"
                                    isActive={activeTab === 'accessibility'}
                                    onClick={() => setActiveTab('accessibility')}
                                />
                                <TabButton
                                    icon="🎤"
                                    label="Voice"
                                    isActive={activeTab === 'voice'}
                                    onClick={() => setActiveTab('voice')}
                                />
                            </div>
                        </div>

                        {/* Content Area */}
                        <div className="flex-1 overflow-y-auto p-6">
                            {activeTab === 'appearance' && (
                                <AppearanceSettings
                                    currentTheme={currentTheme}
                                    displayMode={displayMode || 'desktop'}
                                    onThemeChange={switchTheme}
                                    onDisplayModeChange={switchDisplayMode}
                                    onEditCustomTheme={() => setIsEditingCustom(true)}
                                />
                            )}
                            {activeTab === 'account' && <AccountSettings />}
                            {activeTab === 'agents' && <AgentSettings />}
                            {activeTab === 'export' && <ExportSettings />}
                            {activeTab === 'privacy' && <PrivacySettings />}
                            {activeTab === 'accessibility' && <AccessibilitySettings />}
                            {activeTab === 'voice' && <VoiceSettings />}
                        </div>
                    </div>
                </div>
            </div>

            {/* Custom Theme Editor */}
            {isEditingCustom && (
                <CustomThemeEditor
                    customTheme={THEMES.custom}
                    onSave={updateCustomTheme}
                    onClose={() => setIsEditingCustom(false)}
                />
            )}
        </>
    );
}

function TabButton({ icon, label, isActive, onClick }: any) {
    return (
        <button
            onClick={onClick}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${isActive
                ? 'bg-cyan-400/10 text-cyan-400'
                : 'text-gray-400 hover:bg-gray-700 hover:text-white'
                }`}
        >
            <span className="text-lg">{icon}</span>
            <span className="text-sm font-medium">{label}</span>
        </button>
    );
}

function AppearanceSettings({ currentTheme, displayMode, onThemeChange, onDisplayModeChange, onEditCustomTheme }: any) {
    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-lg font-bold text-white mb-4">📐 Display Format</h3>
                <div className="grid grid-cols-3 gap-4">
                    {Object.entries(DISPLAY_MODES).map(([key, mode]) => (
                        <button
                            key={key}
                            onClick={() => onDisplayModeChange(key as DisplayMode)}
                            className={`p-4 rounded-lg border-2 transition-all ${displayMode === key
                                ? 'border-cyan-400 bg-cyan-400/10'
                                : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                                }`}
                        >
                            <div className="text-3xl mb-2">
                                {key === 'mobile' ? '📱' : key === 'tablet' ? '📲' : '🖥️'}
                            </div>
                            <div className="text-sm font-bold text-white capitalize">{key}</div>
                            <div className="text-xs text-gray-400 mt-1">
                                {key === 'mobile' ? 'Compact' : key === 'tablet' ? 'Balanced' : 'Spacious'}
                            </div>
                        </button>
                    ))}
                </div>
            </div>

            <div>
                <h3 className="text-lg font-bold text-white mb-4">🎨 Color Theme</h3>
                <div className="grid grid-cols-3 gap-3">
                    {Object.entries(THEMES).map(([key, theme]) => (
                        <button
                            key={key}
                            onClick={() => {
                                if (key === 'custom') {
                                    onEditCustomTheme();
                                } else {
                                    onThemeChange(key);
                                }
                            }}
                            className={`p-3 rounded-lg border-2 transition-all ${currentTheme === key
                                ? 'border-cyan-400 bg-cyan-400/10'
                                : 'border-gray-700 bg-gray-800 hover:border-gray-600'
                                } ${key === 'custom' ? 'ring-2 ring-purple-500/30' : ''}`}
                        >
                            <div className="text-xs font-bold text-white mb-2 truncate">{theme.name}</div>
                            <div className="grid grid-cols-5 gap-1">
                                {[
                                    theme.colors.background.primary,
                                    theme.colors.accent.primary,
                                    theme.colors.accent.secondary,
                                    theme.colors.status.success,
                                    theme.colors.status.error,
                                ].map((color, i) => (
                                    <div key={i} className="h-4 rounded" style={{ backgroundColor: color }} />
                                ))}
                            </div>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}

function AccountSettings() {
    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-lg font-bold text-white mb-4">🔐 Google Account</h3>
                <div className="bg-gray-800 rounded-lg p-6">
                    <div className="flex items-center gap-4 mb-4">
                        <div className="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center">
                            <span className="text-3xl">👤</span>
                        </div>
                        <div>
                            <div className="text-white font-bold">Not signed in</div>
                            <div className="text-sm text-gray-400">Sign in to sync across devices</div>
                        </div>
                    </div>
                    <button className="w-full px-4 py-3 bg-white text-gray-900 font-bold rounded-lg hover:bg-gray-100 transition-colors flex items-center justify-center gap-2">
                        <svg className="w-5 h-5" viewBox="0 0 24 24">
                            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                        </svg>
                        Sign in with Google
                    </button>
                </div>
            </div>

            <div>
                <h3 className="text-lg font-bold text-white mb-4">👥 Identity Verification</h3>
                <div className="bg-gray-800 rounded-lg p-4">
                    <div className="text-sm text-gray-400">
                        Sign in to enable identity-based features:
                    </div>
                    <ul className="mt-3 space-y-2 text-sm text-gray-300">
                        <li className="flex items-center gap-2">
                            <span className="text-green-400">✓</span> Multi-device sync
                        </li>
                        <li className="flex items-center gap-2">
                            <span className="text-green-400">✓</span> Personalized responses
                        </li>
                        <li className="flex items-center gap-2">
                            <span className="text-green-400">✓</span> Cloud backup
                        </li>
                        <li className="flex items-center gap-2">
                            <span className="text-green-400">✓</span> Usage analytics
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    );
}

function AgentSettings() {
    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-lg font-bold text-white mb-4">🤖 Interaction Patterns</h3>
                <div className="space-y-4">
                    <SettingRow
                        label="Response Style"
                        description="How Evoki communicates with you"
                        control={
                            <select className="px-3 py-2 bg-gray-800 text-white rounded border border-gray-700 focus:border-cyan-400 outline-none">
                                <option>Professional</option>
                                <option>Casual</option>
                                <option>Technical</option>
                                <option>Empathetic</option>
                            </select>
                        }
                    />
                    <SettingRow
                        label="Response Length"
                        description="Preferred answer detail level"
                        control={
                            <select className="px-3 py-2 bg-gray-800 text-white rounded border border-gray-700 focus:border-cyan-400 outline-none">
                                <option>Concise</option>
                                <option>Balanced</option>
                                <option>Detailed</option>
                                <option>Comprehensive</option>
                            </select>
                        }
                    />
                    <SettingRow
                        label="Use Analogies"
                        description="Explain complex topics with examples"
                        control={<ToggleSwitch />}
                    />
                    <SettingRow
                        label="Code Examples"
                        description="Include code snippets when relevant"
                        control={<ToggleSwitch defaultChecked />}
                    />
                </div>
            </div>

            <div>
                <h3 className="text-lg font-bold text-white mb-4">🧠 Memory & Context</h3>
                <div className="space-y-4">
                    <SettingRow
                        label="Remember Preferences"
                        description="Learn from past interactions"
                        control={<ToggleSwitch defaultChecked />}
                    />
                    <SettingRow
                        label="Context Window"
                        description="How many messages to remember"
                        control={
                            <select className="px-3 py-2 bg-gray-800 text-white rounded border border-gray-700 focus:border-cyan-400 outline-none">
                                <option>Last 10 messages</option>
                                <option>Last 50 messages</option>
                                <option>Entire session</option>
                            </select>
                        }
                    />
                </div>
            </div>
        </div>
    );
}

function ExportSettings() {
    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-lg font-bold text-white mb-4">💾 Export Chat History</h3>
                <div className="grid grid-cols-2 gap-4">
                    <ExportButton icon="📄" label="Export as JSON" format="json" />
                    <ExportButton icon="📝" label="Export as Markdown" format="md" />
                    <ExportButton icon="📊" label="Export as CSV" format="csv" />
                    <ExportButton icon="📋" label="Export as PDF" format="pdf" />
                </div>
            </div>

            <div>
                <h3 className="text-lg font-bold text-white mb-4">🗂️ Backup & Restore</h3>
                <div className="space-y-3">
                    <button className="w-full px-4 py-3 bg-blue-500 text-white font-bold rounded-lg hover:bg-blue-600 transition-colors">
                        📦 Create Full Backup
                    </button>
                    <button className="w-full px-4 py-3 bg-gray-800 text-white font-bold rounded-lg hover:bg-gray-700 transition-colors border border-gray-700">
                        📥 Restore from Backup
                    </button>
                </div>
            </div>

            <div>
                <h3 className="text-lg font-bold text-white mb-4">☁️ Cloud Sync</h3>
                <div className="bg-gray-800 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                        <div>
                            <div className="text-white font-bold">Auto-Sync</div>
                            <div className="text-sm text-gray-400">Automatically backup to cloud</div>
                        </div>
                        <ToggleSwitch />
                    </div>
                    <div className="text-xs text-gray-500">
                        Last synced: Never (Sign in required)
                    </div>
                </div>
            </div>
        </div>
    );
}

function PrivacySettings() {
    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-lg font-bold text-white mb-4">🔒 Data Privacy</h3>
                <div className="space-y-4">
                    <SettingRow
                        label="Save Chat History"
                        description="Store conversations locally"
                        control={<ToggleSwitch defaultChecked />}
                    />
                    <SettingRow
                        label="Analytics"
                        description="Help improve Evoki with anonymous usage data"
                        control={<ToggleSwitch />}
                    />
                    <SettingRow
                        label="Crash Reports"
                        description="Automatically send error reports"
                        control={<ToggleSwitch defaultChecked />}
                    />
                </div>
            </div>

            <div>
                <h3 className="text-lg font-bold text-white mb-4">🗑️ Data Management</h3>
                <div className="space-y-3">
                    <button className="w-full px-4 py-3 bg-yellow-500 text-black font-bold rounded-lg hover:bg-yellow-600 transition-colors">
                        🧹 Clear Chat History
                    </button>
                    <button className="w-full px-4 py-3 bg-red-500 text-white font-bold rounded-lg hover:bg-red-600 transition-colors">
                        ⚠️ Delete All Data
                    </button>
                </div>
            </div>
        </div>
    );
}

function AccessibilitySettings() {
    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-lg font-bold text-white mb-4">♿ Visual</h3>
                <div className="space-y-4">
                    <SettingRow
                        label="High Contrast"
                        description="Increase color contrast"
                        control={<ToggleSwitch />}
                    />
                    <SettingRow
                        label="Large Text"
                        description="Increase font size (+2px)"
                        control={<ToggleSwitch />}
                    />
                    <SettingRow
                        label="Reduce Motion"
                        description="Minimize animations"
                        control={<ToggleSwitch />}
                    />
                </div>
            </div>

            <div>
                <h3 className="text-lg font-bold text-white mb-4">🔊 Audio</h3>
                <div className="space-y-4">
                    <SettingRow
                        label="Screen Reader Support"
                        description="Optimize for screen readers"
                        control={<ToggleSwitch />}
                    />
                    <SettingRow
                        label="Sound Effects"
                        description="Play sounds for notifications"
                        control={<ToggleSwitch defaultChecked />}
                    />
                </div>
            </div>

            <div>
                <h3 className="text-lg font-bold text-white mb-4">⌨️ Keyboard</h3>
                <div className="bg-gray-800 rounded-lg p-4">
                    <div className="text-sm text-gray-300 space-y-2">
                        <div><kbd className="px-2 py-1 bg-gray-700 rounded text-xs">Ctrl + K</kbd> Open settings</div>
                        <div><kbd className="px-2 py-1 bg-gray-700 rounded text-xs">Ctrl + /</kbd> Focus chat input</div>
                        <div><kbd className="px-2 py-1 bg-gray-700 rounded text-xs">Esc</kbd> Close modals</div>
                    </div>
                </div>
            </div>
        </div>
    );
}

function VoiceSettings() {
    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-lg font-bold text-white mb-4">🎤 Voice Input</h3>
                <div className="space-y-4">
                    <SettingRow
                        label="Enable Voice Input"
                        description="Speak instead of typing"
                        control={<ToggleSwitch />}
                    />
                    <SettingRow
                        label="Language"
                        description="Voice recognition language"
                        control={
                            <select className="px-3 py-2 bg-gray-800 text-white rounded border border-gray-700 focus:border-cyan-400 outline-none">
                                <option>Deutsch</option>
                                <option>English</option>
                                <option>Español</option>
                                <option>Français</option>
                            </select>
                        }
                    />
                </div>
            </div>

            <div>
                <h3 className="text-lg font-bold text-white mb-4">🔊 Text-to-Speech</h3>
                <div className="space-y-4">
                    <SettingRow
                        label="Read Responses Aloud"
                        description="Use TTS for Evoki's responses"
                        control={<ToggleSwitch />}
                    />
                    <SettingRow
                        label="Voice"
                        description="TTS voice selection"
                        control={
                            <select className="px-3 py-2 bg-gray-800 text-white rounded border border-gray-700 focus:border-cyan-400 outline-none">
                                <option>Neural (Female)</option>
                                <option>Neural (Male)</option>
                                <option>Standard (Female)</option>
                                <option>Standard (Male)</option>
                            </select>
                        }
                    />
                    <SettingRow
                        label="Speed"
                        description="Playback speed"
                        control={
                            <input
                                type="range"
                                min="0.5"
                                max="2"
                                step="0.1"
                                defaultValue="1"
                                className="w-32"
                            />
                        }
                    />
                </div>
            </div>
        </div>
    );
}

function SettingRow({ label, description, control }: any) {
    return (
        <div className="flex items-center justify-between p-4 bg-gray-800 rounded-lg">
            <div>
                <div className="text-white font-medium">{label}</div>
                <div className="text-sm text-gray-400">{description}</div>
            </div>
            <div>{control}</div>
        </div>
    );
}

function ToggleSwitch({ defaultChecked = false }: { defaultChecked?: boolean }) {
    const [checked, setChecked] = useState(defaultChecked);
    return (
        <button
            onClick={() => setChecked(!checked)}
            className={`w-12 h-6 rounded-full transition-colors ${checked ? 'bg-cyan-400' : 'bg-gray-700'
                }`}
        >
            <div
                className={`w-5 h-5 bg-white rounded-full transition-transform ${checked ? 'translate-x-6' : 'translate-x-1'
                    }`}
            />
        </button>
    );
}

function ExportButton({ icon, label, format }: any) {
    return (
        <button className="p-4 bg-gray-800 rounded-lg hover:bg-gray-700 transition-colors border border-gray-700 hover:border-cyan-400">
            <div className="text-3xl mb-2">{icon}</div>
            <div className="text-sm font-bold text-white">{label}</div>
            <div className="text-xs text-gray-400 mt-1">Download .{format}</div>
        </button>
    );
}

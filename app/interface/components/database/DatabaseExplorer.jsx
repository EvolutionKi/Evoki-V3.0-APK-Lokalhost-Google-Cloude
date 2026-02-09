import React, { useState, useMemo } from 'react';
import {
    Database,
    Activity,
    ShieldAlert,
    BrainCircuit,
    Share2,
    Search,
    ArrowRight,
    Lock,
    Layers,
    Fingerprint,
    Terminal,
    ChevronRight,
    Info,
    Zap
} from 'lucide-react';

const DB_DATA = {
    metadata: {
        id: 'evoki_metadata.db',
        name: 'Structural Layer',
        icon: Database,
        color: 'blue',
        purpose: 'Session management, data integrity, and raw prompt-pair storage.',
        tables: [
            { name: 'sessions', desc: 'Unique session containers and state management.' },
            { name: 'prompt_pairs', desc: 'Atomic User + AI text blocks with unique SHA-256 hashes.' },
            { name: 'session_chain', desc: 'Blockchain-style integrity chain for tamper detection.' }
        ],
        metrics: [],
        highlights: ['SHA-256 Integrity', 'Dual-Pair Atomic Storage']
    },
    resonance: {
        id: 'evoki_resonance.db',
        name: 'Resonance Layer',
        icon: Activity,
        color: 'emerald',
        purpose: 'Core affect, physics engine outputs, and 7D Soul-Signature tracking.',
        tables: [
            { name: 'core_metrics', desc: 'm1-m20 (Affekt, PCI, ZLF, LL, z_prox).' },
            { name: 'physics_metrics', desc: 'm21-m35 (A_Phys Engine raw outputs).' },
            { name: 'b_state_evolution', desc: '7D B-Vektor (Life, Truth, Depth, Init, Warmth, Safety, Clarity).' },
            { name: 'gradient_analysis', desc: '∇A, ∇B, and Disharmony calculations.' }
        ],
        metrics: ['m1-m100', 'B_life-B_align'],
        highlights: ['Dual-Gradient Analysis', 'A_Phys V11 Logic']
    },
    triggers: {
        id: 'evoki_triggers.db',
        name: 'Guardian Layer',
        icon: ShieldAlert,
        color: 'red',
        purpose: 'Crisis detection, trauma markers, and safety intervention logs.',
        tables: [
            { name: 'trauma_metrics', desc: 'm101-m115 (Panic, Disso, Integ, Shock, Fog).' },
            { name: 'hazard_events', desc: 'm151 Hazard logs and Guardian Trip records.' },
            { name: 'personal_triggers', desc: 'Learned user-specific trauma keywords.' },
            { name: 'interventions', desc: 'Guardian action history and efficacy tracking.' }
        ],
        metrics: ['m101-m115', 'm151', 'm160'],
        highlights: ['Privacy Isolation', 'Pattern Learning']
    },
    metapatterns: {
        id: 'evoki_metapatterns.db',
        name: 'Cognitive Layer',
        icon: BrainCircuit,
        color: 'purple',
        purpose: 'Meta-cognition, system health, and advanced linguistic fingerprinting.',
        tables: [
            { name: 'meta_metrics', desc: 'm116-m150 (Recursive depth, Paradox detection).' },
            { name: 'system_metrics', desc: 'm152-m168 (A51 Compliance, Cumulative Stress).' },
            { name: 'user_vocabulary', desc: 'Lexical diversity and word frequency maps.' },
            { name: 'metaphors', desc: 'Recurring symbolic expressions used by the architect.' }
        ],
        metrics: ['m116-m150', 'm152-m168'],
        highlights: ['Linguistic Fingerprinting', 'N-Gram Analysis']
    },
    graph: {
        id: 'evoki_v3_graph.db',
        name: 'Relational Layer',
        icon: Share2,
        color: 'amber',
        purpose: 'Relationship graph, thematic clustering, and precomputed navigation paths.',
        tables: [
            { name: 'graph_nodes', desc: 'Prompt pairs as nodes with denormalized critical metrics.' },
            { name: 'graph_edges', desc: 'Semantic + Metric similarity links between nodes.' },
            { name: 'graph_clusters', desc: 'Auto-generated thematic groups (Trauma, Joy, etc.).' }
        ],
        metrics: ['Denormalized Copies'],
        highlights: ['Hybrid Similarity', 'Thematic Clustering']
    }
};

const METRIC_REGISTRY = [
    { id: 'm1_A', db: 'resonance', cat: 'Core' },
    { id: 'm15_affekt_a', db: 'resonance', cat: 'Physics' },
    { id: 'm19_z_prox', db: 'resonance', cat: 'Safety' },
    { id: 'm101_T_panic', db: 'triggers', cat: 'Trauma' },
    { id: 'm110_black_hole', db: 'triggers', cat: 'Trauma' },
    { id: 'm151_hazard', db: 'triggers', cat: 'Hazard' },
    { id: 'm116_meta_1', db: 'metapatterns', cat: 'Meta' },
    { id: 'm168_cum_stress', db: 'metapatterns', cat: 'System' },
];

export default function App() {
    const [activeTab, setActiveTab] = useState('metadata');
    const [search, setSearch] = useState('');

    const filteredMetrics = useMemo(() => {
        return METRIC_REGISTRY.filter(m =>
            m.id.toLowerCase().includes(search.toLowerCase()) ||
            m.db.toLowerCase().includes(search.toLowerCase())
        );
    }, [search]);

    // Handle Dynamic Tailwind Color Mapping (Safe listing via lookup)
    const colorMap = {
        blue: { bg: 'bg-blue-500', text: 'text-blue-500', border: 'border-blue-500', tint: 'bg-blue-100', darkTint: 'dark:bg-blue-900/30' },
        emerald: { bg: 'bg-emerald-500', text: 'text-emerald-500', border: 'border-emerald-500', tint: 'bg-emerald-100', darkTint: 'dark:bg-emerald-900/30' },
        red: { bg: 'bg-red-500', text: 'text-red-500', border: 'border-red-500', tint: 'bg-red-100', darkTint: 'dark:bg-red-900/30' },
        purple: { bg: 'bg-purple-500', text: 'text-purple-500', border: 'border-purple-500', tint: 'bg-purple-100', darkTint: 'dark:bg-purple-900/30' },
        amber: { bg: 'bg-amber-500', text: 'text-amber-500', border: 'border-amber-500', tint: 'bg-amber-100', darkTint: 'dark:bg-amber-900/30' }
    };

    const currentDb = DB_DATA[activeTab];
    const ActiveIcon = currentDb.icon;
    const activeColors = colorMap[currentDb.color];

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 font-sans p-4 md:p-8 transition-colors duration-300">
            {/* Header */}
            <header className="max-w-6xl mx-auto mb-12">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <div className="bg-blue-600 p-2 rounded-lg shadow-lg shadow-blue-500/20">
                            <Layers className="text-white w-6 h-6" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold tracking-tight">EVOKI V3.0 Hybrid DB</h1>
                            <p className="text-sm text-slate-500 dark:text-slate-400 uppercase tracking-widest font-semibold">Architectural Specification</p>
                        </div>
                    </div>
                    <div className="hidden sm:flex items-center gap-2 bg-white dark:bg-slate-900 px-4 py-2 rounded-full border border-slate-200 dark:border-slate-800 text-xs font-mono">
                        <Lock className="w-3 h-3 text-emerald-500" />
                        <span>GENESIS_SHA256: bdb3443...</span>
                    </div>
                </div>
            </header>

            <main className="max-w-6xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-8">

                {/* Navigation Sidebar */}
                <nav className="lg:col-span-3 flex flex-col gap-2">
                    <div className="mb-4">
                        <p className="text-xs font-bold text-slate-400 uppercase mb-2 ml-2 tracking-widest">Storage Units</p>
                        {Object.entries(DB_DATA).map(([key, db]) => {
                            const NavIcon = db.icon;
                            return (
                                <button
                                    key={key}
                                    onClick={() => setActiveTab(key)}
                                    className={`w-full flex items-center gap-3 p-3 rounded-xl transition-all duration-200 ${activeTab === key
                                            ? 'bg-white dark:bg-slate-900 shadow-md border border-slate-200 dark:border-slate-800'
                                            : 'hover:bg-slate-200 dark:hover:bg-slate-900/50 text-slate-500'
                                        }`}
                                >
                                    <NavIcon className={`w-5 h-5 ${activeTab === key ? colorMap[db.color].text : ''}`} />
                                    <span className={`font-semibold text-sm ${activeTab === key ? 'text-slate-900 dark:text-white' : ''}`}>
                                        {db.id}
                                    </span>
                                    {activeTab === key && <ChevronRight className="w-4 h-4 ml-auto text-slate-400" />}
                                </button>
                            );
                        })}
                    </div>

                    <div className="mt-4 p-4 bg-slate-100 dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800">
                        <div className="flex items-center gap-2 mb-4 text-xs font-bold text-slate-400 uppercase tracking-widest">
                            <Search className="w-3 h-3" />
                            <span>Metric Registry</span>
                        </div>
                        <input
                            type="text"
                            placeholder="Search m-ID..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg p-2 text-xs mb-4 outline-none focus:ring-2 focus:ring-blue-500 transition-all shadow-inner"
                        />
                        <div className="space-y-2 max-h-48 overflow-y-auto pr-2 custom-scrollbar">
                            {filteredMetrics.map(m => {
                                const metricDbColors = colorMap[DB_DATA[m.db].color];
                                return (
                                    <div key={m.id} className="flex items-center justify-between text-xs p-2 bg-white dark:bg-slate-800/50 rounded border border-slate-200/50 dark:border-slate-700/50">
                                        <span className="font-mono font-bold text-slate-700 dark:text-slate-300">{m.id}</span>
                                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold uppercase ${metricDbColors.tint} ${metricDbColors.text} ${metricDbColors.darkTint}`}>
                                            {m.db.split('_')[1]}
                                        </span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </nav>

                {/* Content Area */}
                <section className="lg:col-span-9 space-y-6">

                    {/* Main DB Details Card */}
                    <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-sm transition-all duration-500">
                        <div className={`h-2 ${activeColors.bg}`} />
                        <div className="p-6 md:p-8">
                            <div className="flex flex-col md:flex-row md:items-start justify-between gap-6 mb-8">
                                <div>
                                    <div className="flex items-center gap-3 mb-2">
                                        <ActiveIcon className={`w-8 h-8 ${activeColors.text}`} />
                                        <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">{currentDb.name}</h2>
                                    </div>
                                    <p className="text-slate-500 dark:text-slate-400 max-w-xl text-sm leading-relaxed">
                                        {currentDb.purpose}
                                    </p>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                    {currentDb.highlights.map(h => (
                                        <span key={h} className="bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider">
                                            {h}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                {/* Table Schema */}
                                <div className="space-y-4">
                                    <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-widest">
                                        <Terminal className="w-3 h-3" />
                                        <span>Relational Schema</span>
                                    </div>
                                    <div className="space-y-3">
                                        {currentDb.tables.map(table => (
                                            <div key={table.name} className="group p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-600 transition-all">
                                                <h4 className="text-sm font-bold font-mono text-slate-900 dark:text-white mb-1 group-hover:text-blue-500 transition-colors">
                                                    {table.name}
                                                </h4>
                                                <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                                                    {table.desc}
                                                </p>
                                            </div>
                                        ))}
                                    </div>
                                </div>

                                {/* Functionality & Metrics */}
                                <div className="space-y-6">
                                    <div>
                                        <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">
                                            <Zap className="w-3 h-3" />
                                            <span>Metric Scope</span>
                                        </div>
                                        {currentDb.metrics.length > 0 ? (
                                            <div className="flex flex-wrap gap-2">
                                                {currentDb.metrics.map(m => (
                                                    <span key={m} className={`${activeColors.text} bg-slate-50 dark:bg-slate-800 border border-slate-100 dark:border-slate-700 px-3 py-1.5 rounded-lg text-xs font-bold font-mono shadow-sm`}>
                                                        {m}
                                                    </span>
                                                ))}
                                            </div>
                                        ) : (
                                            <div className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-dashed border-slate-200 dark:border-slate-800 text-center">
                                                <p className="text-xs text-slate-400 italic">No direct metric storage. Functional data only.</p>
                                            </div>
                                        )}
                                    </div>

                                    <div className="p-6 bg-slate-900 rounded-2xl text-white relative overflow-hidden group">
                                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:scale-125 transition-transform duration-500">
                                            <Fingerprint className="w-12 h-12" />
                                        </div>
                                        <h5 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Reversibility Check</h5>
                                        <p className="text-xs text-slate-300 leading-relaxed mb-4">
                                            Every entry in <span className="font-mono text-white">{currentDb.id}</span> is cross-validated using the 4-phase calculation pipeline to ensure 100% state reconstruction.
                                        </p>
                                        <div className="flex items-center gap-4 text-[10px] font-mono text-slate-500 uppercase tracking-tighter">
                                            <div className="flex items-center gap-1">
                                                <div className="w-2 h-2 rounded-full bg-emerald-500" />
                                                <span>Forward: Text → DB</span>
                                            </div>
                                            <div className="flex items-center gap-1">
                                                <div className="w-2 h-2 rounded-full bg-blue-500" />
                                                <span>Backward: DB → State</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Ingestion Flow Visualizer */}
                    <div className="bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-8 shadow-sm">
                        <div className="flex items-center justify-between mb-8">
                            <div className="flex items-center gap-2">
                                <Activity className="w-5 h-5 text-blue-500" />
                                <h3 className="text-xl font-bold tracking-tight">Ingestion Pipeline</h3>
                            </div>
                            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                                Real-time Sequential Flow
                            </div>
                        </div>

                        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                            <FlowStep icon={Terminal} label="Parser" sub="Metadata" color="blue" />
                            <ArrowRight className="w-4 h-4 text-slate-300 hidden md:block" />
                            <FlowStep icon={Fingerprint} label="A51" sub="Integrity" color="emerald" />
                            <ArrowRight className="w-4 h-4 text-slate-300 hidden md:block" />
                            <FlowStep icon={BrainCircuit} label="Calculators" sub="m1-m168" color="purple" />
                            <ArrowRight className="w-4 h-4 text-slate-300 hidden md:block" />
                            <FlowStep icon={Share2} label="Distributor" sub="5x SQLite" color="amber" />
                        </div>

                        <div className="mt-8 pt-8 border-t border-slate-100 dark:border-slate-800 flex items-start gap-3">
                            <Info className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                            <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
                                <span className="font-bold">Protocol A71 Enforcement:</span> Before the first user input, the system signs a snapshot of the initial state. Any deviation detected in the <span className="font-mono text-slate-900 dark:text-white">session_chain</span> triggers a Guardian Lockdown.
                            </p>
                        </div>
                    </div>
                </section>
            </main>

            <footer className="max-w-6xl mx-auto mt-12 pb-12 text-center border-t border-slate-200 dark:border-slate-800 pt-8">
                <p className="text-xs text-slate-500 dark:text-slate-400 font-mono">
                    EVOKI HYBRID DATA LAYER VERSION 3.0.0 // STATUS: READY FOR T4 BACKFILL
                </p>
            </footer>

            {/* Dynamic Styling Helpers */}
            <style dangerouslySetInnerHTML={{
                __html: `
        .custom-scrollbar::-webkit-scrollbar {
          width: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #cbd5e1;
          border-radius: 10px;
        }
        .dark .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #334155;
        }
      `}} />
        </div>
    );
}

function FlowStep({ icon: Icon, label, sub, color }) {
    const colorMap = {
        blue: 'bg-blue-500',
        emerald: 'bg-emerald-500',
        purple: 'bg-purple-500',
        amber: 'bg-amber-500',
        red: 'bg-red-500'
    };

    return (
        <div className="flex flex-col items-center group w-full md:w-auto">
            <div className={`w-14 h-14 ${colorMap[color]} rounded-2xl flex items-center justify-center text-white shadow-lg group-hover:scale-110 transition-all duration-300 mb-3`}>
                <Icon className="w-6 h-6" />
            </div>
            <div className="text-center">
                <div className="text-sm font-bold tracking-tight">{label}</div>
                <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">{sub}</div>
            </div>
        </div>
    );
}

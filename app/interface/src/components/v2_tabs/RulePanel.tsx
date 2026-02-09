import React, { useState, useCallback } from 'react';
import { ChatMessage, RuleHit } from '../types';
import { Search, Filter, X } from './icons';

interface RulePanelProps {
    mergedData: ChatMessage[];
    ruleHits: RuleHit[];
    setRuleHits: (hits: RuleHit[]) => void;
}

const RulePanel: React.FC<RulePanelProps> = ({ mergedData, ruleHits, setRuleHits }) => {
    const [searchTerm, setSearchTerm] = useState('');
    const [searchType, setSearchType] = useState<'exact' | 'regex' | 'keyword'>('keyword');
    const [isCaseSensitive, setIsCaseSensitive] = useState(false);

    const handleSearch = useCallback(() => {
        if (!searchTerm.trim()) {
            alert('Bitte geben Sie einen Suchbegriff ein.');
            return;
        }

        const newHits: RuleHit[] = [];
        let searchRegex: RegExp;

        try {
            const flags = isCaseSensitive ? 'g' : 'gi';
            if (searchType === 'regex') {
                searchRegex = new RegExp(searchTerm, flags);
            } else if (searchType === 'exact') {
                const escapedTerm = searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                searchRegex = new RegExp(`\\b${escapedTerm}\\b`, flags);
            } else { // keyword
                const escapedTerm = searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                searchRegex = new RegExp(escapedTerm, flags);
            }
        } catch (error) {
            alert(`Ungültiger regulärer Ausdruck: ${error instanceof Error ? error.message : 'Unknown error'}`);
            return;
        }

        mergedData.forEach(message => {
            let match;
            searchRegex.lastIndex = 0;
            while ((match = searchRegex.exec(message.text)) !== null) {
                const snippetRadius = 50;
                const startIndex = Math.max(0, match.index - snippetRadius);
                const endIndex = Math.min(message.text.length, match.index + match[0].length + snippetRadius);
                
                const prefix = startIndex > 0 ? '...' : '';
                const suffix = endIndex < message.text.length ? '...' : '';
                const snippet = `${prefix}${message.text.substring(startIndex, endIndex)}${suffix}`;

                newHits.push({
                    id: `${message.eid}-${match.index}`,
                    version: '1.0',
                    date: new Date().toISOString(),
                    kind: 'GEN',
                    line: searchTerm,
                    status: 'HIT',
                    snippet,
                    source: message.source,
                    messageEid: message.eid,
                });
            }
        });

        setRuleHits(newHits);

    }, [searchTerm, searchType, isCaseSensitive, mergedData, setRuleHits]);

    const clearSearch = () => {
        setSearchTerm('');
        setRuleHits([]);
    };

    return (
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold mb-2 text-white">Regelwerk-Suche</h2>
                <p className="text-gray-400">Durchsuchen Sie die gemergten Chat-Daten mit Stichwörtern oder regulären Ausdrücken, um spezifische Muster zu finden.</p>
            </div>

            <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 space-y-4">
                <div className="flex flex-wrap gap-4 items-end">
                    <div className="flex-grow min-w-[250px]">
                        <label htmlFor="search-term" className="text-sm font-medium text-gray-300">Suchbegriff / Regex</label>
                        <div className="relative mt-1">
                             <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2" />
                             <input
                                id="search-term"
                                type="text"
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                                placeholder="z.B. 'projekt alpha' oder /[0-9]{3}-[A-Z]{2}/"
                                className="w-full bg-gray-700 border border-gray-600 rounded-md pl-10 pr-4 py-2 text-white focus:ring-blue-500 focus:border-blue-500"
                            />
                        </div>
                    </div>
                     <div className="flex items-center gap-4 flex-wrap">
                        <div>
                             <label htmlFor="search-type" className="text-sm font-medium text-gray-300">Suchtyp</label>
                             <select id="search-type" value={searchType} onChange={(e) => setSearchType(e.target.value as any)} className="w-full mt-1 bg-gray-700 border border-gray-600 rounded-md px-2 py-2 text-sm text-white">
                                <option value="keyword">Stichwort</option>
                                <option value="exact">Exaktes Wort</option>
                                <option value="regex">RegEx</option>
                            </select>
                        </div>
                        <div className="flex items-center pt-6">
                            <input
                                id="case-sensitive"
                                type="checkbox"
                                checked={isCaseSensitive}
                                onChange={(e) => setIsCaseSensitive(e.target.checked)}
                                className="h-4 w-4 rounded border-gray-500 bg-gray-700 text-blue-600 focus:ring-blue-600"
                            />
                            <label htmlFor="case-sensitive" className="ml-2 text-sm text-gray-300">Groß/Klein</label>
                        </div>
                    </div>
                    <div className="flex gap-2 pt-6">
                        <button onClick={handleSearch} className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded-md flex items-center gap-2">
                            <Search className="w-5 h-5"/> Suchen
                        </button>
                         <button onClick={clearSearch} className="bg-gray-600 hover:bg-gray-700 text-white font-semibold py-2 px-4 rounded-md flex items-center gap-2">
                            <X className="w-5 h-5"/> Zurücksetzen
                        </button>
                    </div>
                </div>
            </div>

            <div className="bg-gray-900 rounded-lg border border-gray-700">
                <div className="p-4 border-b border-gray-700">
                    <h3 className="text-lg font-semibold text-blue-400">Scan-Ergebnisse ({ruleHits.length})</h3>
                </div>
                <div className="max-h-[60vh] overflow-y-auto">
                    {ruleHits.length > 0 ? (
                        <table className="w-full text-sm text-left text-gray-300">
                            <thead className="text-xs text-gray-400 uppercase bg-gray-800 sticky top-0">
                                <tr>
                                    <th scope="col" className="px-6 py-3">Regel</th>
                                    <th scope="col" className="px-6 py-3">Snippet</th>
                                    <th scope="col" className="px-6 py-3">Quelldatei</th>
                                    <th scope="col" className="px-6 py-3">Message EID</th>
                                </tr>
                            </thead>
                            <tbody>
                                {ruleHits.map(hit => (
                                    <tr key={hit.id} className="bg-gray-900 border-b border-gray-800 hover:bg-gray-700/50">
                                        <td className="px-6 py-4 font-mono text-xs whitespace-pre-wrap break-all">{hit.line}</td>
                                        <td className="px-6 py-4">{hit.snippet}</td>
                                        <td className="px-6 py-4 whitespace-nowrap">{hit.source}</td>
                                        <td className="px-6 py-4 font-mono text-xs" title={hit.messageEid}>{hit.messageEid.substring(0, 12)}...</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    ) : (
                        <div className="text-center py-16 text-gray-500">
                            <Filter className="w-12 h-12 mx-auto mb-4" />
                            <p>Keine Ergebnisse gefunden.</p>
                            <p className="text-xs mt-1">Starten Sie eine Suche, um Ergebnisse anzuzeigen.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default RulePanel;
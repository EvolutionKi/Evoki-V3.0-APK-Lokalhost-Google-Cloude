import { useState } from 'react';
import TempleTab from './components/core/TempleTab';
import MetricsDashboard from './components/core/MetricsDashboard';
import DeepEarthTab from './components/core/DeepEarthTab';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('temple');

  const LAYERS = [
    "01_surface", "02_shallow", "03_sediment", "04_bedrock",
    "05_fault", "06_mantle", "07_magma", "08_trench",
    "09_pressure", "10_crystal", "11_glacier", "12_abyss"
  ];

  const renderContent = () => {
    if (activeTab === 'temple') return <TempleTab />;
    if (activeTab === 'metrics') return <MetricsDashboard />;
    if (LAYERS.includes(activeTab)) return <DeepEarthTab activeLayer={activeTab} />;
    return <div>Select a module</div>;
  };

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', background: '#000', color: '#fff' }}>
      {/* Sidebar */}
      <div style={{ width: '250px', borderRight: '1px solid #333', display: 'flex', flexDirection: 'column', background: '#0a0a0a' }}>
        <div style={{ padding: '20px', fontSize: '1.2rem', fontWeight: 'bold', borderBottom: '1px solid #333', letterSpacing: '2px' }}>
          EVOKI V3.0
        </div>

        <div style={{ flex: 1, overflowY: 'auto' }}>
          <button
            onClick={() => setActiveTab('temple')}
            style={{ width: '100%', padding: '15px', textAlign: 'left', background: activeTab === 'temple' ? '#222' : 'transparent', border: 'none', color: '#fff', cursor: 'pointer', borderLeft: activeTab === 'temple' ? '3px solid #0cf' : '3px solid transparent' }}
          >
            🏛️ TEMPLE
          </button>

          <button
            onClick={() => setActiveTab('metrics')}
            style={{ width: '100%', padding: '15px', textAlign: 'left', background: activeTab === 'metrics' ? '#222' : 'transparent', border: 'none', color: '#fff', cursor: 'pointer', borderLeft: activeTab === 'metrics' ? '3px solid #0cf' : '3px solid transparent' }}
          >
            📊 METRICS (150+)
          </button>

          <div style={{ padding: '10px', fontSize: '10px', color: '#666', marginTop: '10px' }}>DEEP EARTH LAYERS</div>

          {LAYERS.map(layer => (
            <button
              key={layer}
              onClick={() => setActiveTab(layer)}
              style={{ width: '100%', padding: '10px 15px', textAlign: 'left', background: activeTab === layer ? '#1a1a1a' : 'transparent', border: 'none', color: '#aaa', cursor: 'pointer', fontSize: '13px', borderLeft: activeTab === layer ? '3px solid #f0f' : '3px solid transparent' }}
            >
              {layer.toUpperCase()}
            </button>
          ))}
        </div>

        <div style={{ padding: '10px', borderTop: '1px solid #333', fontSize: '10px', color: '#444' }}>
          Running on Localhost<br />
          Protocol V5.0 Enforced
        </div>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, overflow: 'hidden' }}>
        {renderContent()}
      </div>
    </div>
  );
}

export default App;

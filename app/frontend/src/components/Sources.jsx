import React, { useState, useEffect } from 'react';
import api from '../api/api';

function Sources() {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    try {
      const data = await api.getSources();
      setSources(data.sources || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const filteredSources = filter === 'all' 
    ? sources 
    : sources.filter(s => s.tier === parseInt(filter));

  const getBiasColor = (bias) => {
    const colors = {
      'left': 'bg-blue-500',
      'left-center': 'bg-blue-400',
      'center': 'bg-green-500',
      'right-center': 'bg-orange-400',
      'right': 'bg-orange-500',
    };
    return colors[bias?.toLowerCase()] || 'bg-gray-500';
  };

  const tierColors = {
    1: { border: 'border-l-green-500', badge: 'bg-green-500' },
    2: { border: 'border-l-blue-500', badge: 'bg-blue-500' },
    3: { border: 'border-l-orange-500', badge: 'bg-orange-500' },
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-gray-400">
        <div className="w-12 h-12 border-4 border-rose-500/20 border-t-rose-500 rounded-full animate-spin mb-4" />
        <p>Loading sources...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] text-gray-400">
        <p className="mb-4">⚠️ Error loading sources: {error}</p>
        <button 
          onClick={fetchSources}
          className="bg-rose-500 text-white px-4 py-2 rounded-lg hover:bg-rose-600 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">📚 Trusted Sources</h1>
        <p className="text-gray-400">Our fact-checking system uses these verified sources for cross-referencing.</p>
      </div>

      {/* Filters */}
      <div className="flex justify-center gap-2 mb-8">
        {['all', '1', '2', '3'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-5 py-2.5 rounded-full border transition-all duration-300
              ${filter === f 
                ? 'bg-rose-500 border-rose-500 text-white' 
                : 'bg-transparent border-white/20 text-gray-400 hover:border-rose-500 hover:text-rose-500'
              }`}
          >
            {f === 'all' ? `All (${sources.length})` : `Tier ${f}`}
          </button>
        ))}
      </div>

      {/* Sources Grid */}
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
        {filteredSources.map((source, index) => (
          <div 
            key={index} 
            className={`bg-slate-900/80 rounded-xl p-6 border-l-4 transition-transform duration-300 hover:-translate-y-1 ${tierColors[source.tier]?.border || 'border-l-gray-500'}`}
          >
            <div className="flex justify-between items-start mb-2">
              <h3 className="text-white font-semibold">{source.name}</h3>
              <span className={`px-2.5 py-1 rounded-full text-xs font-bold text-white ${tierColors[source.tier]?.badge || 'bg-gray-500'}`}>
                Tier {source.tier}
              </span>
            </div>
            <div className="text-gray-400 text-sm mb-4">{source.domain}</div>
            
            <div className="space-y-3">
              {/* Credibility */}
              <div className="flex items-center gap-3">
                <span className="text-gray-400 text-sm min-w-[80px]">Credibility</span>
                <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-rose-500 to-green-500 rounded-full"
                    style={{ width: `${source.credibility * 100}%` }}
                  />
                </div>
                <span className="text-white text-sm min-w-[40px]">{Math.round(source.credibility * 100)}%</span>
              </div>
              
              {/* Bias */}
              <div className="flex items-center gap-3">
                <span className="text-gray-400 text-sm min-w-[80px]">Bias</span>
                <span className={`px-2.5 py-1 rounded-full text-xs text-white capitalize ${getBiasColor(source.bias)}`}>
                  {source.bias || 'Unknown'}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Legend */}
      <div className="bg-slate-900/80 p-8 rounded-xl">
        <h3 className="text-white font-semibold text-center mb-6">Tier Explanation</h3>
        <div className="grid md:grid-cols-3 gap-4">
          {[
            { tier: 1, color: 'bg-green-500', desc: 'Highest credibility sources with strong fact-checking standards' },
            { tier: 2, color: 'bg-blue-500', desc: 'Reliable sources with good journalistic practices' },
            { tier: 3, color: 'bg-orange-500', desc: 'Sources with mixed reliability, used with caution' },
          ].map((item) => (
            <div key={item.tier} className="flex items-start gap-3">
              <span className={`px-3 py-1 rounded-full text-sm font-bold text-white whitespace-nowrap ${item.color}`}>
                Tier {item.tier}
              </span>
              <p className="text-gray-400 text-sm">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Sources;
import React, { useState, useEffect } from 'react';
import api from '../api/api';
import sourcesPattern from '../assets/sources-pattern.png';

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

  const getBadge = (tier) => {
    if (tier === 1) return { label: 'Trusted', className: 'bg-emerald-100 text-emerald-800' };
    if (tier === 2) return { label: 'Neutral', className: 'bg-slate-200 text-slate-800' };
    return { label: 'Flagged', className: 'bg-red-100 text-red-800' };
  };

  const getFavicon = (domain) => `https://www.google.com/s2/favicons?sz=64&domain=${domain || 'news'}`;

  if (loading) {
    return (
      <section className="section bg-[#f9f5f0]" data-aos="fade-up">
        <div className="section-inner flex min-h-[260px] flex-col items-center justify-center text-slate-700">
          <div className="mb-4 h-12 w-12 animate-spin rounded-full border-4 border-[#e8490f]/20 border-t-[#e8490f]" />
          <p className="text-[1.125rem]">Loading sources...</p>
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className="section bg-[#f9f5f0]" data-aos="fade-up">
        <div className="section-inner flex min-h-[260px] flex-col items-center justify-center text-slate-700">
          <p className="mb-5 text-[1.125rem]">Error loading sources: {error}</p>
        <button 
          onClick={fetchSources}
          className="btn-pill"
        >
          Retry
        </button>
        </div>
      </section>
    );
  }

  return (
    <section
      className="section bg-[#f9f5f0]"
      data-aos="fade-up"
      style={{
        backgroundImage: `linear-gradient(rgba(249,245,240,0.95), rgba(249,245,240,0.95)), url(${sourcesPattern})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed',
      }}
    >
      <div className="section-inner">
        <h1 className="section-title section-title-dark">Cross-Referenced Sources</h1>
        <div className="orange-underline" />
        <p className="mb-8 max-w-[900px] text-[1.125rem] text-slate-700">
          Browse the source index used in analysis. Sources are grouped by trust tier and presented with key credibility metadata.
        </p>

        <div className="mb-8 flex flex-wrap gap-2">
          {['all', '1', '2', '3'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`rounded-full border px-5 py-3 text-base font-semibold transition-all
                ${filter === f
                  ? 'border-[#e8490f] bg-[#e8490f] text-white shadow-[0_8px_24px_rgba(232,73,15,0.28)]'
                  : 'border-slate-300 bg-white text-slate-700 hover:border-[#e8490f] hover:text-[#e8490f]'
                }`}
            >
              {f === 'all' ? `All (${sources.length})` : `Tier ${f}`}
            </button>
          ))}
        </div>

        <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
          {filteredSources.map((source, index) => {
            const badge = getBadge(source.tier);
            return (
              <article key={`${source.name}-${index}`} className="rounded-2xl border-l-[6px] border-[#ff5722] bg-white p-6 shadow-[0_10px_28px_rgba(0,0,0,0.09)]">
                <div className="flex items-start gap-4">
                  <img src={getFavicon(source.domain)} alt={`${source.name} logo`} className="h-12 w-12 rounded-full border border-slate-200" />
                  <div className="flex-1">
                    <div className="mb-2 flex flex-wrap items-center justify-between gap-3">
                      <h3 className="m-0 text-[1.25rem] font-bold text-[#121421]">{source.name}</h3>
                      <span className={`rounded-full px-3 py-1 text-sm font-semibold ${badge.className}`}>{badge.label}</span>
                    </div>
                    <p className="mb-3 text-base text-slate-600">
                      Matched claim snippet: Coverage from {source.domain} is indexed for corroboration and contradiction checks.
                    </p>
                    <div className="mb-3 text-base text-slate-600">
                      Credibility: <strong>{Math.round((source.credibility || 0) * 100)}%</strong> | Bias: {source.bias || 'Unknown'}
                    </div>
                    <a
                      href={`https://${source.domain}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-base font-semibold text-[#e8490f] no-underline hover:text-[#ff5722]"
                    >
                      View Article -&gt;
                    </a>
                  </div>
                </div>
              </article>
            );
          })}
        </div>

        {filteredSources.length === 0 && (
          <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center text-[1.125rem] text-slate-600">
            No sources found for this tier.
          </div>
        )}
      </div>
    </section>
  );
}

export default Sources;
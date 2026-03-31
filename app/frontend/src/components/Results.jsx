import React from 'react';
import sourcesPattern from '../assets/sources-pattern.png';

function Results({ result, onBack }) {
  if (!result) {
    return (
      <section className="section" data-aos="fade-up">
        <div className="section-inner text-center">
          <p className="mb-6 text-[1.125rem] text-white/75">No results available. Please analyze content first.</p>
          <button onClick={onBack} className="btn-outline">
            Go Back
          </button>
        </div>
      </section>
    );
  }

  const confidence = Math.max(0, Math.min(100, Math.round((result.final_score || 0) * 100)));
  const matched = result.matching_sources?.length || 0;
  const contradicted = result.contradicting_sources?.length || 0;
  const checked = result.sources_checked ?? (matched + contradicted);

  const deriveVerdict = () => {
    const raw = (result.verdict || '').toUpperCase();
    const noSources = checked === 0 || matched === 0;

    if (noSources) {
      return { label: 'UNVERIFIED', cardClass: 'bg-gray-500/15 border-gray-400 text-gray-100' };
    }
    if (raw.includes('FALSE') || confidence < 35) {
      return { label: 'FAKE', cardClass: 'bg-red-500/15 border-red-400 text-red-100' };
    }
    if (raw.includes('TRUE') || confidence >= 70) {
      return { label: 'CREDIBLE', cardClass: 'bg-green-500/15 border-green-400 text-green-100' };
    }
    return { label: 'QUESTIONABLE', cardClass: 'bg-amber-500/15 border-amber-400 text-amber-100' };
  };

  const buildSummary = () => {
    const redFlags = result.red_flags?.slice(0, 2).join('; ');
    const greenFlags = result.green_flags?.slice(0, 2).join('; ');

    if (checked === 0 || matched === 0) {
      return 'We could not find any sources to verify this claim.';
    }

    const parts = [
      `We compared this claim against ${checked} tracked sources and found ${matched} supporting references with ${contradicted} contradictory references.`,
    ];
    if (greenFlags) parts.push(`Positive indicators include: ${greenFlags}.`);
    if (redFlags) parts.push(`Risk indicators include: ${redFlags}.`);
    return parts.join(' ');
  };

  const verdict = deriveVerdict();
  const ringStyle = {
    background: `conic-gradient(#ff5722 ${confidence * 3.6}deg, rgba(255,255,255,0.12) 0deg)`,
  };

  const sourceCards = [
    ...(result.matching_sources || []).map((source) => ({
      ...source,
      credibilityBadge: 'Trusted',
      badgeClass: 'bg-emerald-100 text-emerald-800',
    })),
    ...(result.contradicting_sources || []).map((source) => ({
      ...source,
      credibilityBadge: 'Flagged',
      badgeClass: 'bg-red-100 text-red-800',
    })),
  ];

  const getFavicon = (url) => {
    if (!url) return 'https://www.google.com/s2/favicons?sz=64&domain=news';
    try {
      const parsed = new URL(url);
      return `https://www.google.com/s2/favicons?sz=64&domain=${parsed.hostname}`;
    } catch {
      return 'https://www.google.com/s2/favicons?sz=64&domain=news';
    }
  };

  const getSnippet = (source) => {
    if (source.snippet) return source.snippet;
    if (source.title) return source.title;
    return 'Relevant reporting found for this claim.';
  };

  return (
    <>
      <section className="section bg-[#0d0d1a]" data-aos="fade-up">
        <div className="section-inner">
          <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <h1 className="section-title m-0">Analysis Results</h1>
            <button onClick={onBack} className="btn-outline">
              Analyze Another
            </button>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.1fr_0.9fr]">
            <article className={`rounded-3xl border p-8 ${verdict.cardClass}`}>
              <h2 className="mb-3 text-[1.5rem] font-bold tracking-wide">Verdict</h2>
              <div className="mb-5 text-[clamp(2rem,6vw,2.8rem)] font-extrabold leading-none">{verdict.label}</div>
              <p className="m-0 text-[1.125rem] text-white/90">
                Processed in {result.processing_time_s || 0}s with {checked || 0} sources checked.
              </p>
            </article>

            <article className="rounded-3xl border border-white/15 bg-white/5 p-8 text-white">
              <h2 className="mb-6 text-[1.5rem] font-bold">Credibility Score</h2>
              <div className="mx-auto grid h-[170px] w-[170px] place-items-center rounded-full p-3" style={ringStyle}>
                <div className="grid h-full w-full place-items-center rounded-full bg-[#0d0d1a] text-[2.625rem] font-extrabold text-white">
                  {confidence}%
                </div>
              </div>
            </article>
          </div>

          <article className="mt-6 rounded-2xl border-l-[6px] border-[#ff5722] bg-white p-7 text-[#111426] shadow-[0_16px_45px_rgba(0,0,0,0.22)]">
            <h3 className="mb-3 text-[1.5rem] font-bold">Why we think this:</h3>
            <p className="m-0 text-[1.125rem] leading-relaxed">{buildSummary()}</p>
          </article>
        </div>
      </section>

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
          <h2 className="section-title section-title-dark">Cross-Referenced Sources</h2>
          <div className="orange-underline" />
          <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
            {sourceCards.map((source, index) => (
              <article
                key={`${source.source || source.title || 'source'}-${index}`}
                className="rounded-2xl border-l-[6px] border-[#ff5722] bg-white p-6 shadow-[0_10px_28px_rgba(0,0,0,0.09)]"
              >
                <div className="flex items-start gap-4">
                  <img src={getFavicon(source.url)} alt="source logo" className="h-12 w-12 rounded-full border border-slate-200" />
                  <div className="flex-1">
                    <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
                      <h3 className="m-0 text-[1.25rem] font-bold text-[#121421]">{source.source || 'News Source'}</h3>
                      <span className={`rounded-full px-3 py-1 text-sm font-semibold ${source.badgeClass}`}>
                        {source.credibilityBadge}
                      </span>
                    </div>
                    <p className="mb-3 text-base text-slate-600">{getSnippet(source)}</p>
                    {source.url ? (
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-base font-semibold text-[#e8490f] no-underline hover:text-[#ff5722]"
                      >
                        View Article -&gt;
                      </a>
                    ) : (
                      <span className="text-base font-semibold text-[#e8490f]">No external link available</span>
                    )}
                  </div>
                </div>
              </article>
            ))}
          </div>
          {sourceCards.length === 0 && (
            <div className="rounded-2xl border border-slate-200 bg-white p-8 text-center text-[1.125rem] text-slate-600">
              No cross-referenced sources found for this analysis.
            </div>
          )}
        </div>
      </section>
    </>
  );
}

export default Results;

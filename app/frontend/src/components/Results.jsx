import React from 'react';

function Results({ result, onBack }) {
  if (!result) {
    return (
      <div className="max-w-4xl mx-auto px-8 text-center py-16">
        <p className="text-gray-400 mb-4">No results available. Please analyze content first.</p>
        <button 
          onClick={onBack}
          className="bg-transparent text-rose-500 border border-rose-500 px-5 py-2.5 rounded-lg cursor-pointer transition-all hover:bg-rose-500/10"
        >
          Go Back
        </button>
      </div>
    );
  }

  const getVerdictStyle = (verdict) => {
    const styles = {
      'LIKELY TRUE':   { bg: 'bg-green-500/20', border: 'border-green-500', text: 'text-green-400' },
      'MOSTLY TRUE':   { bg: 'bg-green-500/10', border: 'border-green-400', text: 'text-green-300' },
      'UNCERTAIN':     { bg: 'bg-yellow-500/20', border: 'border-yellow-500', text: 'text-yellow-400' },
      'MOSTLY FALSE':  { bg: 'bg-orange-500/20', border: 'border-orange-500', text: 'text-orange-400' },
      'LIKELY FALSE':  { bg: 'bg-red-500/20', border: 'border-red-500', text: 'text-red-400' },
    };
    return styles[verdict] || styles['UNCERTAIN'];
  };

  const getScoreColor = (score) => {
    if (score >= 0.7) return 'bg-green-500';
    if (score >= 0.5) return 'bg-yellow-500';
    if (score >= 0.3) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const verdictStyle = getVerdictStyle(result.verdict);
  const finalScore = result.final_score || 0;

  return (
    <div className="max-w-5xl mx-auto px-8 pb-12">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-white">📊 Analysis Results</h1>
        <button 
          onClick={onBack}
          className="bg-transparent text-rose-500 border border-rose-500 px-5 py-2.5 rounded-lg cursor-pointer transition-all hover:bg-rose-500/10"
        >
          ← Analyze Another
        </button>
      </div>

      {/* Main Verdict */}
      <div className={`text-center p-8 rounded-2xl border-2 mb-8 ${verdictStyle.bg} ${verdictStyle.border}`}>
        <div className="text-6xl mb-4">
          {result.verdict === 'LIKELY TRUE' && '✅'}
          {result.verdict === 'MOSTLY TRUE' && '👍'}
          {result.verdict === 'UNCERTAIN' && '❓'}
          {result.verdict === 'MOSTLY FALSE' && '⚠️'}
          {result.verdict === 'LIKELY FALSE' && '❌'}
        </div>
        <h2 className={`text-4xl font-bold mb-2 ${verdictStyle.text}`}>
          {result.verdict}
        </h2>
        <p className="text-white text-2xl">
          Credibility Score: <span className="font-bold">{(finalScore * 100).toFixed(1)}%</span>
        </p>
        <p className="text-gray-400 mt-2">
          Processed in {result.processing_time_s}s • {result.sources_checked} sources checked
        </p>
      </div>

      {/* Score Breakdown */}
      <div className="mb-8">
        <h2 className="text-xl font-semibold text-white mb-4">📈 Score Breakdown</h2>
        <div className="bg-slate-900/80 p-6 rounded-xl border border-white/10">
          {result.score_breakdown?.map((item, index) => (
            <div key={index} className="mb-4 last:mb-0">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-gray-300">{item.factor}</span>
                <span className="text-white font-medium">
                  {(item.score * 100).toFixed(0)}% (weight: {(item.weight * 100).toFixed(0)}%)
                </span>
              </div>
              <div className="h-3 bg-white/10 rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all duration-500 ${getScoreColor(item.score)}`}
                  style={{ width: `${item.score * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Flags Section */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        {/* Red Flags */}
        {result.red_flags?.length > 0 && (
          <div className="bg-red-500/10 border border-red-500/30 p-6 rounded-xl">
            <h3 className="text-lg font-semibold text-red-400 mb-3">🚩 Red Flags</h3>
            <ul className="space-y-2">
              {result.red_flags.map((flag, index) => (
                <li key={index} className="text-red-300 flex items-start gap-2">
                  <span>•</span>
                  <span>{flag}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Green Flags */}
        {result.green_flags?.length > 0 && (
          <div className="bg-green-500/10 border border-green-500/30 p-6 rounded-xl">
            <h3 className="text-lg font-semibold text-green-400 mb-3">✅ Green Flags</h3>
            <ul className="space-y-2">
              {result.green_flags.map((flag, index) => (
                <li key={index} className="text-green-300 flex items-start gap-2">
                  <span>•</span>
                  <span>{flag}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Matching Sources */}
      {result.matching_sources?.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">
            ✓ Matching Sources ({result.matching_sources.length})
            {result.nepal_sources_count > 0 && (
              <span className="text-sm font-normal text-gray-400 ml-2">
                ({result.nepal_sources_count} from Nepal)
              </span>
            )}
          </h2>
          <div className="space-y-3">
            {result.matching_sources.map((source, index) => (
              <div key={index} className="bg-slate-900/80 p-4 rounded-xl border border-white/10 hover:border-green-500/30 transition-colors">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h4 className="text-white font-medium mb-1">{source.title}</h4>
                    <div className="flex flex-wrap gap-2 text-sm">
                      <span className="text-gray-400">{source.source}</span>
                      <span className="text-gray-600">•</span>
                      <span className={`px-2 py-0.5 rounded text-xs font-medium
                        ${source.tier === 1 ? 'bg-green-500/20 text-green-400' : 
                          source.tier === 2 ? 'bg-blue-500/20 text-blue-400' : 
                          'bg-orange-500/20 text-orange-400'}`}
                      >
                        Tier {source.tier}
                      </span>
                      <span className="text-gray-600">•</span>
                      <span className="text-gray-400">
                        {(source.similarity * 100).toFixed(0)}% match
                      </span>
                    </div>
                  </div>
                  {source.url && (
                    <a 
                      href={source.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-rose-500 hover:text-rose-400 text-sm whitespace-nowrap"
                    >
                      View →
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Contradicting Sources */}
      {result.contradicting_sources?.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">
            ⚠️ Contradicting Sources ({result.contradicting_sources.length})
          </h2>
          <div className="space-y-3">
            {result.contradicting_sources.map((source, index) => (
              <div key={index} className="bg-red-500/5 p-4 rounded-xl border border-red-500/20">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <h4 className="text-white font-medium mb-1">{source.title}</h4>
                    <div className="flex flex-wrap gap-2 text-sm">
                      <span className="text-gray-400">{source.source}</span>
                      <span className="text-gray-600">•</span>
                      <span className="text-red-400">
                        {(source.credibility * 100).toFixed(0)}% credibility
                      </span>
                    </div>
                  </div>
                  {source.url && (
                    <a 
                      href={source.url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-rose-500 hover:text-rose-400 text-sm whitespace-nowrap"
                    >
                      View →
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Extracted Entities */}
      {(result.extracted_entities?.people_and_orgs?.length > 0 || result.extracted_entities?.locations?.length > 0) && (
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-white mb-4">🔍 Extracted Entities</h2>
          <div className="bg-slate-900/80 p-6 rounded-xl border border-white/10">
            {result.extracted_entities.people_and_orgs?.length > 0 && (
              <div className="mb-4">
                <h4 className="text-gray-400 text-sm mb-2">People & Organizations</h4>
                <div className="flex flex-wrap gap-2">
                  {result.extracted_entities.people_and_orgs.map((entity, index) => (
                    <span key={index} className="bg-blue-500/20 text-blue-300 px-3 py-1 rounded-full text-sm">
                      {entity}
                    </span>
                  ))}
                </div>
              </div>
            )}
            {result.extracted_entities.locations?.length > 0 && (
              <div>
                <h4 className="text-gray-400 text-sm mb-2">Locations</h4>
                <div className="flex flex-wrap gap-2">
                  {result.extracted_entities.locations.map((location, index) => (
                    <span key={index} className="bg-purple-500/20 text-purple-300 px-3 py-1 rounded-full text-sm">
                      📍 {location}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Raw Data */}
      <div className="mt-8">
        <details className="group">
          <summary className="text-gray-400 cursor-pointer p-4 bg-slate-900/80 rounded-lg hover:text-white transition-colors">
            View Raw API Response
          </summary>
          <pre className="bg-black/30 p-4 rounded-lg text-gray-400 overflow-x-auto text-sm mt-2 max-h-96">
            {JSON.stringify(result, null, 2)}
          </pre>
        </details>
      </div>
    </div>
  );
}

export default Results;
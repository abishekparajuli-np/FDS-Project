import React, { useState } from 'react';
import api from '../api/api';
import analyzerBg from '../assets/analyzer-bg.jpg';

function Analyze({ onAnalysisComplete }) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!title.trim() && !content.trim()) {
      setError('Please provide a title or article content to analyze.');
      return;
    }

    setLoading(true);
    try {
      const result = await api.analyze(title, content);
      onAnalysisComplete(result);
    } catch (err) {
      setError(err.message || 'An error occurred during analysis.');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setTitle('');
    setContent('');
    setError(null);
  };

  return (
    <section
      className="section"
      data-aos="fade-up"
      style={{
        backgroundImage: `linear-gradient(rgba(13,13,26,0.85), rgba(13,13,26,0.92)), url(${analyzerBg})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundAttachment: 'fixed',
      }}
    >
      <div className="section-inner max-w-[920px]">
        <h1 className="section-title">Analyze a News Article</h1>
        <div className="orange-underline" />
        <p className="section-subtitle mb-10">
          Submit article content to verify claims against trusted sources and receive an instant verdict.
        </p>

        <form onSubmit={handleSubmit} className="glass-card border-white/10 bg-[#121226]/85 p-6 md:p-10">
          <div className="mb-7">
            <label htmlFor="title" className="mb-2 block text-[1.1rem] font-semibold text-white">
              Article Title
            </label>
            <input
              type="text"
              id="title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Enter the headline or claim title..."
              maxLength={300}
              disabled={loading}
              className="w-full rounded-2xl border border-white/20 bg-black/30 p-4 text-[1.0625rem] text-white outline-none transition-all duration-300 placeholder:text-white/45 focus:border-[#ff5722] focus:ring-2 focus:ring-[#ff5722]/30"
            />
          </div>

          <div className="mb-7">
            <label htmlFor="content" className="mb-2 block text-[1.15rem] font-semibold text-white">
              Article Content
            </label>
            <textarea
              id="content"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Paste the news article or claim you want to verify..."
              rows={10}
              maxLength={10000}
              disabled={loading}
              className="min-h-[200px] w-full resize-y rounded-2xl border border-white/20 bg-black/30 p-5 text-[1.0625rem] text-white outline-none transition-all duration-300 placeholder:text-white/45 focus:border-[#ff5722] focus:ring-2 focus:ring-[#ff5722]/30"
            />
            <div className="mt-2 text-right text-base text-white/60">{content.length}/10000</div>
          </div>

          {error && (
            <div className="mb-7 rounded-2xl border border-red-400/70 bg-red-500/15 px-4 py-4 text-[1.0625rem] text-red-200">
              {error}
            </div>
          )}

          <div className="flex flex-col gap-4 sm:flex-row sm:justify-end">
            <button
              type="button"
              onClick={handleClear}
              disabled={loading}
              className="btn-outline border-white/45"
            >
              Clear
            </button>
            <button type="submit" disabled={loading} className="btn-pill">
              {loading ? 'Analyzing...' : 'Analyze Now'}
            </button>
          </div>
        </form>
      </div>
    </section>
  );
}

export default Analyze;
import React, { useState } from 'react';
import api from '../api/api';

function Analyze({ onAnalysisComplete }) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!title.trim() && !content.trim()) {
      setError('Please provide at least a title or content to analyze.');
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
    <div className="max-w-3xl mx-auto px-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">🔍 Content Analysis</h1>
        <p className="text-gray-400">Enter the title and/or content of the article you want to fact-check.</p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="bg-slate-900/80 p-8 rounded-xl border border-rose-500/20">
        {/* Title Input */}
        <div className="mb-6">
          <label htmlFor="title" className="block text-white font-medium mb-2">
            Article Title
          </label>
          <input
            type="text"
            id="title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter the article title..."
            disabled={loading}
            className="w-full p-4 bg-black/30 border border-white/10 rounded-lg text-white text-base transition-all duration-300 focus:outline-none focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20 disabled:opacity-50 placeholder-gray-500"
          />
        </div>

        {/* Content Textarea */}
        <div className="mb-6">
          <label htmlFor="content" className="flex justify-between items-center text-white font-medium mb-2">
            Article Content
            <span className="text-sm text-gray-400 font-normal">{content.length}/10000</span>
          </label>
          <textarea
            id="content"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Paste the article content here..."
            rows={12}
            maxLength={10000}
            disabled={loading}
            className="w-full p-4 bg-black/30 border border-white/10 rounded-lg text-white text-base transition-all duration-300 focus:outline-none focus:border-rose-500 focus:ring-2 focus:ring-rose-500/20 disabled:opacity-50 resize-y min-h-[200px] placeholder-gray-500"
          />
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-500/10 border border-red-500 text-red-500 p-4 rounded-lg mb-6 flex items-center gap-2">
            <span>⚠️</span> {error}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-4 justify-end">
          <button 
            type="button" 
            onClick={handleClear} 
            disabled={loading}
            className="bg-transparent text-gray-400 border border-gray-400 px-6 py-3 rounded-lg cursor-pointer transition-all duration-300 hover:text-white hover:border-white disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Clear
          </button>
          <button 
            type="submit" 
            disabled={loading}
            className="bg-rose-500 text-white px-8 py-3 rounded-lg text-base cursor-pointer flex items-center gap-2 transition-all duration-300 hover:bg-rose-600 disabled:opacity-60 disabled:cursor-not-allowed border-none"
          >
            {loading ? (
              <>
                <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Analyzing...
              </>
            ) : (
              'Analyze Content'
            )}
          </button>
        </div>
      </form>

      {/* Info Section */}
      <div className="mt-8 p-6 bg-green-500/10 border border-green-500/30 rounded-xl">
        <h3 className="text-green-500 font-semibold mb-4">How it works:</h3>
        <ol className="text-gray-400 pl-6 list-decimal space-y-2">
          <li>Enter the article title and/or content</li>
          <li>Our AI cross-references with trusted sources</li>
          <li>Get a detailed credibility analysis</li>
        </ol>
      </div>
    </div>
  );
}

export default Analyze;
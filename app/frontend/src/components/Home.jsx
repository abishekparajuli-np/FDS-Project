import React from 'react';

function Home({ onNavigate }) {
  const features = [
    {
      icon: '🔍',
      title: 'Cross-Reference Check',
      description: 'Compare content against multiple trusted news sources to verify accuracy.',
    },
    {
      icon: '🤖',
      title: 'AI-Powered Analysis',
      description: 'Advanced machine learning models detect patterns of misinformation.',
    },
    {
      icon: '📊',
      title: 'Credibility Scoring',
      description: 'Get detailed credibility scores with source breakdowns.',
    },
    {
      icon: '📈',
      title: 'Model Evaluation',
      description: 'Transparent model performance metrics and evaluation results.',
    },
  ];

  return (
    <div className="max-w-6xl mx-auto px-8">
      {/* Hero Section */}
      <div className="text-center py-16 px-8 bg-gradient-to-br from-rose-500/10 to-slate-800/50 rounded-2xl mb-12">
        <h1 className="text-5xl font-bold text-white mb-2">Welcome to NirikshanAI</h1>
        <p className="text-xl text-rose-500 mb-6">Intelligent Fact-Checking & Cross-Reference Analysis</p>
        <p className="max-w-2xl mx-auto text-gray-400 leading-relaxed mb-8">
          NirikshanAI is an advanced fact-checking system that analyzes news articles 
          and content against trusted sources to determine credibility and detect misinformation.
        </p>
        <div className="flex gap-4 justify-center">
          <button 
            onClick={() => onNavigate('analyze')}
            className="bg-rose-500 text-white px-8 py-4 text-lg rounded-lg border-none cursor-pointer transition-all duration-300 hover:bg-rose-600 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-rose-500/40"
          >
            Start Analysis
          </button>
          <button 
            onClick={() => onNavigate('sources')}
            className="bg-transparent text-rose-500 border-2 border-rose-500 px-8 py-4 text-lg rounded-lg cursor-pointer transition-all duration-300 hover:bg-rose-500/10"
          >
            View Sources
          </button>
        </div>
      </div>

      {/* Features Section */}
      <div>
        <h2 className="text-center text-3xl font-bold text-white mb-8">Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => (
            <div 
              key={index}
              className="bg-slate-900/80 p-8 rounded-xl text-center border border-rose-500/20 transition-all duration-300 hover:-translate-y-1 hover:border-rose-500 hover:shadow-lg hover:shadow-rose-500/20"
            >
              <span className="text-5xl block mb-4">{feature.icon}</span>
              <h3 className="text-white text-lg font-semibold mb-2">{feature.title}</h3>
              <p className="text-gray-400 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Home;
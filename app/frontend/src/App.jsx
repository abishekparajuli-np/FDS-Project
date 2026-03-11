import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Home from './components/Home';
import Analyze from './components/Analyze';
import Sources from './components/Sources';
import Results from './components/Results';
import ModelEvaluation from './components/ModelEvaluation';
import api from './api/api';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isHealthy, setIsHealthy] = useState(null);

  useEffect(() => {
    api.checkHealth()
      .then(() => setIsHealthy(true))
      .catch(() => setIsHealthy(false));
  }, []);

  const handleAnalysisComplete = (result) => {
    setAnalysisResult(result);
    setCurrentPage('results');
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <Home onNavigate={setCurrentPage} />;
      case 'analyze':
        return <Analyze onAnalysisComplete={handleAnalysisComplete} />;
      case 'results':
        return <Results result={analysisResult} onBack={() => setCurrentPage('analyze')} />;
      case 'sources':
        return <Sources />;
      case 'evaluation':
        return <ModelEvaluation />;
      default:
        return <Home onNavigate={setCurrentPage} />;
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Navbar currentPage={currentPage} onNavigate={setCurrentPage} isHealthy={isHealthy} />
      <main className="flex-1 pt-4">
        {renderPage()}
      </main>
      <footer className="text-center py-8 bg-black/30 text-gray-400 mt-auto">
        <p className="text-sm">NirikshanAI - Foundation of Data Science Project</p>
      </footer>
    </div>
  );
}

export default App;
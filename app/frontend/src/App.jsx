import React, { useEffect, useState } from 'react';
import AOS from 'aos';
import 'aos/dist/aos.css';
import Navbar from './components/Navbar';
import Home from './components/Home';
import Analyze from './components/Analyze';
import Sources from './components/Sources';
import Results from './components/Results';
import api from './api/api';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isHealthy, setIsHealthy] = useState(null);

  useEffect(() => {
    AOS.init({
      duration: 700,
      easing: 'ease-out-cubic',
      once: true,
      offset: 80,
    });
  }, []);

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
      default:
        return <Home onNavigate={setCurrentPage} />;
    }
  };

  return (
    <div className="app-shell">
      <Navbar currentPage={currentPage} onNavigate={setCurrentPage} isHealthy={isHealthy} />
      <main className="app-main">
        {renderPage()}
      </main>
      <footer className="app-footer" data-aos="fade-up">
        <div className="footer-accent" />
        <div className="footer-content">
          <div>
            <h2 className="footer-logo">Nirikshyak AI</h2>
            <p className="footer-tagline">Fact-check news with trusted source references.</p>
          </div>
          <div className="footer-links">
            <button type="button" onClick={() => setCurrentPage('home')}>Home</button>
            <button type="button" onClick={() => setCurrentPage('analyze')}>Analyze</button>
            <button type="button" onClick={() => setCurrentPage('sources')}>Sources</button>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
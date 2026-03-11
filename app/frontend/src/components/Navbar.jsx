import React from 'react';

function Navbar({ currentPage, onNavigate, isHealthy }) {
  const navItems = [
    { key: 'home', label: 'Home' },
    { key: 'analyze', label: 'Analyze' },
    { key: 'sources', label: 'Sources' },
    { key: 'evaluation', label: 'Model Evaluation' },
  ];

  return (
    <nav className="flex justify-between items-center px-8 py-4 bg-gradient-to-r from-slate-900 to-slate-800 shadow-lg sticky top-0 z-50">
      {/* Brand */}
      <div 
        className="flex items-center gap-2 cursor-pointer" 
        onClick={() => onNavigate('home')}
      >
        <span className="text-3xl">🔍</span>
        <h1 className="text-rose-500 text-2xl font-bold m-0">NirikshanAI</h1>
      </div>

      {/* Menu */}
      <ul className="flex list-none gap-2 m-0 p-0">
        {navItems.map((item) => (
          <li key={item.key}>
            <button
              className={`px-5 py-2.5 rounded-lg text-base transition-all duration-300 border-none cursor-pointer
                ${currentPage === item.key 
                  ? 'bg-rose-500 text-white' 
                  : 'bg-transparent text-gray-400 hover:text-white hover:bg-rose-500/20'
                }`}
              onClick={() => onNavigate(item.key)}
            >
              {item.label}
            </button>
          </li>
        ))}
      </ul>

      {/* Status Indicator */}
      <div className="flex items-center gap-2">
        <span 
          className={`w-2.5 h-2.5 rounded-full
            ${isHealthy === true ? 'bg-green-500 shadow-[0_0_8px_#4caf50]' : ''}
            ${isHealthy === false ? 'bg-red-500 shadow-[0_0_8px_#f44336]' : ''}
            ${isHealthy === null ? 'bg-orange-500 animate-pulse-glow' : ''}
          `}
        />
        <span className="text-gray-400 text-sm">
          {isHealthy === true && 'API Connected'}
          {isHealthy === false && 'API Offline'}
          {isHealthy === null && 'Checking...'}
        </span>
      </div>
    </nav>
  );
}

export default Navbar;
import React from 'react';

function Navbar({ currentPage, onNavigate, isHealthy }) {
  const navItems = [
    { key: 'home', label: 'Home' },
    { key: 'analyze', label: 'Analyze' },
    { key: 'sources', label: 'Sources' },
  ];

  return (
    <nav className="sticky top-0 z-50 border-b border-white/10 bg-[#0d0d1a]/95 backdrop-blur">
      <div className="mx-auto flex w-full max-w-[1200px] items-center justify-between px-4 py-4 md:px-6">
        <div
          className="flex items-center gap-2 cursor-pointer"
          onClick={() => onNavigate('home')}
        >
          <h1 className="m-0 text-2xl font-extrabold text-white">Nirikshyak AI</h1>
        </div>

        <ul className="m-0 hidden list-none gap-2 p-0 md:flex">
          {navItems.map((item) => (
            <li key={item.key}>
              <button
                className={`cursor-pointer rounded-full border-none px-6 py-3 text-base font-semibold transition-all duration-300
                ${currentPage === item.key
                  ? 'bg-[#ff5722] text-white shadow-[0_10px_24px_rgba(255,87,34,0.35)]'
                  : 'bg-transparent text-white/80 hover:bg-white/10 hover:text-white'
                }`}
                onClick={() => onNavigate(item.key)}
              >
                {item.label}
              </button>
            </li>
          ))}
        </ul>

        <div className="flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-3 py-2">
          <span
            className={`w-2.5 h-2.5 rounded-full
            ${isHealthy === true ? 'bg-green-500 shadow-[0_0_8px_#4caf50]' : ''}
            ${isHealthy === false ? 'bg-red-500 shadow-[0_0_8px_#f44336]' : ''}
            ${isHealthy === null ? 'bg-[#ff5722] animate-pulse-glow' : ''}
          `}
          />

          <span className="text-sm text-white/80">
            {isHealthy === true && 'API Connected'}
            {isHealthy === false && 'API Offline'}
            {isHealthy === null && 'Checking...'}
          </span>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
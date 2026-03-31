import React from 'react';
import heroNewsroom from '../assets/hero-newsroom.jpg';

function Home({ onNavigate }) {
  return (
    <section
      className="section min-h-[calc(100vh-80px)] bg-[#0d0d1a]"
      data-aos="fade-up"
      style={{
        backgroundImage: `linear-gradient(rgba(13,13,26,0.8), rgba(13,13,26,0.86)), url(${heroNewsroom})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      <div className="section-inner flex min-h-[70vh] flex-col items-start justify-center">
        <h1 className="mb-4 max-w-[900px] text-left text-[clamp(2.8rem,7vw,3.6rem)] font-extrabold leading-[1.08] text-white">
          Nirikshyak AI
        </h1>
        <p className="mb-10 max-w-[760px] text-[1.125rem] text-white/90">
          A simple fact-checking platform to verify news claims using trusted sources.
        </p>
        <button type="button" onClick={() => onNavigate('analyze')} className="btn-pill">
          Analyze Now 
        </button>
      </div>
    </section>
  );
}

export default Home;
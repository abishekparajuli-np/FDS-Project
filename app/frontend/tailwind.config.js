/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#e94560',
          dark: '#d63850',
          light: '#ff6b6b',
        },
        dark: {
          DEFAULT: '#1a1a2e',
          deeper: '#0f0f1a',
          lighter: '#16213e',
        },
      },
      animation: {
        'spin-slow': 'spin 1s linear infinite',
      },
    },
  },
  plugins: [],
}
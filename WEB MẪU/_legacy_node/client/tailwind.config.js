/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dustyRose: '#C97F8E',
        rosePink: '#D98F9F',
        blushPink: '#F5DDE2',
        softPink: '#FBECEF',
        ivoryWhite: '#FFF9F8',
        darkRose: '#A85C69',
        textCharcoal: '#343039',
      },
      fontFamily: {
        playfair: ['"Playfair Display"', 'Georgia', 'serif'],
        montserrat: ['"Montserrat"', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 8px 30px rgba(217, 143, 159, 0.12)',
        'card': '0 10px 25px -5px rgba(201, 127, 142, 0.08), 0 8px 10px -6px rgba(201, 127, 142, 0.04)',
      }
    },
  },
  plugins: [],
}

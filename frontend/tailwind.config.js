/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#21b621',
        "primary-dark": '#188518',
        "accent": '#6afff7'
      }
    },
  },
  plugins: [],
}
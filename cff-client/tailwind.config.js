/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        "cff-red": "#EB0000",
        "cff-blue": "#2d327d",
        "cff-anthracite": "#5A5A5A",
        "cff-charcoal": "#212121",
        "cff-midnight": "#151515",
        "cff-black": "#000000",
      },
    },
  },
  plugins: [],
};

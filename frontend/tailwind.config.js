/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "#ea580c",
          dark: "#c2410c",
          light: "#fb923c",
        },
        surface: {
          DEFAULT: "#ffffff",
          muted: "#f8fafc",
          dark: "#0f172a",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Oswald", "Inter", "sans-serif"],
      },
    },
  },
  plugins: [],
};

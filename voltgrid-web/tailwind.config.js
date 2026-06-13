/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx}",
    "./components/**/*.{js,ts,jsx,tsx}",
    "./lib/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // El color primario por defecto es verde (#16a34a) pero el whitelabel
        // lo sobreescribe en runtime mediante la variable CSS --primary.
        primary: "var(--primary, #16a34a)",
      },
    },
  },
  plugins: [],
};

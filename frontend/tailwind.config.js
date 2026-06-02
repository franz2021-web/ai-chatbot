/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      animation: {
        "slideIn": "slideIn 0.3s ease",
        "blink": "blink 1s infinite",
        "bounce-custom": "bounce-custom 1.4s infinite",
      },
      keyframes: {
        slideIn: {
          "from": {
            "opacity": "0",
            "transform": "translateY(10px)",
          },
          "to": {
            "opacity": "1",
            "transform": "translateY(0)",
          },
        },
        blink: {
          "0%, 49%": { "opacity": "1" },
          "50%, 100%": { "opacity": "0" },
        },
        "bounce-custom": {
          "0%, 80%, 100%": {
            "opacity": "0.4",
            "transform": "translateY(0)",
          },
          "40%": {
            "opacity": "1",
            "transform": "translateY(-8px)",
          },
        },
      },
    },
  },
  plugins: [],
}

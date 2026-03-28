// Tailwind configuration for the Fello Intelligence React dashboard.
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#07111f",
        panel: "#0e1a2b",
        line: "#1d3047",
        glow: "#34d399",
        ember: "#fb923c",
        mist: "#9db0c8"
      },
      boxShadow: {
        panel: "0 20px 60px rgba(2, 6, 23, 0.45)"
      },
      backgroundImage: {
        "hero-grid":
          "linear-gradient(rgba(157, 176, 200, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(157, 176, 200, 0.05) 1px, transparent 1px)"
      },
      backgroundSize: {
        "hero-grid": "28px 28px"
      },
      animation: {
        pulseDot: "pulseDot 1.8s ease-in-out infinite"
      },
      keyframes: {
        pulseDot: {
          "0%, 100%": { transform: "scale(1)", opacity: "0.7" },
          "50%": { transform: "scale(1.25)", opacity: "1" }
        }
      }
    }
  },
  plugins: []
};

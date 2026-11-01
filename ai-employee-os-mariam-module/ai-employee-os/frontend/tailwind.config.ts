import type { Config } from "tailwindcss";

// Design tokens for AI Employee OS: an operations console, not a marketing page.
// Deep navy/graphite base with a single signal-amber accent reserved for
// live/active states (running agents, alerts) — everything else stays quiet.
const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0B0F14",       // page background
        panel: "#12181F",     // card / panel surface
        line: "#232C36",      // hairline borders
        muted: "#7C8894",     // secondary text
        paper: "#E8ECEF",     // primary text on dark
        signal: "#E8A33D",    // amber — active agents, alerts, primary actions
        signalDim: "#8A6425",
        ok: "#3FA875",
        danger: "#C15A5A",
      },
      fontFamily: {
        display: ["'IBM Plex Sans'", "system-ui", "sans-serif"],
        mono: ["'IBM Plex Mono'", "ui-monospace", "monospace"],
      },
      borderRadius: {
        sm: "4px",
        md: "6px",
      },
    },
  },
  plugins: [],
};

export default config;

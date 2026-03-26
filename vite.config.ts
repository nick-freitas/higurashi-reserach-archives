/// <reference types="vitest/config" />
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 4737,
    strictPort: true,
    allowedHosts: ["higurashi.test"],
    proxy: {
      "/api": {
        target: "http://localhost:4738",
        changeOrigin: true,
      },
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
  },
});

import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "../console_dist",
    emptyOutDir: true,
    sourcemap: false,
    rollupOptions: {
      output: {
        entryFileNames: "assets/app.js",
        chunkFileNames: "assets/[name].js",
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith(".css")) {
            return "assets/styles.css";
          }
          return "assets/[name][extname]";
        }
      }
    }
  },
  server: {
    proxy: {
      "/api": "http://127.0.0.1:7893",
      "/health": "http://127.0.0.1:7893"
    }
  }
});

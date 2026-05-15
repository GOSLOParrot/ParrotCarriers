import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "../console_dist",
    emptyOutDir: false,
    sourcemap: false,
    rollupOptions: {
      input: "index.html",
      output: {
        entryFileNames: "assets/app-[hash].js",
        chunkFileNames: "assets/[name]-[hash].js",
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.endsWith(".css")) {
            return "assets/styles-[hash][extname]";
          }
          return "assets/[name]-[hash][extname]";
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

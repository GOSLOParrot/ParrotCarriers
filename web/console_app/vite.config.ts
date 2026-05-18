import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";

function cleanTarget(value: string | undefined): string {
  const cleaned = (value || "http://127.0.0.1:7893").trim();
  return cleaned.endsWith("/") ? cleaned.slice(0, -1) : cleaned;
}

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const apiTarget = cleanTarget(
    env.PARROT_WEB_CONSOLE_API_TARGET
      || env.VITE_PARROT_WEB_CONSOLE_API_TARGET
  );

  return {
    plugins: [react()],
    build: {
      outDir: "../console_dist",
      emptyOutDir: false,
      sourcemap: false,
      rollupOptions: {
        input: "index.html",
        output: {
          entryFileNames: "assets/app.js",
          chunkFileNames: "assets/[name].js",
          assetFileNames: (assetInfo) => {
            if (assetInfo.name && assetInfo.name.endsWith(".css")) {
              return "assets/styles[extname]";
            }
            return "assets/[name][extname]";
          }
        }
      }
    },
    server: {
      proxy: {
        "/api": apiTarget,
        "/health": apiTarget
      }
    }
  };
});

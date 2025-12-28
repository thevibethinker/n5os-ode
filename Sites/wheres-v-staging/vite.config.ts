import path from "path";
import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react-swc";
import { defineConfig } from "vite";
import config from "./zosite.json";

const isInternal = Boolean(process.env.INTERNAL_DEV);
export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  cacheDir: isInternal ? undefined : `/dev/shm/.vite-${config.name}`,
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
  server: {
    port: 54179,
    proxy: {
      '/api': {
        target: 'http://localhost:3002',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:3002',
        changeOrigin: true,
      }
    }
  }
});




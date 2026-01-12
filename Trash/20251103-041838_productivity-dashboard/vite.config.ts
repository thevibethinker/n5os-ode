import react from "@vitejs/plugin-react-swc";
import { defineConfig } from "vite";
import config from "./zosite.json";

export default defineConfig({
  plugins: [react()],
  cacheDir: `/dev/shm/.vite-${config.name}`,
  build: {
    outDir: "dist",
    emptyOutDir: true,
  },
});

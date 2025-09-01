import { defineConfig } from "vite";
import { resolve } from "path";
import autoprefixer from "autoprefixer";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  root: "src",
  build: {
    outDir: "../dist",
    emptyOutDir: true,
    rollupOptions: {
      input: {
        main: resolve(process.cwd(), "src/index.html"),
      },
    },
    assetsDir: "assets",
  },
  server: {
    port: 3000,
    open: true,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  css: {
    postcss: {
      plugins: [autoprefixer],
    },
  },
});

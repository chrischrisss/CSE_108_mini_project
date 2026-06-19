import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],

  server: {
    proxy: {
      "/login": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },

      "/logout": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },

      "/me": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },

      "/courses": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },

      "/my-courses": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },

      "/enroll": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },

      "/drop": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },

      "/teacher": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },
    },
  },
});
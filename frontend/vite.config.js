import { resolve } from "node:path";
import { defineConfig, loadEnv } from "vite";
import viteReact from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";


// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [viteReact(), tailwindcss()],
    test: {
      globals: true,
      environment: "jsdom",
    },
    resolve: {
      alias: {
        '@': resolve(__dirname, './src'),
      },
    },
    build: {
      sourcemap: false
    },
    server: {
      host: '0.0.0.0',
      port: 3000,
      proxy: {
        '/api': {
          target: env.VITE_API_URL,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        }
      }
    }
  }
}
);

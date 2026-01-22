import { defineConfig } from "vite";
import tsFlaskUrlsPlugin from "rollup-plugin-ts-flask-urls";
import react from "@vitejs/plugin-react";


// https://vite.dev/config/
export default defineConfig({
    plugins: [
        react(),
        tsFlaskUrlsPlugin({
            outDir: "src/flask_urls",
            backendRoot: "../backend"
        })
    ],
    server: {
        cors: true,
    }
});

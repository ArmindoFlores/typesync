import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import typesyncPlugin from "rollup-plugin-typesync";

// https://vite.dev/config/
export default defineConfig({
    plugins: [
        react(),
        typesyncPlugin({
            backendRoot: "../backend"
        })
    ],
    server: {
        cors: true,
    }
});

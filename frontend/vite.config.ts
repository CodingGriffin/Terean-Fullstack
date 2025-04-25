import {defineConfig} from 'vite';
import dotenv from 'dotenv';
import react from '@vitejs/plugin-react'

dotenv.config();

// Set default if undefined
if (process.env.VITE_PORT === undefined) {
    process.env.VITE_PORT = "5173"
}
if (process.env.VITE_HOST === undefined) {
    process.env.VITE_HOST = "localhost"
}

export default defineConfig({
    server: {
        port: parseInt(process.env.VITE_PORT),
        host: process.env.VITE_HOST,
        allowedHosts: [
            ".localhost",
            ".terean.com",
        ]
    },
    plugins: [react()],
})

/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    DEFAULT: '#2563eb', // blue-600
                    foreground: '#ffffff',
                },
                destructive: {
                    DEFAULT: '#ef4444', // red-500
                    foreground: '#ffffff',
                },
                muted: {
                    DEFAULT: '#f3f4f6', // gray-100
                    foreground: '#6b7280', // gray-500
                },
            },
        },
    },
    plugins: [],
}

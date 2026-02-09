/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // V2.0 Original Navy Theme
                'navy': {
                    900: '#0a1628', // Darkest navy background
                    800: '#0d1b2a', // Card backgrounds  
                    700: '#1b263b', // Borders
                },
                'cyan': {
                    400: '#00d9ff', // EVOKI brand color
                },
            },
        },
    },
    plugins: [],
}

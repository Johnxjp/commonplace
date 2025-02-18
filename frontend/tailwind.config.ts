import type { Config } from "tailwindcss";

export default {
	content: [
		"./pages/**/*.{js,ts,jsx,tsx,mdx}",
		"./components/**/*.{js,ts,jsx,tsx,mdx}",
		"./app/**/*.{js,ts,jsx,tsx,mdx}",
	],
	theme: {
		fontFamily: {
			sans: ["Inter", "sans-serif"],
		},
		extend: {
			colors: {
				background: "var(--background)",
				foreground: "var(--foreground)",
				breakfast: "#f8c366",
			},
		},
	},
	plugins: [],
} satisfies Config;

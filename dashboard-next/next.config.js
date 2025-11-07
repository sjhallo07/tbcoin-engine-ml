/** @type {import('next').NextConfig} */
const nextConfig = {
	reactStrictMode: true,
	// Enable SWC transform for styled-components. See:
	// https://styled-components.com/docs/tooling#babel-plugin
	// https://nextjs.org/docs/app/api-reference/next-config-js/compiler#styledcomponents
	compiler: {
		styledComponents: {
			// Enabled by default in dev; we keep it explicit for clarity
			displayName: process.env.NODE_ENV !== 'production',
			// Enable server-side rendering support
			ssr: true,
			// Annotate filenames in classnames to aid debugging
			fileName: true,
			// Allow optimizing styled-components output
			minify: true,
			// Inline template literal values when possible
			transpileTemplateLiterals: true,
			// Mark styled-components helpers as pure for tree-shaking
			pure: true,
			// Support the css prop
			cssProp: true,
			// Optional knobs kept at defaults
			meaninglessFileNames: ['index'],
		},
		relay: {
			// This should match relay.config.js if you add one
			src: './',
			artifactDirectory: './__generated__',
			language: 'typescript',
			eagerEsModules: false,
		},
	},
};

module.exports = nextConfig;

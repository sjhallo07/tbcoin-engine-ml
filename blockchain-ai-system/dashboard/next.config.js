/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    appDir: true,
  },
  env: {
    DEEPSEEK_API_KEY: process.env.DEEPSEEK_API_KEY,
    COINGECKO_API_KEY: process.env.COINGECKO_API_KEY,
  },
};

module.exports = nextConfig;

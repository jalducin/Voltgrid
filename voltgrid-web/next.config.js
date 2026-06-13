/** @type {import('next').NextConfig} */

// PWA: se deshabilita en desarrollo y se habilita en producción.
const withPWA = require('next-pwa')({
  dest: 'public',
  disable: process.env.NODE_ENV === 'development',
  register: true,
  skipWaiting: true,
});

const nextConfig = {
  reactStrictMode: true,
  // Imagen Docker ligera (servidor autónomo).
  output: 'standalone',
};

module.exports = withPWA(nextConfig);

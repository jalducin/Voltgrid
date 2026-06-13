import type { Metadata, Viewport } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'VoltGrid',
  description: 'Plataforma de gestión de estaciones de carga eléctrica',
  manifest: '/manifest.json',
};

export const viewport: Viewport = {
  themeColor: '#16a34a',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="es-MX">
      <body>{children}</body>
    </html>
  );
}

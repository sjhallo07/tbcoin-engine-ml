import './globals.css';
import { Inter } from 'next/font/google';
import type { ReactNode } from 'react';

import { BlockchainProvider } from '../context/BlockchainContext';
import { SocketProvider } from '../context/SocketContext';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'AI Blockchain Predictive Dashboard',
  description: 'Real-time blockchain predictions and AI-powered insights',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <BlockchainProvider>
          <SocketProvider>{children}</SocketProvider>
        </BlockchainProvider>
      </body>
    </html>
  );
}

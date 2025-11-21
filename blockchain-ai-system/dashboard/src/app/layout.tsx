// Note: Avoid next/font and global CSS during the production build path here to
// reduce Next.js postcss/font-loader surface area in environments with
// differing toolchains. If you need fonts/styles, add them via static
// imports or .env-based configuration.
import type { ReactNode } from 'react';

import { BlockchainProvider } from '../context/BlockchainContext';
import { SocketProvider } from '../context/SocketContext';

export const metadata = {
  title: 'AI Blockchain Predictive Dashboard',
  description: 'Real-time blockchain predictions and AI-powered insights',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
  <body>
        <BlockchainProvider>
          <SocketProvider>{children}</SocketProvider>
        </BlockchainProvider>
      </body>
    </html>
  );
}

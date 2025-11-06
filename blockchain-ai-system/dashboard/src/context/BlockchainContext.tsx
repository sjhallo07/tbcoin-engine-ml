import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';

interface BlockchainContextValue {
  connectedNetwork: string | null;
  setConnectedNetwork: (network: string | null) => void;
}

const BlockchainContext = createContext<BlockchainContextValue | undefined>(undefined);

export function BlockchainProvider({ children }: { children: ReactNode }) {
  const [connectedNetwork, setConnectedNetwork] = useState<string | null>(null);

  const value = useMemo(
    () => ({ connectedNetwork, setConnectedNetwork }),
    [connectedNetwork],
  );

  return <BlockchainContext.Provider value={value}>{children}</BlockchainContext.Provider>;
}

export function useBlockchain() {
  const context = useContext(BlockchainContext);
  if (!context) {
    throw new Error('useBlockchain must be used within a BlockchainProvider');
  }
  return context;
}

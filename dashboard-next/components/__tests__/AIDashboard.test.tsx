import { render, screen, waitFor } from '@testing-library/react';
import { AIDashboard } from '../AIDashboard';

const fetchMock = jest.fn();
const originalFetch = global.fetch;

describe('AIDashboard', () => {
  beforeAll(() => {
    Object.defineProperty(global, 'fetch', {
      configurable: true,
      writable: true,
      value: fetchMock
    });
  });

  beforeEach(() => {
    fetchMock.mockReset();
  });

  afterAll(() => {
    if (originalFetch) {
      Object.defineProperty(global, 'fetch', {
        configurable: true,
        writable: true,
        value: originalFetch
      });
    } else {
      delete (global as { fetch?: typeof fetch }).fetch;
    }
  });

  it('shows token name and logo when Solana overview returns data', async () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        status: 'success',
        data: {
          price: 123.45,
          change24h: 1.23,
          marketCap: 987654321,
          volume24h: 456789,
          timestamp: new Date().toISOString(),
          display: {
            name: 'Test Token',
            symbol: 'TEST',
            logo: 'https://example.com/logo.png'
          }
        }
      })
    } as Response);

    render(<AIDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Test Token (TEST)')).toBeInTheDocument();
    });

    const logo = screen.getByRole('img', { name: 'Test Token' });
    expect(logo).toHaveAttribute('src', 'https://example.com/logo.png');
    expect(fetchMock).toHaveBeenCalledWith('/api/solana/price');
  });

  it('falls back gracefully when Solana overview request fails', async () => {
    fetchMock.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({})
    } as Response);

    render(<AIDashboard />);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith('/api/solana/price');
    });

    // Heading fallback is always Solana, but ensure no custom display shows
    expect(screen.getByText('Solana')).toBeInTheDocument();
  });
});

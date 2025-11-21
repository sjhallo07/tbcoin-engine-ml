import axios from 'axios';

export interface CoinData {
  id: string;
  symbol: string;
  name: string;
  current_price: number;
  market_cap: number;
  market_cap_rank: number;
  price_change_percentage_24h: number;
  price_change_percentage_7d: number;
  total_volume: number;
  sparkline_in_7d: { price: number[] };
}

export interface MarketChartData {
  prices: [number, number][];
  market_caps: [number, number][];
  total_volumes: [number, number][];
}

class CoinGeckoService {
  private readonly baseURL = 'https://api.coingecko.com/api/v3';

  async getTopCryptos(limit: number = 50): Promise<CoinData[]> {
    try {
      const response = await axios.get<CoinData[]>(
        `${this.baseURL}/coins/markets`,
        {
          params: {
            vs_currency: 'usd',
            order: 'market_cap_desc',
            per_page: limit,
            page: 1,
            sparkline: true,
            price_change_percentage: '24h,7d',
            x_cg_demo_api_key: process.env.NEXT_PUBLIC_COINGECKO_API_KEY,
          },
        },
      );
      return response.data;
    } catch (error) {
      console.error('CoinGecko API Error:', error);
      return this.getDemoData();
    }
  }

  async getCoinHistory(coinId: string, days: number = 30): Promise<MarketChartData> {
    try {
      const response = await axios.get<MarketChartData>(
        `${this.baseURL}/coins/${coinId}/market_chart`,
        {
          params: {
            vs_currency: 'usd',
            days,
            x_cg_demo_api_key: process.env.NEXT_PUBLIC_COINGECKO_API_KEY,
          },
        },
      );
      return response.data;
    } catch (error) {
      console.error('CoinGecko History Error:', error);
      return this.generateDemoChartData();
    }
  }

  async getCoinDetail(coinId: string) {
    try {
      const response = await axios.get(
        `${this.baseURL}/coins/${coinId}`,
        {
          params: {
            localization: false,
            tickers: false,
            market_data: true,
            community_data: false,
            developer_data: false,
            sparkline: true,
            x_cg_demo_api_key: process.env.NEXT_PUBLIC_COINGECKO_API_KEY,
          },
        },
      );
      return response.data;
    } catch (error) {
      console.error('CoinGecko Detail Error:', error);
      return null;
    }
  }

  private getDemoData(): CoinData[] {
    return [
      {
        id: 'bitcoin',
        symbol: 'btc',
        name: 'Bitcoin',
        current_price: 45000 + Math.random() * 5000,
        market_cap: 880_000_000_000,
        market_cap_rank: 1,
        price_change_percentage_24h: 2.5 + (Math.random() - 0.5) * 4,
        price_change_percentage_7d: 8.2 + (Math.random() - 0.5) * 6,
        total_volume: 25_000_000_000,
        sparkline_in_7d: { price: Array.from({ length: 168 }, () => 44_000 + Math.random() * 3_000) },
      },
      {
        id: 'ethereum',
        symbol: 'eth',
        name: 'Ethereum',
        current_price: 2_500 + Math.random() * 500,
        market_cap: 300_000_000_000,
        market_cap_rank: 2,
        price_change_percentage_24h: 1.8 + (Math.random() - 0.5) * 4,
        price_change_percentage_7d: 6.5 + (Math.random() - 0.5) * 6,
        total_volume: 15_000_000_000,
        sparkline_in_7d: { price: Array.from({ length: 168 }, () => 2_400 + Math.random() * 400) },
      },
    ];
  }

  private generateDemoChartData(): MarketChartData {
    const basePrice = 45_000;
    const prices: [number, number][] = [];
    const now = Date.now();

    for (let i = 30; i >= 0; i -= 1) {
      const time = now - i * 24 * 60 * 60 * 1_000;
      const price = basePrice + (Math.random() - 0.5) * 4_000;
      prices.push([time, price]);
    }

    return {
      prices,
      market_caps: prices.map(([time, price]) => [time, price * 19_500_000]),
      total_volumes: prices.map(([time, price]) => [time, price * 500_000]),
    };
  }
}

export const coinGeckoService = new CoinGeckoService();

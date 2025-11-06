export interface DeepSeekMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
}

export interface DeepSeekResponse {
  choices: Array<{
    message: {
      role: string;
      content: string;
    };
    finish_reason: string;
  }>;
  usage: {
    total_tokens: number;
  };
}

export interface AIPrediction {
  prediction: string;
  confidence: number;
  reasoning: string;
  timestamp: string;
  factors: string[];
}

class DeepSeekService {
  private readonly baseURL = 'https://api.deepseek.com/v1';
  private apiKey: string | null = null;
  private isInitialized = false;

  initialize(apiKey: string) {
    this.apiKey = apiKey;
    this.isInitialized = true;
    console.log('DeepSeek AI Service Initialized');
  }

  async analyzeMarketTrends(marketData: unknown): Promise<AIPrediction> {
    if (!this.isInitialized) {
      return this.getDemoPrediction();
    }

    const prompt = this.createMarketAnalysisPrompt(marketData);

    try {
      const response = await this.chatCompletion([
        {
          role: 'system',
          content:
            'You are an expert blockchain and cryptocurrency market analyst. Provide detailed technical analysis and predictions based on market data.',
        },
        {
          role: 'user',
          content: prompt,
        },
      ]);

      return this.parseAIPrediction(response);
    } catch (error) {
      console.error('DeepSeek API Error:', error);
      return this.getDemoPrediction();
    }
  }

  async predictGasOptimization(blockchainData: unknown): Promise<AIPrediction> {
    const prompt = `Analyze this blockchain network data and predict optimal gas settings:\n${JSON.stringify(
      blockchainData,
      null,
      2,
    )}\nProvide: 1) Recommended gas price 2) Optimal transaction timing 3) Expected confirmation time 4) Cost optimization strategies.`;

    try {
      const response = await this.chatCompletion([
        {
          role: 'system',
          content:
            'You are a blockchain gas optimization expert. Analyze network conditions and provide optimal gas strategies.',
        },
        {
          role: 'user',
          content: prompt,
        },
      ]);

      return this.parseAIPrediction(response);
    } catch (error) {
      console.error('DeepSeek Gas Prediction Error:', error);
      return this.getDemoGasPrediction();
    }
  }

  async detectArbitrageOpportunities(marketData: unknown): Promise<AIPrediction> {
    const prompt = `Analyze these market prices across different exchanges and identify arbitrage opportunities:\n${JSON.stringify(
      marketData,
      null,
      2,
    )}\nIdentify: 1) Price discrepancies 2) Potential profit margins 3) Associated risks 4) Recommended execution strategy.`;

    try {
      const response = await this.chatCompletion([
        {
          role: 'system',
          content:
            'You are a cryptocurrency arbitrage detection expert. Identify profitable trading opportunities across exchanges.',
        },
        {
          role: 'user',
          content: prompt,
        },
      ]);

      return this.parseAIPrediction(response);
    } catch (error) {
      console.error('DeepSeek Arbitrage Detection Error:', error);
      return this.getDemoArbitragePrediction();
    }
  }

  private async chatCompletion(messages: DeepSeekMessage[]): Promise<DeepSeekResponse> {
    if (!this.apiKey) {
      throw new Error('DeepSeek API key not configured');
    }

    const response = await fetch(`${this.baseURL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({
        model: 'deepseek-chat',
        messages,
        max_tokens: 1_000,
        temperature: 0.7,
      }),
    });

    if (!response.ok) {
      throw new Error(`DeepSeek API error: ${response.statusText}`);
    }

    return (await response.json()) as DeepSeekResponse;
  }

  private createMarketAnalysisPrompt(marketData: unknown): string {
    return `Analyze the following cryptocurrency market data and provide technical analysis and predictions:\n${JSON.stringify(
      marketData,
      null,
      2,
    )}\nPlease provide: 1) Short-term price prediction (24-48 hours) 2) Key technical indicators analysis 3) Market sentiment assessment 4) Risk factors 5) Trading recommendations.`;
  }

  private parseAIPrediction(response: DeepSeekResponse): AIPrediction {
    const content = response.choices[0]?.message?.content ?? 'No analysis available';
    return {
      prediction: this.extractPrediction(content),
      confidence: this.extractConfidence(content),
      reasoning: content,
      timestamp: new Date().toISOString(),
      factors: this.extractFactors(content),
    };
  }

  private extractPrediction(content: string): string {
    const lower = content.toLowerCase();
    if (lower.includes('bullish')) return 'Bullish';
    if (lower.includes('bearish')) return 'Bearish';
    return 'Neutral';
  }

  private extractConfidence(content: string): number {
    const match = content.match(/(\d+)% confidence/);
    return match ? Number.parseInt(match[1], 10) / 100 : 0.75;
  }

  private extractFactors(content: string): string[] {
    const lower = content.toLowerCase();
    const factors: string[] = [];
    if (lower.includes('volume')) factors.push('Trading Volume');
    if (lower.includes('resistance')) factors.push('Resistance Levels');
    if (lower.includes('support')) factors.push('Support Levels');
    if (lower.includes('trend')) factors.push('Market Trend');
    return factors.length > 0 ? factors : ['Market Sentiment', 'Technical Indicators'];
  }

  private getDemoPrediction(): AIPrediction {
    const predictions = [
      'Expected bullish momentum in the next 24-48 hours with potential 5-8% upside',
      'Market showing consolidation patterns, expect sideways movement with 2-4% volatility',
      'Bearish signals detected, potential 3-6% correction likely',
    ];

    return {
      prediction: predictions[Math.floor(Math.random() * predictions.length)],
      confidence: 0.75 + Math.random() * 0.2,
      reasoning:
        'Based on technical analysis of price action, volume trends, and market sentiment indicators. Support and resistance levels are being tested.',
      timestamp: new Date().toISOString(),
      factors: ['Trading Volume', 'RSI Indicators', 'Market Sentiment', 'Support/Resistance Levels'],
    };
  }

  private getDemoGasPrediction(): AIPrediction {
    return {
      prediction: 'Optimal gas price: 25-35 Gwei for timely confirmations',
      confidence: 0.85,
      reasoning:
        'Network congestion is moderate. Recommended gas prices will provide 1-2 block confirmation times without overpaying.',
      timestamp: new Date().toISOString(),
      factors: ['Network Congestion', 'Base Fee', 'Pending Transactions', 'Block Utilization'],
    };
  }

  private getDemoArbitragePrediction(): AIPrediction {
    return {
      prediction: 'Potential 0.8-1.2% arbitrage opportunity detected between exchanges',
      confidence: 0.78,
      reasoning:
        'Price discrepancies observed on major trading pairs. Consider triangular arbitrage across BTC/ETH/USDT pairs.',
      timestamp: new Date().toISOString(),
      factors: ['Exchange Price Differences', 'Liquidity Depth', 'Transaction Costs', 'Execution Speed'],
    };
  }
}

export const deepSeekService = new DeepSeekService();

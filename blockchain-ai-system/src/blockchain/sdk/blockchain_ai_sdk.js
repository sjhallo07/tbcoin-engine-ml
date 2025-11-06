/*
 * Lightweight SDK for interacting with the Blockchain AI prediction APIs.
 */

export class BlockchainAISDK {
  /**
   * @param {string} apiKey - API key issued by the prediction service.
   * @param {string} baseUrl - Base URL for the blockchain AI API.
   * @param {RequestInit} [defaults] - Optional default fetch options.
   */
  constructor(apiKey, baseUrl, defaults = {}) {
    if (!apiKey) {
      throw new Error('API key is required');
    }
    if (!baseUrl) {
      throw new Error('API base URL is required');
    }
    this.apiKey = apiKey;
    this.baseUrl = baseUrl.replace(/\/+$/, '');
    this.defaults = { ...defaults };
  }

  /**
   * Fetch optimal trade parameters for a token pair and amount.
   * @param {string} tokenPair
   * @param {number} amount
   * @param {object} [options]
   * @returns {Promise<object>}
   */
  async getOptimalTradeParameters(tokenPair, amount, options = {}) {
    const payload = {
      network: options.network || 'ethereum.mainnet',
      token_pair: tokenPair,
      amount,
    };
    const response = await this._post('/api/v1/predictions/gas-optimization', payload, options.abortSignal);
    return {
      network: response.network,
      gas: response.gas,
      telemetry: response.telemetry,
      timestamp: response.timestamp,
    };
  }

  /**
   * Execute a trade using previously obtained AI-optimized parameters.
   * @param {object} tradeParams
   * @param {AbortSignal} [abortSignal]
   * @returns {Promise<object>}
   */
  async executeAIOptimizedTrade(tradeParams, abortSignal) {
    if (!tradeParams || typeof tradeParams !== 'object') {
      throw new TypeError('tradeParams must be provided');
    }
    const payload = {
      network: tradeParams.network || 'ethereum.mainnet',
      prediction_data: tradeParams.prediction_data,
      private_key: tradeParams.private_key,
      account_address: tradeParams.account_address,
    };
    return this._post('/api/v1/execute/smart-contract', payload, abortSignal);
  }

  async _post(path, body, abortSignal) {
    const headers = {
      'Content-Type': 'application/json',
      'X-API-Key': this.apiKey,
      ...(this.defaults.headers || {}),
    };
    const response = await fetch(`${this.baseUrl}${path}`, {
      method: 'POST',
      headers,
      body: JSON.stringify(body),
      signal: abortSignal,
      ...this.defaults,
    });
    if (!response.ok) {
      const message = await response.text();
      throw new Error(`API request failed (${response.status}): ${message}`);
    }
    return response.json();
  }
}

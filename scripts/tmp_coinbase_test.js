const axios = require('axios');
const ccxt = require('ccxt');
const path = require('path');

axios.post = async (url, data, config) => {
  console.log(`\n[MOCK AXIOS POST] URL: ${url}`);
  console.log('[DATA]:', JSON.stringify(data, null, 2));
  if (config && config.headers) {
    console.log('[HEADERS]:', JSON.stringify(config.headers, null, 2));
  }
  return { data: { status: 'mocked_success', url, data } };
};

axios.get = async (url, config) => {
  console.log(`\n[MOCK AXIOS GET] URL: ${url}`);
  if (config && config.headers) {
    console.log('[HEADERS]:', JSON.stringify(config.headers, null, 2));
  }
  return { data: { status: 'mocked_success', url } };
};

class MockExchange {
  constructor(config) {
    this.apiKey = config.apiKey;
    this.secret = config.secret;
    console.log(`[MOCK CCXT] Exchange initialized with key: ${this.apiKey}`);
  }
  async fetchBalance() {
    console.log('[MOCK CCXT] fetchBalance called');
    return { total: { USDT: 1000 } };
  }
  async createOrder(symbol, type, side, amount, price) {
    console.log(`[MOCK CCXT] createOrder called: ${symbol} ${type} ${side} ${amount} @ ${price || 'MARKET'}`);
    return { id: 'mock-order-id', symbol, type, side, amount, price };
  }
}

ccxt.coinbase = MockExchange;

const routeTo = async (target, payload, options = {}) => {
  const platform = target.toLowerCase();
  const adapterPath = path.resolve(__dirname, '../trading-templates/adapters/', `${platform}-adapter.js`);
  console.log(`\n[Engram Router] Routing to platform: ${platform} via ${adapterPath}`);

  const adapter = require(adapterPath);
  const methodName = `mapAndExecute${platform.charAt(0).toUpperCase() + platform.slice(1)}`;
  const result = await adapter[methodName](payload, options);
  console.log(`[Engram Router] Successfully executed ${platform} adapter.`);
  return result;
};

(async () => {
  console.log('=== Engram Trading Templates Coinbase + Balance Check ===');
  await routeTo(
    'coinbase',
    { action: 'buy', symbol: 'BTC-USD', quantity: 0.001 },
    { COINBASE_API_KEY: 'test_key', COINBASE_SECRET: 'test_secret' }
  );
  await routeTo(
    'coinbase',
    { action: 'balance' },
    { COINBASE_API_KEY: 'test_key', COINBASE_SECRET: 'test_secret' }
  );
})();

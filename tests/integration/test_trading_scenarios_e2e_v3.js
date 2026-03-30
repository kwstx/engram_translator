const fs = require('fs');
const ccxt = require('ccxt');
const axios = require('axios');
const dotenv = require('dotenv');

// MOCKING PREPARATION
dotenv.config = () => {}; // Mock before requiring templates

// Actually override the require cache for dotenv to prevent noise
require.cache[require.resolve('dotenv')] = {
  exports: {
    config: () => ({ error: null, parsed: {} })
  }
};

const { binance, coinbase, kalshi, stripe } = require('./trading-templates');

// Mock CCXT
ccxt.binance = class {
  constructor(config) { this.config = config; }
  async fetchBalance() {
    if (!this.config.apiKey || this.config.apiKey === 'INVALID_KEY') throw new Error('401: Unauthorized');
    return { BTC: 0.5 };
  }
  async createOrder(symbol, side, quantity, price) {
    if (global.SIMULATE_429) { const e = new Error('Rate Limit'); e.code = 429; throw e; }
    return { id: 'binance-order-123', status: 'filled', symbol, side, quantity };
  }
};

ccxt.coinbase = class {
  constructor(config) { this.config = config; }
  async createOrder(symbol, side, quantity, price) {
    if (!symbol || !quantity) throw new Error('Params Missing');
    return { id: 'coinbase-order-456', status: 'pending', symbol, side, quantity };
  }
};

axios.post = async (url, data, config) => {
  if (config.headers?.Authorization?.includes('INVALID_KEY')) throw new Error('401: Unauthorized');
  if (url === '/markets/orders') return { data: { orderId: 'kalsh-bet-789' } };
  if (url.includes('payment_intents')) return { data: { id: 'pi_test_123' } };
  return { data: { success: true } };
};

const validConfig = {
  BINANCE_API_KEY: 'k', BINANCE_SECRET: 's', COINBASE_API_KEY: 'k', 
  KALSHI_TOKEN: 't', STRIPE_SECRET: 'k'
};

const buyP = { action: 'buy', symbol: 'BTC/USDT', quantity: 0.1, side: 'buy' };

async function runTests() {
  const results = [];
  
  // S1: Seq
  try {
    const r1 = await binance(buyP, validConfig);
    const r2 = await coinbase(buyP, validConfig);
    const r3 = await kalshi({ symbol: 'X', quantity: 1, action: 'yes' }, validConfig);
    const r4 = await stripe({ amount: 10 }, validConfig);
    results.push({ scenario: '1 Sequential Routing', status: 'SUCCESS', details: 'All platforms hit' });
  } catch (err) { results.push({ scenario: '1 Sequential Routing', status: 'FAILED', message: err.message }); }

  // S2: Invalid Key
  try {
    await binance({ action: 'balance' }, { BINANCE_API_KEY: 'INVALID_KEY' });
    results.push({ scenario: '2 Invalid Keys', status: 'FAILED' });
  } catch (err) { results.push({ scenario: '2 Invalid Keys', status: 'SUCCESS', message: 'Caught 401' }); }

  // S3: Rate Limit
  try {
    global.SIMULATE_429 = true;
    await binance(buyP, validConfig);
    results.push({ scenario: '3 Rate Limit', status: 'FAILED' });
  } catch (err) { results.push({ scenario: '3 Rate Limit', status: 'SUCCESS', message: 'Caught 429' }); }
  finally { global.SIMULATE_429 = false; }

  // S4: Malformed
  try {
    await coinbase({ action: 'buy' }, validConfig);
    results.push({ scenario: '4 Malformed Payload', status: 'FAILED' });
  } catch (err) { results.push({ scenario: '4 Malformed Payload', status: 'SUCCESS', message: 'Caught Validation Error' }); }

  // S5: Batch
  try {
    for (let i = 0; i < 10; i++) await binance(buyP, validConfig);
    results.push({ scenario: '5 High Volume', status: 'SUCCESS', count: 10 });
  } catch (err) { results.push({ scenario: '5 High Volume', status: 'FAILED' }); }

  // Write to JSON file
  fs.writeFileSync('test_results_e2e.json', JSON.stringify(results, null, 2));
  console.log("Results written to test_results_e2e.json");
}

runTests();

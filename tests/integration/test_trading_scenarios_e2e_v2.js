const { binance, coinbase, kalshi, stripe, feeds } = require('./trading-templates');
const ccxt = require('ccxt');
const axios = require('axios');
const dotenv = require('dotenv');

// MOCKING PREPARATION
// Mock dotenv to prevent noise
dotenv.config = () => {};

// Mock CCXT
ccxt.binance = class {
  constructor(config) {
    this.config = config;
  }
  async fetchBalance() {
    if (!this.config.apiKey || this.config.apiKey === 'INVALID_KEY') {
      throw new Error('401: Unauthorized');
    }
    return { BTC: 0.5 };
  }
  async createOrder(symbol, side, quantity, price) {
    if (global.SIMULATE_429) {
      const err = new Error('Request Rate Limit Exceeded');
      err.code = 429;
      throw err;
    }
    return { id: 'binance-order-123', status: 'filled', symbol, side, quantity };
  }
};

ccxt.coinbase = class {
  constructor(config) { this.config = config; }
  async createOrder(symbol, side, quantity, price) {
    if (!symbol || !side || !quantity) throw new Error('Validation Error: Missing parameters');
    return { id: 'coinbase-order-456', status: 'pending', symbol, side, quantity };
  }
};

// Mock Axios
axios.post = async (url, data, config) => {
  if (config.headers?.Authorization?.includes('INVALID_KEY')) {
    throw new Error('401: Unauthorized');
  }
  if (url === '/markets/orders') {
    return { data: { orderId: 'kalsh-bet-789', status: 'placed' } };
  }
  if (url.includes('payment_intents')) {
    return { data: { id: 'pi_test_123', status: 'succeeded' } };
  }
  return { data: { success: true } };
};

// TEST DATA
const validConfig = {
  BINANCE_API_KEY: 'valid-key',
  BINANCE_SECRET: 'valid-secret',
  COINBASE_API_KEY: 'valid-key',
  KALSHI_TOKEN: 'valid-token',
  STRIPE_SECRET: 'valid-key'
};

const buyPayload = { action: 'buy', symbol: 'BTC/USDT', quantity: 0.1, side: 'buy' };
const betPayload = { action: 'yes', symbol: 'FED-HIKE-NOV', quantity: 10 };
const stripePayload = { amount: 100, currency: 'usd' };

async function runTests() {
  const results = [];

  console.log("=== STARTING TRADING ENGINE E2E HYBRID TEST SUITE ===\n");

  // SCENARIO 1: Unified Sequential Hybrid Routing
  try {
    console.log("Scenario 1: Sequential Hybrid Routing...");
    const r1 = await binance(buyPayload, validConfig);
    results.push({ scenario: '1.1 Binance Buy', status: 'SUCCESS', id: r1.id });
    
    const r2 = await coinbase(buyPayload, validConfig);
    results.push({ scenario: '1.2 Coinbase Buy', status: 'SUCCESS', id: r2.id });
    
    const r3 = await kalshi(betPayload, validConfig);
    results.push({ scenario: '1.3 Kalshi Bet', status: 'SUCCESS', id: r3.data.orderId });
    
    const r4 = await stripe(stripePayload, validConfig);
    results.push({ scenario: '1.4 Stripe Payout', status: 'SUCCESS', id: r4.data.id });
  } catch (err) {
    results.push({ scenario: '1 Sequential Routing', status: 'FAILED', message: err.message });
  }

  // SCENARIO 2: Error Handling - Invalid Keys
  try {
    console.log("Scenario 2: Invalid API Keys...");
    await binance({ action: 'balance' }, { BINANCE_API_KEY: 'INVALID_KEY' });
    results.push({ scenario: '2 Invalid Keys', status: 'FAILED (Should have thrown)', message: 'No error thrown' });
  } catch (err) {
    results.push({ scenario: '2 Invalid Keys', status: 'SUCCESS (Caught Error)', message: err.message });
  }

  // SCENARIO 3: Rate Limit Simulation
  try {
    console.log("Scenario 3: Rate Limit (429) Handling...");
    global.SIMULATE_429 = true;
    await binance(buyPayload, validConfig);
    results.push({ scenario: '3 Rate Limit', status: 'FAILED (Should have thrown)', message: 'No 429 error' });
  } catch (err) {
    results.push({ scenario: '3 Rate Limit', status: 'SUCCESS (Caught 429)', message: err.message });
  } finally {
    global.SIMULATE_429 = false;
  }

  // SCENARIO 4: Malformed Payload
  try {
    console.log("Scenario 4: Malformed Payload...");
    await coinbase({ action: 'buy' }, validConfig); // Missing symbol and quantity
    results.push({ scenario: '4 Malformed Payload', status: 'FAILED (Should have thrown)', message: 'No validation error' });
  } catch (err) {
    results.push({ scenario: '4 Malformed Payload', status: 'SUCCESS (Caught Error)', message: err.message });
  }

  // SCENARIO 5: High Volume Sequential Loop
  try {
    console.log("Scenario 5: High Volume (10 Dispatches)...");
    for (let i = 0; i < 10; i++) {
       await binance(buyPayload, validConfig);
    }
    results.push({ scenario: '5 High Volume', status: 'SUCCESS', count: 10 });
  } catch (err) {
    results.push({ scenario: '5 High Volume', status: 'FAILED', message: err.message });
  }

  // PRINT SUMMARY
  console.log("\n" + "=".repeat(60));
  console.log("TRADING TEMPLATES TEST SUMMARY");
  console.log("=".repeat(60));
  console.table(results);
  console.log("=".repeat(60));
  
  const allPassed = results.every(r => r.status.includes('SUCCESS'));
  if (allPassed) {
    console.log("\nALL SCENARIOS PASSED SUCCESSFULLY!");
  } else {
    console.log("\nSOME SCENARIOS FAILED. CHECK LOGS.");
  }
}

runTests();

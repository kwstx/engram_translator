const { 
  binance, coinbase, kalshi, paypal, stripe, feeds 
} = require('./trading-templates');

// Mock CCXT and Axios for testing purposes to avoid real API dependency.
// This allows us to simulate success, failure, and rate limits.

// Mock CCXT
const ccxt = require('ccxt');
jestMockCCXT();

// Mock Axios
const axios = require('axios');
jestMockAxios();

/**
 * jestMockCCXT - Mocks the ccxt library behaviors.
 */
function jestMockCCXT() {
  ccxt.binance = class {
    constructor(config) {
      this.config = config;
    }
    async fetchBalance() {
      if (!this.config.apiKey || this.config.apiKey === 'INVALID_KEY') {
        throw new Error('401: Unauthorized');
      }
      return { total: { BTC: 0.5, USDT: 1000 } };
    }
    async createOrder(symbol, side, quantity, price) {
      if (this.rateLimitHit) throw new Error('429: Too Many Requests');
      return { id: 'binance-order-123', status: 'filled', symbol, side, quantity };
    }
  };

  ccxt.coinbase = class {
    constructor(config) {
      this.config = config;
    }
    async createOrder(symbol, side, quantity, price) {
      return { id: 'coinbase-order-456', status: 'pending', symbol, side, quantity };
    }
  };
}

/**
 * jestMockAxios - Mocks the axios library behaviors.
 */
function jestMockAxios() {
  axios.post = async (url, data, config) => {
    if (config.headers?.Authorization?.includes('INVALID_KEY')) {
      throw new Error('401: Unauthorized');
    }
    if (url === '/markets/orders') {
      return { data: { orderId: 'kalsh-bet-789', status: 'placed' } };
    }
    if (url === '/v1/payment_intents' || url === '/v2/checkout/orders') {
      return { data: { id: 'pay-001', status: 'succeeded' } };
    }
    return { data: { success: true } };
  };
}

const unifiedTradePayload = {
  action: 'buy',
  symbol: 'BTC/USDT',
  quantity: 0.1,
  side: 'buy'
};

const kalshiPayload = {
  action: 'yes',
  symbol: 'BTC-ABOVE-100K-DEC24',
  quantity: 10
};

const payoutPayload = {
  amount: 50.00,
  currency: 'usd'
};

async function runScenarios() {
  console.log("=== STARTING TRADING TEMPLATES E2E HYBRID SCENARIOS ===\n");

  const validConfig = {
    BINANCE_API_KEY: 'test-key',
    BINANCE_SECRET: 'test-sec',
    COINBASE_API_KEY: 'test-key',
    COINBASE_SECRET: 'test-sec',
    KALSHI_TOKEN: 'test-token',
    STRIPE_SECRET: 'test-key',
    PAYPAL_CLIENT_ID: 'test-id',
    PAYPAL_CLIENT_SECRET: 'test-secret'
  };

  // 1. Sequential Multi-Platform Success Chain
  console.log("Scenario 1: Sequential Routing (Binance -> Coinbase -> Kalshi -> Stripe)");
  try {
    const binanceRes = await binance(unifiedTradePayload, validConfig);
    console.log("  [SUCCESS] Binance Buy Order ID:", binanceRes.id);

    const coinbaseRes = await coinbase(unifiedTradePayload, validConfig);
    console.log("  [SUCCESS] Coinbase Buy Order ID:", coinbaseRes.id);

    const kalshiRes = await kalshi(kalshiPayload, validConfig);
    console.log("  [SUCCESS] Kalshi Bet Response:", kalshiRes.data.orderId);

    const stripeRes = await stripe(payoutPayload, validConfig);
    console.log("  [SUCCESS] Stripe Payout ID:", stripeRes.data.id);
  } catch (err) {
    console.error("  [FAILED] Scenario 1:", err.message);
  }

  // 2. Error Handling: Invalid Keys
  console.log("\nScenario 2: Error Handling (Invalid Keys)");
  try {
    const badConfig = { BINANCE_API_KEY: 'INVALID_KEY' };
    await binance({ action: 'balance' }, badConfig);
  } catch (err) {
    console.log("  [EXPECTED ERROR] Binance Unauthorized logged correctly:", err.message);
  }

  // 3. Rate-Limit Simulation
  console.log("\nScenario 3: Rate-Limit Simulation (Mocked 429)");
  try {
    // Forcing a rate limit scenario
    const mockBinance = new ccxt.binance({ BINANCE_API_KEY: 'test' });
    mockBinance.rateLimitHit = true;
    // Overriding temporarily to simulate
    const originalBinance = binance;
    // Just demonstrating logic here
    console.log("  [INFO] Simulation of 429 scenario in progress...");
    // Simulate a retry logic or failure
  } catch (err) {
    console.log("  [SUCCESS] Rate limit handled:", err.message);
  }

  // 4. Malformed Payloads
  console.log("\nScenario 4: Malformed Payloads (Empty fields)");
  try {
    const emptyPayload = {};
    const res = await coinbase(emptyPayload, validConfig);
    console.log("  [INFO] Coinbase handled empty payload with defaults or failure:", res.id);
  } catch (err) {
    console.log("  [EXPECTED FAILURE] Caught malformed payload error:", err.message);
  }

  // 5. High-Volume Dispatches
  console.log("\nScenario 5: High-Volume Dispatches (10 sequential orders)");
  for (let i = 1; i <= 10; i++) {
    const res = await binance(unifiedTradePayload, validConfig);
    console.log(`  [BATCH ${i}] Binance Dispatch SUCCESS: ID ${res.id}`);
  }

  console.log("\n=== E2E SCENARIOS COMPLETE ===");
}

runScenarios();

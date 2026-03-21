const fs = require('fs');
const ccxt = require('ccxt');
const axios = require('axios');
const dotenv = require('dotenv');

// State tracking for balances
let mockBalances = {
  USDT: 5000,
  BTC: 0.1
};

// MOCKING PREPARATION
require.cache[require.resolve('dotenv')] = {
  exports: {
    config: () => ({ error: null, parsed: {} })
  }
};

const { binance, robinhood, feeds } = require('./trading-templates');

// Mock CCXT for Binance
ccxt.binance = class {
  constructor(config) { 
    this.config = config; 
    console.log(`[Engram Log] [Adapter:Binance] Initializing with API key ${config.apiKey.substring(0,4)}...`);
  }
  async fetchBalance() {
    console.log(`[Engram Log] [Adapter:Binance] Fetching balance...`);
    return { 
      USDT: { free: mockBalances.USDT, used: 0, total: mockBalances.USDT },
      BTC: { free: mockBalances.BTC, used: 0, total: mockBalances.BTC }
    };
  }
  async createOrder(symbol, side, quantity, price) {
    console.log(`[Engram Log] [Adapter:Binance] Normalizing Unified Payload to Binance. API Call: createOrder(${symbol}, ${side}, ${quantity})`);
    
    const feeRate = 0.001; // 0.1%
    const feeCost = quantity * feeRate;

    // Handle case-insensitive side (adapter passes 'BUY')
    if (side.toLowerCase() === 'buy') {
      mockBalances.BTC += (quantity - feeCost);
    }
    
    return { 
      id: 'binance-order-777', 
      status: 'filled', 
      symbol, 
      side, 
      quantity, 
      filled: quantity - feeCost,
      remaining: 0,
      fee: { currency: symbol.split('/')[0], cost: feeCost },
      timestamp: Date.now()
    };
  }
};

// Mock Axios for Feeds and Robinhood
axios.get = async (url) => {
  if (url.includes('api.x.com')) {
    console.log(`[Engram Log] [Adapter:Feeds] Fetching from X (Search query: BTC sentiment)`);
    return {
      data: {
        data: [
          { id: '1', text: 'BTC is going to the moon! Sentiment is very high today. #crypto #bullish' },
          { id: '2', text: 'Institutional adoption of BTC is increasing rapidly.' },
          { id: '3', text: 'Market looks strong for the week ahead.' }
        ],
        meta: { result_count: 3 }
      }
    };
  }
  if (url.includes('api.stlouisfed.org')) {
    console.log(`[Engram Log] [Adapter:Feeds] Fetching from FRED (Series: UNRATE)`);
    return {
      data: {
        observations: [
          { date: '2026-03-21', value: '3.5' }
        ]
      }
    };
  }
  return { data: {} };
};

axios.post = async (url, data, config) => {
  if (url.includes('robinhood.com')) {
    console.log(`[Engram Log] [Adapter:Robinhood] Normalizing Unified Payload. API Call: POST /orders (symbol: ${data.symbol}, side: ${data.side})`);
    return {
      data: {
        id: 'rh-order-888',
        state: 'filled',
        side: data.side,
        symbol: data.symbol,
        quantity: data.quantity,
        price: '65000.00',
        executions: [{ id: 'exec-1', price: '65000.00', quantity: data.quantity, fee: '2.50' }],
        updated_at: new Date().toISOString()
      }
    };
  }
  return { data: { success: true } };
};

const userConfig = {
  BINANCE_API_KEY: 'binance_key_123',
  BINANCE_SECRET: 'binance_secret_123',
  ROBINHOOD_API_KEY: 'rh_key_456',
  ROBINHOOD_ACCESS_TOKEN: 'rh_token_789',
  X_BEARER_TOKEN: 'x_token_abc',
  FRED_API_KEY: 'fred_key_def'
};

// Simple sentiment analysis mock
function analyzeSentiment(tweets) {
  const positiveWords = ['moon', 'bullish', 'high', 'increasing', 'good', 'great', 'strong'];
  let score = 0;
  tweets.forEach(t => {
    positiveWords.forEach(word => {
      if (t.text.toLowerCase().includes(word)) score += 0.2;
    });
  });
  return Math.min(score, 1.0);
}

async function runPredictExecuteWorkflow() {
  const workflowLogs = [];
  console.log("=== PREDICT-EXECUTE CHAIN VALIDATION STARTING ===\n");
  
  try {
    // 1. DATA GATHERING
    console.log("[Phase 1] DATA GATHERING & SEMANTIC NORMALIZATION");
    const xFeed = await feeds({ source: 'x', query: 'BTC sentiment' }, userConfig);
    const fredFeed = await feeds({ source: 'fred', query: 'UNRATE' }, userConfig);
    console.log(`- X Data normalized successfully. count=${xFeed.data.length}`);
    console.log(`- FRED Data normalized successfully. source=${fredFeed.source}\n`);

    // 2. CONTEXT ENRICHMENT & DECISION
    console.log("[Phase 2] CONTEXT ENRICHMENT & DECISION MAKING");
    const sentiment = analyzeSentiment(xFeed.data);
    const unemploymentRate = parseFloat(fredFeed.data[0].value);
    
    console.log(`[Agent Decision Engine] Processing enriched context: sentiment=${sentiment.toFixed(2)}, macro_indicator=${unemploymentRate}%`);
    
    const threshold = 0.7;
    const shouldBuy = sentiment > threshold;
    console.log(`[Agent Decision Engine] Output: ${shouldBuy ? 'TRIGGER_BUY' : 'WAIT'} (Threshold: ${threshold})\n`);

    // 3. MULTI-PLATFORM EXECUTION
    if (shouldBuy) {
      console.log("[Phase 3] MULTI-PLATFORM EXECUTION (Unified Dispatch)");
      
      const tradeOrder = {
        action: 'buy',
        symbol: 'BTC/USDT',
        quantity: 0.1,
        side: 'buy'
      };

      console.log(`[Engram Router] Dispatching Unified TradeOrder to [Binance, Robinhood]...`);
      const binanceResult = await binance(tradeOrder, userConfig);
      const robinhoodResult = await robinhood(tradeOrder, userConfig);
      
      console.log(`[Engram Unified Response] Binance status: ${binanceResult.status}, Fill: ${binanceResult.filled} BTC, Fee: ${binanceResult.fee.cost} BTC`);
      console.log(`[Engram Unified Response] Robinhood status: ${robinhoodResult.data.state}, Fill: ${robinhoodResult.data.quantity} BTC, Fee: $${robinhoodResult.data.executions[0].fee}\n`);
      
      workflowLogs.push({ 
        phase: 'execution', 
        binance: { fill: binanceResult.filled, fee: binanceResult.fee.cost },
        robinhood: { fill: robinhoodResult.data.quantity, fee: robinhoodResult.data.executions[0].fee }
      });
    }

    // 4. RESPONSE UNIFICATION & BALANCE REFLECTION
    console.log("[Phase 4] BALANCE REFLECTION & UNIFICATION");
    const finBalance = await binance({ action: 'balance' }, userConfig);
    console.log(`[Final State] Account Balance (Binance BTC): ${finBalance.BTC.total}`);
    
    workflowLogs.push({ phase: 'final_balance', btc: finBalance.BTC.total });

    console.log("\n=== FULL WORKFLOW VALIDATION COMPLETE (SUCCESS) ===");
    fs.writeFileSync('predict_execute_results.json', JSON.stringify({
        summary: "End-to-end predict-execute chain validation",
        timestamp: new Date().toISOString(),
        logs: workflowLogs,
        status: "PASSED"
    }, null, 2));

  } catch (error) {
    console.error("\n!!! WORKFLOW FAILURE DETECTED !!!");
    console.error(error);
    process.exit(1);
  }
}

runPredictExecuteWorkflow();

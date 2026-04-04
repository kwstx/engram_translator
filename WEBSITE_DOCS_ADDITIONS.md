# Website Documentation Update: New Features Guide

---

## 2. New Feature: Trading Semantic Templates
**Location Suggestions**: "Solutions" Page, "Fintech/DeFi" Section, or Developer API Reference.

### Copy for Solutions Page
**Title**: Multi-Platform Trading Templates  
**Subtitle**: One-click adapters for exchanges, predictions, and payments.  
**Description**:  
Stop writing custom API wrappers for every exchange. Engram’s Trading Semantic Templates provide a unified schema for trades, balance queries, and payment intents. Route the exact same payload to Binance, Coinbase, Robinhood, Kalshi, Stripe, or PayPal instantly. We handle the semantic mapping, authentication, and response unification.

### Technical Guide (The "In-Depth" Part)
**The Unified Schema**:
We've collapsed different API structures into four simple objects:
*   **Trade Order**: Covers limit/market/stop orders plus balance checks.
*   **Payment Intent**: Standardizes Stripe and PayPal flows.
*   **Feed Request**: Fetches live data from X, FRED, Reuters, and Bloomberg.
*   **Rich Response**: Normalizes heterogeneous platform data into one consistent JSON structure.

**Setup & Security**:
*   **Zero Shared Keys**: API keys are stored in your local `.env` and never touch Engram's central servers (if self-hosted).
*   **Drop-in Adapters**: Use `npm install @engram/trading-templates` to add support to your agent.

**Example Code (Unified Multi-Platform Order)**:
```ts
// The same object works for both Binance and Coinbase
const order = {
  tradeOrder: { symbol: 'BTC/USDT', action: 'limit', quantity: 0.05, price: 63000 }
};

await engram.routeTo('binance', order);
await engram.routeTo('coinbase', order);
```

---

## 3. Updates for Existing Pages

### `ABOUT_PAGE.md` Additions
*   **Add under "The Solution"**: 
    - "One-click multi-platform trading and payment adapters via semantic templates."
*   **Add under "The Vision"**:
    - "We are moving beyond simple chat."

### `FAQ_PAGE.md` Additions
**Q: Does Engram see my trading API keys?**  
**A**: No. If you are self-hosting Engram (via Docker or local install), your keys stay in your local environment. Engram only provides the translation logic to use them.


**Q: Can I fetch market data without placing a trade?**  
**A**: Yes. Use the `feeds` adapter within the Trading Templates to fetch sentiment, news, and economic indicators (FRED, X, etc.) independently.

### `MISSION.md` Additions
*   **New Key Goal**: 
    - **Execute Everywhere**: Enable agents to move value across crypto, prediction markets, and fiat rails using a single semantic standard.

---

## 4. Documentation Mapping (Quick Reference)

| Topic | File/Page to Update | Depth |
| :--- | :--- | :--- |
| **Logic/Workflow** | `ARCHITECTURE.md` | In-depth (API flow) |
| **Developer API** | `API_REFERENCE.md` | High (Add `tradeOrder` and `feedRequest` schemas) |
| **Case Studies** | `USE_CASES.md` | High (Predict-Execute loop example) |

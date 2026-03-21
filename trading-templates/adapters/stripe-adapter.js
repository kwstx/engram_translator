const axios = require('axios');

/**
 * mapAndExecuteStripe - Stripe Adapter for Unified Trade Schema Payment Intents
 *
 * This adapter uses axios to interact with the Stripe Payment Intents API.
 * It maps the unifiedIntent to Stripe's expected format.
 *
 * @param {Object} unifiedIntent - The intent object conforming to the unified-trade-schema.
 * @param {Object} userConfig - User configuration containing STRIPE_SECRET_KEY.
 * @returns {Promise<Object>} - The response from Stripe.
 */
async function mapAndExecuteStripe(unifiedIntent, userConfig) {
  return await axios.post('https://api.stripe.com/v1/payment_intents', {
    amount: unifiedIntent.amount * 100,
    currency: unifiedIntent.currency,
    customer: unifiedIntent.customerId
  }, {
    headers: {
      Authorization: `Bearer ${userConfig.STRIPE_SECRET_KEY}`
    }
  });
}

module.exports = { mapAndExecuteStripe };

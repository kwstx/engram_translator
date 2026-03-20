const axios = require('axios');

/**
 * mapAndExecutePayPal - PayPal Adapter for Unified Trade Schema Payment Intents
 *
 * This adapter uses axios to interact with the PayPal Orders API.
 * It first retrieves an access token via OAuth2 with client credentials.
 * Then it executes the order creation.
 *
 * @param {Object} unifiedIntent - The intent object conforming to the unified-trade-schema.
 * @param {Object} userConfig - User configuration containing PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET.
 * @returns {Promise<Object>} - The final response from PayPal.
 */
async function mapAndExecutePayPal(unifiedIntent, userConfig) {
  const auth = Buffer.from(`${userConfig.PAYPAL_CLIENT_ID}:${userConfig.PAYPAL_CLIENT_SECRET}`).toString('base64');
  
  const tokenResponse = await axios.post('https://api-m.paypal.com/v1/oauth2/token', 'grant_type=client_credentials', {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Authorization': `Basic ${auth}`
    }
  });

  const accessToken = tokenResponse.data.access_token;

  return await axios.post('https://api-m.paypal.com/v2/checkout/orders', {
    intent: 'CAPTURE',
    purchase_units: [{
      amount: {
        currency_code: (unifiedIntent.currency || 'USD').toUpperCase(),
        value: unifiedIntent.amount.toString()
      },
      reference_id: unifiedIntent.customerId
    }]
  }, {
    headers: {
      Authorization: `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  });
}

module.exports = { mapAndExecutePayPal };

const axios = require('axios');
const dotenv = require('dotenv');

dotenv.config();

/**
 * getXFirehose - Fetches recent tweets from X (Twitter) using the query from the unified feed.
 * GET https://api.x.com/2/tweets/search/recent?query=unifiedFeed.query
 * 
 * @param {Object} unifiedFeed - The unified feed object containing the search query.
 * @param {Object} userConfig - Configuration containing X_BEARER_TOKEN.
 * @returns {Promise<Object>} - The latest tweets and metadata.
 */
async function getXFirehose(unifiedFeed, userConfig) {
  const url = `https://api.x.com/2/tweets/search/recent?query=${encodeURIComponent(unifiedFeed.query)}`;
  const response = await axios.get(url, {
    headers: {
      Authorization: `Bearer ${userConfig.X_BEARER_TOKEN}`,
    },
  });
  return response.data;
}

/**
 * getFREDIndicator - Fetches economic indicator observations from St. Louis Fed (FRED).
 * GET https://api.stlouisfed.org/fred/series/observations?series_id=unifiedFeed.query&api_key=userConfig.FRED_API_KEY
 * 
 * @param {Object} unifiedFeed - The unified feed object containing the series ID in the query field.
 * @param {Object} userConfig - Configuration containing FRED_API_KEY.
 * @returns {Promise<Object>} - The observations and metadata.
 */
async function getFREDIndicator(unifiedFeed, userConfig) {
  const url = `https://api.stlouisfed.org/fred/series/observations?series_id=${unifiedFeed.query}&api_key=${userConfig.FRED_API_KEY}&file_type=json`;
  const response = await axios.get(url);
  return response.data;
}

/**
 * getReutersIndicator - Placeholder for Reuters paid endpoint (sentiment/news).
 * @param {Object} unifiedFeed - The unified feed object.
 * @param {Object} userConfig - Configuration for Reuters (REUTERS_APP_KEY, etc.).
 * @returns {Promise<Object>} - Placeholder response.
 */
async function getReutersIndicator(unifiedFeed, userConfig) {
  console.log('Reuters placeholder called for query:', unifiedFeed.query);
  return {
    source: 'reuters',
    status: 'placeholder',
    message: 'Reuters integration requires an enterprise license and institutional partner key.'
  };
}

/**
 * getBloombergIndicator - Placeholder for Bloomberg paid endpoint (economic indicators).
 * @param {Object} unifiedFeed - The unified feed object.
 * @param {Object} userConfig - Configuration for Bloomberg (BLOOMBERG_SERVICE_ID, etc.).
 * @returns {Promise<Object>} - Placeholder response.
 */
async function getBloombergIndicator(unifiedFeed, userConfig) {
  console.log('Bloomberg placeholder called for query:', unifiedFeed.query);
  return {
    source: 'bloomberg',
    status: 'placeholder',
    message: 'Bloomberg Terminal access requires dedicated hardware/license and local B-PIPE server.'
  };
}

module.exports = {
  getXFirehose,
  getFREDIndicator,
  getReutersIndicator,
  getBloombergIndicator
};

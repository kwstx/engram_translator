const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    baseUrl: process.env.CYPRESS_BASE_URL || "http://localhost:8001",
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    video: false,
    screenshotOnRunFailure: true,
    env: {
      AUTH_JWT_SECRET:
        process.env.CYPRESS_AUTH_JWT_SECRET || "local-test-secret",
      AUTH_ISSUER:
        process.env.CYPRESS_AUTH_ISSUER || "https://auth.example.com/",
      AUTH_AUDIENCE:
        process.env.CYPRESS_AUTH_AUDIENCE || "translator-middleware",
    },
  },
});

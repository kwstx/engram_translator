const jwt = require("jsonwebtoken");

const buildToken = (scopes) => {
  const now = Math.floor(Date.now() / 1000);
  const payload = {
    sub: "cypress-user",
    iss: Cypress.env("AUTH_ISSUER"),
    aud: Cypress.env("AUTH_AUDIENCE"),
    iat: now,
    exp: now + 60 * 60,
    scope: scopes.join(" "),
  };

  return jwt.sign(payload, Cypress.env("AUTH_JWT_SECRET"), {
    algorithm: "HS256",
  });
};

const authHeaders = (scopes) => ({
  Authorization: `Bearer ${buildToken(scopes)}`,
});

describe("API E2E smoke", () => {
  it("reports metrics endpoint", () => {
    cy.request("/metrics").then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body).to.include("translations_total");
    });
  });

  it("translates A2A -> MCP via beta endpoint", () => {
    cy.request({
      method: "POST",
      url: "/api/v1/beta/translate",
      headers: authHeaders(["translate:beta"]),
      body: {
        source_protocol: "A2A",
        target_protocol: "MCP",
        payload: {
          payload: {
            intent: "dispatch",
          },
        },
      },
    }).then((response) => {
      expect(response.status).to.eq(200);
      expect(response.body.status).to.eq("success");
      expect(response.body.payload).to.have.property("data_bundle");
    });
  });

  it("returns a 422 when no route exists (A2A -> ACP)", () => {
    cy.request({
      method: "POST",
      url: "/api/v1/beta/translate",
      headers: authHeaders(["translate:beta"]),
      failOnStatusCode: false,
      body: {
        source_protocol: "A2A",
        target_protocol: "ACP",
        payload: {
          payload: {
            intent: "force_failure",
          },
        },
      },
    }).then((response) => {
      expect(response.status).to.eq(422);
      expect(response.body).to.have.property("detail");
    });
  });
});

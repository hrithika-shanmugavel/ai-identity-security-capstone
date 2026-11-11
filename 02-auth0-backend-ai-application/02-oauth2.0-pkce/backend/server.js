
require("dotenv").config();

const express = require("express");
const cors = require("cors");
const { auth } = require("express-openid-connect");
const { createRemoteJWKSet, jwtVerify } = require("jose");

const app = express();

app.use(express.json());

app.use(
  cors({
    origin: process.env.FRONTEND_URL,
    credentials: true
  })
);

const DOMAIN = process.env.AUTH0_DOMAIN;
const AUDIENCE = process.env.AUTH0_AUDIENCE;
const ISSUER = `https://${DOMAIN}/`;

const JWKS = createRemoteJWKSet(
  new URL(`https://${DOMAIN}/.well-known/jwks.json`)
);

// Auth0 Regular Web Application configuration
app.use(
  auth({
    authRequired: false,
    auth0Logout: true,

    secret: process.env.SESSION_SECRET,
    baseURL: process.env.BASE_URL,
    routes: {
      postLogoutRedirect: process.env.FRONTEND_URL
    },
    logoutParams: {
      federated: true
    },

    clientID: process.env.AUTH0_CLIENT_ID,
    clientSecret: process.env.AUTH0_CLIENT_SECRET,

    issuerBaseURL: ISSUER,

    authorizationParams: {
      response_type: "code",
      audience: AUDIENCE,
      scope: "openid profile email read:ai-data write:admin"
    }
  })
);

// Return to React after logout
app.get("/", (req, res) => {
  res.redirect(process.env.FRONTEND_URL);
});

// Check whether user is logged in
function requireLogin(req, res, next) {
  if (!req.oidc.isAuthenticated()) {
    return res.status(401).json({
      error: "Please login first"
    });
  }

  next();
}

// Verify Auth0 access token
async function getVerifiedPayload(req) {
  const accessToken = req.oidc.accessToken?.access_token;

  if (!accessToken) {
    throw new Error("Access token unavailable");
  }

  const { payload } = await jwtVerify(
    accessToken,
    JWKS,
    {
      issuer: ISSUER,
      audience: AUDIENCE,
      algorithms: ["RS256"]
    }
  );

  return { accessToken, payload };
}

// Permission checking middleware
function requirePermission(permission) {
  return async (req, res, next) => {
    try {
      const { payload } = await getVerifiedPayload(req);

      const permissions = payload.permissions || [];

      if (!permissions.includes(permission)) {
        return res.status(403).json({
          error: "Forbidden",
          message: `Missing permission: ${permission}`
        });
      }

      req.tokenPayload = payload;
      next();

    } catch (error) {
      console.error(error.message);

      return res.status(401).json({
        error: "Unauthorized",
        message: "Invalid or expired access token"
      });
    }
  };
}

// Get authenticated user and permissions
app.get("/api/session", requireLogin, async (req, res) => {
  try {
    const { payload } = await getVerifiedPayload(req);

    res.json({
      authenticated: true,
      user: {
        name: req.oidc.user.name,
        email: req.oidc.user.email
      },
      permissions: payload.permissions || []
    });

  } catch (error) {
    res.status(401).json({
      error: "Unable to verify access token"
    });
  }
});

// Endpoint 1: Normal user access
app.get(
  "/api/ai-data",
  requireLogin,
  requirePermission("read:ai-data"),
  (req, res) => {
    res.json({
      status: 200,
      message: "AI data accessed successfully",
      data: "This is protected AI data."
    });
  }
);

// Endpoint 2: Admin-only access
app.post(
  "/api/admin",
  requireLogin,
  requirePermission("write:admin"),
  (req, res) => {
    res.json({
      status: 200,
      message: "Welcome Admin!",
      data: "Administrative operation completed."
    });
  }
);

// Development-only: obtain JWT for jwt.io inspection
app.get(
  "/api/dev/access-token",
  requireLogin,
  async (req, res) => {
    if (process.env.NODE_ENV === "production") {
      return res.sendStatus(404);
    }

    try {
      const { accessToken } = await getVerifiedPayload(req);

      res.json({
        access_token: accessToken
      });

    } catch (error) {
      res.status(401).json({
        error: "Unable to retrieve access token"
      });
    }
  }
);

app.listen(3000, () => {
  console.log("Backend running at http://localhost:3000");
});

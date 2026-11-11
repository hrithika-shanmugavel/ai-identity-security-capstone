
import { useEffect, useState } from "react";
import "./App.css";

const API = "https://vigilant-adventure-6vwj7jpp4pqw39vg-3000.app.github.dev";

function App() {
  const [user, setUser] = useState(null); // stores (email, name)
  const [permissions, setPermissions] = useState([]); // read: ai-data, write:admin
  const [loading, setLoading] = useState(true);
  const [results, setResults] = useState({}); // response from API endpoints
  const [token, setToken] = useState(""); // JWT Access Token from Auth0

  // checkSession verifies if the user has an active session and retrieves user info and permissions.
  async function checkSession() {
    try {
      const response = await fetch(`${API}/api/session`, {
        credentials: "include"
      });

      if (!response.ok) {
        setUser(null);
        return;
      }

      const data = await response.json();

      setUser(data.user);
      setPermissions(data.permissions || []);

    } catch (error) {
      console.error(error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    checkSession();
  }, []);

  // login redirects the user to the Auth0 login page.
  function login() {
    window.location.href = `${API}/login`;
  }

  // logout redirects the user to the Auth0 logout page.
  function logout() {
    window.location.href = `${API}/logout`; 
  }

  async function callEndpoint(name, path, method) {
    setResults(prev => ({
      ...prev,
      [name]: { loading: true }
    }));

    try {
      const response = await fetch(`${API}${path}`, {
        method,
        credentials: "include"
      });

      const data = await response.json();

      setResults(prev => ({
        ...prev,
        [name]: {
          status: response.status,
          data
        }
      }));

    } catch (error) {
      setResults(prev => ({
        ...prev,
        [name]: {
          status: "Error",
          data: { message: error.message }
        }
      }));
    }
  }

  async function getJWT() {
    try {
      const response = await fetch(
        `${API}/api/dev/access-token`,
        { credentials: "include" }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error);
      }

      setToken(data.access_token);

    } catch (error) {
      alert(error.message);
    }
  }

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="app">
      {!user ? (

        <main className="welcome">
          <h2>Welcome to SecureNova Inc.</h2>
          <p>
            Sign in to access the AI powered Customer Service.
          </p>

          <button className="login main-login" onClick={login}>
            Login with Auth0
          </button>
        </main>

      ) : (

        <main className="dashboard">

          <div className="user-section">
            <span>{user.email}</span>
            <button className="logout" onClick={logout}>
              Logout
            </button>
          </div>

          <h2>API Dashboard</h2>

          <p className="welcome-user">
            Welcome, {user.name}
          </p>

        {/*
          <div className="permission-box">
            <h3>Your permissions</h3>

            {permissions.map(permission => (
              <span className="permission" key={permission}>
                {permission}
              </span>
            ))}
          </div>
        */}

          <div className="endpoint-grid">

            <div className="endpoint-card">
              <div className="endpoint-heading">
                <span className="method get">GET</span>
                <span className="endpoint">/api/ai-data</span>
                <button
                  className="call-endpoint-button"
                  onClick={() =>
                    callEndpoint(
                      "ai",
                      "/api/ai-data",
                      "GET"
                    )
                  }
                >
                  Send
                </button>
              </div>

              <span className="permission-text">
                Permission (Scope): read:ai-data
              </span>

              {results.ai && (
                <pre>
                  {results.ai.loading
                    ? "Loading..."
                    : JSON.stringify(results.ai, null, 2)}
                </pre>
              )}
            </div>

            <div className="endpoint-card">
              <div className="endpoint-heading">
                <span className="method post">POST</span>
                <span className="endpoint">/api/admin</span>
                <button className="call-endpoint-button"
                  onClick={() =>
                    callEndpoint(
                      "admin",
                      "/api/admin",
                      "POST"
                    )
                  }
                >Send</button>
              </div>

              <span className="permission-text">
                Permission (Scope): write:admin
              </span>

              {results.admin && (
                <pre>
                  {results.admin.loading
                    ? "Loading..."
                    : JSON.stringify(results.admin, null, 2)}
                </pre>
              )}
            </div>

          </div>

          <div className="jwt-section">
            <h3>JWT Access Token</h3>

            <span className="retrieve-jwt-token-text">
              Retrieve your Auth0 access token
              and inspect its claims.
            </span>

            <button className="access-jwt-token-button" onClick={getJWT}>
              Obtain JWT Access Token
            </button>

            {token && (
              <>
                <textarea
                  value={token}
                  readOnly
                  rows={5}
                />

                <button className="copy-jwt-button"
                  onClick={() =>
                    navigator.clipboard.writeText(token)
                  }
                >
                  Copy JWT
                </button>

                <a
                  href="https://jwt.io/"
                  target="_blank"
                  rel="noreferrer"
                  className="decode-jwt-link"
                >
                  Decode on jwt.io
                </a>
              </>
            )}
          </div>

        </main>
      )}

    </div>
  );
}

export default App;

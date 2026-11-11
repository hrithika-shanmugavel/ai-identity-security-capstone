
import { useAuth0 } from '@auth0/auth0-react';
import { useState, useEffect } from 'react';

function App() {
  const {
    loginWithRedirect,
    logout,
    isAuthenticated,
    user,
    getIdTokenClaims,
    isLoading
  } = useAuth0();

  const [token, setToken] = useState('');
  const [error, setError] = useState('');

  // Automatically retrieve ID token after login
  useEffect(() => {
    const fetchToken = async () => {
      if (isAuthenticated) {
        try {
          const claims = await getIdTokenClaims();

          if (claims) {
            setToken(claims.__raw);
          }
        } catch (err) {
          setError(err.message);
        }
      }
    };

    fetchToken();
  }, [isAuthenticated, getIdTokenClaims]);

  // Copy ID token
  const copyToken = async () => {
    try {
      await navigator.clipboard.writeText(token);
      alert('ID Token copied successfully!');
    } catch (err) {
      setError('Unable to copy token. Please select and copy it manually.');
    }
  };

  if (isLoading) {
    return <h2>Loading Auth0...</h2>;
  }

  return (
    <div style={{
      padding: '40px',
      fontFamily: 'Arial',
      maxWidth: '900px',
      margin: 'auto'
    }}>

      <h1>Auth0 Agent Identity Demo</h1>

      {!isAuthenticated ? (
        <>
          <p>Please log in to obtain your ID token.</p>

          <button
            onClick={() =>
              loginWithRedirect({
                authorizationParams: {
                  prompt: 'login'
                }
              })
            }
          >
            Login with Auth0
          </button>
        </>
      ) : (
        <>
          <h2>Login Successful!</h2>

          <p>
            <strong>User:</strong>{' '}
            {user.name || user.email}
          </p>

          <h3>Your ID Token</h3>

          {token ? (
            <>
              <textarea
                value={token}
                readOnly
                rows={10}
                style={{
                  width: '100%',
                  padding: '10px',
                  boxSizing: 'border-box',
                  fontSize: '12px',
                  wordBreak: 'break-all'
                }}
              />

              <br /><br />

              <button onClick={copyToken}>
                Copy ID Token
              </button>

              <button
                onClick={() =>
                  window.open('https://jwt.io/', '_blank')
                }
                style={{ marginLeft: '10px' }}
              >
                Open jwt.io
              </button>
            </>
          ) : (
            <p>Retrieving ID token...</p>
          )}

          {error && <p style={{ color: 'red' }}>{error}</p>}

          <br /><br />

          <button
            onClick={() =>
              logout({
                logoutParams: {
                  returnTo: window.location.origin
                }
              })
            }
          >
            Logout
          </button>
        </>
      )}
    </div>
  );
}

export default App;

import { useState } from "react";

function Login({ handleLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  function submitLogin(event) {
    event.preventDefault();

    handleLogin(username, password, setMessage);
  }

  return (
    <div className="page">
      <h1 className="page-title">UC Merced</h1>

      <div className="login-card">
        <h1>Welcome Back</h1>

        <p className="subtitle">
          Log in to Dashboard
        </p>

        <form onSubmit={submitLogin}>
          <div className="input-group">
            <label htmlFor="username">
              Username
            </label>

            <input
              id="username"
              type="text"
              placeholder="Enter your username"
              value={username}
              onChange={(event) => {
                setUsername(event.target.value);
              }}
            />
          </div>

          <div className="input-group">
            <label htmlFor="password">
              Password
            </label>

            <input
              id="password"
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(event) => {
                setPassword(event.target.value);
              }}
            />
          </div>

          <button
            className="login-button"
            type="submit"
          >
            Log In
          </button>

          {message !== "" && (
            <p className="message">
              {message}
            </p>
          )}
        </form>
      </div>
    </div>
  );
}

export default Login;
import { useState } from "react";
import "./App.css";

function App() 
{
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  function handleLogin(event) 
  {
    event.preventDefault();

    if (email.trim() === "" || password.trim() === "") 
    {
      alert("Please enter both email and password.");
      return;
    }

    setMessage("Login button clicked. Backend is not connected yet.");
  }

  return (
    
    <div className="page">

      <h1 className="page-title">UC Merced</h1>

      <div className="login-card">

        <h1>Welcome Back</h1>
        <p className="subtitle">Log in to Dashboard</p>

        <form onSubmit={handleLogin}>

          <div className="input-group">

            <label>Email</label>

            <input
              type="email"
              placeholder="Enter your email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
            />

          </div>

          <div className="input-group">

            <label>Password</label>

            <input
              type="password"
              placeholder="Enter your password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
            />
          </div>

          <button type="submit">Log In</button>

          {message !== "" && <p className="message">{message}</p>}

        </form>
      </div>
    </div>
  );
}

export default App;

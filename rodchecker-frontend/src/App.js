import { useState, useEffect } from "react";
import axios from "axios";

function App() {
  // States
  const [email, setEmail] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  // 🔐 Auth-related states
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [username, setUsername] = useState(localStorage.getItem("username") || "");
  const [usernameInput, setUsernameInput] = useState("");
  const [passwordInput, setPasswordInput] = useState("");
  const [showAuth, setShowAuth] = useState(false);

  // 📨 Submit email for prediction
  const handleSubmit = async () => {
    try {
      setLoading(true);
      const res = await axios.post(
        "http://localhost:5000/predict",
        { email },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setResult(res.data.prediction);
    } catch (error) {
      console.error(error);
      setResult("❌ Unauthorized or API error.");
    } finally {
      setLoading(false);
    }
  };

  // 🔐 Login
  const handleLogin = async () => {
    try {
      const res = await axios.post("http://localhost:5000/login", {
        username: usernameInput,
        password: passwordInput,
      });
      setToken(res.data.access_token);
      setUsername(usernameInput);
      localStorage.setItem("token", res.data.access_token);
      localStorage.setItem("username", usernameInput);
      setShowAuth(false);
    } catch (err) {
      alert("❌ Login failed. Check your credentials.");
    }
  };

  // 🆕 Register
  const handleRegister = async () => {
    try {
      await axios.post("http://localhost:5000/register", {
        username: usernameInput,
        password: passwordInput,
      });
      alert("✅ User registered! You can now log in.");
    } catch (err) {
      alert("❌ Username already exists.");
    }
  };

  return (
    <>
      {/* MAIN CONTENT */}
      <div style={{ maxWidth: "600px", margin: "50px auto", textAlign: "center", fontFamily: "Arial" }}>
        <h1>RodChecker 🛡️</h1>
        <textarea
          style={{ width: "100%", height: "200px", padding: "10px", fontSize: "16px" }}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Paste the email text here..."
        />
        <br />
        <button
          style={{ marginTop: "20px", padding: "10px 30px", fontSize: "18px", cursor: "pointer" }}
          onClick={handleSubmit}
          disabled={loading || email.trim() === ""}
        >
          {loading ? "Checking..." : "Check Email"}
        </button>
        {result && (
          <h2 style={{ marginTop: "30px" }}>
            Result: <span>{result}</span>
          </h2>
        )}
      </div>

      {/* AUTH AREA */}
      <div style={{ position: "absolute", top: 10, right: 20 }}>
        {!token ? (
          <button onClick={() => setShowAuth(!showAuth)}>🔒 Login</button>
        ) : (
          <span>
            👤 {username}{" "}
            <button onClick={() => {
              setToken(""); setUsername(""); localStorage.clear();
            }}>
              🚪 Logout
            </button>
          </span>
        )}
      </div>

      {showAuth && (
        <div style={{
          position: "absolute", top: 50, right: 20, background: "#f4f4f4",
          padding: 15, borderRadius: 10
        }}>
          <input placeholder="Username" onChange={(e) => setUsernameInput(e.target.value)} /><br />
          <input placeholder="Password" type="password" onChange={(e) => setPasswordInput(e.target.value)} /><br />
          <button onClick={handleLogin}>Login</button>
          <button onClick={handleRegister}>Register</button>
        </div>
      )}
    </>
  );
}

export default App;

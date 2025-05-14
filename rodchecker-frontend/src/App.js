import React, { useState, useEffect } from "react";
import axios from "axios";
import { PieChart, Pie, Cell, Tooltip } from "recharts";
import logo from "./rodchecker_logo.png";

const COLORS = ["#00C49F", "#FF8042"]; // legit, phishing

// Error boundary to catch render errors in Dashboard
class Boundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return <p>Whoops! Something went wrong.</p>;
    }
    return this.props.children;
  }
}

// Dashboard now accepts a refreshCount prop to re-fetch data on demand
function Dashboard({ token, refreshCount }) {
  const [data, setData] = useState({ total: 0, legit: 0, phishing: 0 });
  const [isReady, setIsReady] = useState(false);
  const [unauthorized, setUnauthorized] = useState(false);

  useEffect(() => {
    if (!token) return;
    setIsReady(false);
    setUnauthorized(false);
    axios
      .get("http://localhost:5000/dashboard", {
        headers: { Authorization: `Bearer ${token}` },
        withCredentials: true,
      })
      .then((res) => {
        const { total, legit, phishing } = res.data || {};
        setData({
          total: Number(total) || 0,
          legit: Number(legit) || 0,
          phishing: Number(phishing) || 0,
        });
        setIsReady(true);
      })
      .catch((err) => {
        console.error("Dashboard error:", err);
        if (err.response && err.response.status === 401) {
          setUnauthorized(true);
        } else {
          alert("Failed to load dashboard data.");
        }
      });
  }, [token, refreshCount]); // re-run whenever refreshCount changes

  if (!token || unauthorized) {
    return <p>Please log in to see your stats.</p>;
  }
  if (!isReady) {
    return <p>📉 Loading chart...</p>;
  }

  const chartData = [
    { name: "Legit ✅", value: Number(data.legit) || 0 },
    { name: "Phishing 🚨", value: Number(data.phishing) || 0 },
  ];

  if (!chartData.every((d) => typeof d.value === "number" && !isNaN(d.value))) {
    return <p>Error: invalid chart data.</p>;
  }

  return (
    <div style={{ textAlign: "center", marginTop: 50 }}>
      <h2>📊 Your RodChecker Stats</h2>
      <p>Total Emails Checked: {data.total}</p>
      <PieChart
        width={300}
        height={300}
        style={{ display: "block", margin: "0 auto" }}
      >
        <Tooltip />
        <Pie
          data={chartData}
          dataKey="value"
          nameKey="name"
          outerRadius={100}
          label={false}
        >
          {chartData.map((entry, index) => (
            <Cell
              key={`cell-${index}`}
              fill={COLORS[index % COLORS.length]}
            />
          ))}
        </Pie>
      </PieChart>
    </div>
  );
}

function App() {
  const [email, setEmail] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);
  const [refreshCount, setRefreshCount] = useState(0); // tracks when to reload dashboard

  const [token, setToken] = useState(
    localStorage.getItem("token") || ""
  );
  const [username, setUsername] = useState(
    localStorage.getItem("username") || ""
  );
  const [usernameInput, setUsernameInput] = useState("");
  const [passwordInput, setPasswordInput] = useState("");
  const [showAuth, setShowAuth] = useState(false);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const res = await axios.post(
        "http://localhost:5000/predict",
        { email },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const pred = res.data?.prediction;
      setResult(
        typeof pred === "string" ? pred : JSON.stringify(pred)
      );
      // bump refreshCount so Dashboard re-fetches
      setRefreshCount((c) => c + 1);
    } catch (error) {
      console.error("Predict error:", error);
      setResult("❌ Unauthorized or API error.");
    } finally {
      setLoading(false);
    }
  };

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
      <div
        style={{
          maxWidth: "600px",
          margin: "50px auto",
          textAlign: "center",
          fontFamily: "Arial",
        }}
      >
        <h1 style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "10px" }}>
          <img src={logo} alt="RodChecker Logo" style={{ height: 40 }} />
          RodChecker
        </h1>
        <textarea
          style={{ width: "100%", height: "200px", padding: "10px", fontSize: 16 }}
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Paste the email text here..."
        />
        <br />
        <button
          style={{ marginTop: "20px", padding: "10px 30px", fontSize: 18, cursor: "pointer" }}
          onClick={handleSubmit}
          disabled={loading || email.trim() === ""}
        >
          {loading ? "Checking..." : "Check Email"}
        </button>
        {result && (
          <h2 style={{ marginTop: 30 }}>Result: {result}</h2>
        )}
        {token && (
          <Boundary>
            <Dashboard token={token} refreshCount={refreshCount} />
          </Boundary>
        )}
      </div>
      <div style={{ position: "absolute", top: 10, right: 20 }}>
        {!token ? (
          <button onClick={() => setShowAuth((s) => !s)}>🔒 Login</button>
        ) : (
          <span>
            👤 {username} <button onClick={() => { setToken(""); localStorage.clear(); }}>🚪 Logout</button>
          </span>
        )}
      </div>
      {showAuth && (
        <div
          style={{ position: "absolute", top: 50, right: 20, background: "#f4f4f4", padding: 15, borderRadius: 10 }}
        >
          <input
            placeholder="Username"
            value={usernameInput}
            onChange={(e) => setUsernameInput(e.target.value)}
          />
          <br />
          <input
            placeholder="Password"
            type="password"
            value={passwordInput}
            onChange={(e) => setPasswordInput(e.target.value)}
          />
          <br />
          <button onClick={handleLogin}>Login</button>
          <button onClick={handleRegister}>Register</button>
        </div>
      )}
    </>
  );
}

export default App;

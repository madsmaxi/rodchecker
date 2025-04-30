import { useState } from "react";
import axios from "axios";

function App() {
  const [email, setEmail] = useState("");
  const [result, setResult] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      const res = await axios.post("http://localhost:5000/predict", { email });
      setResult(res.data.prediction);
    } catch (error) {
      console.error(error);
      setResult("Error contacting RodChecker API 😞");
    } finally {
      setLoading(false);
    }
  };

  return (
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
  );
}

export default App;

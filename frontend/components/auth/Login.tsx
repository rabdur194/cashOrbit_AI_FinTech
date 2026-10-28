import { useState } from "react";
import { ArrowUpRight } from "lucide-react";
export function Login({
  onLogin,
  error,
}: {
  onLogin: (e: string, p: string) => void;
  error: string;
}) {
  const [email, setEmail] = useState("demo@cashorbit.local");
  const [password, setPassword] = useState("CashOrbitDemo123!");
  return (
    <div className="login-wrap">
      <div className="login-art">
        <div className="brand">
          <div className="brand-mark">C</div>cashorbit
          <span style={{ color: "#20c997" }}>.</span>
        </div>
        <div>
          <div className="eyebrow" style={{ color: "#38d6a5" }}>
            FINANCIAL OPERATIONS, CONNECTED
          </div>
          <h1>Make every payment tell a clearer story.</h1>
          <p>
            Receivables, reconciliation and working-capital insights in one
            workspace. Built for teams that need more control over their cash
            flow.
          </p>
          <div style={{ display: "flex", gap: 22, marginTop: 35 }}>
            <div>
              <strong style={{ fontSize: 20 }}>01</strong>
              <div style={{ fontSize: 10, color: "#9eafc6", marginTop: 4 }}>
                One finance workspace
              </div>
            </div>
            <div>
              <strong style={{ fontSize: 20 }}>02</strong>
              <div style={{ fontSize: 10, color: "#9eafc6", marginTop: 4 }}>
                Clear audit history
              </div>
            </div>
            <div>
              <strong style={{ fontSize: 20 }}>03</strong>
              <div style={{ fontSize: 10, color: "#9eafc6", marginTop: 4 }}>
                Smarter collections
              </div>
            </div>
          </div>
        </div>
        <div style={{ fontSize: 10, color: "#778aa5" }}>
          CASHORBIT MVP · DEMO DATA ONLY
        </div>
      </div>
      <div className="login-content">
        <div className="login-card">
          <div className="eyebrow">WELCOME BACK</div>
          <h2>Sign in to CashOrbit</h2>
          <p>Access your financial operations workspace.</p>
          {error && <div className="notice error">{error}</div>}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              onLogin(email, password);
            }}
          >
            <div className="field">
              <label>Work email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div className="field">
              <label>Password</label>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
            <button className="button">
              Sign in securely <ArrowUpRight size={15} />
            </button>
          </form>
          <div className="demo-note">
            <strong>Demo credentials</strong>
            <br />
            Email: demo@cashorbit.local
            <br />
            Password: CashOrbitDemo123!
            <br />
            <span style={{ color: "#a16a17" }}>
              Local demo only. Change credentials and secrets before any public
              deployment.
            </span>
          </div>
          <div
            style={{
              textAlign: "center",
              fontSize: 10,
              color: "#9aa4b3",
              marginTop: 24,
            }}
          >
            Protected workspace · Role-based access · Audit history
          </div>
        </div>
      </div>
    </div>
  );
}

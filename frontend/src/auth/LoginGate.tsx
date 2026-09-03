import { type FormEvent, type ReactNode, useState } from "react";

import { api, ApiError } from "../lib/api";
import { clearCreds, hasCreds, setCreds } from "../lib/auth";

export default function LoginGate({ children }: { children: ReactNode }) {
  const [authed, setAuthed] = useState(hasCreds());
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    setCreds(username, password);
    try {
      await api.ping();
      setAuthed(true);
    } catch (err) {
      clearCreds();
      setError(
        err instanceof ApiError && err.status === 401
          ? "Wrong username or password."
          : "Could not reach the server.",
      );
    } finally {
      setBusy(false);
    }
  }

  if (authed) return <>{children}</>;

  return (
    <main className="login">
      <h1>Wardrobe Manager</h1>
      <form onSubmit={submit}>
        <label>
          Username
          <input value={username} onChange={(e) => setUsername(e.target.value)} autoFocus />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button disabled={busy}>{busy ? "Checking…" : "Sign in"}</button>
      </form>
    </main>
  );
}

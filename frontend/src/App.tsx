import { useEffect, useState } from "react";

type Health = { status: string; environment: string };

export default function App() {
  const [health, setHealth] = useState<Health | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/health")
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json() as Promise<Health>;
      })
      .then(setHealth)
      .catch((e: unknown) => setError(String(e)));
  }, []);

  return (
    <main>
      <h1>Wardrobe Manager</h1>
      <p>Phase 0 — scaffold. Nothing to see here yet.</p>
      <p>
        API health:{" "}
        {health ? (
          <strong>
            {health.status} ({health.environment})
          </strong>
        ) : error ? (
          <span>unreachable — {error}</span>
        ) : (
          <span>checking…</span>
        )}
      </p>
    </main>
  );
}

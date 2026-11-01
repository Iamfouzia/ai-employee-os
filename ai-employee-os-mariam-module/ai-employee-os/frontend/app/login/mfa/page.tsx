"use client";

import { Suspense, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { setToken } from "@/lib/api";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function MfaForm() {
  const router = useRouter();
  const params = useSearchParams();
  const email = params.get("email") || "";
  const [code, setCode] = useState("");
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    const res = await fetch(`${API_BASE}/api/auth/mfa/verify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, code }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      setError(body.detail || "Invalid code.");
      return;
    }
    const data = await res.json();
    setToken(data.access_token);
    router.push("/dashboard");
  }

  return (
    <main className="min-h-screen flex items-center justify-center px-6">
      <form onSubmit={handleSubmit} className="w-full max-w-sm border border-line bg-panel rounded-md p-8">
        <h1 className="font-display text-2xl font-semibold text-paper mb-1">Two-factor code</h1>
        <p className="text-sm text-muted mb-6">Enter the 6-digit code from your authenticator app.</p>

        <input
          type="text"
          inputMode="numeric"
          maxLength={6}
          required
          value={code}
          onChange={(e) => setCode(e.target.value)}
          className="w-full mb-6 rounded-sm bg-ink border border-line px-3 py-2 text-paper tracking-[0.5em] text-center font-mono focus-visible:border-signal"
        />

        {error && <p className="text-danger text-sm mb-4">{error}</p>}

        <button
          type="submit"
          className="w-full rounded-sm bg-signal py-2 text-ink font-medium hover:bg-signalDim transition-colors"
        >
          Verify
        </button>
      </form>
    </main>
  );
}

export default function MfaPage() {
  return (
    <Suspense fallback={null}>
      <MfaForm />
    </Suspense>
  );
}
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { api, setToken } from "@/lib/api";

export default function RegisterPage() {
  const router = useRouter();
  const [form, setForm] = useState({ email: "", password: "", full_name: "", organization_name: "" });
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function update(field: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement>) => setForm((f) => ({ ...f, [field]: e.target.value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await api.register(form);
      setToken(res.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong. Try again.");
    } finally {
      setLoading(false);
    }
  }

  const fields: [keyof typeof form, string, string][] = [
    ["organization_name", "Company name", "text"],
    ["full_name", "Your name", "text"],
    ["email", "Work email", "email"],
    ["password", "Password", "password"],
  ];

  return (
    <main className="min-h-screen flex items-center justify-center px-6">
      <form onSubmit={handleSubmit} className="w-full max-w-sm border border-line bg-panel rounded-md p-8">
        <h1 className="font-display text-2xl font-semibold text-paper mb-1">Create your console</h1>
        <p className="text-sm text-muted mb-6">Starts on the Basic plan — upgrade anytime.</p>

        {fields.map(([key, label, type]) => (
          <div key={key} className="mb-4">
            <label className="block text-sm text-muted mb-1" htmlFor={key}>
              {label}
            </label>
            <input
              id={key}
              type={type}
              required
              value={form[key]}
              onChange={update(key)}
              className="w-full rounded-sm bg-ink border border-line px-3 py-2 text-paper focus-visible:border-signal"
            />
          </div>
        ))}

        {error && <p className="text-danger text-sm mb-4">{error}</p>}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-sm bg-signal py-2 text-ink font-medium hover:bg-signalDim transition-colors disabled:opacity-50"
        >
          {loading ? "Creating…" : "Create account"}
        </button>
      </form>
    </main>
  );
}

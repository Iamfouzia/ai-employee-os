"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, clearToken } from "@/lib/api";
import { UsageMeter } from "@/components/UsageMeter";

type Usage = {
  plan_tier: string;
  ai_requests_used: number;
  ai_requests_limit: number | null;
  seats_used: number;
  seats_limit: number | null;
};

export default function DashboardPage() {
  const router = useRouter();
  const [usage, setUsage] = useState<Usage | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .usage()
      .then(setUsage)
      .catch(() => {
        // Not authenticated (or token expired) — send back to sign in
        router.push("/login");
      });
  }, [router]);

  function handleSignOut() {
    clearToken();
    router.push("/login");
  }

  return (
    <main className="min-h-screen">
      <header className="border-b border-line px-8 py-5 flex items-center justify-between">
        <span className="font-mono text-sm tracking-widest text-muted">CONSOLE</span>
        <button onClick={handleSignOut} className="text-sm text-muted hover:text-paper transition-colors">
          Sign out
        </button>
      </header>

      <section className="px-8 py-10 max-w-3xl">
        <h1 className="font-display text-2xl font-semibold text-paper mb-1">Overview</h1>
        {usage && (
          <p className="text-sm text-muted mb-8 capitalize">
            {usage.plan_tier} plan
          </p>
        )}

        {error && <p className="text-danger text-sm">{error}</p>}

        {usage && (
          <div className="grid grid-cols-2 gap-4">
            <UsageMeter label="AI requests this month" used={usage.ai_requests_used} limit={usage.ai_requests_limit} />
            <UsageMeter label="Seats" used={usage.seats_used} limit={usage.seats_limit} />
          </div>
        )}
      </section>
    </main>
  );
}

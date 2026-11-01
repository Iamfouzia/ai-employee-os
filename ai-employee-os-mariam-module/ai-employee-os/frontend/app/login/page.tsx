"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { UsageMeter } from "@/components/UsageMeter";
import { Sidebar } from "@/components/Sidebar";

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
        router.push("/login");
      });
  }, [router]);

  return (
    <main className="min-h-screen flex">
      <Sidebar />

      <section className="flex-1 px-8 py-10 max-w-3xl">
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
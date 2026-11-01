"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, SalesAnalytics, AIInsights } from "@/lib/api";
import { Sidebar } from "@/components/Sidebar";

export default function ReportsPage() {
  const router = useRouter();
  const [analytics, setAnalytics] = useState<SalesAnalytics | null>(null);
  const [insights, setInsights] = useState<AIInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [insightsLoading, setInsightsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .salesAnalytics()
      .then(setAnalytics)
      .catch(() => router.push("/login"))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function loadInsights() {
    setInsightsLoading(true);
    setError(null);
    try {
      const result = await api.aiInsights();
      setInsights(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to generate insights");
    } finally {
      setInsightsLoading(false);
    }
  }

  return (
    <main className="min-h-screen flex">
      <Sidebar />

      <section className="flex-1 px-8 py-10 max-w-4xl">
        <h1 className="font-display text-2xl font-semibold text-paper mb-1">Reports</h1>
        <p className="text-sm text-muted mb-8">Sales analytics, sourced live from paid invoices</p>

        {loading ? (
          <p className="text-sm text-muted">Loading analytics...</p>
        ) : analytics ? (
          <>
            <div className="grid grid-cols-3 gap-4 mb-8">
              <div className="border border-line rounded-md bg-panel p-4">
                <p className="text-sm text-muted mb-1">Total revenue</p>
                <p className="font-mono text-xl text-paper">${analytics.total_revenue.toFixed(2)}</p>
              </div>
              <div className="border border-line rounded-md bg-panel p-4">
                <p className="text-sm text-muted mb-1">Paid orders</p>
                <p className="font-mono text-xl text-paper">{analytics.total_orders}</p>
              </div>
              <div className="border border-line rounded-md bg-panel p-4">
                <p className="text-sm text-muted mb-1">Avg order value</p>
                <p className="font-mono text-xl text-paper">${analytics.average_order_value.toFixed(2)}</p>
              </div>
            </div>

            {Object.keys(analytics.revenue_by_month).length > 0 && (
              <div className="border border-line rounded-md bg-panel p-4 mb-8">
                <p className="text-sm text-muted mb-3">Revenue by month</p>
                <div className="flex items-end gap-3 h-32">
                  {Object.entries(analytics.revenue_by_month).map(([month, amount]) => {
                    const max = Math.max(...Object.values(analytics.revenue_by_month));
                    const heightPct = max > 0 ? (amount / max) * 100 : 0;
                    return (
                      <div key={month} className="flex-1 flex flex-col items-center gap-2">
                        <div
                          className="w-full bg-signal rounded-sm"
                          style={{ height: `${heightPct}%`, minHeight: "4px" }}
                        />
                        <span className="text-xs text-muted">{month}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </>
        ) : null}

        <div className="border border-line rounded-md bg-panel p-4">
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm text-muted">AI insights</p>
            <button
              onClick={loadInsights}
              disabled={insightsLoading}
              className="bg-signal text-ink font-medium rounded-sm px-3 py-1.5 text-xs hover:opacity-90 transition-opacity disabled:opacity-50"
            >
              {insightsLoading ? "Generating..." : "Generate insights"}
            </button>
          </div>

          {error && <p className="text-danger text-sm mb-2">{error}</p>}

          {insights && (
            <div className="space-y-4">
              <div>
                <p className="text-xs text-muted mb-1">Forecast (next quarter)</p>
                <p className="font-mono text-paper">${insights.forecast_next_quarter.toFixed(2)}</p>
              </div>
              {insights.insights.length > 0 && (
                <div>
                  <p className="text-xs text-muted mb-1">Insights</p>
                  <ul className="list-disc list-inside text-sm text-paper space-y-1">
                    {insights.insights.map((i, idx) => (
                      <li key={idx}>{i}</li>
                    ))}
                  </ul>
                </div>
              )}
              {insights.recommendations.length > 0 && (
                <div>
                  <p className="text-xs text-muted mb-1">Recommendations</p>
                  <ul className="list-disc list-inside text-sm text-paper space-y-1">
                    {insights.recommendations.map((r, idx) => (
                      <li key={idx}>{r}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </section>
    </main>
  );
}
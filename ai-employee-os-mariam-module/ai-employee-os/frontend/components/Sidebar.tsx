"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clearToken } from "@/lib/api";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Overview" },
  { href: "/dashboard/crm", label: "CRM" },
  { href: "/dashboard/quotations", label: "Quotations" },
  { href: "/dashboard/invoices", label: "Invoices" },
  { href: "/dashboard/documents", label: "Documents" },
  { href: "/dashboard/reports", label: "Reports" },
  { href: "/dashboard/assistant", label: "AI Assistant" },
];

export function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  function handleSignOut() {
    clearToken();
    router.push("/login");
  }

  return (
    <aside className="w-56 shrink-0 border-r border-line min-h-screen flex flex-col justify-between">
      <div>
        <div className="px-6 py-5 border-b border-line">
          <span className="font-mono text-sm tracking-widest text-muted">CONSOLE</span>
        </div>
        <nav className="px-3 py-4 flex flex-col gap-1">
          {NAV_ITEMS.map((item) => {
            const active = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`px-3 py-2 rounded-sm text-sm transition-colors ${
                  active
                    ? "bg-panel text-paper"
                    : "text-muted hover:text-paper hover:bg-panel"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
      <div className="px-3 py-4 border-t border-line">
        <button
          onClick={handleSignOut}
          className="w-full text-left px-3 py-2 rounded-sm text-sm text-muted hover:text-paper hover:bg-panel transition-colors"
        >
          Sign out
        </button>
      </div>
    </aside>
  );
}
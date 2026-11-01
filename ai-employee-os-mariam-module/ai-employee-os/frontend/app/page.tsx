import Link from "next/link";

const AGENTS = [
  "AI CEO Assistant",
  "AI Sales Manager",
  "AI Customer Support",
  "AI HR Assistant",
  "AI Recruiter",
  "AI Finance Assistant",
  "AI Accountant",
  "AI Marketing Assistant",
];

export default function Home() {
  return (
    <main className="min-h-screen flex flex-col">
      <header className="border-b border-line px-8 py-5 flex items-center justify-between">
        <span className="font-mono text-sm tracking-widest text-muted">AI EMPLOYEE OS</span>
        <nav className="flex gap-6 text-sm">
          <Link href="/login" className="text-paper hover:text-signal transition-colors">
            Sign in
          </Link>
          <Link
            href="/register"
            className="rounded-sm bg-signal px-4 py-1.5 text-ink font-medium hover:bg-signalDim transition-colors"
          >
            Get started
          </Link>
        </nav>
      </header>

      <section className="flex-1 px-8 py-20 max-w-4xl">
        <h1 className="font-display text-5xl font-semibold leading-tight text-paper">
          A workforce that never
          <br />
          clocks out.
        </h1>
        <p className="mt-6 max-w-xl text-muted text-lg">
          Hire an AI employee for every seat you can&apos;t fill fast enough — sales, support,
          finance, HR — each one running on your company&apos;s own knowledge.
        </p>

        <div className="mt-12 grid grid-cols-2 gap-px bg-line border border-line rounded-md overflow-hidden max-w-xl">
          {AGENTS.map((agent, i) => (
            <div key={agent} className="bg-panel px-4 py-3 flex items-center gap-3">
              <span
                className="h-1.5 w-1.5 rounded-full bg-ok"
                style={{ animationDelay: `${i * 120}ms` }}
              />
              <span className="text-sm text-paper">{agent}</span>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

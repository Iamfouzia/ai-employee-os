"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api, Invoice, Customer } from "@/lib/api";
import { Sidebar } from "@/components/Sidebar";

export default function InvoicesPage() {
  const router = useRouter();
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const [customerId, setCustomerId] = useState("");
  const [description, setDescription] = useState("");
  const [quantity, setQuantity] = useState("1");
  const [unitPrice, setUnitPrice] = useState("");
  const [dueDate, setDueDate] = useState("");

  function loadData() {
    Promise.all([api.listInvoices(), api.listCustomers()])
      .then(([inv, cust]) => {
        setInvoices(inv);
        setCustomers(cust);
      })
      .catch(() => router.push("/login"))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    const customer = customers.find((c) => String(c.id) === customerId);
    if (!customer) {
      setError("Pick a customer first — add one on the CRM page if the list is empty.");
      return;
    }
    if (!customer.email) {
      setError("Selected customer has no email on file — invoices require one.");
      return;
    }

    setSubmitting(true);
    try {
      await api.createInvoice({
        customer_id: customer.id,
        customer_name: customer.customer_name,
        customer_email: customer.email,
        items: [{ description, quantity: Number(quantity), unit_price: Number(unitPrice) }],
        due_date: new Date(dueDate).toISOString(),
      });
      setDescription("");
      setQuantity("1");
      setUnitPrice("");
      setDueDate("");
      loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create invoice");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main className="min-h-screen flex">
      <Sidebar />

      <section className="flex-1 px-8 py-10 max-w-4xl">
        <h1 className="font-display text-2xl font-semibold text-paper mb-1">Invoices</h1>
        <p className="text-sm text-muted mb-8">Create and track invoices</p>

        <form
          onSubmit={handleSubmit}
          className="border border-line rounded-md bg-panel p-4 mb-8 grid grid-cols-2 gap-3"
        >
          <select
            required
            value={customerId}
            onChange={(e) => setCustomerId(e.target.value)}
            className="bg-ink border border-line rounded-sm px-3 py-2 text-sm text-paper col-span-2"
          >
            <option value="">Select customer</option>
            {customers.map((c) => (
              <option key={c.id} value={c.id}>
                {c.customer_name}
              </option>
            ))}
          </select>
          <input
            required
            placeholder="Item description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="bg-ink border border-line rounded-sm px-3 py-2 text-sm text-paper placeholder:text-muted col-span-2"
          />
          <input
            required
            type="number"
            min="1"
            placeholder="Quantity"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            className="bg-ink border border-line rounded-sm px-3 py-2 text-sm text-paper placeholder:text-muted"
          />
          <input
            required
            type="number"
            step="0.01"
            min="0"
            placeholder="Unit price"
            value={unitPrice}
            onChange={(e) => setUnitPrice(e.target.value)}
            className="bg-ink border border-line rounded-sm px-3 py-2 text-sm text-paper placeholder:text-muted"
          />
          <input
            required
            type="date"
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            className="bg-ink border border-line rounded-sm px-3 py-2 text-sm text-paper col-span-2"
          />
          {error && <p className="text-danger text-sm col-span-2">{error}</p>}
          <button
            type="submit"
            disabled={submitting}
            className="col-span-2 bg-signal text-ink font-medium rounded-sm py-2 text-sm hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {submitting ? "Creating..." : "Create invoice"}
          </button>
        </form>

        {loading ? (
          <p className="text-sm text-muted">Loading invoices...</p>
        ) : invoices.length === 0 ? (
          <p className="text-sm text-muted">No invoices yet — create one above.</p>
        ) : (
          <div className="border border-line rounded-md overflow-hidden">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-line text-muted text-left">
                  <th className="px-4 py-3 font-normal">Customer</th>
                  <th className="px-4 py-3 font-normal">Total</th>
                  <th className="px-4 py-3 font-normal">Status</th>
                  <th className="px-4 py-3 font-normal">Due</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((inv) => (
                  <tr key={inv.id} className="border-b border-line last:border-0">
                    <td className="px-4 py-3 text-paper">{inv.customer_name}</td>
                    <td className="px-4 py-3 font-mono text-paper">${inv.total_amount.toFixed(2)}</td>
                    <td className="px-4 py-3 text-muted capitalize">{inv.status.toLowerCase()}</td>
                    <td className="px-4 py-3 text-muted">
                      {new Date(inv.due_date).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </main>
  );
}
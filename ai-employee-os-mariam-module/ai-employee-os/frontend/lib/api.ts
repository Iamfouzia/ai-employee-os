const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function getToken(): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(/(?:^|; )access_token=([^;]*)/);
  return match ? decodeURIComponent(match[1]) : null;
}

export function setToken(token: string) {
  // httpOnly cookies should be set server-side in production; this is a
  // client-readable cookie for local/dev wiring.
  document.cookie = `access_token=${token}; path=/; samesite=lax`;
}

export function clearToken() {
  document.cookie = "access_token=; path=/; max-age=0";
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export const api = {
  register: (data: { email: string; password: string; full_name: string; organization_name: string }) =>
    request<{ access_token: string; refresh_token: string }>("/api/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  login: (data: { email: string; password: string }) =>
    request<{ access_token: string; refresh_token: string; mfa_required: boolean }>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  me: () => request<{ email: string; full_name: string; role: string }>("/api/auth/me"),

  usage: () =>
    request<{ plan_tier: string; ai_requests_used: number; ai_requests_limit: number | null; seats_used: number; seats_limit: number | null }>(
      "/api/pricing/usage"
    ),

  // --- CRM ---
  listCustomers: () =>
    request<Customer[]>("/api/crm/customers?limit=200"),

  createCustomer: (data: { customer_name: string; email?: string; phone?: string; company?: string }) =>
    request<Customer>("/api/crm/customers", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateCustomer: (id: number, data: { customer_name?: string; email?: string; phone?: string; company?: string }) =>
    request<Customer>(`/api/crm/customers/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  deleteCustomer: (id: number) =>
    request<void>(`/api/crm/customers/${id}`, { method: "DELETE" }),

  listLeads: (statusFilter?: string) =>
    request<Lead[]>(`/api/crm/leads${statusFilter ? `?status_filter=${encodeURIComponent(statusFilter)}` : ""}`),

  createLead: (data: { customer_id: number; source?: string; status?: string; assigned_to?: string }) =>
    request<Lead>("/api/crm/leads", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateLead: (id: number, data: { source?: string; assigned_to?: string }) =>
    request<Lead>(`/api/crm/leads/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  moveLeadStatus: (id: number, newStatus: string) =>
    request<Lead>(`/api/crm/leads/${id}/status?new_status=${encodeURIComponent(newStatus)}`, {
      method: "PATCH",
    }),

  deleteLead: (id: number) =>
    request<void>(`/api/crm/leads/${id}`, { method: "DELETE" }),

  scheduleMeeting: (
    leadId: number,
    data: { title: string; start_time: string; duration_minutes: number; customer_id: number; notes?: string }
  ) =>
    request<{ htmlLink?: string }>(`/api/crm/leads/${leadId}/schedule-meeting`, {
      method: "POST",
      body: JSON.stringify(data),
    }),

  listTasks: () =>
    request<Task[]>("/api/crm/tasks?limit=200"),

  createTask: (data: { title: string; assigned_to?: string; priority?: string; deadline?: string | null; status?: string }) =>
    request<Task>("/api/crm/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  updateTask: (id: number, data: { title?: string; assigned_to?: string; priority?: string; deadline?: string | null }) =>
    request<Task>(`/api/crm/tasks/${id}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),

  moveTaskStatus: (id: number, newStatus: string) =>
    request<Task>(`/api/crm/tasks/${id}/status?new_status=${encodeURIComponent(newStatus)}`, {
      method: "PATCH",
    }),

  deleteTask: (id: number) =>
    request<void>(`/api/crm/tasks/${id}`, { method: "DELETE" }),

  runReminders: () =>
    request<{ reminders_created: number }>("/api/crm/reminders/run", { method: "POST" }),

  getTimeline: (customerId: number) =>
    request<Activity[]>(`/api/crm/customers/${customerId}/timeline`),

  logActivity: (data: { customer_id: number; type: string; description: string }) =>
    request<Activity>("/api/crm/activities", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // --- Finance ---
  listInvoices: () =>
    request<Invoice[]>("/api/finance/invoices"),

  createInvoice: (data: {
    customer_id: number;
    customer_name: string;
    customer_email: string;
    items: { description: string; quantity: number; unit_price: number }[];
    due_date: string;
  }) =>
    request<Invoice>("/api/finance/invoices", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // --- Quotations ---
  listQuotations: () =>
    request<Quotation[]>("/api/finance/quotations"),

  createQuotation: (data: {
    customer_id: number;
    customer_name: string;
    customer_email: string;
    items: { description: string; quantity: number; unit_price: number }[];
    tax_percentage?: number;
    discount_amount?: number;
  }) =>
    request<Quotation>("/api/finance/quotations", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // --- Documents ---
  listDocuments: () =>
    request<UploadedDocument[]>("/api/documents/"),

  uploadDocument: async (file: File): Promise<UploadedDocument> => {
    const token = getToken();
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/api/documents/upload`, {
      method: "POST",
      headers: {
        "ngrok-skip-browser-warning": "true",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: formData,
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail || `Upload failed: ${res.status}`);
    }
    return res.json();
  },

  askDocumentQuestion: (question: string) =>
    request<{ answer: string; sources: { document_id: number; relevance_score: number }[] }>("/api/documents/qa", {
      method: "POST",
      body: JSON.stringify({ query: question }),
    }),

  // --- Reporting ---
  salesAnalytics: () =>
    request<SalesAnalytics>("/api/reports/sales"),

  aiInsights: () =>
    request<AIInsights>("/api/reports/insights"),

  // --- AI Executive Assistant ---
  sendCommand: (data: { text: string; session_id?: string }) =>
    request<AssistantResponse>("/api/assistant/command", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};

export type Customer = {
  id: number;
  customer_name: string;
  email: string | null;
  phone: string | null;
  company: string | null;
  created_at: string;
};

export type Lead = {
  id: number;
  customer_id: number;
  source: string | null;
  status: "New" | "Contacted" | "Negotiation" | "Closed";
  assigned_to: string | null;
  created_at: string;
};

export type Task = {
  id: number;
  title: string;
  assigned_to: string | null;
  priority: "High" | "Medium" | "Low";
  deadline: string | null;
  status: "Pending" | "In-Progress" | "Done";
  created_at: string;
};

export type Activity = {
  id: number;
  customer_id: number;
  type: string;
  description: string;
  timestamp: string;
};

export type Invoice = {
  id: number;
  customer_id: number;
  customer_name: string;
  customer_email: string;
  items: { description: string; quantity: number; unit_price: number }[];
  due_date: string;
  total_amount: number;
  status: string;
  qr_code_path: string | null;
  payment_link: string | null;
  created_at: string;
};

export type SalesAnalytics = {
  total_revenue: number;
  total_orders: number;
  average_order_value: number;
  revenue_by_month: Record<string, number>;
};

export type AIInsights = {
  insights: string[];
  forecast_next_quarter: number;
  recommendations: string[];
};

export type AssistantResponse = {
  session_id: string;
  raw_input: string;
  results: { step_id: number; outcome: string }[];
};

export type Quotation = {
  id: number;
  customer_id: number;
  customer_name: string;
  customer_email: string;
  items: { description: string; quantity: number; unit_price: number }[];
  tax_percentage: number;
  discount_amount: number;
  subtotal: number;
  tax_amount: number;
  total_amount: number;
  status: string;
  created_at: string;
};

export type UploadedDocument = {
  id: number;
  filename: string;
  file_url: string;
  file_type: string;
  extracted_text: string | null;
  created_at: string;
};
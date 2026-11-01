"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "@/components/Sidebar";
import { api, Customer, Lead, Task, Activity } from "@/lib/api";

type View = "overview" | "customers" | "pipeline" | "tasks";
const STAGES: Lead["status"][] = ["New", "Contacted", "Negotiation", "Closed"];

function esc(s: string | null | undefined) {
  return s ?? "";
}
function fmtDate(iso: string) {
  try {
    return new Date(iso).toLocaleDateString("en-GB", { day: "2-digit", month: "short", year: "numeric" });
  } catch {
    return iso;
  }
}
function fmtDateTime(iso: string) {
  try {
    return new Date(iso).toLocaleString("en-GB", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit" });
  } catch {
    return iso;
  }
}

export default function CRMPage() {
  const router = useRouter();
  const [view, setView] = useState<View>("overview");
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [leads, setLeads] = useState<Lead[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [connected, setConnected] = useState<"checking" | "ok" | "err">("checking");
  const [toast, setToast] = useState<{ text: string; error?: boolean } | null>(null);

  const showToast = (text: string, error = false) => {
    setToast({ text, error });
    setTimeout(() => setToast(null), 2600);
  };

  const loadAll = useCallback(async () => {
    try {
      const custs = await api.listCustomers();
      setCustomers(custs);
      setConnected("ok");
    } catch {
      setConnected("err");
      showToast("Could not reach the CRM server.", true);
      router.push("/login");
      return;
    }
    try {
      const leadLists = await Promise.all(STAGES.map((s) => api.listLeads(s).catch(() => [])));
      setLeads(leadLists.flat());
    } catch {
      setLeads([]);
    }
    try {
      setTasks(await api.listTasks());
    } catch {
      setTasks([]);
    }
  }, [router]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  const customerName = (id: number) => customers.find((c) => c.id === id)?.customer_name || `#${id}`;

  // ---- Customer modal ----
  const [custModalOpen, setCustModalOpen] = useState(false);
  const [editingCustomerId, setEditingCustomerId] = useState<number | null>(null);
  const [custForm, setCustForm] = useState({ name: "", email: "", phone: "", company: "" });
  const [custError, setCustError] = useState("");

  const openCustomerModal = (id?: number) => {
    setEditingCustomerId(id ?? null);
    if (id) {
      const c = customers.find((c) => c.id === id);
      setCustForm({
        name: c?.customer_name || "",
        email: c?.email || "",
        phone: c?.phone || "",
        company: c?.company || "",
      });
    } else {
      setCustForm({ name: "", email: "", phone: "", company: "" });
    }
    setCustError("");
    setCustModalOpen(true);
  };

  const submitCustomer = async () => {
    if (!custForm.name.trim()) {
      setCustError("Customer name is required.");
      return;
    }
    const payload = {
      customer_name: custForm.name.trim(),
      email: custForm.email.trim() || undefined,
      phone: custForm.phone.trim() || undefined,
      company: custForm.company.trim() || undefined,
    };
    try {
      if (editingCustomerId) {
        await api.updateCustomer(editingCustomerId, payload);
        showToast("Customer updated");
      } else {
        await api.createCustomer(payload);
        showToast("Customer added");
      }
      setCustModalOpen(false);
      await loadAll();
    } catch (e) {
      setCustError(e instanceof Error ? e.message : "Failed to save customer");
    }
  };

  const deleteCustomer = async (id: number) => {
    if (!confirm("Delete this customer? This will also remove their leads and activity history.")) return;
    try {
      await api.deleteCustomer(id);
      showToast("Customer deleted");
      await loadAll();
    } catch (e) {
      showToast(e instanceof Error ? e.message : "Failed to delete", true);
    }
  };

  // ---- Lead modal ----
  const [leadModalOpen, setLeadModalOpen] = useState(false);
  const [editingLeadId, setEditingLeadId] = useState<number | null>(null);
  const [leadForm, setLeadForm] = useState({ customerId: "", source: "", assignedTo: "" });
  const [leadError, setLeadError] = useState("");

  const openLeadModal = () => {
    setEditingLeadId(null);
    setLeadForm({ customerId: customers[0] ? String(customers[0].id) : "", source: "", assignedTo: "" });
    setLeadError("");
    setLeadModalOpen(true);
  };

  const openLeadEditModal = (leadId: number) => {
    const lead = leads.find((l) => l.id === leadId);
    if (!lead) return;
    setEditingLeadId(leadId);
    setLeadForm({ customerId: String(lead.customer_id), source: lead.source || "", assignedTo: lead.assigned_to || "" });
    setLeadError("");
    setLeadModalOpen(true);
  };

  const submitLead = async () => {
    try {
      if (editingLeadId) {
        await api.updateLead(editingLeadId, {
          source: leadForm.source.trim() || undefined,
          assigned_to: leadForm.assignedTo.trim() || undefined,
        });
        showToast("Lead updated");
      } else {
        if (!leadForm.customerId) {
          setLeadError("Add a customer first.");
          return;
        }
        await api.createLead({
          customer_id: Number(leadForm.customerId),
          source: leadForm.source.trim() || undefined,
          status: "New",
          assigned_to: leadForm.assignedTo.trim() || undefined,
        });
        showToast("Lead added to pipeline");
      }
      setLeadModalOpen(false);
      await loadAll();
    } catch (e) {
      setLeadError(e instanceof Error ? e.message : "Failed to save lead");
    }
  };

  const moveLead = async (leadId: number, newStatus: string) => {
    try {
      await api.moveLeadStatus(leadId, newStatus);
      showToast("Lead moved to " + newStatus);
      await loadAll();
    } catch (e) {
      showToast(e instanceof Error ? e.message : "Failed to move lead", true);
    }
  };

  const deleteLead = async (leadId: number) => {
    if (!confirm("Delete this lead?")) return;
    try {
      await api.deleteLead(leadId);
      showToast("Lead deleted");
      await loadAll();
    } catch (e) {
      showToast(e instanceof Error ? e.message : "Failed to delete lead", true);
    }
  };

  // ---- Meeting modal ----
  const [meetingModalOpen, setMeetingModalOpen] = useState(false);
  const [meetingLeadId, setMeetingLeadId] = useState<number | null>(null);
  const [meetingCustomerId, setMeetingCustomerId] = useState<number | null>(null);
  const [meetingForm, setMeetingForm] = useState({ title: "", start: "", duration: "30", notes: "" });
  const [meetingError, setMeetingError] = useState("");
  const [meetingSaving, setMeetingSaving] = useState(false);

  const openMeetingModal = (leadId: number, customerId: number) => {
    setMeetingLeadId(leadId);
    setMeetingCustomerId(customerId);
    setMeetingForm({ title: "", start: "", duration: "30", notes: "" });
    setMeetingError("");
    setMeetingModalOpen(true);
  };

  const submitMeeting = async () => {
    if (!meetingForm.title.trim() || !meetingForm.start) {
      setMeetingError("Title and date/time are required.");
      return;
    }
    setMeetingSaving(true);
    try {
      const event = await api.scheduleMeeting(meetingLeadId!, {
        title: meetingForm.title.trim(),
        start_time: new Date(meetingForm.start).toISOString(),
        duration_minutes: Number(meetingForm.duration) || 30,
        customer_id: meetingCustomerId!,
        notes: meetingForm.notes.trim() || undefined,
      });
      setMeetingModalOpen(false);
      showToast("Meeting scheduled on Google Calendar");
      if (event?.htmlLink) window.open(event.htmlLink, "_blank");
      await loadAll();
    } catch (e) {
      setMeetingError(e instanceof Error ? e.message : "Could not schedule meeting.");
    } finally {
      setMeetingSaving(false);
    }
  };

  // ---- Task modal ----
  const [taskModalOpen, setTaskModalOpen] = useState(false);
  const [editingTaskId, setEditingTaskId] = useState<number | null>(null);
  const [taskForm, setTaskForm] = useState({ title: "", assignedTo: "", priority: "Medium", deadline: "" });
  const [taskError, setTaskError] = useState("");

  const openTaskModal = () => {
    setEditingTaskId(null);
    setTaskForm({ title: "", assignedTo: "", priority: "Medium", deadline: "" });
    setTaskError("");
    setTaskModalOpen(true);
  };

  const openTaskEditModal = (taskId: number) => {
    const t = tasks.find((t) => t.id === taskId);
    if (!t) return;
    setEditingTaskId(taskId);
    setTaskForm({
      title: t.title,
      assignedTo: t.assigned_to || "",
      priority: t.priority,
      deadline: t.deadline ? t.deadline.split("T")[0] : "",
    });
    setTaskError("");
    setTaskModalOpen(true);
  };

  const submitTask = async () => {
    if (!taskForm.title.trim()) {
      setTaskError("Task title is required.");
      return;
    }
    const deadlineVal = taskForm.deadline || null;
    try {
      if (editingTaskId) {
        await api.updateTask(editingTaskId, {
          title: taskForm.title.trim(),
          assigned_to: taskForm.assignedTo.trim() || undefined,
          priority: taskForm.priority,
          deadline: deadlineVal,
        });
        showToast("Task updated");
      } else {
        await api.createTask({
          title: taskForm.title.trim(),
          assigned_to: taskForm.assignedTo.trim() || undefined,
          priority: taskForm.priority,
          status: "Pending",
          deadline: deadlineVal,
        });
        showToast("Task added");
      }
      setTaskModalOpen(false);
      await loadAll();
    } catch (e) {
      setTaskError(e instanceof Error ? e.message : "Failed to save task");
    }
  };

  const moveTask = async (taskId: number, newStatus: string) => {
    try {
      await api.moveTaskStatus(taskId, newStatus);
      showToast("Task updated to " + newStatus);
      await loadAll();
    } catch (e) {
      showToast(e instanceof Error ? e.message : "Failed to move task", true);
    }
  };

  const deleteTask = async (taskId: number) => {
    if (!confirm("Delete this task?")) return;
    try {
      await api.deleteTask(taskId);
      showToast("Task deleted");
      await loadAll();
    } catch (e) {
      showToast(e instanceof Error ? e.message : "Failed to delete task", true);
    }
  };

  const runReminders = async () => {
    try {
      const result = await api.runReminders();
      const n = result.reminders_created || 0;
      showToast(n > 0 ? `Created ${n} reminder task(s) for stale leads` : "No stale leads right now — nothing to remind");
      await loadAll();
    } catch (e) {
      showToast("Could not run reminders: " + (e instanceof Error ? e.message : ""), true);
    }
  };

  // ---- Timeline modal ----
  const [timelineOpen, setTimelineOpen] = useState(false);
  const [timelineCustomerId, setTimelineCustomerId] = useState<number | null>(null);
  const [timeline, setTimeline] = useState<Activity[]>([]);
  const [timelineLoading, setTimelineLoading] = useState(false);
  const [timelineError, setTimelineError] = useState("");
  const [activityForm, setActivityForm] = useState({ type: "Email", description: "" });

  const openTimelineModal = async (customerId: number) => {
    setTimelineCustomerId(customerId);
    setActivityForm({ type: "Email", description: "" });
    setTimelineError("");
    setTimelineOpen(true);
    setTimelineLoading(true);
    try {
      setTimeline(await api.getTimeline(customerId));
    } catch {
      setTimeline([]);
    } finally {
      setTimelineLoading(false);
    }
  };

  const submitActivity = async () => {
    if (!activityForm.description.trim()) {
      setTimelineError("Description is required.");
      return;
    }
    try {
      await api.logActivity({
        customer_id: timelineCustomerId!,
        type: activityForm.type,
        description: activityForm.description.trim(),
      });
      setActivityForm({ ...activityForm, description: "" });
      showToast("Activity logged");
      setTimeline(await api.getTimeline(timelineCustomerId!));
    } catch (e) {
      setTimelineError(e instanceof Error ? e.message : "Failed to log activity");
    }
  };

  const pillClass = (value: string, kind: "priority" | "activity") => {
    if (kind === "priority") {
      return value === "High" ? "pill-high" : value === "Medium" ? "pill-medium" : "pill-low";
    }
    const map: Record<string, string> = { Email: "pill-new", Call: "pill-contacted", Meeting: "pill-negotiation", Note: "pill-low" };
    return map[value] || "pill-low";
  };

  const openLeads = leads.filter((l) => l.status !== "Closed").length;
  const openTasks = tasks.filter((t) => t.status !== "Done").length;
  const closedLeads = leads.filter((l) => l.status === "Closed").length;
  const recentCustomers = [...customers]
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5);
  const sortedTasks = [...tasks].sort((a, b) => {
    const order: Record<string, number> = { High: 0, Medium: 1, Low: 2 };
    return order[a.priority] - order[b.priority];
  });

  return (
    <main className="min-h-screen flex">
      <Sidebar />

      <section className="flex-1 crm-scope">
        <link
          rel="stylesheet"
          href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap"
        />

        <div className="crm-main">
          <div className="page-header">
            <div>
              <div className="eyebrow">Ledger — {view === "overview" ? "01" : view === "customers" ? "02" : view === "pipeline" ? "03" : "04"}</div>
              <h1 className="disp">
                {view === "overview" && "Overview"}
                {view === "customers" && "Customers"}
                {view === "pipeline" && "Sales pipeline"}
                {view === "tasks" && "Tasks"}
              </h1>
              <p>
                {view === "overview" && "A snapshot of customers, leads, and open work across the pipeline."}
                {view === "customers" && "Every contact and company your team is tracking."}
                {view === "pipeline" && "Move a lead's stage forward as it progresses toward close."}
                {view === "tasks" && "What the team needs to follow up on."}
              </p>
            </div>
            <div className="flex gap-2 items-end">
              <div className="crm-subnav">
                {(["overview", "customers", "pipeline", "tasks"] as View[]).map((v) => (
                  <button key={v} onClick={() => setView(v)} className={`crm-tab ${view === v ? "active" : ""}`}>
                    {v[0].toUpperCase() + v.slice(1)}
                  </button>
                ))}
              </div>
              {view === "customers" && (
                <button className="btn btn-primary" onClick={() => openCustomerModal()}>
                  + Add customer
                </button>
              )}
              {view === "pipeline" && (
                <button className="btn btn-primary" onClick={openLeadModal}>
                  + Add lead
                </button>
              )}
              {view === "tasks" && (
                <div className="flex gap-2">
                  <button className="btn btn-ghost" onClick={runReminders}>
                    Run AI reminders
                  </button>
                  <button className="btn btn-primary" onClick={openTaskModal}>
                    + Add task
                  </button>
                </div>
              )}
            </div>
          </div>

          {connected === "err" && <p className="text-sm mb-4" style={{ color: "#B4432F" }}>Server not reachable.</p>}

          {view === "overview" && (
            <>
              <div className="stat-row">
                <div className="stat-card">
                  <div className="label">Customers</div>
                  <div className="value mono">{customers.length}</div>
                  <div className="sub">total on record</div>
                </div>
                <div className="stat-card">
                  <div className="label">Open leads</div>
                  <div className="value mono">{openLeads}</div>
                  <div className="sub">not yet closed</div>
                </div>
                <div className="stat-card">
                  <div className="label">Open tasks</div>
                  <div className="value mono">{openTasks}</div>
                  <div className="sub">pending or in progress</div>
                </div>
                <div className="stat-card">
                  <div className="label">Closed deals</div>
                  <div className="value mono">{closedLeads}</div>
                  <div className="sub">leads marked closed</div>
                </div>
              </div>
              <div className="panel">
                <div className="panel-head">
                  <h2 className="disp">Recent customers</h2>
                </div>
                {recentCustomers.length === 0 ? (
                  <div className="empty-state">
                    <div className="mark mono">— · —</div>
                    <p className="t">No customers yet</p>
                    <p className="s">Add your first customer from the Customers tab.</p>
                  </div>
                ) : (
                  <table>
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Company</th>
                        <th>Email</th>
                        <th>Added</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentCustomers.map((c) => (
                        <tr key={c.id}>
                          <td className="cell-name">{esc(c.customer_name)}</td>
                          <td className="cell-muted">{esc(c.company) || "—"}</td>
                          <td className="cell-muted">{esc(c.email) || "—"}</td>
                          <td className="cell-mono">{fmtDate(c.created_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </>
          )}

          {view === "customers" && (
            <div className="panel">
              {customers.length === 0 ? (
                <div className="empty-state">
                  <div className="mark mono">— · —</div>
                  <p className="t">No customers yet</p>
                  <p className="s">Click &ldquo;Add customer&rdquo; to create your first record.</p>
                </div>
              ) : (
                <table>
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Company</th>
                      <th>Email</th>
                      <th>Phone</th>
                      <th>ID</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {customers.map((c) => (
                      <tr key={c.id}>
                        <td className="cell-name">{esc(c.customer_name)}</td>
                        <td className="cell-muted">{esc(c.company) || "—"}</td>
                        <td className="cell-muted">{esc(c.email) || "—"}</td>
                        <td className="cell-muted">{esc(c.phone) || "—"}</td>
                        <td className="cell-mono">#{c.id}</td>
                        <td>
                          <button className="edit-link" onClick={() => openTimelineModal(c.id)}>
                            Timeline
                          </button>
                          <button className="edit-link" style={{ marginLeft: 10 }} onClick={() => openCustomerModal(c.id)}>
                            Edit
                          </button>
                          <button className="edit-link" style={{ color: "#C15B45", marginLeft: 10 }} onClick={() => deleteCustomer(c.id)}>
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}

          {view === "pipeline" && (
            <div className="board">
              {STAGES.map((stage) => {
                const stageLeads = leads.filter((l) => l.status === stage);
                const colClass =
                  stage === "New" ? "col-top-new" : stage === "Contacted" ? "col-top-contacted" : stage === "Negotiation" ? "col-top-negotiation" : "col-top-closed";
                return (
                  <div className="board-col" key={stage}>
                    <div className={`board-col-head ${colClass}`}>
                      <span className="title">{stage}</span>
                      <span className="n mono">{stageLeads.length}</span>
                    </div>
                    <div className="board-col-body">
                      {stageLeads.length === 0 ? (
                        <div style={{ padding: "16px 4px", color: "var(--ink-faint)", fontSize: 12 }}>No leads here</div>
                      ) : (
                        stageLeads.map((l) => (
                          <div className="lead-card" key={l.id}>
                            <div className="lname">{customerName(l.customer_id)}</div>
                            <div className="lmeta">
                              {esc(l.source) || "no source"} · {esc(l.assigned_to) || "unassigned"}
                            </div>
                            <select value={l.status} onChange={(e) => moveLead(l.id, e.target.value)}>
                              {STAGES.map((s) => (
                                <option key={s} value={s}>
                                  {s}
                                </option>
                              ))}
                            </select>
                            <div>
                              <button className="edit-link" style={{ marginTop: 6 }} onClick={() => openLeadEditModal(l.id)}>
                                Edit details
                              </button>
                              <button className="edit-link" style={{ marginTop: 6, marginLeft: 10 }} onClick={() => openMeetingModal(l.id, l.customer_id)}>
                                Schedule meeting
                              </button>
                              <button className="edit-link" style={{ marginTop: 6, marginLeft: 10, color: "#C15B45" }} onClick={() => deleteLead(l.id)}>
                                Delete
                              </button>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {view === "tasks" && (
            <div className="panel">
              {tasks.length === 0 ? (
                <div className="empty-state">
                  <div className="mark mono">— · —</div>
                  <p className="t">No tasks yet</p>
                  <p className="s">Click &ldquo;Add task&rdquo; to create your first one.</p>
                </div>
              ) : (
                <table>
                  <thead>
                    <tr>
                      <th>Task</th>
                      <th>Assigned to</th>
                      <th>Priority</th>
                      <th>Deadline</th>
                      <th>Status</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {sortedTasks.map((t) => (
                      <tr key={t.id}>
                        <td className="cell-name">{esc(t.title)}</td>
                        <td className="cell-muted">{esc(t.assigned_to) || "—"}</td>
                        <td>
                          <span className={`pill ${pillClass(t.priority, "priority")}`}>{t.priority}</span>
                        </td>
                        <td className="cell-mono">{t.deadline ? fmtDate(t.deadline) : "—"}</td>
                        <td>
                          <select
                            value={t.status}
                            onChange={(e) => moveTask(t.id, e.target.value)}
                            style={{ fontSize: 12, padding: "5px 8px", borderRadius: 6, border: "1px solid var(--line-strong)", fontFamily: "Inter", background: "#fff" }}
                          >
                            {["Pending", "In-Progress", "Done"].map((s) => (
                              <option key={s} value={s}>
                                {s}
                              </option>
                            ))}
                          </select>
                        </td>
                        <td>
                          <button className="edit-link" onClick={() => openTaskEditModal(t.id)}>
                            Edit
                          </button>
                          <button className="edit-link" style={{ color: "#C15B45", marginLeft: 14 }} onClick={() => deleteTask(t.id)}>
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          )}
        </div>

        {/* Customer modal */}
        {custModalOpen && (
          <div className="overlay show">
            <div className="modal">
              <h3 className="disp">{editingCustomerId ? "Edit customer" : "Add customer"}</h3>
              <p className="hint">{editingCustomerId ? "Update this contact's details." : "Create a new contact in the CRM."}</p>
              {custError && <div className="modal-error" style={{ display: "block" }}>{custError}</div>}
              <div className="field">
                <label>Customer name *</label>
                <input value={custForm.name} onChange={(e) => setCustForm({ ...custForm, name: e.target.value })} placeholder="e.g. Ali Raza" />
              </div>
              <div className="field">
                <label>Email</label>
                <input value={custForm.email} onChange={(e) => setCustForm({ ...custForm, email: e.target.value })} placeholder="ali@example.com" />
              </div>
              <div className="field">
                <label>Phone</label>
                <input value={custForm.phone} onChange={(e) => setCustForm({ ...custForm, phone: e.target.value })} placeholder="03001234567" />
              </div>
              <div className="field">
                <label>Company</label>
                <input value={custForm.company} onChange={(e) => setCustForm({ ...custForm, company: e.target.value })} placeholder="Raza Traders" />
              </div>
              <div className="modal-actions">
                <button className="btn btn-ghost" onClick={() => setCustModalOpen(false)}>
                  Cancel
                </button>
                <button className="btn btn-primary" onClick={submitCustomer}>
                  {editingCustomerId ? "Save changes" : "Save customer"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Lead modal */}
        {leadModalOpen && (
          <div className="overlay show">
            <div className="modal">
              <h3 className="disp">{editingLeadId ? "Edit lead" : "Add lead"}</h3>
              <p className="hint">Attach a new opportunity to an existing customer.</p>
              {leadError && <div className="modal-error" style={{ display: "block" }}>{leadError}</div>}
              <div className="field">
                <label>Customer *</label>
                <select
                  value={leadForm.customerId}
                  disabled={!!editingLeadId}
                  onChange={(e) => setLeadForm({ ...leadForm, customerId: e.target.value })}
                >
                  {customers.length === 0 && <option value="">No customers yet — add one first</option>}
                  {customers.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.customer_name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="field">
                <label>Source</label>
                <input value={leadForm.source} onChange={(e) => setLeadForm({ ...leadForm, source: e.target.value })} placeholder="website, referral, walk-in…" />
              </div>
              <div className="field">
                <label>Assigned to</label>
                <input value={leadForm.assignedTo} onChange={(e) => setLeadForm({ ...leadForm, assignedTo: e.target.value })} placeholder="e.g. Ayesha" />
              </div>
              <div className="modal-actions">
                <button className="btn btn-ghost" onClick={() => setLeadModalOpen(false)}>
                  Cancel
                </button>
                <button className="btn btn-primary" onClick={submitLead}>
                  {editingLeadId ? "Save changes" : "Save lead"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Meeting modal */}
        {meetingModalOpen && (
          <div className="overlay show">
            <div className="modal">
              <h3 className="disp">Schedule meeting</h3>
              <p className="hint">Creates a Google Calendar event for {meetingCustomerId ? customerName(meetingCustomerId) : "this lead"}.</p>
              {meetingError && <div className="modal-error" style={{ display: "block" }}>{meetingError}</div>}
              <div className="field">
                <label>Title *</label>
                <input value={meetingForm.title} onChange={(e) => setMeetingForm({ ...meetingForm, title: e.target.value })} placeholder="e.g. Pricing discussion" />
              </div>
              <div className="field">
                <label>Date &amp; time *</label>
                <input type="datetime-local" value={meetingForm.start} onChange={(e) => setMeetingForm({ ...meetingForm, start: e.target.value })} />
              </div>
              <div className="field">
                <label>Duration (minutes)</label>
                <input type="number" min={5} step={5} value={meetingForm.duration} onChange={(e) => setMeetingForm({ ...meetingForm, duration: e.target.value })} />
              </div>
              <div className="field">
                <label>Notes</label>
                <input value={meetingForm.notes} onChange={(e) => setMeetingForm({ ...meetingForm, notes: e.target.value })} placeholder="Optional notes" />
              </div>
              <div className="modal-actions">
                <button className="btn btn-ghost" onClick={() => setMeetingModalOpen(false)}>
                  Cancel
                </button>
                <button className="btn btn-primary" disabled={meetingSaving} onClick={submitMeeting}>
                  {meetingSaving ? "Scheduling…" : "Schedule meeting"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Task modal */}
        {taskModalOpen && (
          <div className="overlay show">
            <div className="modal">
              <h3 className="disp">{editingTaskId ? "Edit task" : "Add task"}</h3>
              <p className="hint">Create a follow-up or internal task.</p>
              {taskError && <div className="modal-error" style={{ display: "block" }}>{taskError}</div>}
              <div className="field">
                <label>Title *</label>
                <input value={taskForm.title} onChange={(e) => setTaskForm({ ...taskForm, title: e.target.value })} placeholder="e.g. Follow up with Ali" />
              </div>
              <div className="field">
                <label>Assigned to</label>
                <input value={taskForm.assignedTo} onChange={(e) => setTaskForm({ ...taskForm, assignedTo: e.target.value })} placeholder="e.g. Ayesha" />
              </div>
              <div className="field">
                <label>Priority</label>
                <select value={taskForm.priority} onChange={(e) => setTaskForm({ ...taskForm, priority: e.target.value })}>
                  <option>Low</option>
                  <option>Medium</option>
                  <option>High</option>
                </select>
              </div>
              <div className="field">
                <label>Deadline</label>
                <input type="date" value={taskForm.deadline} onChange={(e) => setTaskForm({ ...taskForm, deadline: e.target.value })} />
              </div>
              <div className="modal-actions">
                <button className="btn btn-ghost" onClick={() => setTaskModalOpen(false)}>
                  Cancel
                </button>
                <button className="btn btn-primary" onClick={submitTask}>
                  {editingTaskId ? "Save changes" : "Save task"}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Timeline modal */}
        {timelineOpen && (
          <div className="overlay show">
            <div className="modal" style={{ width: 460 }}>
              <h3 className="disp">Activity timeline</h3>
              <p className="hint">
                {timelineCustomerId ? customerName(timelineCustomerId) : ""} — every interaction logged, most recent first.
              </p>
              {timelineError && <div className="modal-error" style={{ display: "block" }}>{timelineError}</div>}

              <div className="timeline-list">
                {timelineLoading ? (
                  <div className="timeline-loading">Loading…</div>
                ) : timeline.length === 0 ? (
                  <div className="timeline-empty">No activity logged yet for this customer.</div>
                ) : (
                  timeline.map((a) => (
                    <div className="timeline-item" key={a.id}>
                      <div className="timeline-item-head">
                        <span className={`pill ${pillClass(a.type, "activity")}`}>{a.type}</span>
                        <span className="cell-mono">{fmtDateTime(a.timestamp)}</span>
                      </div>
                      <div className="timeline-item-desc">{esc(a.description)}</div>
                    </div>
                  ))
                )}
              </div>

              <div className="field">
                <label>Type</label>
                <select value={activityForm.type} onChange={(e) => setActivityForm({ ...activityForm, type: e.target.value })}>
                  <option>Email</option>
                  <option>Call</option>
                  <option>Meeting</option>
                  <option>Note</option>
                </select>
              </div>
              <div className="field">
                <label>Description</label>
                <input
                  value={activityForm.description}
                  onChange={(e) => setActivityForm({ ...activityForm, description: e.target.value })}
                  placeholder="e.g. Sent quotation for 25 laptops"
                />
              </div>

              <div className="modal-actions">
                <button className="btn btn-ghost" onClick={() => setTimelineOpen(false)}>
                  Close
                </button>
                <button className="btn btn-primary" onClick={submitActivity}>
                  Log activity
                </button>
              </div>
            </div>
          </div>
        )}

        {toast && (
          <div className="toast show">
            <span className="dot" style={{ background: toast.error ? "#C15B45" : "#4BA987" }} />
            <span>{toast.text}</span>
          </div>
        )}

        <style jsx global>{`
          .crm-scope {
            --ink: #14171f;
            --ink-soft: #5b6172;
            --ink-faint: #9297a6;
            --paper: #f7f6f3;
            --panel: #ffffff;
            --line: #e3e1da;
            --line-strong: #d4d1c7;
            --brass: #b98b3e;
            --brass-deep: #92702e;
            --brass-tint: #fbf2e2;
            --teal: #2f7d6b;
            --teal-tint: #e6f1ee;
            --red: #b4432f;
            --red-tint: #fbebe7;
            --blue: #35618f;
            --blue-tint: #e9eff6;
            --violet: #6b4e8e;
            --violet-tint: #f0ebf5;
            background: var(--paper);
            color: var(--ink);
            font-family: "Inter", sans-serif;
            font-size: 14px;
            min-height: 100vh;
          }
          .crm-scope .disp {
            font-family: "Space Grotesk", sans-serif;
            letter-spacing: -0.01em;
          }
          .crm-scope .mono {
            font-family: "IBM Plex Mono", monospace;
            font-variant-numeric: tabular-nums;
          }
          .crm-main {
            padding: 40px 46px;
            max-width: 1180px;
          }
          .crm-scope .page-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-bottom: 30px;
            gap: 20px;
            flex-wrap: wrap;
          }
          .crm-scope .eyebrow {
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: var(--brass-deep);
            margin-bottom: 6px;
          }
          .crm-scope .page-header h1 {
            font-family: "Space Grotesk", sans-serif;
            font-size: 25px;
            font-weight: 700;
          }
          .crm-scope .page-header p {
            color: var(--ink-soft);
            font-size: 13px;
            margin-top: 5px;
            max-width: 46ch;
          }
          .crm-subnav {
            display: flex;
            gap: 2px;
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 3px;
          }
          .crm-tab {
            font-size: 12.5px;
            font-weight: 600;
            padding: 7px 12px;
            border-radius: 6px;
            color: var(--ink-soft);
            background: transparent;
            border: none;
            cursor: pointer;
          }
          .crm-tab.active {
            background: var(--ink);
            color: #fff;
          }
          .crm-scope .btn {
            font-family: "Inter", sans-serif;
            font-weight: 600;
            font-size: 13px;
            padding: 10px 18px;
            border-radius: 7px;
            border: none;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
          }
          .crm-scope .btn-primary {
            background: var(--ink);
            color: #fff;
          }
          .crm-scope .btn-primary:hover {
            background: #262b38;
          }
          .crm-scope .btn-ghost {
            background: transparent;
            color: var(--ink);
            border: 1px solid var(--line-strong);
          }
          .crm-scope .edit-link {
            background: none;
            border: none;
            cursor: pointer;
            font-family: "Inter", sans-serif;
            font-size: 12px;
            font-weight: 600;
            color: var(--brass-deep);
            padding: 0;
          }
          .crm-scope .edit-link:hover {
            text-decoration: underline;
          }
          .crm-scope .stat-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0;
            margin-bottom: 36px;
            border: 1px solid var(--line);
            border-radius: 10px;
            overflow: hidden;
            background: var(--panel);
          }
          .crm-scope .stat-card {
            padding: 20px 22px;
            border-right: 1px solid var(--line);
          }
          .crm-scope .stat-card:last-child {
            border-right: none;
          }
          .crm-scope .stat-card .label {
            font-size: 11px;
            color: var(--ink-soft);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            font-weight: 600;
          }
          .crm-scope .stat-card .value {
            font-family: "IBM Plex Mono", monospace;
            font-size: 30px;
            font-weight: 600;
            margin-top: 8px;
          }
          .crm-scope .stat-card .sub {
            font-size: 11.5px;
            color: var(--ink-faint);
            margin-top: 4px;
          }
          .crm-scope .panel {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 10px;
            overflow: hidden;
          }
          .crm-scope .panel-head {
            padding: 16px 22px;
            border-bottom: 1px solid var(--line);
          }
          .crm-scope .panel-head h2 {
            font-family: "Space Grotesk", sans-serif;
            font-size: 14px;
            font-weight: 600;
          }
          .crm-scope table {
            width: 100%;
            border-collapse: collapse;
          }
          .crm-scope th {
            text-align: left;
            padding: 11px 22px;
            font-size: 10.5px;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            color: var(--ink-faint);
            font-weight: 600;
            border-bottom: 1px solid var(--line);
          }
          .crm-scope td {
            padding: 13px 22px;
            border-bottom: 1px dashed var(--line);
            font-size: 13.5px;
          }
          .crm-scope tr:last-child td {
            border-bottom: none;
          }
          .crm-scope tr:hover td {
            background: #fcfbf8;
          }
          .crm-scope .cell-name {
            font-weight: 600;
          }
          .crm-scope .cell-muted {
            color: var(--ink-soft);
          }
          .crm-scope .cell-mono {
            font-family: "IBM Plex Mono", monospace;
            font-size: 12px;
            color: var(--ink-faint);
          }
          .crm-scope .empty-state {
            padding: 50px 20px;
            text-align: center;
            color: var(--ink-faint);
          }
          .crm-scope .empty-state .mark {
            font-family: "IBM Plex Mono", monospace;
            font-size: 20px;
            margin-bottom: 10px;
            color: var(--line-strong);
          }
          .crm-scope .empty-state p.t {
            font-size: 13.5px;
            font-weight: 600;
            color: var(--ink-soft);
          }
          .crm-scope .empty-state p.s {
            font-size: 12.5px;
            margin-top: 3px;
          }
          .crm-scope .pill {
            display: inline-flex;
            align-items: center;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
          }
          .crm-scope .pill-new {
            background: var(--blue-tint);
            color: var(--blue);
          }
          .crm-scope .pill-contacted {
            background: var(--brass-tint);
            color: var(--brass-deep);
          }
          .crm-scope .pill-negotiation {
            background: var(--violet-tint);
            color: var(--violet);
          }
          .crm-scope .pill-closed {
            background: var(--teal-tint);
            color: var(--teal);
          }
          .crm-scope .pill-high {
            background: var(--red-tint);
            color: var(--red);
          }
          .crm-scope .pill-medium {
            background: var(--brass-tint);
            color: var(--brass-deep);
          }
          .crm-scope .pill-low {
            background: #eeeeea;
            color: var(--ink-soft);
          }
          .crm-scope .board {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 14px;
          }
          .crm-scope .board-col {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 10px;
            min-height: 200px;
          }
          .crm-scope .board-col-head {
            padding: 13px 15px;
            border-bottom: 1px solid var(--line);
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 3px solid;
            border-radius: 10px 10px 0 0;
          }
          .crm-scope .board-col-head .title {
            font-family: "Space Grotesk", sans-serif;
            font-weight: 600;
            font-size: 12.5px;
          }
          .crm-scope .board-col-head .n {
            font-family: "IBM Plex Mono", monospace;
            font-size: 11px;
            color: var(--ink-soft);
            background: var(--paper);
            padding: 2px 7px;
            border-radius: 20px;
          }
          .crm-scope .col-top-new {
            border-top-color: var(--blue);
          }
          .crm-scope .col-top-contacted {
            border-top-color: var(--brass);
          }
          .crm-scope .col-top-negotiation {
            border-top-color: var(--violet);
          }
          .crm-scope .col-top-closed {
            border-top-color: var(--teal);
          }
          .crm-scope .board-col-body {
            padding: 10px;
            display: flex;
            flex-direction: column;
            gap: 8px;
          }
          .crm-scope .lead-card {
            background: var(--paper);
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 12px 13px;
          }
          .crm-scope .lead-card .lname {
            font-weight: 600;
            font-size: 13px;
          }
          .crm-scope .lead-card .lmeta {
            font-size: 11.5px;
            color: var(--ink-soft);
            margin-top: 3px;
          }
          .crm-scope .lead-card select {
            margin-top: 8px;
            width: 100%;
            font-size: 11.5px;
            padding: 6px 7px;
            border-radius: 6px;
            border: 1px solid var(--line-strong);
            font-family: "Inter";
            background: #fff;
          }
          .crm-scope .overlay {
            position: fixed;
            inset: 0;
            background: rgba(20, 23, 31, 0.45);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 50;
          }
          .crm-scope .overlay.show {
            display: flex;
          }
          .crm-scope .modal {
            background: #fff;
            border-radius: 12px;
            width: 420px;
            max-width: 92vw;
            padding: 26px;
            box-shadow: 0 24px 70px rgba(20, 23, 31, 0.28);
            border-top: 3px solid var(--brass);
            color: var(--ink);
          }
          .crm-scope .modal h3 {
            font-family: "Space Grotesk", sans-serif;
            font-size: 17px;
            margin-bottom: 4px;
          }
          .crm-scope .modal .hint {
            font-size: 12.5px;
            color: var(--ink-soft);
            margin-bottom: 18px;
          }
          .crm-scope .field {
            margin-bottom: 14px;
          }
          .crm-scope .field label {
            display: block;
            font-size: 11.5px;
            font-weight: 600;
            margin-bottom: 6px;
            color: var(--ink-soft);
            text-transform: uppercase;
            letter-spacing: 0.03em;
          }
          .crm-scope .field input,
          .crm-scope .field select {
            width: 100%;
            padding: 9px 11px;
            border: 1px solid var(--line-strong);
            border-radius: 7px;
            font-family: "Inter";
            font-size: 13.5px;
            background: var(--paper);
            color: var(--ink);
          }
          .crm-scope .modal-actions {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            justify-content: flex-end;
          }
          .crm-scope .modal-error {
            background: var(--red-tint);
            color: var(--red);
            font-size: 12.5px;
            padding: 9px 12px;
            border-radius: 7px;
            margin-bottom: 14px;
          }
          .crm-scope .timeline-list {
            max-height: 280px;
            overflow-y: auto;
            margin-bottom: 18px;
            border: 1px solid var(--line);
            border-radius: 8px;
          }
          .crm-scope .timeline-item {
            padding: 11px 14px;
            border-bottom: 1px dashed var(--line);
          }
          .crm-scope .timeline-item:last-child {
            border-bottom: none;
          }
          .crm-scope .timeline-item-head {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 10px;
          }
          .crm-scope .timeline-item-desc {
            font-size: 13px;
            margin-top: 6px;
            line-height: 1.45;
          }
          .crm-scope .timeline-empty,
          .crm-scope .timeline-loading,
          .crm-scope .timeline-error {
            padding: 18px 14px;
            color: var(--ink-faint);
            font-size: 12.5px;
          }
          .crm-scope .toast {
            position: fixed;
            bottom: 26px;
            left: 50%;
            transform: translateX(-50%);
            background: var(--ink);
            color: #fff;
            padding: 12px 20px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 100;
          }
          .crm-scope .toast .dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
          }
          @media (max-width: 900px) {
            .crm-scope .stat-row {
              grid-template-columns: repeat(2, 1fr);
            }
            .crm-scope .board {
              grid-template-columns: 1fr;
            }
            .crm-main {
              padding: 24px 18px;
            }
          }
        `}</style>
      </section>
    </main>
  );
}
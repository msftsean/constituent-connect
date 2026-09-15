import { useEffect, useMemo, useState } from "react";

type Citation = { title: string; public_url: string; excerpt: string };
type Sample = { id: string; label: string; message: string; channel: string };
type Workflow = {
  message: Record<string, unknown>;
  inquiry: Record<string, any>;
  route: Record<string, any>;
  response: Record<string, any>;
};
type ApprovalSession = {
  approval_role: string;
  approver_token: string;
  approver_id: string;
};
type ApprovalSessionResponse = ApprovalSession | { data?: ApprovalSession };

const api = async <T,>(path: string, init?: RequestInit): Promise<T> => {
  const { headers, ...rest } = init ?? {};
  const response = await fetch(path, {
    ...rest,
    headers: { "Content-Type": "application/json", ...(headers ?? {}) },
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error ?? "Request failed");
  return data as T;
};

const JsonPanel = ({ value }: { value: unknown }) => (
  <pre className="json-panel">{JSON.stringify(value, null, 2)}</pre>
);

export function App() {
  const [samples, setSamples] = useState<Sample[]>([]);
  const [sampleId, setSampleId] = useState("");
  const [message, setMessage] = useState("");
  const [channel, setChannel] = useState("web");
  const [reviewer, setReviewer] = useState("workshop-reviewer");
  const [draft, setDraft] = useState("");
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [caseRecord, setCaseRecord] = useState<unknown>(null);
  const [status, setStatus] = useState("Ready for a synthetic inquiry.");
  const [busy, setBusy] = useState(false);
  const [approvalSession, setApprovalSession] = useState<ApprovalSession | null>(null);

  useEffect(() => {
    api<{ items: Sample[] }>("/api/synthetic/inquiries")
      .then(({ items }) => setSamples(items))
      .catch((error: Error) => setStatus(error.message));
    api<ApprovalSessionResponse>("/api/workshop/approval-session")
      .then((session) => {
        if ("approver_token" in session) {
          setApprovalSession(session);
        } else {
          setApprovalSession(session.data ?? null);
        }
      })
      .catch(() => setApprovalSession(null));
  }, []);

  const selectedSample = useMemo(
    () => samples.find((item) => item.id === sampleId),
    [sampleId, samples],
  );

  const process = async () => {
    setBusy(true);
    setCaseRecord(null);
    try {
      const result = await api<Workflow>("/api/respond", {
        method: "POST",
        body: JSON.stringify({ message, channel }),
      });
      setWorkflow(result);
      setDraft(result.response.draft);
      setStatus("Draft ready for human review.");
    } catch (error) {
      setStatus((error as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const approve = async () => {
    if (!workflow) return;
    setBusy(true);
    try {
      const response = await api<Record<string, any>>(
        `/api/responses/${workflow.response.response_id}/approve`,
        {
          method: "POST",
          headers: {
            "X-Approval-Role": approvalSession?.approval_role ?? "approver",
            ...(approvalSession?.approver_token ? { "X-Approver-Token": approvalSession.approver_token } : {}),
          },
          body: JSON.stringify({ reviewer, edited_text: draft, decision: "approve" }),
        },
      );
      setWorkflow({ ...workflow, response: { ...workflow.response, ...response } });
      setStatus(`Approved by ${response.approved_by}.`);
    } catch (error) {
      setStatus((error as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const createCase = async () => {
    if (!workflow) return;
    setBusy(true);
    try {
      const created = await api<Record<string, unknown>>("/api/cases", {
        method: "POST",
        body: JSON.stringify({ response_id: workflow.response.response_id }),
      });
      setCaseRecord(created);
      setStatus("Synthetic case created after human approval.");
    } catch (error) {
      setStatus((error as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const emergency = workflow?.inquiry.emergency_signal;
  const approved = workflow?.response.approval_status === "approved";

  return (
    <div className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">LOCAL SYNTHETIC CONTACT CENTER</p>
          <h1>Maryland Constituent Connect</h1>
          <p className="subtitle">Grounded, human-reviewed help for non-emergency service inquiries.</p>
        </div>
        <span className="status-pill"><span className="status-dot" /> Local mode</span>
      </header>

      <main>
        <section className="intake-card" aria-labelledby="intake-title">
          <div className="section-heading">
            <div>
              <p className="eyebrow">LISTEN</p>
              <h2 id="intake-title">New inquiry</h2>
            </div>
            <span className="safety-note">Synthetic data only</span>
          </div>
          <div className="form-grid">
            <label>Example
              <select value={sampleId} onChange={(event) => {
                const value = event.target.value;
                setSampleId(value);
                const sample = samples.find((item) => item.id === value);
                if (sample) { setMessage(sample.message); setChannel(sample.channel); }
              }}>
                <option value="">Choose a synthetic inquiry</option>
                {samples.map((sample) => <option key={sample.id} value={sample.id}>{sample.label}</option>)}
              </select>
            </label>
            <label>Channel
              <select value={channel} onChange={(event) => setChannel(event.target.value)}>
                {["web", "chat", "email", "voice"].map((option) => <option key={option}>{option}</option>)}
              </select>
            </label>
          </div>
          <label htmlFor="message">Constituent message</label>
          <textarea id="message" value={message} onChange={(event) => setMessage(event.target.value)}
            placeholder="Enter synthetic content only." rows={5} />
          <div className="action-row">
            <button className="primary" disabled={busy || !message.trim()} onClick={process}>
              {busy ? "Processing..." : "Process inquiry"}
            </button>
            <span role="status" className="status-text">{status}</span>
          </div>
        </section>

        {emergency && <section className="emergency" role="alert">
          <p className="eyebrow">EMERGENCY EXIT</p>
          <h2>Routine processing stopped</h2>
          <p>{workflow?.inquiry.emergency_guidance}</p>
          <strong>No emergency dispatch action was created.</strong>
        </section>}

        <section className="dashboard" aria-live="polite">
          <article className="panel"><PanelTitle eyebrow="LISTEN" title="Conversation" /><JsonPanel value={workflow?.message ?? "No inquiry selected."} /></article>
          <article className="panel"><PanelTitle eyebrow="PRIVACY" title="Summary" /><JsonPanel value={workflow ? {
            summary: workflow.inquiry.summary,
            redacted_content: workflow.inquiry.redacted_content,
            detected_language: workflow.inquiry.detected_language,
            pii_findings: workflow.inquiry.pii_findings,
          } : "Waiting for intake."} /></article>
          <article className="panel"><PanelTitle eyebrow="EVIDENCE" title="Approved sources" />
            {workflow?.response.citations?.length ? workflow.response.citations.map((citation: Citation, index: number) =>
              <div className="citation" key={`${citation.public_url}-${index}`}><a href={citation.public_url} target="_blank" rel="noreferrer">[{index + 1}] {citation.title}</a><p>{citation.excerpt}</p></div>) :
              <p className="muted">No approved evidence retrieved.</p>}
          </article>
          <article className="panel"><PanelTitle eyebrow="ROUTE" title="Accountability" /><JsonPanel value={workflow?.route ?? "No route proposed."} /></article>
          <article className="panel wide"><PanelTitle eyebrow="RESPOND" title="Response & human approval" />
            {workflow && <p className="disclosure">{workflow.response.ai_disclosure}</p>}
            <textarea aria-label="Response draft" value={draft} onChange={(event) => setDraft(event.target.value)}
              disabled={!workflow || emergency || approved} rows={7} />
            <div className="action-row">
              <input aria-label="Reviewer name" value={reviewer} onChange={(event) => setReviewer(event.target.value)} />
              <button className="primary" disabled={!workflow || busy || emergency || approved} onClick={approve}>Approve draft</button>
              <button disabled={!approved || busy || Boolean(caseRecord)} onClick={createCase}>Create synthetic case</button>
            </div>
            {caseRecord ? <JsonPanel value={caseRecord} /> : null}
          </article>
          <article className="panel wide"><PanelTitle eyebrow="COACH" title="Trace" />
            <JsonPanel value={workflow?.inquiry.transformation_history ?? "No trace available."} />
          </article>
        </section>
      </main>
      <footer>AI-assisted drafts remain pending until a human approves them · Not for emergencies · Synthetic data only</footer>
    </div>
  );
}

function PanelTitle({ eyebrow, title }: { eyebrow: string; title: string }) {
  return <div className="panel-title"><p className="eyebrow">{eyebrow}</p><h2>{title}</h2></div>;
}

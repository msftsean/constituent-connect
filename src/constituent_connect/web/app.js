const byId = (id) => document.getElementById(id);
let currentResponseId = null;

const showJson = (id, value) => {
  byId(id).textContent = JSON.stringify(value, null, 2);
};

async function request(path, options = {}) {
  const response = await fetch(path, {
    headers: {"Content-Type": "application/json"},
    ...options,
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Request failed");
  return data;
}

async function loadSamples() {
  const data = await request("/api/synthetic/inquiries");
  data.items.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = item.label;
    option.dataset.message = item.message;
    option.dataset.channel = item.channel;
    byId("sample").appendChild(option);
  });
}

byId("sample").addEventListener("change", (event) => {
  const option = event.target.selectedOptions[0];
  if (!option.dataset.message) return;
  byId("message").value = option.dataset.message;
  byId("channel").value = option.dataset.channel;
});

byId("process").addEventListener("click", async () => {
  byId("request-status").textContent = "Processing…";
  byId("approve").disabled = true;
  byId("case").disabled = true;
  byId("case-result").textContent = "";
  try {
    const data = await request("/api/respond", {
      method: "POST",
      body: JSON.stringify({message: byId("message").value, channel: byId("channel").value}),
    });
    currentResponseId = data.response.response_id;
    showJson("conversation", {
      channel: data.message.channel,
      received_at: data.message.received_at,
      content: data.message.raw_content,
    });
    showJson("summary", {
      summary: data.inquiry.summary,
      redacted_content: data.inquiry.redacted_content,
      detected_language: data.inquiry.detected_language,
      pii_findings: data.inquiry.pii_findings,
      injection_detected: data.inquiry.injection_detected,
    });
    showJson("route", data.route);
    byId("draft").value = data.response.draft;
    byId("disclosure").textContent = data.response.ai_disclosure;
    byId("trace").textContent = data.inquiry.transformation_history
      .map((item) => `${item.stage}: ${item.outcome}\n${JSON.stringify(item.details, null, 2)}`)
      .join("\n\n");
    byId("evidence").replaceChildren();
    data.response.citations.forEach((citation, index) => {
      const link = document.createElement("a");
      link.href = citation.public_url;
      link.target = "_blank";
      link.rel = "noreferrer";
      link.textContent = `[${index + 1}] ${citation.title}`;
      byId("evidence").appendChild(link);
      const excerpt = document.createElement("p");
      excerpt.textContent = citation.excerpt;
      byId("evidence").appendChild(excerpt);
    });
    if (!data.response.citations.length) byId("evidence").textContent = "No approved evidence retrieved; response abstains or provides safety guidance.";
    byId("emergency").classList.toggle("hidden", !data.inquiry.emergency_signal);
    byId("emergency-text").textContent = data.inquiry.emergency_guidance || "";
    byId("approve").disabled = data.inquiry.emergency_signal;
    byId("request-status").textContent = "Draft ready for human review.";
  } catch (error) {
    byId("request-status").textContent = error.message;
  }
});

byId("approve").addEventListener("click", async () => {
  try {
    const data = await request(`/api/responses/${currentResponseId}/approve`, {
      method: "POST",
      body: JSON.stringify({
        reviewer: byId("reviewer").value,
        edited_text: byId("draft").value,
        decision: "approve",
      }),
    });
    byId("request-status").textContent = `Approved by ${data.approved_by}.`;
    byId("approve").disabled = true;
    byId("case").disabled = false;
  } catch (error) {
    byId("request-status").textContent = error.message;
  }
});

byId("case").addEventListener("click", async () => {
  try {
    const data = await request("/api/cases", {
      method: "POST",
      body: JSON.stringify({response_id: currentResponseId}),
    });
    showJson("case-result", data);
    byId("case").disabled = true;
  } catch (error) {
    byId("request-status").textContent = error.message;
  }
});

loadSamples().catch((error) => {
  byId("request-status").textContent = error.message;
});

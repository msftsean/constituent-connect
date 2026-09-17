## 🧭 Summary

- What changed:
- Why it changed:
- Deferred work:

## ✅ Validation evidence

- [ ] Python tests: `python -m unittest discover -s tests -v`
- [ ] Eval gate: `python -m constituent_connect.eval_runner --output reports\local`
- [ ] Frontend build: `npm --prefix frontend run build -- --emptyOutDir`
- [ ] Secret/PII scan reviewed
- [ ] Docs/specs updated

## 🛡️ Safety checklist

- [ ] No real constituent, participant, tenant, subscription, endpoint, or secret data
- [ ] Emergency routing still exits routine processing and does not dispatch
- [ ] Raw PII is not exposed to normal browser/API/log/report/work-item paths
- [ ] Human approval remains server-side and authenticated
- [ ] External outbound connectors remain disabled by default

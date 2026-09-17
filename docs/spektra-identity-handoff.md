# 🔐 Spektra Identity Handoff for Codespaces

**Revision:** 2026-09-17 · **Scope:** Spektra clone / Codespaces · **Status:** 🟩🟩🟩⬜⬜ user-authenticated only

Use this when the workshop repository is running from a Spektra-owned clone. The assistant must not sign in as another user, receive passwords, paste device codes into chat, or store GitHub/Azure tokens. Authentication is an interactive user step.

## GitHub identity

In the Codespace terminal, sign in with the Spektra GitHub identity in the browser/device flow:

```bash
gh auth status
gh auth logout --hostname github.com
gh auth login --hostname github.com --web
gh auth status
gh api user --jq '.login'
```

Expected:

- `gh auth status` shows the active GitHub.com account.
- `gh api user --jq '.login'` returns the Spektra account login that owns or can write to the clone.
- Do not paste tokens, passwords, recovery codes, or device codes into chat.

## Git remote verification

Confirm the Codespace is using the Spektra clone remote, not a personal fork unless that is intentional:

```bash
git remote -v
git status --short --branch
git branch --show-current
```

If the remote is wrong, change it only to a repository you are authorized to access:

```bash
git remote set-url origin https://github.com/OWNER/REPOSITORY.git
git fetch origin --prune
```

## Azure identity

Sign in interactively with the Azure identity approved for the Spektra development environment:

```bash
az account show --output table
az logout
az login
az account show --query '{name:name,user:user.name,tenantId:tenantId}' -o table
azd auth login
```

Before deployment, select only the approved subscription:

```bash
az account list --query '[].{name:name,isDefault:isDefault,state:state}' -o table
az account set --subscription "<approved-subscription-name-or-id>"
az account show --query '{name:name,user:user.name}' -o table
```

Do not place tenant IDs, subscription IDs, secrets, or private endpoints in committed files or chat transcripts.

## Deployment guardrails

Run preview before deployment:

```bash
azd env new constituent-connect-dev
azd env set AZURE_LOCATION eastus2
azd provision --preview --no-prompt
```

Proceed to deployment only if the preview target is authorized and no policy, quota, role-assignment, naming, or budget blocker appears:

```bash
azd up --no-prompt
```

Keep these defaults unless explicitly approved for synthetic use:

- `enableCommunicationServices=false`
- outbound email disabled
- outbound SMS disabled
- outbound phone disabled
- emergency dispatch disabled
- production case-system integrations disabled

## Post-auth verification

After GitHub and Azure login, run:

```bash
python scripts/readiness.py --full-eval
npm --prefix frontend ci
npm --prefix frontend run build -- --emptyOutDir
```

Then follow `docs/codespaces-pre-coach-validation.md` for app smoke tests.

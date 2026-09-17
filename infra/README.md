# Azure infrastructure

`main.bicep` is a subscription-scope template that creates a dedicated resource group
and production-shaped baseline for the synthetic Constituent Connect workshop:

- Azure Container Registry and a Container Apps environment/app with HTTPS ingress,
  startup, readiness, and liveness probes, single-revision deployment, and bounded
  HTTP scaling.
- A user-assigned managed identity used for ACR image pulls and all data-plane access.
- RBAC-enabled Key Vault with purge protection, Blob Storage with public and shared-key
  access disabled, Cosmos DB for NoSQL with local authentication disabled, and Azure AI
  Search with local authentication disabled.
- Log Analytics and workspace-based Application Insights with a configurable retention
  period.
- Cosmos containers for synthetic messages, approvals, cases, and evaluation results,
  plus private Blob containers for knowledge and smoke-test evidence.

No password, connection string, API key, token, constituent record, or other secret is
accepted in `main.parameters.json`. The template uses managed identity and exposes only
service endpoints as deployment outputs. Application Insights receives its platform
connection string directly in the Container App configuration.

## Deployment contract

`azure.yaml` uses Bicep and packages the root `Dockerfile` for the `web` Container Apps
service. It enables Azure remote container build so a Codespace does not need a
running local Docker daemon. `SERVICE_WEB_IMAGE` is supplied by `azd` during the
service build/deploy flow; direct Bicep validation still requires an explicit
non-secret image override. Ensure the deployment workflow configures the registry
identity or preserves the template's managed-identity registry configuration.

Configure non-secret deployment values through Azure Developer CLI environment settings:

```powershell
azd env set AZURE_ENV_NAME workshop-dev
azd env set AZURE_LOCATION eastus2
```

Azure Developer CLI commands are facilitator-only. Participants should stay on
the credential-free local synthetic path. For a controlled production rollout,
first review the application adapter and
production authentication plan, then pass non-secret deployment parameter overrides
for replica bounds or retention using your approved CI/CD deployment command. Do not
add credentials to parameter files or `azd` environment files.

Before validation, a facilitator may run:

```powershell
python scripts\azure_facilitator_preflight.py --location eastus2
```

The script is read-only and checks provider registration, a quota sample, and
likely role-assignment permission.

## Feature flags and safety boundaries

`enableCommunicationServices` defaults to `false`. Setting it to `true` creates only
the ACS resource and surfaces `CC_FEATURE_COMMUNICATION_SERVICES=true`; it does not
enable outreach, sending, dispatch, or bypass human approval. The Container App is
configured with:

- `CC_EMERGENCY_DISPATCH_ENABLED=false`
- `CC_HUMAN_APPROVAL_REQUIRED=true`
- Azure AI Search and Cosmos feature indicators for a future identity-aware adapter

The current local-first implementation does not consume the Azure data-plane endpoints
and has not been production-validated against these resources. Do not enable data
persistence, ACS actions, or automated sending until the application adapter and
production authentication/authorization boundary have been reviewed for the same
synthetic-only, no-dispatch, human-approval constraints.

## Network posture

The storage account denies anonymous Blob access and shared keys; Key Vault denies
public traffic by default except Azure platform services. ACR denies public network
traffic by default. Cosmos DB, AI Search, and the Container App remain publicly
reachable at their service endpoints so the baseline can validate without a managed
VNet and private DNS zone dependency. Production rollout should add a managed
environment VNet, private endpoints, private DNS zones, approved egress, and then
disable public network access for each supported service.

## Validation

Run the following without deploying resources:

```powershell
az bicep build --file infra\main.bicep
az deployment sub validate `
  --location eastus2 `
  --template-file infra\main.bicep `
  --parameters infra\main.parameters.json environmentName=workshop-dev
```

The second command requires an Azure identity with permission to validate resource-group
creation and role assignments. It does not apply a deployment.

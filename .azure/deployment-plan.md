# Constituent Connect Azure Deployment Plan

**Status:** Validated

## Scope

Production-shaped Azure infrastructure, Azure Developer CLI configuration, and workshop
documentation have been prepared. No deployment will be performed.

## Decisions

- **Mode:** Modify an existing Python local-first application without changing its
  backend, API adapter, frontend package, evaluation datasets, or Spec Kit artifacts.
- **Recipe:** Azure Developer CLI with subscription-scoped Bicep in `infra/` and the
  existing root Dockerfile.
- **Architecture:** Dedicated resource group; ACR; Container Apps environment and API;
  user-assigned managed identity; RBAC-enabled Key Vault; private Blob containers;
  Cosmos DB for NoSQL; Azure AI Search; Log Analytics/Application Insights; optional,
  default-disabled ACS.
- **Operational controls:** HTTPS ingress, health probes, min/max replica bounds,
  diagnostic retention, managed identity RBAC, disabled shared-key/local authentication
  where supported, and public-network lockdown documented as the next production
  networking phase.
- **Feature controls:** ACS is opt-in and does not authorize sending. Environment
  indicators preserve no-dispatch and human-approval requirements.
- **Workshop deliverables:** Fresh-user quickstart, participant Lab 00-06 path, coach
  site/runbook, architecture page and editable Draw.io source, scorecard, and
  synthetic concurrent smoke-test evidence/template.

## Safety boundaries

- Use synthetic data only.
- Keep constituent outreach in no-dispatch mode.
- Preserve human approval boundaries.
- Do not store secrets in source control or deployment parameters.

## Role Assignment Verification

- **Status:** Verified
- **Identity checked:** The Container App's user-assigned managed identity.
- **Roles confirmed:** `AcrPull` scoped to the registry; `Storage Blob Data
  Contributor` scoped to the storage account; `Key Vault Secrets User` scoped to the
  vault; `Search Index Data Contributor` scoped to the AI Search service; and Cosmos
  DB Built-in Data Contributor scoped to the Cosmos account root.
- **Finding:** No generic Owner or Contributor role is assigned. ACS has no data-plane
  integration or send permission in this baseline.

## Validation Proof

- **Bicep compilation:** `az bicep build --file infra\main.bicep --outfile
  .azure\main.compiled.json` passed on 2026-09-09. The generated JSON was removed
  immediately after the check.
- **Bicep lint:** `az bicep lint --file infra\main.bicep` passed.
- **Authentication:** `az account show --output none` passed against the configured
  default subscription.
- **Subscription validation:** `az deployment sub validate` passed with the
  subscription-scope template, `workshopvalidate` environment name, public placeholder
  image, and ACS disabled.
- **What-if:** `az deployment sub what-if --result-format ResourceIdOnly` passed with
  the same non-secret inputs. It did not create or modify any resources.
- **Workshop assets:** Participant/coach HTML and Markdown links, plus both synthetic
  smoke-test JSON artifacts, were validated locally.

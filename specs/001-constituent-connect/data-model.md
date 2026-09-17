# Data Model: Maryland Constituent Connect

## ConstituentMessage

- `message_id`
- `channel`
- `received_at`
- `language`
- `raw_content`
- `attachments`
- `consent_flags`

## NormalizedInquiry

- `inquiry_id`
- `summary`
- `redacted_content`
- `detected_language`
- `intent_candidates`
- `urgency`
- `emergency_signal`
- `pii_findings`
- `trace_id`
- `transformation_history`

## AgencyService

- `service_id`
- `agency_id`
- `name`
- `description`
- `eligibility_disclaimer`
- `geography`
- `queue_id`
- `owner_id`
- `public_urls`
- `effective_date`

## RouteRecommendation

- `primary_service_id`
- `secondary_service_ids`
- `confidence`
- `reason`
- `clarifying_question`
- `human_review_required`
- `status`

## GroundedResponse

- `response_id`
- `channel`
- `language`
- `draft`
- `citations`
- `prohibited_commitment_check`
- `approval_status`
- `ai_disclosure`
- `approved_text`
- `approved_by`
- `approved_at`

## CaseRecord

- `case_id`
- `inquiry_id`
- `approved_summary`
- `agency_work_items`
- `status`
- `assigned_queues`
- `audit_events`

## EvaluationResult

- `case_id`
- `category`
- `expected_route`
- `actual_route`
- `scores`
- `severity`
- `trace_id`

## Implemented safety categories

- Emergency states: `routine`, `emergency_exit`, `clarification_required`, `route_proposed`.
- Human decision states: `pending`, `approved`, `rejected`, `escalated`.
- PII categories: social security number, email address, phone number, street address, date of birth, driver/professional license, benefit/tax/case/account identifier, payment card, bank information, password, token/secret, and one-time code.

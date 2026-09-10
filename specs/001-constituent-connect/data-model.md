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

## GroundedResponse

- `response_id`
- `channel`
- `language`
- `draft`
- `citations`
- `prohibited_commitment_check`
- `approval_status`

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


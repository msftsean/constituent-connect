from __future__ import annotations

import argparse
import os
from collections.abc import Callable
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .api_models import (
    ApiResponse,
    ApprovalRequest,
    CaseRequest,
    ErrorResponse,
    HealthResponse,
    InquiryRequest,
)
from .eval_runner import run_evaluations
from .models import to_dict
from .workflow import ConstituentConnectWorkflow


CORRELATION_HEADER = "X-Correlation-ID"
APPROVER_TOKEN_HEADER = "X-Approver-Token"
AUTHENTICATED_REVIEWER_HEADER = "X-Authenticated-Reviewer-ID"


def create_app(workflow: ConstituentConnectWorkflow | None = None) -> FastAPI:
    service = workflow or ConstituentConnectWorkflow()
    app = FastAPI(
        title="Maryland Constituent Connect API",
        version="0.1.0",
        description="Synthetic-only, approval-gated constituent workflow API.",
    )
    app.state.workflow = service

    @app.middleware("http")
    async def correlation_middleware(request: Request, call_next: Callable[..., Any]):
        correlation_id = request.headers.get(CORRELATION_HEADER) or f"corr-{uuid4().hex[:12]}"
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers[CORRELATION_HEADER] = correlation_id
        return response

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        return _error(request, "Request validation failed.", 422, exc.errors())

    @app.exception_handler(ValueError)
    async def value_error(request: Request, exc: ValueError):
        return _error(request, str(exc), 400)

    @app.exception_handler(KeyError)
    async def key_error(request: Request, exc: KeyError):
        return _error(request, str(exc).strip("'"), 404)

    @app.get("/health", response_model=HealthResponse)
    async def health(request: Request) -> dict[str, str]:
        return _with_correlation(
            {"status": "healthy", "mode": "local-synthetic"}, request
        )

    @app.post("/api/intake", response_model=ApiResponse)
    async def intake(payload: InquiryRequest, request: Request) -> dict[str, Any]:
        inquiry = service.assess_intake(
            payload.message, payload.channel, payload.language
        )
        return _with_correlation({"data": _safe_inquiry(inquiry)}, request)

    @app.post("/api/classify", response_model=ApiResponse)
    async def classify(payload: InquiryRequest, request: Request) -> dict[str, Any]:
        inquiry = service.assess_intake(
            payload.message, payload.channel, payload.language
        )
        return _with_correlation(
            {
                "data": {
                    "inquiry_id": inquiry.inquiry_id,
                    "intent_candidates": to_dict(inquiry.intent_candidates),
                    "urgency": inquiry.urgency,
                    "emergency_signal": inquiry.emergency_signal,
                    "trace_id": inquiry.trace_id,
                }
            },
            request,
        )

    @app.post("/api/respond", response_model=ApiResponse)
    async def respond(payload: InquiryRequest, request: Request) -> dict[str, Any]:
        result = service.process(payload.message, payload.channel, payload.language)
        return _with_correlation({"data": _safe_result(result)}, request)

    @app.post("/api/route", response_model=ApiResponse)
    async def route(payload: InquiryRequest, request: Request) -> dict[str, Any]:
        result = service.process(payload.message, payload.channel, payload.language)
        return _with_correlation(
            {
                "data": {
                    "inquiry_id": result.inquiry.inquiry_id,
                    "response_id": result.response.response_id,
                    "route": to_dict(result.route),
                }
            },
            request,
        )

    @app.post("/api/approval", response_model=ApiResponse)
    async def approval(
        payload: ApprovalRequest,
        request: Request,
        reviewer_id: str | None = Header(default=None, alias=AUTHENTICATED_REVIEWER_HEADER),
        approval_role: str | None = Header(default=None, alias="X-Approval-Role"),
        approver_token: str | None = Header(default=None, alias=APPROVER_TOKEN_HEADER),
    ) -> dict[str, Any]:
        if not payload.response_id:
            raise ValueError("response_id is required.")
        configured_token = os.environ.get("CONSTITUENT_CONNECT_APPROVER_TOKEN")
        if (
            not configured_token
            or not approver_token
            or approver_token != configured_token
            or not reviewer_id
            or approval_role != "approver"
        ):
            raise ValueError(
                "Authenticated approver headers X-Authenticated-Reviewer-ID and "
                "X-Approval-Role: approver plus a configured approval token are required."
            )
        response = service.approve_response(
            payload.response_id,
            reviewer_id,
            payload.edited_text,
            payload.decision,
        )
        return _with_correlation({"data": to_dict(response)}, request)

    @app.post("/api/responses/{response_id}/approve", response_model=ApiResponse)
    async def approve_legacy(
        response_id: str,
        payload: ApprovalRequest,
        request: Request,
        reviewer_id: str | None = Header(default=None, alias=AUTHENTICATED_REVIEWER_HEADER),
        approval_role: str | None = Header(default=None, alias="X-Approval-Role"),
        approver_token: str | None = Header(default=None, alias=APPROVER_TOKEN_HEADER),
    ) -> dict[str, Any]:
        if payload.response_id and payload.response_id != response_id:
            raise ValueError("Path response_id must match the request response_id.")
        return await approval(
            payload.model_copy(update={"response_id": response_id}),
            request,
            reviewer_id,
            approval_role,
            approver_token,
        )

    @app.post("/api/cases", response_model=ApiResponse, status_code=201)
    async def create_case(
        payload: CaseRequest, request: Request
    ) -> dict[str, Any]:
        case = service.create_case(payload.response_id)
        return _with_correlation({"data": to_dict(case)}, request)

    @app.get("/api/cases/{case_id}", response_model=ApiResponse)
    async def get_case(case_id: str, request: Request) -> dict[str, Any]:
        try:
            case = service.cases[case_id]
        except KeyError as exc:
            raise KeyError(f"Unknown case ID: {case_id}") from exc
        return _with_correlation({"data": to_dict(case)}, request)

    @app.post("/api/evals/run", response_model=ApiResponse, status_code=202)
    async def evaluations(request: Request) -> dict[str, Any]:
        report = run_evaluations()
        return _with_correlation({"data": report}, request)

    return app


def _with_correlation(payload: dict[str, Any], request: Request) -> dict[str, Any]:
    return {**payload, "correlation_id": request.state.correlation_id}


def _safe_inquiry(inquiry: Any) -> dict[str, Any]:
    data = to_dict(inquiry)
    data.pop("message_id", None)
    data.pop("raw_content", None)
    data.pop("attachments", None)
    return data


def _safe_result(result: Any) -> dict[str, Any]:
    data = to_dict(result)
    data["message"].pop("raw_content", None)
    data["message"].pop("attachments", None)
    data["message"].pop("consent_flags", None)
    return data


def _error(
    request: Request, message: str, status_code: int, details: Any | None = None
) -> JSONResponse:
    correlation_id = getattr(request.state, "correlation_id", f"corr-{uuid4().hex[:12]}")
    response = JSONResponse(
        status_code=status_code,
        content=ErrorResponse(
            error=message, correlation_id=correlation_id, details=details
        ).model_dump(),
    )
    response.headers[CORRELATION_HEADER] = correlation_id
    return response


app = create_app()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the Constituent Connect FastAPI API.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()

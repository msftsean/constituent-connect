namespace ConstituentConnect.Api;

public sealed record IntakeRequest(string Message, string Channel = "web", string? Language = null);
public sealed record ApprovalRequest(string Reviewer, string? EditedText = null, string Decision = "approve");
public sealed record CaseRequest(string ResponseId);

public sealed record PiiFinding(string Category, int Count);
public sealed record IntentCandidate(string ServiceId, string AgencyId, double Score, IReadOnlyList<string> MatchedTerms);
public sealed record Citation(string Title, string PublicUrl, string Excerpt);
public sealed record TraceEvent(string Stage, string Outcome, IReadOnlyDictionary<string, object?> Details);
public sealed record Inquiry(
    string InquiryId, string Summary, string RedactedContent, string DetectedLanguage, IReadOnlyList<IntentCandidate> IntentCandidates,
    bool EmergencySignal, bool InjectionDetected, bool DiscriminatoryInstructionDetected, IReadOnlyList<PiiFinding> PiiFindings,
    string? EmergencyGuidance, IReadOnlyList<TraceEvent> TransformationHistory);
public sealed record RouteRecommendation(
    string? PrimaryServiceId, IReadOnlyList<string> SecondaryServiceIds, double Confidence, string Reason,
    string? ClarifyingQuestion, bool HumanReviewRequired, string Status);
public sealed class GroundedResponse
{
    public required string ResponseId { get; init; }
    public required string InquiryId { get; init; }
    public required string Channel { get; init; }
    public required string Language { get; init; }
    public required string Draft { get; init; }
    public required IReadOnlyList<Citation> Citations { get; init; }
    public required string ApprovalStatus { get; set; }
    public required string AiDisclosure { get; init; }
    public string? ApprovedText { get; set; }
    public string? ApprovedBy { get; set; }
}
public sealed record AgencyWorkItem(string ServiceId, string QueueId, string Summary, string DisclosureNote);
public sealed record CaseRecord(string CaseId, string InquiryId, string ResponseId, string ApprovedSummary,
    IReadOnlyList<AgencyWorkItem> AgencyWorkItems, string Status, IReadOnlyList<string> AssignedQueues);
public sealed record WorkflowResult(Inquiry Inquiry, RouteRecommendation Route, GroundedResponse Response, int ModelCalls);

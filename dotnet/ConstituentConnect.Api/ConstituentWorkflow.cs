using System.Text.RegularExpressions;

namespace ConstituentConnect.Api;

public sealed class ConstituentWorkflow
{
    private const string Disclosure = "This draft was generated with AI assistance and requires human review.";
    public const string ApprovalAuthorityHeader = "X-Local-Synthetic-Approver-Role";
    public const string ApprovalTokenHeader = "X-Local-Synthetic-Approver-Token";
    public const string AuthenticatedReviewerHeader = "X-Authenticated-Reviewer-ID";
    public const string ApprovalAuthorityRole = "human-reviewer";
    private static readonly Regex Emergency = new(@"\b(smoke|fire|trapped|shooting|gun|immediate danger|cannot breathe|not breathing|overdose|medical emergency|suicide|kill myself|active violence|bleeding badly)\b", RegexOptions.IgnoreCase | RegexOptions.Compiled);
    private static readonly Regex Historical = new(@"\b(last year|years ago|historically|old report|past incident)\b", RegexOptions.IgnoreCase | RegexOptions.Compiled);
    private static readonly Regex CurrentDanger = new(@"\b(now|right now|currently|at this moment|today|still|ongoing|active|happening|here|there is|there are|i am|we are|can't|cannot)\b", RegexOptions.IgnoreCase | RegexOptions.Compiled);
    private static readonly Regex CurrentFire = new(@"\b(?:there is|there's|in my|inside my|at my)\b.{0,40}\bfire\b|\bfire\b.{0,40}\b(?:now|right now|currently|today|ongoing|active)\b", RegexOptions.IgnoreCase | RegexOptions.Compiled);
    private static readonly Regex Injection = new(@"\b(ignore (all |your )?(previous |prior )?(rules|instructions)|system prompt|system instructions|hidden instructions|developer message|override (the )?(policy|route|safety)|route .* executive queue|do not follow.*policy)\b", RegexOptions.IgnoreCase | RegexOptions.Compiled);
    private static readonly Regex Discrimination = new(@"\b((slower|faster|lower priority|deny) queue.*(neighborhood|race|religion|sex|language)|(neighborhood|race|religion|sex|language).*(slower|faster|lower priority|deny) queue|route.*based on.*(race|religion|sex|neighborhood|disability))\b", RegexOptions.IgnoreCase | RegexOptions.Compiled);
    private static readonly (string Category, Regex Pattern)[] PiiPatterns =
    [
        ("social_security_number", new(@"\b\d{3}-\d{2}-\d{4}\b", RegexOptions.Compiled)),
        ("email_address", new(@"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", RegexOptions.IgnoreCase | RegexOptions.Compiled)),
        ("phone_number", new(@"(?<!\d)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{3}[-.\s]\d{4}(?!\d)", RegexOptions.Compiled)),
        ("payment_card", new(@"\b(?:\d[ -]*?){13,16}\b", RegexOptions.Compiled)),
        ("password", new(@"\b(?:password|passcode|pin)\s*(?:is|:|=)\s*\S+", RegexOptions.IgnoreCase | RegexOptions.Compiled))
    ];
    private readonly Catalog _catalog;
    private readonly object _lock = new();
    private readonly Dictionary<string, WorkflowResult> _results = [];

    public ConstituentWorkflow() : this(new Catalog()) { }
    public ConstituentWorkflow(Catalog catalog) => _catalog = catalog;

    public Inquiry AssessIntake(string content, string channel = "web", string? language = null) =>
        BuildInquiry(content, language);

    public WorkflowResult Process(string content, string channel = "web", string? language = null)
    {
        if (!new[] { "web", "chat", "email", "voice" }.Contains(channel, StringComparer.OrdinalIgnoreCase))
            throw new ArgumentOutOfRangeException(nameof(channel), "Channel must be web, chat, email, or voice.");

        var inquiry = BuildInquiry(content, language);
        var candidates = inquiry.EmergencySignal ? [] : Classify(inquiry.RedactedContent);
        inquiry = inquiry with { IntentCandidates = candidates };
        var route = Route(inquiry);
        var citations = Retrieve(inquiry, route);
        var response = Draft(inquiry, route, citations, channel);
        var result = new WorkflowResult(inquiry, route, response, 0);
        lock (_lock) _results.Add(response.ResponseId, result);
        return result;
    }

    public GroundedResponse ApproveResponse(string responseId, string reviewer, string? editedText = null, string decision = "approve", string? approverRole = null, string? approverToken = null)
    {
        lock (_lock)
        {
            var result = GetResult(responseId);
            var configuredToken = Environment.GetEnvironmentVariable("CONSTITUENT_CONNECT_APPROVER_TOKEN");
            if (!string.Equals(approverRole, ApprovalAuthorityRole, StringComparison.Ordinal) ||
                string.IsNullOrWhiteSpace(configuredToken) ||
                !string.Equals(approverToken, configuredToken, StringComparison.Ordinal))
                throw new UnauthorizedAccessException("Approval requires configured authenticated approver credentials.");
            if (result.Response.ApprovalStatus != "pending") throw new InvalidOperationException("This response already has a human decision.");
            if (decision is not ("approve" or "reject")) throw new InvalidOperationException("Decision must be 'approve' or 'reject'.");
            var candidate = (editedText ?? result.Response.Draft).Trim();
            if (decision == "approve" && Regex.IsMatch(candidate, @"\b(guarantee|promise payment|approve.*automatically)\b", RegexOptions.IgnoreCase))
                throw new InvalidOperationException("Edited response contains a prohibited commitment.");
            result.Response.ApprovalStatus = decision == "approve" ? "approved" : "rejected";
            result.Response.ApprovedBy = reviewer;
            result.Response.ApprovedText = decision == "approve" ? $"{candidate} {Disclosure}".Trim() : null;
            return result.Response;
        }
    }

    public CaseRecord CreateCase(string responseId)
    {
        lock (_lock)
        {
            var result = GetResult(responseId);
            if (result.Inquiry.EmergencySignal) throw new InvalidOperationException("Emergency inquiries cannot become routine cases.");
            if (result.Response.ApprovalStatus != "approved") throw new InvalidOperationException("Human approval is required before case creation.");
            if (result.Route.Status != "route_proposed" || result.Route.PrimaryServiceId is null) throw new InvalidOperationException("A confirmed proposed route is required before case creation.");
            var workItems = new[] { result.Route.PrimaryServiceId }.Concat(result.Route.SecondaryServiceIds)
                .Select(serviceId => {
                    var service = _catalog.ServiceById(serviceId);
                    return new AgencyWorkItem(serviceId, service.QueueId, BuildServiceScopedSummary(result.Inquiry, service),
                        "Contains only the redacted constituent summary needed for this synthetic service handoff.");
                }).ToList();
            return new CaseRecord(NewId("case"), result.Inquiry.InquiryId, responseId, result.Inquiry.Summary, workItems, "open", workItems.Select(item => item.QueueId).ToList());
        }
    }

    private Inquiry BuildInquiry(string content, string? language)
    {
        var findings = new List<PiiFinding>();
        var redacted = content ?? string.Empty;
        foreach (var (category, pattern) in PiiPatterns)
        {
            var count = pattern.Count(redacted);
            if (count > 0) { findings.Add(new(category, count)); redacted = pattern.Replace(redacted, $"[REDACTED] {category.ToUpperInvariant()}"); }
        }
        var sensitiveRequest = Regex.IsMatch(content ?? "", @"\b(repeat|show|include|disclose).{0,35}(social security|ssn|password|credential|passcode)", RegexOptions.IgnoreCase);
        if (sensitiveRequest && findings.Count == 0) findings.Add(new("sensitive_data_request", 1));
        var injection = Injection.IsMatch(content ?? "");
        if (injection) redacted = Injection.Replace(redacted, "[IGNORED UNTRUSTED INSTRUCTION]");
        var hasEmergencyLanguage = Emergency.IsMatch(content ?? "");
        var emergency = hasEmergencyLanguage && (!Historical.IsMatch(content ?? "") || CurrentDanger.IsMatch(content ?? "") || CurrentFire.IsMatch(content ?? ""));
        var detectedLanguage = !string.IsNullOrWhiteSpace(language) && language != "und" ? language :
            Regex.Matches(content ?? "", @"\b(necesito|licencia|impuesto|ayuda|solicitud|permiso|gracias)\b", RegexOptions.IgnoreCase).Count >= 2 ? "es" : "en";
        var summary = BuildSafeSummary(redacted, findings, injection, emergency);
        var guidance = emergency ? "If anyone is in immediate danger, call 911 now. This application cannot dispatch emergency services. A human contact-center escalation is required." : null;
        return new Inquiry(NewId("inq"), summary, redacted, detectedLanguage, [], emergency, injection, Discrimination.IsMatch(content ?? ""), findings, guidance,
            [new("safety_privacy", emergency ? "emergency_exit" : "routine_allowed", new Dictionary<string, object?> { ["model_calls"] = 0, ["pii_categories"] = findings.Select(f => f.Category).ToArray() })]);
    }

    private List<IntentCandidate> Classify(string text) => _catalog.Services.Select(service =>
    {
        var matched = service.Keywords.Where(keyword => Regex.IsMatch(text, $@"\b{Regex.Escape(keyword)}\b", RegexOptions.IgnoreCase)).ToList();
        var points = matched.Sum(term => term.Contains(' ') ? 1.0 : .45);
        return new IntentCandidate(service.ServiceId, service.AgencyId, Math.Min(.99, .25 + points * .4), matched);
    }).Where(candidate => candidate.MatchedTerms.Count > 0).OrderByDescending(candidate => candidate.Score).ToList();

    private RouteRecommendation Route(Inquiry inquiry)
    {
        if (inquiry.EmergencySignal) return new(null, [], 1, "Emergency language requires immediate guidance and human escalation; no routine queue or dispatch action was created.", null, true, "emergency_exit");
        if (inquiry.DiscriminatoryInstructionDetected) return new(null, [], 0, "Discriminatory routing instructions are not permitted.", "Which service need should be considered without protected characteristics?", true, "clarification_required");
        if (inquiry.IntentCandidates.Count == 0 || inquiry.IntentCandidates[0].Score < _catalog.MinimumConfidence)
            return new(null, [], inquiry.IntentCandidates.FirstOrDefault()?.Score ?? 0, "No configured service has enough evidence for a reliable route.", "Which Maryland service or type of permit, license, payment, or registration do you need help with?", true, "clarification_required");
        var primary = inquiry.IntentCandidates[0];
        var secondaries = inquiry.IntentCandidates.Skip(1).Where(candidate => candidate.Score >= _catalog.SecondaryConfidence && candidate.AgencyId != primary.AgencyId).Select(candidate => candidate.ServiceId).ToList();
        return new(primary.ServiceId, secondaries, primary.Score, $"Matched configured terms for {_catalog.ServiceById(primary.ServiceId).Name}.", null, true, "route_proposed");
    }

    private List<Citation> Retrieve(Inquiry inquiry, RouteRecommendation route)
    {
        if (inquiry.EmergencySignal || route.PrimaryServiceId is null) return [];
        var ids = new HashSet<string>(new[] { route.PrimaryServiceId }.Concat(route.SecondaryServiceIds));
        return _catalog.Knowledge.Where(document => document.Approved && ids.Contains(document.ServiceId) && !Injection.IsMatch(document.Content))
            .Take(3).Select(document => new Citation(document.Title, document.PublicUrl, document.Content)).ToList();
    }

    private GroundedResponse Draft(Inquiry inquiry, RouteRecommendation route, IReadOnlyList<Citation> citations, string channel)
    {
        string draft;
        if (inquiry.EmergencySignal) draft = inquiry.EmergencyGuidance!;
        else if (inquiry.DiscriminatoryInstructionDetected) draft = "I cannot recommend different service levels based on protected characteristics or neighborhood. A human reviewer can identify the correct service using only the service need.";
        else if (inquiry.InjectionDetected) draft = "Untrusted prompt injection was detected and ignored. A human reviewer can help identify the correct public service.";
        else if (inquiry.PiiFindings.Any(f => f.Category == "sensitive_data_request")) draft = "For your privacy, do not send passwords, Social Security numbers, or other credentials. Sensitive details are excluded from this draft. A human reviewer can help identify the correct public service.";
        else if (route.Status == "clarification_required") draft = $"I do not have enough approved information to choose a service. {route.ClarifyingQuestion}";
        else if (citations.Count == 0) draft = "I cannot answer this from approved public information. A human agent must review the request.";
        else draft = $"The proposed service is {_catalog.ServiceById(route.PrimaryServiceId!).Name}. {citations[0].Excerpt} [1] Review the cited public page before submitting.";
        if (inquiry.DetectedLanguage == "es") draft = $"Borrador en lenguaje sencillo: {draft} Un agente humano debe revisar esta respuesta.";
        return new GroundedResponse { ResponseId = NewId("resp"), InquiryId = inquiry.InquiryId, Channel = channel, Language = inquiry.DetectedLanguage, Draft = draft, Citations = citations, ApprovalStatus = "pending", AiDisclosure = Disclosure };
    }

    private WorkflowResult GetResult(string id) => _results.TryGetValue(id, out var result) ? result : throw new KeyNotFoundException($"Unknown response ID: {id}");

    private string BuildSafeSummary(string redacted, IReadOnlyList<PiiFinding> findings, bool injection, bool emergency)
    {
        if (emergency) return "Immediate danger was detected; routine service processing was stopped.";
        if (injection) return "A routine service request contained untrusted instructions.";
        var matchedServices = _catalog.Services
            .Where(service => service.Keywords.Any(keyword => Regex.IsMatch(redacted, $@"\b{Regex.Escape(keyword)}\b", RegexOptions.IgnoreCase)))
            .Select(service => service.Name)
            .Distinct()
            .ToList();
        if (matchedServices.Count > 0) return $"Constituent requested guidance related to {string.Join(" and ", matchedServices)}.";
        if (findings.Count > 0) return "Constituent requested public service guidance; sensitive details were redacted.";
        return "Constituent requested public service guidance.";
    }

    private static string BuildServiceScopedSummary(Inquiry inquiry, Service service)
    {
        var matchedTerms = service.Keywords
            .Where(keyword => Regex.IsMatch(inquiry.RedactedContent, $@"\b{Regex.Escape(keyword)}\b", RegexOptions.IgnoreCase))
            .Distinct(StringComparer.OrdinalIgnoreCase)
            .Take(3)
            .ToList();
        var scope = matchedTerms.Count == 0 ? "the configured service" : string.Join(", ", matchedTerms);
        return $"Service-specific handoff for {service.Name}: constituent requested guidance about {scope}.";
    }

    private static string NewId(string prefix) => $"{prefix}-{Guid.NewGuid():N}"[..(prefix.Length + 13)];
}

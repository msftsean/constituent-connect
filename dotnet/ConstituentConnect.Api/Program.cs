using ConstituentConnect.Api;

var builder = WebApplication.CreateBuilder(args);
builder.Services.ConfigureHttpJsonOptions(options =>
    options.SerializerOptions.PropertyNamingPolicy = System.Text.Json.JsonNamingPolicy.CamelCase);
builder.Services.AddSingleton<ConstituentWorkflow>();

var app = builder.Build();
app.UseDefaultFiles();
app.UseStaticFiles();

app.MapGet("/health", () => Results.Ok(new { status = "healthy", mode = "local-synthetic", modelCalls = 0 }));
app.MapPost("/api/intake", (IntakeRequest request, ConstituentWorkflow workflow) =>
    Results.Ok(workflow.AssessIntake(request.Message, request.Channel, request.Language)));
app.MapPost("/api/respond", (IntakeRequest request, ConstituentWorkflow workflow) =>
    Results.Ok(workflow.Process(request.Message, request.Channel, request.Language)));
app.MapPost("/api/responses/{responseId}/approve", (string responseId, ApprovalRequest request, HttpRequest httpRequest, ConstituentWorkflow workflow) =>
{
    try
    {
        var approverRole = httpRequest.Headers[ConstituentWorkflow.ApprovalAuthorityHeader].ToString();
        var approverToken = httpRequest.Headers[ConstituentWorkflow.ApprovalTokenHeader].ToString();
        return Results.Ok(workflow.ApproveResponse(responseId, request.Reviewer, request.EditedText, request.Decision, approverRole, approverToken));
    }
    catch (KeyNotFoundException exception) { return Results.NotFound(new { error = exception.Message }); }
    catch (UnauthorizedAccessException exception) { return Results.Json(new { error = exception.Message }, statusCode: StatusCodes.Status403Forbidden); }
    catch (InvalidOperationException exception) { return Results.Conflict(new { error = exception.Message }); }
});
app.MapPost("/api/cases", (CaseRequest request, ConstituentWorkflow workflow) =>
{
    try { return Results.Created($"/api/cases/{request.ResponseId}", workflow.CreateCase(request.ResponseId)); }
    catch (KeyNotFoundException exception) { return Results.NotFound(new { error = exception.Message }); }
    catch (InvalidOperationException exception) { return Results.Conflict(new { error = exception.Message }); }
});

app.Run();

public partial class Program;

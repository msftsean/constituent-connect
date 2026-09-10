using System.Net;
using System.Net.Http.Json;
using ConstituentConnect.Api;
using Microsoft.AspNetCore.Mvc.Testing;

namespace ConstituentConnect.Tests;

public sealed class ApiTests(WebApplicationFactory<Program> factory) : IClassFixture<WebApplicationFactory<Program>>
{
    [Fact]
    public async Task End_to_end_api_keeps_approval_gate_before_case_creation()
    {
        var response = await factory.CreateClient().PostAsJsonAsync("/api/respond", new
        {
            channel = "web",
            message = "Where do I apply for a replacement professional license?"
        });

        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        var result = await response.Content.ReadFromJsonAsync<WorkflowResult>();
        Assert.NotNull(result);
        Assert.Equal("pending", result.Response.ApprovalStatus);

        var blocked = await factory.CreateClient().PostAsJsonAsync("/api/cases", new
        {
            responseId = result.Response.ResponseId
        });
        Assert.Equal(HttpStatusCode.Conflict, blocked.StatusCode);

        var approval = await factory.CreateClient().PostAsJsonAsync(
            $"/api/responses/{result.Response.ResponseId}/approve", new { reviewer = "human-reviewer" });
        Assert.Equal(HttpStatusCode.OK, approval.StatusCode);

        var created = await factory.CreateClient().PostAsJsonAsync("/api/cases", new
        {
            responseId = result.Response.ResponseId
        });
        Assert.Equal(HttpStatusCode.Created, created.StatusCode);
    }
}

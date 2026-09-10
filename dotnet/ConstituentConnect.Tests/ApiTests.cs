using System.Net;
using System.Net.Http.Json;
using ConstituentConnect.Api;
using Microsoft.AspNetCore.Mvc.Testing;

namespace ConstituentConnect.Tests;

public sealed class ApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> factory;
    public ApiTests(WebApplicationFactory<Program> factory)
    {
        this.factory = factory;
        SetToken();
    }
    private static bool SetToken() { Environment.SetEnvironmentVariable("CONSTITUENT_CONNECT_APPROVER_TOKEN", "test-approver-token"); Environment.SetEnvironmentVariable("CONSTITUENT_CONNECT_APPROVER_ID", "test-configured-reviewer"); return true; }
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
            $"/api/responses/{result.Response.ResponseId}/approve", new { reviewer = "untrusted-body-value" });
        Assert.Equal(HttpStatusCode.Forbidden, approval.StatusCode);

        var authorizedRequest = new HttpRequestMessage(HttpMethod.Post, $"/api/responses/{result.Response.ResponseId}/approve")
        {
            Content = JsonContent.Create(new { reviewer = "untrusted-body-value" })
        };
        authorizedRequest.Headers.Add(ConstituentWorkflow.ApprovalAuthorityHeader, ConstituentWorkflow.ApprovalAuthorityRole);
        authorizedRequest.Headers.Add(ConstituentWorkflow.ApprovalTokenHeader, "test-approver-token");
        approval = await factory.CreateClient().SendAsync(authorizedRequest);
        Assert.Equal(HttpStatusCode.OK, approval.StatusCode);
        var approved = await approval.Content.ReadFromJsonAsync<GroundedResponse>();
        Assert.NotNull(approved);
        Assert.Equal("test-configured-reviewer", approved.ApprovedBy);
        Assert.NotEqual("untrusted-body-value", approved.ApprovedBy);

        var created = await factory.CreateClient().PostAsJsonAsync("/api/cases", new
        {
            responseId = result.Response.ResponseId
        });
        Assert.Equal(HttpStatusCode.Created, created.StatusCode);
    }

    [Fact]
    public async Task Response_does_not_serialize_raw_constituent_content_or_pii()
    {
        const string rawContent = "My full name is Ada Example and my SSN is 123-45-6789. Where do I get a replacement professional license?";
        var response = await factory.CreateClient().PostAsJsonAsync("/api/respond", new
        {
            channel = "web",
            message = rawContent
        });

        var json = await response.Content.ReadAsStringAsync();
        Assert.DoesNotContain(rawContent, json, StringComparison.Ordinal);
        Assert.DoesNotContain("123-45-6789", json, StringComparison.Ordinal);
        Assert.DoesNotContain("Ada Example", json, StringComparison.Ordinal);
        Assert.DoesNotContain("redactedContent", json, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public async Task Mixed_historical_and_current_danger_uses_emergency_exit()
    {
        var response = await factory.CreateClient().PostAsJsonAsync("/api/respond", new
        {
            channel = "web",
            message = "Last year there was a fire, but there is smoke here now and someone is trapped."
        });

        var result = await response.Content.ReadFromJsonAsync<WorkflowResult>();
        Assert.NotNull(result);
        Assert.True(result.Inquiry.EmergencySignal);
        Assert.Equal("emergency_exit", result.Route.Status);
        Assert.Null(result.Route.PrimaryServiceId);
        Assert.Contains("cannot dispatch", result.Response.Draft, StringComparison.OrdinalIgnoreCase);
    }

    [Fact]
    public async Task Cross_agency_case_api_returns_service_scoped_handoffs()
    {
        var client = factory.CreateClient();
        var response = await client.PostAsJsonAsync("/api/respond", new
        {
            channel = "email",
            message = "My business move affects both my license and tax registration."
        });
        var result = await response.Content.ReadFromJsonAsync<WorkflowResult>();
        Assert.NotNull(result);

        using var approvalRequest = new HttpRequestMessage(HttpMethod.Post, $"/api/responses/{result.Response.ResponseId}/approve")
        {
            Content = JsonContent.Create(new { reviewer = "untrusted-body-value" })
        };
        approvalRequest.Headers.Add(ConstituentWorkflow.ApprovalAuthorityHeader, ConstituentWorkflow.ApprovalAuthorityRole);
        approvalRequest.Headers.Add(ConstituentWorkflow.ApprovalTokenHeader, "test-approver-token");
        var approval = await client.SendAsync(approvalRequest);
        Assert.Equal(HttpStatusCode.OK, approval.StatusCode);

        var createdResponse = await client.PostAsJsonAsync("/api/cases", new { responseId = result.Response.ResponseId });
        Assert.Equal(HttpStatusCode.Created, createdResponse.StatusCode);
        var created = await createdResponse.Content.ReadFromJsonAsync<CaseRecord>();
        Assert.NotNull(created);
        var licensing = created.AgencyWorkItems.Single(item => item.ServiceId == "professional-licensing");
        var tax = created.AgencyWorkItems.Single(item => item.ServiceId == "tax-registration");
        Assert.DoesNotContain("tax registration", licensing.Summary, StringComparison.OrdinalIgnoreCase);
        Assert.DoesNotContain("license", tax.Summary, StringComparison.OrdinalIgnoreCase);
    }
}

using System.Text.Json;

namespace ConstituentConnect.Api;

public sealed record Service(string ServiceId, string AgencyId, string Name, string QueueId, IReadOnlyList<string> Keywords);
public sealed record KnowledgeDocument(string ServiceId, string Title, string PublicUrl, string Content, bool Approved);

public sealed class Catalog
{
    public IReadOnlyList<Service> Services { get; }
    public IReadOnlyList<KnowledgeDocument> Knowledge { get; }
    public double MinimumConfidence { get; }
    public double SecondaryConfidence { get; }

    public Catalog()
    {
        var root = FindRepositoryRoot();
        var options = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true,
            PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower
        };
        Services = JsonSerializer.Deserialize<List<Service>>(File.ReadAllText(Path.Combine(root, "data", "services.json")), options)
            ?? throw new InvalidOperationException("Synthetic service catalog is empty.");
        Knowledge = JsonSerializer.Deserialize<List<KnowledgeDocument>>(File.ReadAllText(Path.Combine(root, "data", "public_knowledge.json")), options)
            ?? throw new InvalidOperationException("Synthetic public knowledge catalog is empty.");
        using var appConfig = JsonDocument.Parse(File.ReadAllText(Path.Combine(root, "config", "app.json")));
        MinimumConfidence = appConfig.RootElement.GetProperty("routing").GetProperty("minimum_confidence").GetDouble();
        SecondaryConfidence = appConfig.RootElement.GetProperty("routing").GetProperty("secondary_confidence").GetDouble();
    }

    public Service ServiceById(string id) => Services.First(service => service.ServiceId == id);

    public static string FindRepositoryRoot()
    {
        foreach (var startingPoint in new[] { Directory.GetCurrentDirectory(), AppContext.BaseDirectory })
        {
            for (var directory = new DirectoryInfo(startingPoint); directory is not null; directory = directory.Parent)
            {
                if (File.Exists(Path.Combine(directory.FullName, "CONTEXT.md")) &&
                    File.Exists(Path.Combine(directory.FullName, "data", "services.json")))
                    return directory.FullName;
            }
        }
        throw new DirectoryNotFoundException("Could not locate the Constituent Connect synthetic catalog.");
    }
}

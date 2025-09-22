#:package Aspire.Hosting.DevTunnels@9.6.0-preview.1.25470.2
#:package CommunityToolkit.Aspire.Hosting.McpInspector@9.8.0-beta.389
#:package Aspire.Hosting.Python@9.6.0-preview.1.25470.2
#:sdk Aspire.AppHost.Sdk@9.6.0-preview.1.25470.2

var builder = DistributedApplication.CreateBuilder(args);

var inspector = builder.AddMcpInspector("mcp-inspector");

var tunnel = builder.AddDevTunnel("dev-tunnel");

var pyMcpServer = builder.AddPythonApp(
    name: "pymcp",
    appDirectory: "pymcp",
    scriptPath: "main.py",
    virtualEnvironmentPath: Path.Combine(builder.AppHostDirectory, ".venv")
    )
    .WithHttpEndpoint(env: "PORT")
    .WithUrl("/mcp", "Mcp Server")
    .WithVsCodeMcpUrl();

tunnel.WithReference(pyMcpServer, allowAnonymous: true);

inspector.WithMcpServer(pyMcpServer);

builder.Build().Run();

#region MCP Extension
public static class McpExtensions
{
    public static IResourceBuilder<T> WithVsCodeMcpUrl<T>(this IResourceBuilder<T> builder, string mcpPath = "/mcp")
        where T : IResourceWithEndpoints
    {
        return builder.WithUrls(context =>
        {
            var httpEndpoint = builder.GetEndpoint("http")!;
            var json = $$"""
            {
                "name": "{{builder.Resource.Name}}",
                "type": "http",
                "url": "{{httpEndpoint.Url}}/{{mcpPath.TrimStart('/')}}"
            }
            """;

            context.Urls.Add(new ResourceUrlAnnotation
            {
                Url = "vscode:mcp/install?" + Uri.EscapeDataString(json),
                DisplayText = "Install MCP"
            });
        });
    }
}
#endregion
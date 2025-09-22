#:sdk Aspire.AppHost.Sdk@9.6.0-preview.1.25469.18
#:package Aspire.Hosting.NodeJs@9.6.0-preview.1.25469.18
#:package CommunityToolkit.Aspire.Hosting.NodeJS.Extensions@9.8.0-beta.389
#:project Api

var builder = DistributedApplication.CreateBuilder(args);

var api = builder.AddProject<Projects.Api>("api");

builder.AddViteApp("frontend", "frontend")
       .WithNpmPackageInstallation()
       .WithEnvironment("BACKEND_URL", api.GetEndpoint("http"));

builder.Build().Run();

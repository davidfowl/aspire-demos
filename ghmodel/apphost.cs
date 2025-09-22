#:sdk Aspire.AppHost.Sdk@9.6.0-preview.1.25469.18

#:package Aspire.Hosting.Yarp@9.6.0-preview.1.25469.18
#:package Aspire.Hosting.GitHub.Models@9.6.0-preview.1.25469.18
#:package Aspire.Hosting.NodeJs@9.6.0-preview.1.25469.18
#:package CommunityToolkit.Aspire.Hosting.NodeJS.Extensions@9.8.0-beta.389

using Aspire.Hosting.GitHub;

var builder = DistributedApplication.CreateBuilder(args);

var model = builder.AddGitHubModel("model", GitHubModel.OpenAI.OpenAIGpt5Mini);

var be = builder.AddNpmApp("be", "backend")
       .WithNpmPackageInstallation()
       .WithHttpEndpoint(env: "PORT")
       .WithHttpHealthCheck("/health")
       .WithReference(model);

builder.AddYarp("fe")
       .WithStaticFiles("site")
       .WithConfiguration(c => c.AddRoute(be));

builder.Build().Run();

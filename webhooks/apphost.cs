#:sdk Aspire.AppHost.Sdk@9.6.0-preview.1.25470.2
#:project IngestionService 
#:package Aspire.Hosting.DevTunnels@9.6.0-preview.1.25470.2
#:package Aspire.Hosting.Azure.Storage@9.6.0-preview.1.25470.2
#:package Aspire.Hosting.Azure.AppContainers@9.6.0-preview.1.25470.2

var builder = DistributedApplication.CreateBuilder(args);

builder.AddAzureContainerAppEnvironment("env");

var webhookSecret = builder.AddParameter("webhook-secret", secret: true);

var tunnel = builder.AddDevTunnel("tunnel");

var storage = builder.AddAzureStorage("storage")
                     .RunAsEmulator(c => c.WithLifetime(ContainerLifetime.Persistent));

var events = storage.AddBlobContainer("events");

var ingestion = builder.AddProject<Projects.IngestionService>("ingestion-service")
    .WithReference(events)
    .WithEnvironment("Github__WebhookSecret", webhookSecret)
    .PublishAsAzureContainerApp((_, app) =>
    {
        // Scale to zero to save costs when not in use
        app.Template.Scale.MinReplicas = 0;
    });

tunnel.WithReference(ingestion, allowAnonymous: true);

builder.Build().Run();

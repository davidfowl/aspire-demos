using Azure.Storage.Blobs;
using Microsoft.AspNetCore.HttpLogging;

var builder = WebApplication.CreateBuilder(args);

builder.AddServiceDefaults();

builder.AddAzureBlobContainerClient("events");

builder.Services.AddHttpLogging(o =>
{
    o.LoggingFields = HttpLoggingFields.All;
});

builder.Services.AddSingleton<GithubWebhookSecret>();

var app = builder.Build();

app.UseHttpLogging();

app.MapDefaultEndpoints();

app.MapPost("/webhook/github", async (GithubWebHook webhook, BlobContainerClient blobContainerClient, ILoggerFactory loggerFactory) =>
{
    if (webhook.Result is not null)
    {
        return webhook.Result;
    }

    var eventData = webhook.EventData!;

    var logger = loggerFactory.CreateLogger("GitHubWebhook");
    var eventName = eventData.EventName;
    var deliveryId = eventData.DeliveryId;
    var payloadBytes = eventData.PayloadBytes;

    // Persist payload
    var blobName = $"{deliveryId}-{eventName}.json";
    var blobClient = blobContainerClient.GetBlobClient(blobName);
    var binaryData = BinaryData.FromBytes(payloadBytes);
    await blobClient.UploadAsync(binaryData, overwrite: true);

    logger.LogInformation("Stored GitHub event {Event} (delivery {DeliveryId}) in blob {BlobName}", eventName, deliveryId, blobName);

    return Results.Ok(new { BlobName = blobName });
});

app.Run();

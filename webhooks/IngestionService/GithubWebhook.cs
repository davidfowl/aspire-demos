using System.Reflection;
using System.Security.Cryptography;
using System.Text;

public class GithubWebhookSecret
{
    public byte[] Key { get; }

    public GithubWebhookSecret(IConfiguration configuration)
    {
        var value = configuration["GitHub:WebhookSecret"];
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new InvalidOperationException("GitHub:WebhookSecret configuration value is not set.");
        }

        Key = Encoding.UTF8.GetBytes(value);
    }
}

public class GithubWebHookEventData
{
    public required string EventName { get; init; }
    public required string DeliveryId { get; init; }
    public required byte[] PayloadBytes { get; init; }
}

public class GithubWebHook : IBindableFromHttpContext<GithubWebHook>
{
    public GithubWebHookEventData? EventData { get; init; }
    public IResult? Result { get; init; }

    public static async ValueTask<GithubWebHook?> BindAsync(HttpContext context, ParameterInfo parameter)
    {
        var githubWebhookSecret = context.RequestServices.GetRequiredService<GithubWebhookSecret>();
        var loggerFactory = context.RequestServices.GetRequiredService<ILoggerFactory>();
        var logger = loggerFactory.CreateLogger<GithubWebHook>();

        var request = context.Request;

        if (!request.Headers.TryGetValue("X-GitHub-Event", out var eventNameValues))
        {
            return new GithubWebHook { Result = Results.BadRequest("Missing X-GitHub-Event header") };
        }

        var eventName = eventNameValues.ToString();

        if (!request.Headers.TryGetValue("X-GitHub-Delivery", out var deliveryIdValues))
        {
            return new GithubWebHook { Result = Results.BadRequest("Missing X-GitHub-Delivery header") };
        }

        var deliveryId = deliveryIdValues.ToString();

        var signatureHeader = request.Headers.TryGetValue("X-Hub-Signature-256", out var sig) ? sig.ToString() : null;

        if (string.IsNullOrEmpty(signatureHeader))
        {
            logger.LogWarning("Missing signature header X-Hub-Signature-256");
            return new GithubWebHook { Result = Results.BadRequest("Missing signature header") };
        }

        // Buffer body
        using var ms = new MemoryStream();
        await request.Body.CopyToAsync(ms);
        var payloadBytes = ms.ToArray();

        if (!VerifySignature(githubWebhookSecret.Key, payloadBytes, signatureHeader))
        {
            logger.LogWarning("Invalid signature for delivery {DeliveryId}", deliveryId);
            return new GithubWebHook { Result = Results.Unauthorized() };
        }

        if (string.Equals(eventName, "ping", StringComparison.OrdinalIgnoreCase))
        {
            logger.LogInformation("Received ping delivery {DeliveryId}", deliveryId);
            return new GithubWebHook { Result = Results.Ok(new { Message = "pong", DeliveryId = deliveryId }) };
        }

        context.Request.Body = new MemoryStream(payloadBytes);

        return new GithubWebHook
        {
            EventData = new GithubWebHookEventData
            {
                EventName = eventName,
                DeliveryId = deliveryId,
                PayloadBytes = payloadBytes
            }
        };
    }

    private static bool VerifySignature(byte[] secret, byte[] payload, string signatureHeader)
    {
        const string prefix = "sha256=";
        if (!signatureHeader.StartsWith(prefix, StringComparison.OrdinalIgnoreCase))
        {
            return false;
        }
        var signature = signatureHeader[prefix.Length..];
        var hash = HMACSHA256.HashData(secret, payload);
        var hex = Convert.ToHexStringLower(hash);
        return CryptographicOperations.FixedTimeEquals(Encoding.ASCII.GetBytes(hex), Encoding.ASCII.GetBytes(signature));
    }
}

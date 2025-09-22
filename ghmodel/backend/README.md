# CRUD Backend with Quote Endpoint

This backend is a simple Express API that exposes:

- `GET /health` – health check
- `GET /quote` – returns an inspirational short programming/productivity quote generated via GitHub Models (OpenAI-compatible API).

## Prerequisites

- Node.js 18+ (for native fetch / ESM)
- A GitHub Models connection string stored in env var `ConnectionStrings__GitHubModels` with the format:

```bash
Endpoint=https://models.github.ai/inference;Key=YOUR_KEY;Model=MODEL_ID
```

Set it as an environment variable:

```bash
export ConnectionStrings__GitHubModels="Endpoint=https://models.github.ai/inference;Key=YOUR_KEY;Model=gpt-4o-mini"
```

Replace `gpt-4o-mini` (or similar) with the specific model you have access to.

## Install

```bash
cd backend
npm install
```

## Run

```bash
npm start
```

Server listens on `PORT` env var or 3000 by default.

## Example Request

```bash
curl http://localhost:3000/quote
```

Response:

```json
{ "quote": "Small, steady commits keep big ideas moving." }
```

If the connection string is invalid or missing, `/quote` responds like:

```json
{
  "error": "Model endpoint not configured.",
  "details": ["Environment variable ConnectionStrings__GitHubModels is missing or empty."]
}
```

## Implementation Notes

- Connection string is parsed via `parseConnectionString('GitHubModels')` which performs validation and returns `{ endpoint, key, model, isValid, errors }`.
- Uses the `openai` npm package pointed at the GitHub Models inference endpoint via `baseURL`.
- Validation errors are logged once at startup and echoed (sanitized) in the `/quote` response.

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| 500 error + details array | Missing or malformed env var | Set `ConnectionStrings__GitHubModels` correctly |
| 502 error: No content returned | Empty model response | Retry; check model name correctness |
| Network / 401 errors | Invalid key | Regenerate key / verify token |

## License

Sample code for demo purposes.

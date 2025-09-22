// Utility for parsing GitHub Models style connection strings.
// Format value example:
// Endpoint=https://models.github.ai/inference;Key=key;Model=model
// Stored in env var: ConnectionStrings__GitHubModels

export function parseConnectionString(name, { throwOnError = false } = {}) {
  const errors = [];
  const envKey = `ConnectionStrings__${name}`;
  const cs = process.env[envKey];
  if (!cs || typeof cs !== 'string') {
    errors.push(`Environment variable ${envKey} is missing or empty.`);
    const result = { endpoint: undefined, key: undefined, model: undefined, isValid: false, errors };
    if (throwOnError) throw new Error(errors.join('\n'));
    return result;
  }
  const parts = cs.split(';').filter(p => p.trim().length > 0);
  const map = {};
  for (const part of parts) {
    const idx = part.indexOf('=');
    if (idx === -1) continue;
    const k = part.slice(0, idx).trim();
    const v = part.slice(idx + 1).trim();
    if (k && v) {
      map[k.toLowerCase()] = v;
    }
  }
  const endpoint = map['endpoint'];
  const key = map['key'];
  const model = map['model'];
  if (!endpoint) errors.push('Missing Endpoint=... segment.');
  if (!key) errors.push('Missing Key=... segment.');
  if (!model) errors.push('Missing Model=... segment.');
  const result = { endpoint, key, model, isValid: errors.length === 0, errors };
  if (throwOnError && errors.length) throw new Error(errors.join('\n'));
  return result;
}
